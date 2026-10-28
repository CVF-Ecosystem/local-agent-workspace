#!/usr/bin/env python3
"""Read-only exact quote presence / Kiểm trích dẫn nguyên văn trong vùng dòng.

Only declared plain-text or verified-extract UTF-8 sources are supported.
MATCH establishes textual presence, not entailment, authenticity or legal validity.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata

try:
    from . import result_schema
except ImportError:
    import result_schema

SOURCE_LIMIT = 8 * 1024 * 1024
QUOTE_LIMIT = 64 * 1024
NORMALIZATIONS = ('strict', 'nfc', 'nfc-whitespace')
SOURCE_KINDS = ('plain-text', 'verified-extract', 'unverified-extract', 'ocr', 'table')
REPARSE = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
SCOPE = ('Textual presence only; authenticity, extraction accuracy, entailment, '
         'completeness and current legal validity are not checked.')


class Unverified(Exception):
    """Source or quote file could not be safely inspected."""


def _plain_stat(path):
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & REPARSE:
        raise Unverified('Symlink/junction/reparse point is not supported.')
    return info


def _root(folder):
    path = Path(os.path.abspath(os.fspath(folder)))
    # Reject lexical traversal before abspath can erase it.
    if '..' in Path(folder).parts:
        raise ValueError('Workspace root must not contain traversal.')
    for item in (path,) + tuple(path.parents):
        if not stat.S_ISDIR(_plain_stat(item).st_mode):
            raise Unverified('Workspace root/ancestor is not a directory.')
    return path


def _bounded_path(root, name):
    if not isinstance(name, (str, os.PathLike)) or not os.fspath(name):
        raise ValueError('File path is required.')
    candidate = Path(name)
    if '..' in re.split(r'[/\\]', os.fspath(name)):
        raise ValueError('Traversal is not allowed.')
    candidate = Path(os.path.abspath(root / candidate))
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        raise ValueError('File path is outside workspace root.')
    current = root
    for part in relative.parts:
        current /= part
        _plain_stat(current)
    return candidate


def _snapshot(root, name, limit):
    path = _bounded_path(root, name)
    before = _plain_stat(path)
    if not stat.S_ISREG(before.st_mode):
        raise Unverified('Input is not a regular file.')
    if before.st_size > limit:
        raise Unverified('Input exceeds byte limit: ' + str(limit))
    with open(path, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(limit + 1)
        finished = os.fstat(stream.fileno())
    after = _plain_stat(path)
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if len(data) > limit or any(getattr(before, key) != getattr(item, key)
                                for item in (opened, finished, after) for key in fields):
        raise Unverified('Input changed while reading or exceeded byte limit.')
    # Also recheck the parent path after reading. This reduces accidental races;
    # this portable helper is not a race-proof adversarial filesystem boundary.
    _bounded_path(root, name)
    return data


def _normalize(text, mode):
    if mode == 'strict':
        return text
    text = unicodedata.normalize('NFC', text)
    return re.sub(r'\s+', ' ', text) if mode == 'nfc-whitespace' else text


def check_quote(root, source, expected_sha256, start_line, end_line, quote=None,
                quote_file=None, source_kind=None, normalization='strict'):
    """Return result-v1; no writes/network. Hash and match share one byte snapshot.

    Exit/result codes: 0 MATCH, 1 MISMATCH, 2 UNVERIFIED, 3 ERROR (input).
    Lines are 1-based inclusive, as Python str.splitlines(keepends=True).
    Source kind is a caller declaration, not independently verified provenance.
    """
    details = dict(normalization=normalization, source_kind=source_kind,
                   locator={'start_line': start_line, 'end_line': end_line})

    def outcome(verdict, message):
        status, code = {'MATCH': ('success', 0), 'MISMATCH': ('issues', 1),
                        'UNVERIFIED': ('not_checked', 2), 'ERROR': ('error', 3)}[verdict]
        return result_schema.make(status, code, message, changes=False,
                                  unchecked=[SCOPE], verdict=verdict, **details)

    try:
        if normalization not in NORMALIZATIONS:
            raise ValueError('Unknown normalization mode.')
        if source_kind not in SOURCE_KINDS and source_kind is not None:
            raise ValueError('Unknown source kind.')
        digest = re.sub(r'^sha256:', '', expected_sha256 or '')
        if not re.fullmatch(r'[0-9a-fA-F]{64}', digest):
            raise ValueError('Full expected SHA-256 (64 hex digits) is required.')
        if (type(start_line) is not int or type(end_line) is not int or
                start_line < 1 or end_line < start_line):
            raise ValueError('Locator requires 1 <= start-line <= end-line.')
        if (quote is None) == (quote_file is None):
            raise ValueError('Supply exactly one of quote or quote-file.')
        if quote is not None and not isinstance(quote, str):
            raise ValueError('Quote must be text.')
        if quote is not None and (not quote.strip() or len(quote.encode('utf-8')) > QUOTE_LIMIT):
            raise ValueError('Quote must be nonblank and at most 65536 UTF-8 bytes.')
        if source_kind not in ('plain-text', 'verified-extract'):
            return outcome('UNVERIFIED', 'Source kind missing or extraction/OCR/table is unverified.')
        workspace = _root(root)
        raw = _snapshot(workspace, source, SOURCE_LIMIT)
        actual = hashlib.sha256(raw).hexdigest()
        details['source_sha256'] = actual
        details['source'] = str(Path(os.path.abspath(workspace / source)).relative_to(workspace))
        if actual != digest.lower():
            return outcome('UNVERIFIED', 'Source revision differs from expected SHA-256.')
        text = raw.decode('utf-8', errors='strict')
        if '\x00' in text:
            raise Unverified('NUL-containing source is not supported text.')
        if quote_file is not None:
            quote = _snapshot(workspace, quote_file, QUOTE_LIMIT).decode('utf-8', errors='strict')
        if not quote.strip() or '\x00' in quote:
            raise ValueError('Quote must be nonblank text without NUL.')
        lines = text.splitlines(keepends=True)
        if end_line > len(lines):
            return outcome('UNVERIFIED', 'Locator is outside the source line range.')
        region = ''.join(lines[start_line - 1:end_line])
        present = _normalize(quote, normalization) in _normalize(region, normalization)
        return outcome('MATCH' if present else 'MISMATCH',
                       'Quote found within claimed lines.' if present else 'Quote absent from claimed lines.')
    except (Unverified, OSError, UnicodeError) as exc:
        return outcome('UNVERIFIED', str(exc))
    except (TypeError, ValueError) as exc:
        return outcome('ERROR', str(exc))


class QuoteParser(argparse.ArgumentParser):
    def error(self, message):
        # Invalid CLI input uses the same machine-readable envelope as API errors.
        self.print_usage(sys.stderr)
        result = result_schema.make('error', 3, message, changes=False, verdict='ERROR')
        if '--json' in getattr(self, 'raw_args', []):
            print(json.dumps(result, ensure_ascii=False))
        else:
            print('ERROR: ' + message, file=sys.stderr)
            result_schema.emit(result)
        self.exit(3)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = QuoteParser(description=__doc__)
    parser.raw_args = list(sys.argv[1:] if argv is None else argv)
    parser.add_argument('--root', required=True, help='Workspace root / thư mục được phép đọc')
    parser.add_argument('--source', required=True, help='UTF-8 source path inside root / nguồn')
    parser.add_argument('--expected-sha256', required=True, help='Full SHA256, optionally sha256: prefixed')
    parser.add_argument('--start-line', type=int, required=True, help='1-based inclusive / dòng đầu')
    parser.add_argument('--end-line', type=int, required=True, help='1-based inclusive / dòng cuối')
    quotes = parser.add_mutually_exclusive_group(required=True)
    quotes.add_argument('--quote', help='Literal text / câu trích')
    quotes.add_argument('--quote-file', help='UTF-8 quote file inside root; no newline stripped')
    parser.add_argument('--source-kind', choices=SOURCE_KINDS, help='Caller declaration; missing => UNVERIFIED')
    parser.add_argument('--normalization', choices=NORMALIZATIONS, default='strict')
    parser.add_argument('--json', action='store_true', help='Only JSON on stdout / chỉ JSON')
    args = parser.parse_args(parser.raw_args)
    result = check_quote(args.root, args.source, args.expected_sha256, args.start_line,
                         args.end_line, args.quote, args.quote_file, args.source_kind,
                         args.normalization)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(result['verdict'] + ': ' + result['message'])
        result_schema.emit(result)
    return result['code']


if __name__ == '__main__':
    sys.exit(main())
