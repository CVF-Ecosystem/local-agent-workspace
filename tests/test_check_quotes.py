"""Synthetic text fixtures only; no legal corpus or gold legal conclusions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools import check_quotes as cq

ROOT = Path(__file__).resolve().parents[1]


class QuoteChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.md'
        self.raw = 'Tiêu đề\r\nCâu đúng nguyên văn.\r\nOther line.\r\n'.encode('utf-8')
        self.source.write_bytes(self.raw)
        self.digest = hashlib.sha256(self.raw).hexdigest()

    def check(self, **kwargs):
        options = dict(root=self.root, source='source.md', expected_sha256=self.digest,
                       start_line=2, end_line=2, quote='Câu đúng nguyên văn.',
                       source_kind='plain-text')
        options.update(kwargs)
        return cq.check_quote(**options)

    def assert_verdict(self, verdict, result):
        self.assertEqual(result['verdict'], verdict, result)
        self.assertEqual(result['code'], {'MATCH': 0, 'MISMATCH': 1,
                                         'UNVERIFIED': 2, 'ERROR': 3}[verdict])
        self.assertFalse(result['changes'])
        self.assertEqual(result['schema'], 'local-agent-workspace/result-v1')

    def test_exact_match_binds_raw_hash_and_locator(self):
        result = self.check(expected_sha256='sha256:' + self.digest)
        self.assert_verdict('MATCH', result)
        self.assertEqual(result['source_sha256'], self.digest)
        self.assertEqual(result['locator'], {'start_line': 2, 'end_line': 2})
        self.assertEqual(result['normalization'], 'strict')
        self.assertIn('legal validity', result['unchecked'][0])

    def test_wrong_word(self):
        self.assert_verdict('MISMATCH', self.check(quote='Câu sai nguyên văn.'))

    def test_present_elsewhere_is_not_match(self):
        self.assert_verdict('MISMATCH', self.check(start_line=3, end_line=3))

    def test_multiline_only_inside_claimed_range(self):
        quote = 'nguyên văn.\r\nOther'
        self.assert_verdict('MISMATCH', self.check(quote=quote))
        self.assert_verdict('MATCH', self.check(quote=quote, end_line=3))

    def test_revision_mismatch(self):
        self.source.write_bytes(self.raw + b'changed')
        self.assert_verdict('UNVERIFIED', self.check())

    def test_hash_is_required_and_full(self):
        for digest in (None, '', self.digest[:16], 'z' * 64):
            with self.subTest(digest=digest):
                self.assert_verdict('ERROR', self.check(expected_sha256=digest))

    def test_missing_source(self):
        self.assert_verdict('UNVERIFIED', self.check(source='missing.txt'))

    def test_unreadable_source(self):
        with mock.patch('builtins.open', side_effect=PermissionError('denied')):
            self.assert_verdict('UNVERIFIED', self.check())

    def test_invalid_utf8_and_nul(self):
        for raw in (b'bad\xff', b'has\x00nul'):
            with self.subTest(raw=raw):
                self.source.write_bytes(raw)
                self.assert_verdict('UNVERIFIED', self.check(expected_sha256=hashlib.sha256(raw).hexdigest()))

    def test_ocr_table_missing_kind_and_unverified_extraction(self):
        for kind in ('ocr', 'table', 'unverified-extract', None):
            with self.subTest(kind=kind):
                self.assert_verdict('UNVERIFIED', self.check(source_kind=kind))

    def test_verified_extract_is_explicit_declaration(self):
        self.assert_verdict('MATCH', self.check(source_kind='verified-extract'))
        self.assert_verdict('ERROR', self.check(source_kind='pdf'))

    def test_strict_nfc_and_whitespace_modes_are_declared(self):
        quote = 'Ca\u0302u đúng nguyên văn.'
        self.assert_verdict('MISMATCH', self.check(quote=quote))
        result = self.check(quote=quote, normalization='nfc')
        self.assert_verdict('MATCH', result)
        self.assertEqual(result['normalization'], 'nfc')
        spaced = 'Câu\t đúng\nnguyên văn.'
        self.assert_verdict('MISMATCH', self.check(quote=spaced, normalization='nfc'))
        self.assert_verdict('MATCH', self.check(quote=spaced, normalization='nfc-whitespace'))

    def test_no_casefold_fuzzy_or_hyphen_fix(self):
        for quote in ('câu đúng nguyên văn.', 'Câu đung nguyên văn.', 'Câu đúng nguyên-văn.'):
            with self.subTest(quote=quote):
                self.assert_verdict('MISMATCH', self.check(quote=quote, normalization='nfc-whitespace'))

    def test_no_strip_in_whitespace_mode(self):
        self.assert_verdict('MISMATCH', self.check(quote=' Câu đúng nguyên văn.', normalization='nfc-whitespace'))

    def test_locator_invalid_or_out_of_bounds(self):
        for start, end in ((0, 2), (3, 2), (True, 2), ('2', 2)):
            self.assert_verdict('ERROR', self.check(start_line=start, end_line=end))
        self.assert_verdict('UNVERIFIED', self.check(end_line=4))

    def test_empty_and_ambiguous_quote_inputs(self):
        for quote in ('', ' \t', 42):
            self.assert_verdict('ERROR', self.check(quote=quote))
        self.assert_verdict('ERROR', self.check(quote=None))
        self.assert_verdict('ERROR', self.check(quote_file='quote.txt'))

    def test_quote_file_exact_newline_and_bad_encoding(self):
        path = self.root / 'quote.txt'
        path.write_bytes('Câu đúng nguyên văn.'.encode('utf-8'))
        self.assert_verdict('MATCH', self.check(quote=None, quote_file='quote.txt'))
        path.write_bytes('Câu đúng nguyên văn.\n'.encode('utf-8'))
        self.assert_verdict('MISMATCH', self.check(quote=None, quote_file='quote.txt'))
        path.write_bytes(b'\xff')
        self.assert_verdict('UNVERIFIED', self.check(quote=None, quote_file='quote.txt'))

    def test_limits_source_and_quote(self):
        with mock.patch.object(cq, 'SOURCE_LIMIT', 4):
            self.assert_verdict('UNVERIFIED', self.check())
        self.assert_verdict('ERROR', self.check(quote='x' * (cq.QUOTE_LIMIT + 1)))
        (self.root / 'quote.txt').write_bytes(b'x' * (cq.QUOTE_LIMIT + 1))
        self.assert_verdict('UNVERIFIED', self.check(quote=None, quote_file='quote.txt'))

    def test_traversal_and_absolute_outside_root(self):
        self.assert_verdict('ERROR', self.check(source='../source.md'))
        self.assert_verdict('ERROR', self.check(source=str(self.root.parent / 'outside.txt')))
        self.assert_verdict('ERROR', self.check(quote=None, quote_file='../outside.txt'))
        self.assert_verdict('MATCH', self.check(source=str(self.source)))

    def test_file_link_is_not_followed(self):
        linked = self.root / 'linked.md'
        try:
            linked.symlink_to(self.source)
        except OSError as exc:
            self.skipTest('Host does not permit symlink fixture: ' + str(exc))
        self.assert_verdict('UNVERIFIED', self.check(source='linked.md'))

    def test_reparse_point_detection(self):
        # A synthetic placeholder flag, not a claim of real cloud-only support.
        real_lstat = os.lstat

        def flagged(path):
            if Path(path) == self.source:
                return mock.Mock(st_mode=0, st_file_attributes=cq.REPARSE)
            return real_lstat(path)

        with mock.patch.object(cq.os, 'lstat', side_effect=flagged), mock.patch(
                'builtins.open', side_effect=AssertionError('Reparse source must not be read')):
            result = self.check()
        self.assert_verdict('UNVERIFIED', result)
        self.assertIn('reparse point', result['message'])

    def parent_link_fixture(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name)
        (target / 'source.md').write_bytes(self.raw)
        linked = self.root / 'linked'
        # Cleanup never recursively follows the fixture link to its outside target.
        self.assertEqual(linked.parent.resolve(), self.root.resolve())
        try:
            linked.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            if os.name != 'nt':
                self.skipTest('Directory symlink fixture unavailable: ' + str(exc))
            made = subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(linked), str(target)],
                                  capture_output=True, timeout=10)
            if made.returncode != 0:
                self.skipTest('Directory symlink unavailable (%s); junction creation exit %s: %s'
                              % (exc, made.returncode, made.stderr.decode(errors='replace')))
            self.addCleanup(os.rmdir, str(linked))
        else:
            self.addCleanup(linked.unlink)
        return linked, target

    def test_parent_link_not_followed(self):
        linked, target = self.parent_link_fixture()
        self.assert_verdict('MATCH', self.check())
        with mock.patch('builtins.open', side_effect=AssertionError('Linked source must not be read')):
            result = self.check(source='linked/source.md')
        self.assert_verdict('UNVERIFIED', result)
        self.assertIn('reparse point', result['message'])
        self.assertEqual((target / 'source.md').read_bytes(), self.raw)

    def test_root_link_not_followed(self):
        linked, target = self.parent_link_fixture()
        with mock.patch('builtins.open', side_effect=AssertionError('Linked root must not be read')):
            result = self.check(root=linked, source='source.md')
        self.assert_verdict('UNVERIFIED', result)
        self.assertIn('reparse point', result['message'])
        self.assertEqual((target / 'source.md').read_bytes(), self.raw)

    def test_changed_during_read_is_unverified(self):
        real_fstat = os.fstat
        calls = 0

        def changed(fd):
            nonlocal calls
            calls += 1
            value = real_fstat(fd)
            if calls == 2:
                return mock.Mock(st_dev=value.st_dev, st_ino=value.st_ino,
                                 st_size=value.st_size + 1, st_mtime_ns=value.st_mtime_ns,
                                 st_ctime_ns=value.st_ctime_ns)
            return value

        with mock.patch.object(cq.os, 'fstat', side_effect=changed):
            self.assert_verdict('UNVERIFIED', self.check())

    def test_hash_and_match_use_one_read_and_no_writes(self):
        real_open = open
        opened = []
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

        def readonly(path, mode='r', *args, **kwargs):
            self.assertEqual(mode, 'rb')
            opened.append(str(path))
            return real_open(path, mode, *args, **kwargs)

        with mock.patch('builtins.open', side_effect=readonly):
            self.assert_verdict('MATCH', self.check())
        self.assertEqual(opened, [str(self.source)])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def cli(self, *extra, complete=True):
        args = ['--root', str(self.root), '--source', 'source.md', '--expected-sha256', self.digest,
                '--start-line', '2', '--end-line', '2', '--source-kind', 'plain-text'] if complete else []
        env = dict(os.environ, PYTHONIOENCODING='cp1252:strict', PYTHONUTF8='0',
                   PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable, '-B', str(ROOT / 'tools/check_quotes.py'), *args, *extra],
                              capture_output=True, env=env, timeout=10)

    def test_cli_json_exit_codes(self):
        for quote, code, verdict in (('Câu đúng nguyên văn.', 0, 'MATCH'), ('wrong', 1, 'MISMATCH')):
            result = self.cli('--quote', quote, '--json')
            self.assertEqual(result.returncode, code, result.stderr.decode('utf-8'))
            self.assert_verdict(verdict, json.loads(result.stdout.decode('utf-8')))
        self.source.unlink()
        result = self.cli('--quote', 'anything', '--json')
        self.assertEqual(result.returncode, 2)
        self.assert_verdict('UNVERIFIED', json.loads(result.stdout.decode('utf-8')))

    def test_cli_input_error_json_and_utf8_help(self):
        result = self.cli('--không-hợp-lệ', '--json', complete=False)
        self.assertEqual(result.returncode, 3)
        self.assert_verdict('ERROR', json.loads(result.stdout.decode('utf-8')))
        result.stderr.decode('utf-8')
        help_result = self.cli('--help', complete=False)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn('Kiểm', help_result.stdout.decode('utf-8'))

    def test_cli_default_envelope(self):
        result = self.cli('--quote', 'Câu đúng nguyên văn.')
        self.assertEqual(result.returncode, 0)
        human, envelope = cq.result_schema.split_output(result.stdout.decode('utf-8'))
        self.assertTrue(human.startswith('MATCH:'))
        self.assert_verdict('MATCH', envelope)


if __name__ == '__main__':
    unittest.main()
