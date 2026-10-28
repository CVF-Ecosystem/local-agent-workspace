"""CLI help/errors under a legacy pipe encoding; no operational commands run."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import app
import check_package as cp
import setup_wizard

# Actual entry points inspected for help-before-effects; not inferred from __main__ alone.
CLIS = ('adopt_project', 'app', 'artifacts', 'audit_scripts', 'build_guides_html',
        'build_release', 'check_output', 'check_package', 'context_update', 'current_draft',
        'execution_profile', 'init_project', 'install_skills', 'library', 'native_agents',
        'new_project', 'office', 'office_compute', 'pack', 'publish_new', 'setup_wizard',
        'transaction', 'upgrade_package', 'vn_legal_docx', 'work_status')
REQUIRED = {'adopt_project': ['--project', '.', '--name', 'test'],
            'check_output': ['unused.docx'],
            'context_update': ['--target', 'state', '--content', 'unused', '--expected', 'sha256:' + '0' * 64],
            'current_draft': ['status'], 'init_project': ['--name', 'test'],
            'new_project': ['--name', 'test'], 'pack': ['list'], 'transaction': ['status']}


class LegacyEncoding(unittest.TestCase):
    def run_cli(self, name, argument):
        env = dict(os.environ, PYTHONIOENCODING='cp1252:strict', PYTHONUTF8='0',
                   PYTHONDONTWRITEBYTECODE='1')
        args = REQUIRED.get(name, []) if argument != '--help' else []
        return subprocess.run([sys.executable, str(ROOT / 'tools' / (name + '.py')), *args, argument],
                              cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, timeout=15)

    def test_help_and_unicode_bad_argument_use_utf8_on_both_streams(self):
        for name in CLIS:
            # P-CN1 historically maps argparse's help SystemExit to 2; its pinned bytes stay unchanged.
            for argument, expected in (('--help', 2 if name == 'publish_new' else 0), ('--không-hợp-lệ', 2)):
                with self.subTest(cli=name, argument=argument):
                    result = self.run_cli(name, argument)
                    out, err = result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
                    self.assertEqual(result.returncode, expected, out + err)
                    self.assertNotIn('UnicodeEncodeError', out + err)
                    if argument == '--help':
                        self.assertTrue(out.strip())
                    else:
                        self.assertTrue(out.strip() or err.strip())
                        self.assertIn(argument, out + err)

    def test_app_help_does_not_start_server_browser_or_thread(self):
        with mock.patch.object(app, 'Server') as server, \
                mock.patch.object(app.threading, 'Thread') as thread, \
                mock.patch.object(app.threading, 'Timer') as timer, \
                mock.patch.object(app.webbrowser, 'open') as browser, \
                mock.patch.object(app.os.path, 'isfile') as exists, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as stop:
                app.main(['--help'])
            self.assertEqual(stop.exception.code, 0)
            for effect in (server, thread, timer, browser, exists):
                effect.assert_not_called()

    def test_setup_help_does_not_prompt_load_answers_write_or_open(self):
        with mock.patch.object(sys, 'argv', ['setup_wizard.py', '--help']), \
                mock.patch.object(setup_wizard, 'ask') as ask, \
                mock.patch.object(setup_wizard, 'load_answers') as load, \
                mock.patch.object(setup_wizard.subprocess, 'run') as run, \
                mock.patch.object(setup_wizard.webbrowser, 'open') as browser, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as stop:
                setup_wizard.main()
            self.assertEqual(stop.exception.code, 0)
            for effect in (ask, load, run, browser):
                effect.assert_not_called()


class CrLfWarnings(unittest.TestCase):
    def test_git_unset_and_byte_exact_are_exempt_but_ordinary_crlf_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'release_templates').mkdir()
            subprocess.run(['git', 'init', '-q', tmp], check=True, capture_output=True, timeout=10)
            (root / '.gitattributes').write_bytes(b'* text=auto eol=lf\nraw.py -text\n')
            paths = ['raw.py', 'ordinary.py', 'lf.py', 'tools/context_update.py']
            for rel in paths:
                target = root / rel
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(b'# text\n' if rel == 'lf.py' else b'# text\r\n')
            before = {rel: (root / rel).read_bytes() for rel in paths}
            with mock.patch.object(cp, 'ROOT', tmp):
                self.assertEqual(cp.crlf_warning_paths(paths), ['ordinary.py'])
            self.assertEqual(before, {rel: (root / rel).read_bytes() for rel in paths})

    def test_without_git_only_byte_exact_is_exempt(self):
        with mock.patch.object(cp, 'rd', return_value='text\r\n'), \
                mock.patch.object(cp.os.path, 'isdir', return_value=False):
            self.assertEqual(cp.crlf_warning_paths(['ordinary.py', 'tools/context_update.py']),
                             ['ordinary.py'])


if __name__ == '__main__':
    unittest.main()
