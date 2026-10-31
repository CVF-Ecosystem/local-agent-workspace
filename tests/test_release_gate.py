"""Release gate, Python 3.8 heuristic and check_package envelope checks.

Every build runs in a disposable copy of the package. Builds either set the nested guard
(LOCAL_AGENT_WORKSPACE_GATE_NESTED=1, so the behaviour gate records `nested` and does not re-run this
suite) or run in a copy whose tests/ folder holds only a tiny synthetic test. Nothing in the source tree is written.
"""
import json
import contextlib
import io
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp
import result_schema
import build_release as br

GATE_ENV = 'LOCAL_AGENT_WORKSPACE_GATE_NESTED'
GATE_SCHEMA = 'local-agent-workspace/release-gate-v1'
GATE_NAMES = ['package_check', 'python38_compat', 'behaviour_tests', 'release_tree']
# Chỉ dùng cú pháp và API 3.9+ để kiểm checker: `match` (3.10) ở dòng 2, `.removeprefix(` ở dòng 5.
SYNTH_PY39 = 'import os\nmatch os.name:\n    case "nt":\n        pass\nx = s.removeprefix("a")\n'


def make_copy(base, name, with_tests=True):
    ignore = ['.git', '__pycache__', 'dist', 'roadmap', 'feedback']
    if not with_tests:
        ignore.append('tests')
    dst = base / name
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(*ignore))
    shutil.rmtree(str(dst / '.agent' / 'runtime'), ignore_errors=True)  # dữ liệu vận hành của máy phát triển không vào bản sao / dev-machine runtime data never enters the copy
    [f.unlink() for f in (dst / 'assets').rglob('*') if f.is_file() and f.name != 'README.md']  # logo, font của máy phát triển / dev-machine branding and fonts
    return dst


def run_tool(pkg, script, *args, nested=True):
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    env.pop(GATE_ENV, None)
    if nested:
        env[GATE_ENV] = '1'
    return subprocess.run([sys.executable, str(pkg / 'tools' / script), *map(str, args)],
                          cwd=pkg, env=env, capture_output=True, encoding='utf-8', timeout=300)


def envelope(result):
    human, env = result_schema.split_output(result.stdout)
    return human, env


