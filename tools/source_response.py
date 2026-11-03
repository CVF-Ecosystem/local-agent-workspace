#!/usr/bin/env python3
"""Bounded offline response screening; never confirms source identity or intake."""
import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from datetime import timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

BODY_LIMIT = 1024 * 1024
HEADER_LIMIT = 64 * 1024
INPUT_LIMIT = 2 * 1024 * 1024
MAX_DEPTH = 64
MAX_EVENTS = 20000


class InputError(ValueError):
    """Invalid input; exception text is deliberately never printed."""


class ParseLimit(ValueError):
    pass


class _Signals(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = []
        self.visible = []
        self.password = False
        self.challenge = False
        self.events = 0
        self.malformed = False
        self.saw_tag = False

    def event(self):
        self.events += 1
        if self.events > MAX_EVENTS:
            raise ParseLimit()

    def handle_starttag(self, tag, attrs):
        self.event()
        self.saw_tag = True
        a = dict(attrs)
        # Duplicate attributes have inconsistent browser/parser precedence.
        # Never allow ambiguous markup to hide a password/challenge signal.
        if len(a) != len(attrs):
            self.malformed = True
        style = re.sub(r'\s+', '', (a.get('style') or '').lower())
        classes = (a.get('class') or '').lower().split()
        hidden = (bool(self.stack and self.stack[-1][1]) or
                  tag in ('script', 'style', 'template', 'noscript') or
                  'hidden' in a or (a.get('aria-hidden') or '').lower() == 'true' or
                  'display:none' in style or 'visibility:hidden' in style or
                  'hidden' in classes or 'd-none' in classes or
                  (a.get('type') or '').lower() == 'hidden')
        if tag not in self.VOID:
            if len(self.stack) >= MAX_DEPTH:
                raise ParseLimit()
            self.stack.append((tag, hidden))
        if hidden:
            return
        marker = ' '.join(a.get(k) or '' for k in ('id', 'class', 'action')).lower()
        if tag == 'form' and any(x in marker for x in
                ('challenge-form', 'challenge-platform', 'cf-challenge', 'captcha-form')):
            self.challenge = True
        if tag == 'input' and (a.get('type') or '').lower() == 'password':
            self.password = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        self.event()
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.malformed = True
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.event()
        if self.stack and self.stack[-1][1]:
            return
        if any(t == 'title' for t, _ in self.stack):
            self.title.append(data)
        else:
            self.visible.append(data)

    def handle_comment(self, data):
        self.event()

    def handle_decl(self, decl):
        self.event()


def _validated(status, headers, body, expected):
    if type(status) is not int or not 100 <= status <= 599 or type(expected) is not bool:
        raise InputError()
    if not isinstance(headers, dict) or not isinstance(body, (bytes, str)):
        raise InputError()
    if isinstance(body, str):
        if len(body) > BODY_LIMIT:
            raise InputError()
        body = body.encode('utf-8')
    if len(body) > BODY_LIMIT:
        raise InputError()
    h, size = {}, 0
    for k, v in headers.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise InputError()
        size += len(k.encode('utf-8')) + len(v.encode('utf-8'))
        if size > HEADER_LIMIT or not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", k):
            raise InputError()
        if '\r' in v or '\n' in v or '\x00' in v or k.lower() in h:
            raise InputError()
        h[k.lower()] = v
    return h, body


def _retry(value):
    value = value.strip()
    if re.fullmatch(r'[0-9]{1,10}', value):
        return {'kind': 'seconds', 'value': int(value)}
    # Accept only the fixed HTTP IMF-fixdate shape, never return arbitrary text.
    if not re.fullmatch(r'[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT', value):
        return None
    try:
        dt = parsedate_to_datetime(value)
        return {'kind': 'date', 'value': dt.astimezone(timezone.utc).isoformat()}
    except (ValueError, TypeError, OverflowError):
        return None


def _result(status, reasons, evidence=None):
    return {'status': status, 'reasoncodes': reasons, 'safe_evidence': evidence or {},
            'identity_verified': False, 'fulltext_verified': False, 'importable': False}


def classify_response(status, headers, body, expected_content=False):
    """Screen bytes/UTF-8 HTML offline. Caller contract only permits later parsing.

    Invalid API input returns unknown/input_error. No input data is echoed.
    This is bounded screening, not an OS sandbox or a full HTML/PDF parser.
    """
    try:
        h, raw = _validated(status, headers, body, expected_content)
    except (InputError, UnicodeError, ValueError, TypeError, OverflowError):
        return _result('unknown', ['input_error'])
    evidence = {'http_status': status, 'body_bytes': len(raw),
                'body_sha256': hashlib.sha256(raw).hexdigest()}
    if 'retry-after' in h:
        evidence['retry_after'] = _retry(h['retry-after'])
    reasons = ['http_' + str(status)] if status in (401, 403, 429) else []
    if h.get('cf-mitigated', '').strip().lower() == 'challenge':
        reasons.append('cf_mitigated_challenge')
    if reasons:
        return _result('blocked', reasons, evidence)
    mime = h.get('content-type', '').split(';', 1)[0].strip().lower()
    # A PDF or binary body is never treated as HTML evidence, even with an HTML MIME.
    if raw.startswith(b'%PDF-') or b'\x00' in raw:
        return _result('unknown', ['non_html_body'], evidence)
    try:
        text = raw.decode('utf-8')
    except UnicodeError:
        return _result('unknown', ['invalid_utf8'], evidence)
    html_shape = re.match(r'\s*(?:<!doctype\s+html\b|<(?:html|head|body|title|main|div|form|p|article|section)\b)', text, re.I)
    if mime not in ('', 'text/html', 'application/xhtml+xml') or not html_shape:
        return _result('unknown', ['non_html_body'], evidence)
    parser = _Signals()
    try:
        parser.feed(text)
        # feed buffers unfinished tags/comments; close otherwise treats them as text.
        buffered_markup = bool(parser.rawdata)
        parser.close()
    except ParseLimit:
        return _result('unknown', ['parser_limit'], evidence)
    except (ValueError, AssertionError, RecursionError):
        return _result('unknown', ['html_parse_error'], evidence)
    title = ' '.join(' '.join(parser.title).casefold().split())
    visible = ' '.join(' '.join(parser.visible).casefold().split())
    if any(x in title for x in ('just a moment', 'attention required', 'checking your browser',
                               'verify you are human', 'xác minh bạn là người')):
        reasons.append('challenge_title')
    if parser.challenge:
        reasons.append('challenge_form')
    if any(x in visible for x in ('verify you are human', 'verify you are a human',
            'checking your browser', 'xác minh bạn là người', 'xác minh bạn không phải là robot')):
        reasons.append('visible_human_check')
    if any(x in title + ' ' + visible for x in ('login required', 'sign in required',
            'please log in to continue', 'please sign in to continue',
            'vui lòng đăng nhập để tiếp tục', 'đăng nhập để tiếp tục', 'yêu cầu đăng nhập')):
        reasons.append('login_required')
    if reasons:
        return _result('blocked', reasons, evidence)
    if parser.password:
        return _result('unknown', ['visible_login_form'], evidence)
    if buffered_markup or parser.stack or parser.malformed or not parser.saw_tag:
        return _result('unknown', ['html_incomplete'], evidence)
    if not 200 <= status < 300:
        return _result('unknown', ['http_not_success'], evidence)
    return _result('allow_parse' if expected_content else 'unknown',
                   ['expected_content' if expected_content else 'missing_contract'], evidence)


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise InputError()
        out[key] = value
    return out


def _constant(value):
    raise InputError()


def _read_input():
    data = sys.stdin.buffer.read(INPUT_LIMIT + 1)
    if len(data) > INPUT_LIMIT:
        raise InputError()
    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_constant)
        if not isinstance(value, dict) or set(value) - {'status', 'headers', 'body_base64', 'expected_content'}:
            raise InputError()
        if not {'status', 'headers', 'body_base64'} <= set(value) or not isinstance(value['body_base64'], str):
            raise InputError()
        encoded = value['body_base64']
        if len(encoded) > ((BODY_LIMIT + 2) // 3) * 4:
            raise InputError()
        raw = base64.b64decode(encoded, validate=True)
        if base64.b64encode(raw).decode('ascii') != encoded:
            raise InputError()
        expected = value.get('expected_content', False)
        _validated(value['status'], value['headers'], raw, expected)
        return classify_response(value['status'], value['headers'], raw, expected)
    except (ValueError, TypeError, KeyError, UnicodeError, binascii.Error, RecursionError):
        raise InputError() from None


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError()


def main(argv=None):
    try:
        from .result_schema import make, emit
    except ImportError:
        from result_schema import make, emit
    try:
        ap = _ArgumentParser(description='Kiểm phản hồi đã lưu qua JSON STDIN, offline; chưa phải nhận nguồn.')
        ap.parse_args(argv)
        check = _read_input()
        code = 0 if check['status'] == 'allow_parse' else 1
        state = 'success' if code == 0 else ('blocked' if check['status'] == 'blocked' else 'not_checked')
        result = make(state, code, 'Đã kiểm phản hồi offline; chưa phải nhận nguồn.',
                      changes=False, response_check=check)
    except (InputError, OSError):
        code = 2
        result = make('error', code, 'Đầu vào hoặc cách gọi không hợp lệ; chưa phải nhận nguồn.',
                      changes=False, response_check=_result('unknown', ['input_error']))
    emit(result)
    return code


if __name__ == '__main__':
    sys.exit(main())
