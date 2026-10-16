"""Release gate, Python 3.8 heuristic and check_package envelope checks.

Every build runs in a disposable copy of the package. Builds either set the nested guard
(LOCAL_AGENT_WORKSPACE_GATE_NESTED=1, so the behaviour gate records `nested` and does not re-run this
suite) or run in a copy whose tests/ folder holds only a tiny synthetic test. Nothing in the source tree is written.
"""
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp
import result_schema

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
    [f.unlink() for f in (dst / 'assets').glob('*') if f.is_file() and f.name != 'README.md']  # logo/nhận diện của máy phát triển / dev-machine branding
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


if __name__ == '__main__':
    unittest.main()