def write_lf(path, text):
    with open(str(path), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BehaviourGateBudgetTests(unittest.TestCase):
    def test_default_budget_and_nested_source_only_do_not_spawn(self):
        self.assertEqual(br.BEHAVIOUR_TEST_TIMEOUT_S, 1800)
        with mock.patch.object(br.cp, 'P', return_value='absent'), \
                mock.patch.object(br.os.path, 'isdir', return_value=False), \
                mock.patch.object(br.subprocess, 'Popen') as spawn:
            self.assertEqual(br.gate_behaviour_tests()['status'], 'skipped')
            spawn.assert_not_called()
        with mock.patch.dict(os.environ, {br.GATE_ENV: '1'}), \
                mock.patch.object(br.os.path, 'isdir', return_value=True), \
                mock.patch.object(br.subprocess, 'Popen') as spawn:
            self.assertEqual(br.gate_behaviour_tests()['status'], 'nested')
            spawn.assert_not_called()


class BehaviourGateDurableDiagnosticsTests(unittest.TestCase):
    def run_fixture(self, source, timeout=None):
        with tempfile.TemporaryDirectory(prefix='gate-synthetic-') as directory:
            tests = Path(directory) / 'tests'
            tests.mkdir()
            write_lf(tests / 'test_synthetic.py', source)
            waits = []
            real_popen = subprocess.Popen
            def spawn(*args, **kwargs):
                child = real_popen(*args, **kwargs)
                original = child.wait
                def wait(timeout=None):
                    waits.append(timeout)
                    return original(timeout=timeout)
                child.wait = wait
                return child
            with mock.patch.object(br, 'ROOT', directory), \
                    mock.patch.object(br.cp, 'P', return_value=str(tests)), \
                    mock.patch.dict(os.environ, {br.GATE_ENV: '0'}), \
                    mock.patch.object(br.subprocess, 'Popen', side_effect=spawn), \
                    mock.patch.object(br, 'BEHAVIOUR_TEST_TIMEOUT_S',
                                      1800 if timeout is None else timeout):
                gate = br.gate_behaviour_tests()
        diagnostic = Path(gate['detail'].split(': ')[-1])
        self.addCleanup(shutil.rmtree, str(diagnostic))
        self.assertTrue((diagnostic / 'stdout.log').exists())
        self.assertTrue((diagnostic / 'stderr.log').exists())
        records = [json.loads(line) for line in (diagnostic / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
        return gate, diagnostic, records, waits

    def test_success_retains_raw_streams_order_duration_and_1800(self):
        gate, path, records, waits = self.run_fixture(
            'import unittest,sys\nclass Tiny(unittest.TestCase):\n'
            ' def test_a(self):\n  print("raw stdout",flush=True)\n  print("raw stderr",file=sys.stderr,flush=True)\n'
            ' def test_b(self): pass\n')
        self.assertEqual(gate['status'], 'passed')
        self.assertEqual(waits, [1800])
        self.assertIn('raw stdout', (path / 'stdout.log').read_text())
        self.assertIn('raw stderr', (path / 'stderr.log').read_text())
        starts = [r for r in records if r['event'] == 'test_start']
        ends = [r for r in records if r['event'] == 'test_end']
        self.assertEqual([r['test'].rsplit('.', 1)[-1] for r in starts], ['test_a', 'test_b'])
        self.assertEqual([r['outcome'] for r in ends], ['success', 'success'])
        self.assertTrue(all(r['duration_s'] >= 0 and r['pid'] for r in ends))
        self.assertEqual(records[-1]['current_unfinished'], None)
        self.assertEqual(records[-1]['returncode'], 0)

    def test_failure_and_subtest_failures_preserve_exit(self):
        for body in ['self.fail("synthetic")',
                     'with self.subTest(n=1): self.fail("subtest")']:
            with self.subTest(body=body):
                gate, path, records, waits = self.run_fixture(
                    'import unittest\nclass Tiny(unittest.TestCase):\n def test_a(self):\n  ' + body + '\n')
                self.assertEqual(gate['status'], 'failed')
                self.assertIn('mã thoát 1', gate['detail'])
                self.assertEqual([r['outcome'] for r in records if r['event'] == 'test_end'], ['failure'])

    def test_skip_is_recorded_without_turning_into_success(self):
        gate, path, records, waits = self.run_fixture(
            'import unittest\nclass Tiny(unittest.TestCase):\n @unittest.skip("fixture reason")\n def test_a(self): pass\n')
        self.assertEqual(gate['status'], 'passed')
        self.assertIn('fixture reason', gate['detail'])
        self.assertEqual([r['outcome'] for r in records if r['event'] == 'test_end'], ['skip'])

    def test_class_setup_error_and_cleanup_have_separate_phase_evidence(self):
        gate, path, records, waits = self.run_fixture(
            'import unittest\nclass Tiny(unittest.TestCase):\n @classmethod\n'
            ' def setUpClass(cls): raise RuntimeError("setup failure")\n def test_a(self): pass\n')
        self.assertEqual(gate['status'], 'failed')
        self.assertFalse(any(r['event'] == 'test_start' for r in records))
        self.assertTrue(any(r['event'] == 'outcome' and r['outcome'] == 'error' for r in records))
        self.assertTrue(any(r.get('phase') == 'class_setup' and 'duration_s' in r for r in records))
        gate, path, records, waits = self.run_fixture(
            'import unittest\nclass Tiny(unittest.TestCase):\n def test_a(self): self.addCleanup(lambda: None)\n')
        phases = {r.get('phase') for r in records if r['event'] == 'phase_end'}
        self.assertTrue({'test_setup', 'test_body', 'test_teardown', 'test_cleanup'} <= phases)

    def test_timeout_keeps_partial_raw_current_pid_and_body_phase(self):
        gate, path, records, waits = self.run_fixture(
            'import unittest,time\nclass Tiny(unittest.TestCase):\n def test_a(self):\n'
            '  print("before hang",flush=True)\n  time.sleep(30)\n', timeout=0.8)
        self.assertEqual(gate['status'], 'failed')
        self.assertIn('quá 0 giây', gate['detail'])
        self.assertIn('unfinished', gate['errors'][0])
        self.assertIn('before hang', (path / 'stdout.log').read_text())
        self.assertTrue(records[-1]['timed_out'])
        self.assertEqual(records[-1]['phase'], 'test_body')
        self.assertTrue(records[-1]['current_unfinished'].endswith('.test_a'))
        self.assertEqual(records[-1]['child_pid'], next(r['child_pid'] for r in records if r['event'] == 'spawn'))
        self.assertFalse(any(r['event'] == 'test_end' for r in records))

    def test_trace_survives_body_mocks_of_global_clock_json_and_open(self):
        gate, path, records, waits = self.run_fixture(
            'import unittest,time,json,builtins\nfrom unittest.mock import patch\n'
            'class Tiny(unittest.TestCase):\n def test_a(self):\n'
            '  for target in ["time.monotonic", "json.dumps", "builtins.open"]:\n'
            '   p=patch(target,side_effect=RuntimeError("body mock"));p.start();self.addCleanup(p.stop)\n')
        self.assertEqual(gate['status'], 'passed')
        self.assertTrue(any(r.get('outcome') == 'success' for r in records))

    def test_timeout_before_test_body_identifies_discovery_or_class_setup(self):
        sources = {
            'discovery': 'import time\ntime.sleep(30)\n',
            'class_setup': ('import unittest,time\nclass Tiny(unittest.TestCase):\n'
                            ' @classmethod\n def setUpClass(cls): time.sleep(30)\n'
                            ' def test_a(self): pass\n'),
        }
        for phase, source in sources.items():
            with self.subTest(phase=phase):
                gate, path, records, waits = self.run_fixture(source, timeout=0.8)
                self.assertEqual(gate['status'], 'failed')
                self.assertTrue(records[-1]['timed_out'])
                self.assertEqual(records[-1]['phase'], phase)
                self.assertIsNone(records[-1]['current_unfinished'])
                self.assertFalse(any(r['event'] == 'test_start' for r in records))


class ReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='release-gate-')
        cls.base = Path(cls.tmp.name)
        cls.pkg = make_copy(cls.base, 'pkg')  # shared copy: builds here do not change it
        cls.version = (cls.pkg / 'VERSION').read_text(encoding='utf-8').strip()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def assertBlocked(self, result, code, gate):
        human, env = envelope(result)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertIsNotNone(env, result.stdout)
        self.assertEqual(env['status'], 'blocked')
        self.assertEqual(env['code'], result.returncode)
        self.assertTrue(any(f['message'].startswith(gate + ':') for f in env['findings']), env['findings'])
        return human, env

    def test_official_build_refuses_skip_check(self):
        out = self.base / 'refused'
        r = run_tool(self.pkg, 'build_release.py', '--skip-check', '--out', out, '--result-json')
        self.assertNotEqual(r.returncode, 0)
        human, env = envelope(r)
        self.assertEqual(env['status'], 'blocked')
        self.assertEqual(env['code'], r.returncode)
        self.assertIn('--rc', human)
        self.assertFalse(out.exists(), 'refused build must not create the output folder')

    def test_rc_skip_check_builds_and_report_marks_skipped(self):
        out = self.base / 'rc-skip'
        r = run_tool(self.pkg, 'build_release.py', '--rc', '1', '--skip-check', '--out', out, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        archive = out / ('local-agent-workspace-v%s-rc1.zip' % self.version)
        self.assertTrue(archive.is_file())
        report = json.loads((out / (archive.name + '.gate.json')).read_text(encoding='utf-8'))
        status = {g['name']: g['status'] for g in report['gates']}
        self.assertEqual(status, {'package_check': 'skipped', 'python38_compat': 'skipped',
                                  'behaviour_tests': 'skipped', 'release_tree': 'passed'})
        self.assertEqual(report['kind'], 'rc')
        self.assertTrue(report['skip_check'])
        _, env = envelope(r)
        self.assertEqual((env['status'], env['code']), ('success', 0))
        self.assertEqual({u['gate'] for u in env['unchecked']}, {'package_check', 'python38_compat', 'behaviour_tests'})

    def test_failing_py38_gate_leaves_no_archive(self):
        pkg = make_copy(self.base, 'bad-py38')
        write_lf(pkg / 'tools' / 'zz_synthetic_py39.py', SYNTH_PY39)
        out = self.base / 'bad-py38-out'
        r = run_tool(pkg, 'build_release.py', '--out', out, '--result-json')
        human, _ = self.assertBlocked(r, 1, 'python38_compat')
        self.assertIn('tools/zz_synthetic_py39.py:2:', human)
        self.assertIn('tools/zz_synthetic_py39.py:5:', human)
        self.assertEqual(list(out.glob('*.zip')) if out.exists() else [], [])

    def test_failing_package_check_leaves_no_archive(self):
        pkg = make_copy(self.base, 'bad-template')
        target = pkg / 'release_templates' / 'PROJECT.md'
        target.write_bytes(target.read_bytes().replace('[Tên]'.encode('utf-8'), 'Đã điền'.encode('utf-8')))
        out = self.base / 'bad-template-out'
        r = run_tool(pkg, 'build_release.py', '--out', out, '--result-json')
        self.assertBlocked(r, 1, 'package_check')
        self.assertEqual(list(out.glob('*.zip')) if out.exists() else [], [])

    def test_failing_behaviour_gate_leaves_no_archive(self):
        pkg = make_copy(self.base, 'bad-tests', with_tests=False)
        (pkg / 'tests').mkdir()
        write_lf(pkg / 'tests' / 'test_synthetic_fail.py',
                 'import unittest\n\nclass Synthetic(unittest.TestCase):\n    def test_fail(self):\n        self.fail("synthetic")\n')
        out = self.base / 'bad-tests-out'
        r = run_tool(pkg, 'build_release.py', '--out', out, '--result-json', nested=False)
        self.assertBlocked(r, 1, 'behaviour_tests')
        self.assertEqual(list(out.glob('*.zip')) if out.exists() else [], [])

    def test_behaviour_report_keeps_skipped_test_names_and_reasons(self):
        pkg = make_copy(self.base, 'skip-names', with_tests=False)
        (pkg / 'tests').mkdir()
        write_lf(pkg / 'tests' / 'test_synthetic_skips.py',
                 'import unittest\n\nclass Synthetic(unittest.TestCase):\n'
                 '    def test_pass(self):\n        pass\n'
                 '    @unittest.skip("first reason")\n    def test_first(self):\n        pass\n'
                 '    @unittest.skip("second reason")\n    def test_second(self):\n        pass\n'
                 '    @unittest.skip("documented reason")\n    def test_documented(self):\n'
                 '        """A description printed on a separate line."""\n        pass\n')
        out = self.base / 'skip-names-out'
        r = run_tool(pkg, 'build_release.py', '--rc', '2', '--out', out, '--result-json', nested=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        report = json.loads(next(out.glob('*.gate.json')).read_text(encoding='utf-8'))
        gate = next(g for g in report['gates'] if g['name'] == 'behaviour_tests')
        self.assertEqual(gate['status'], 'passed')
        self.assertIn('OK (skipped=3)', gate['detail'])
        for name, reason in (('test_first', 'first reason'), ('test_second', 'second reason'), ('test_documented', 'documented reason')):
            # unittest 3.8 prints the class in parentheses; newer versions include the method.
            self.assertRegex(gate['detail'], re.escape(name + ' (test_synthetic_skips.Synthetic') +
                             r'(?:\.' + re.escape(name) + r')?\)[^\n]*skipped ' + re.escape(repr(reason)))

    def test_gate_report_platform_python_hash_and_reproducible_zip(self):
        out1, out2 = self.base / 'report-1', self.base / 'report-2'
        r1 = run_tool(self.pkg, 'build_release.py', '--rc', '2', '--out', out1, '--result-json')
        r2 = run_tool(self.pkg, 'build_release.py', '--rc', '2', '--out', out2, '--result-json')
        self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        archive = out1 / ('local-agent-workspace-v%s-rc2.zip' % self.version)
        report = json.loads((out1 / (archive.name + '.gate.json')).read_text(encoding='utf-8'))
        self.assertEqual(report['schema'], GATE_SCHEMA)
        self.assertEqual((report['version'], report['kind'], report['rc']), (self.version, 'rc', 2))
        self.assertEqual(report['platform'], {'system': platform.system(), 'release': platform.release()})
        self.assertEqual(report['python'], platform.python_version())
        self.assertRegex(report['generated_utc'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
        self.assertEqual(report['archive_sha256'], sha256(archive))
        self.assertEqual([g['name'] for g in report['gates']], GATE_NAMES)
        gate_status = {g['name']: g['status'] for g in report['gates']}
        self.assertEqual(gate_status['behaviour_tests'], 'nested')  # the guard is set by run_tool(nested=True)
        self.assertEqual(gate_status['package_check'], 'passed')
        if report['git'] is not None:  # None khi không có git: không được làm build lỗi
            self.assertEqual(set(report['git']), {'commit', 'dirty'})
        # ZIP không có timestamp: hai lần dựng cùng nguồn phải cho cùng SHA-256 và mọi entry có ngày cố định.
        archive2 = out2 / archive.name
        self.assertEqual(sha256(archive), sha256(archive2))
        with zipfile.ZipFile(archive) as z:
            self.assertTrue(all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in z.infolist()))
            self.assertTrue(all(n.startswith('local-agent-workspace-v%s/' % self.version) for n in z.namelist()))

    def test_py38_checker_flags_match_and_removeprefix_and_ignores_strings(self):
        problems = cp.py38_problems(SYNTH_PY39, 'synthetic.py')
        lines = {ln for ln, _ in problems}
        self.assertIn(2, lines)
        self.assertIn(5, lines)
        self.assertTrue(any('removeprefix' in msg for _, msg in problems))
        self.assertTrue(any('Python 3.8' in msg for _, msg in problems))
        clean = ('from typing import Optional\n\ndef f(a: Optional[int] = None) -> str:\n'
                 '    doc = "s.removeprefix(x) and match x:"  # s.removesuffix(y)\n    return str(a)\n')
        self.assertEqual(cp.py38_problems(clean, 'clean.py'), [])

    def test_check_package_result_json_code_matches_exit_code(self):
        pkg = make_copy(self.base, 'cp-envelope')
        r = run_tool(pkg, 'check_package.py', '--write-manifest', '--result-json')
        _, env = envelope(r)
        self.assertEqual((r.returncode, env['code'], env['status']), (0, 0, 'success'))
        self.assertTrue(env['changes'])
        r = run_tool(pkg, 'check_package.py', '--verify', '--result-json')
        _, env = envelope(r)
        self.assertEqual((r.returncode, env['code'], env['status']), (0, 0, 'success'))
        with open(str(pkg / 'tools' / 'result_schema.py'), 'a', encoding='utf-8', newline='\n') as f:
            f.write('# local edit\n')
        r = run_tool(pkg, 'check_package.py', '--verify', '--result-json')
        _, env = envelope(r)
        self.assertEqual((r.returncode, env['code'], env['status']), (1, 1, 'issues'))
        self.assertTrue(any('tools/result_schema.py' in f['message'] for f in env['findings']))
        write_lf(pkg / 'tools' / 'zz_synthetic_py39.py', SYNTH_PY39)
        r = run_tool(pkg, 'check_package.py', '--result-json')
        _, env = envelope(r)
        self.assertEqual((r.returncode, env['code'], env['status']), (1, 1, 'issues'))
        self.assertTrue(any(f['severity'] == 'error' and 'zz_synthetic_py39.py:2:' in f['message'] for f in env['findings']))
        # Không có MANIFEST: mã thoát 2, envelope status error cùng mã.
        bare = self.base / 'no-manifest'
        (bare / 'tools').mkdir(parents=True)
        for name in ('check_package.py', 'result_schema.py'):
            shutil.copyfile(str(ROOT / 'tools' / name), str(bare / 'tools' / name))
        r = run_tool(bare, 'check_package.py', '--verify', '--result-json')
        _, env = envelope(r)
        self.assertEqual((r.returncode, env['code'], env['status']), (2, 2, 'error'))

    def test_branding_ships_in_zip_and_can_be_left_out(self):
        pkg = make_copy(self.base, 'branding-build')  # bản sao riêng, không dùng chung / own copy: builds must not depend on shared branding
        assets = pkg / 'assets'
        (assets / 'fonts').mkdir(parents=True, exist_ok=True)
        logo = b'\x89PNG\r\n\x1a\nfake'
        write_lf(assets / 'branding.json', json.dumps({'title': 'Đơn vị Mẫu', 'subtitle': 'Agent Workspace', 'logo': 'logo.png'}, ensure_ascii=False))
        (assets / 'logo.png').write_bytes(logo)
        (assets / 'fonts' / 'DonVi-Regular.ttf').write_bytes(b'\x00\x01\x00\x00fake font')
        write_lf(assets / 'branding.js', 'window.WORKSPACE_BRANDING = {"title": "cu"};\n')  # bản cũ: build phải thay / stale copy, the build must replace it
        branding = ['assets/branding.js', 'assets/branding.json', 'assets/fonts/DonVi-Regular.ttf', 'assets/logo.png']
        top = 'local-agent-workspace-v%s' % self.version

        out = self.base / 'branding-rc3'
        r = run_tool(pkg, 'build_release.py', '--rc', '3', '--out', out, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('organization branding included', r.stdout)
        archive = out / ('local-agent-workspace-v%s-rc3.zip' % self.version)
        report = json.loads((out / (archive.name + '.gate.json')).read_text(encoding='utf-8'))
        self.assertEqual(report['branding'], branding)
        with zipfile.ZipFile(str(archive)) as z:
            names = set(z.namelist())
            self.assertTrue(all(n.startswith(top + '/') for n in names))
            for rel in branding:
                self.assertIn(top + '/' + rel, names)
            js = z.read(top + '/assets/branding.js').decode('utf-8')
            self.assertIn('Đơn vị Mẫu', js)
            self.assertIn('assets/logo.png', js)
            self.assertNotIn('"cu"', js)
            self.assertEqual(z.read(top + '/assets/logo.png'), logo)
            manifest = z.read(top + '/MANIFEST.sha256').decode('utf-8')
        self.assertNotIn('assets/logo.png', manifest)
        self.assertNotIn('assets/fonts/DonVi-Regular.ttf', manifest)
        self.assertIn('assets/fonts/README.md', manifest)  # README của package vẫn được liệt kê / package README stays listed

        out2 = self.base / 'branding-rc4'
        r = run_tool(pkg, 'build_release.py', '--rc', '4', '--no-branding', '--out', out2, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn('organization branding included', r.stdout)
        archive2 = out2 / ('local-agent-workspace-v%s-rc4.zip' % self.version)
        report2 = json.loads((out2 / (archive2.name + '.gate.json')).read_text(encoding='utf-8'))
        self.assertEqual(report2['branding'], [])
        with zipfile.ZipFile(str(archive2)) as z:
            names2 = set(z.namelist())
        for rel in branding:
            self.assertNotIn(top + '/' + rel, names2)
        self.assertIn(top + '/assets/README.md', names2)

    def test_other_user_files_in_assets_still_block_release(self):
        pkg = make_copy(self.base, 'assets-user-file')
        write_lf(pkg / 'assets' / 'ghi-chu.txt', 'Ghi chú riêng, không phải nhận diện.\n')
        r = run_tool(pkg, 'check_package.py', '--release')
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn('assets/ghi-chu.txt', r.stdout)
        (pkg / 'assets' / 'ghi-chu.txt').unlink()
        write_lf(pkg / 'assets' / 'logo.svg', '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>\n')
        r = run_tool(pkg, 'check_package.py', '--release')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == '__main__':
    unittest.main()
