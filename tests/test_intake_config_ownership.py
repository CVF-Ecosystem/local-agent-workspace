"""Bounded private-config ownership checks; no release build or live project CLI."""
import ast
import builtins
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp
import init_project as init
import upgrade_package as up

CONFIG = '.agent/SOURCE_INTAKE.json'
ALIASES = (CONFIG, 'en/' + CONFIG, '.AGENT/source_intake.JSON', 'EN/.AGENT/source_INTAKE.json',
           '.agent\\SOURCE_INTAKE.json', 'en\\.agent\\SOURCE_INTAKE.json', './' + CONFIG,
           'en//.agent//SOURCE_INTAKE.json', 'a/../' + CONFIG, 'en/a/../' + CONFIG)
UNRELATED = ('docs/SOURCE_INTAKE.json', '.agent/custom/SOURCE_INTAKE.json',
             '.agent/SOURCE_INTAKE.example.json', 'en/en/' + CONFIG)


def config_path(path):
    if not isinstance(path, (str, os.PathLike)):
        return False
    full = Path(path).absolute()
    return any(cp.intake_config(full.relative_to(root).as_posix())
               for root in PrivateConfig.roots if full == root or root in full.parents)


@contextlib.contextmanager
def no_config_io():
    def guarded(fn):
        def opened(path, *args, **kwargs):
            if config_path(path):
                raise AssertionError('private config content access: ' + str(path))
            return fn(path, *args, **kwargs)
        return opened
    with mock.patch('builtins.open', side_effect=guarded(builtins.open)), \
         mock.patch('io.open', side_effect=guarded(io.open)):
        yield


def snapshot(root):
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
            for p in root.rglob('*') if '__pycache__' not in p.parts}


class PrivateConfig(unittest.TestCase):
    roots = []

    @classmethod
    def setUpClass(cls):
        # Keep disposable fixture trees outside ROOT: later tests copy ROOT, so
        # retained in-tree scratch multiplies both traversal and copy costs.
        scratch = tempfile.TemporaryDirectory(prefix='law-config-ownership-DATAMOCK-')
        cls.addClassCleanup(scratch.cleanup)
        cls.base = Path(scratch.name)
        cls.pkg = cls.base / 'consumer'
        cls.roots = [ROOT, cls.pkg]
        original_open, original_io_open = builtins.open, io.open

        def guard(fn):
            def opened(path, *args, **kwargs):
                if isinstance(path, (str, os.PathLike)):
                    full = Path(path).absolute()
                    if ROOT in full.parents and not (cls.base == full or cls.base in full.parents):
                        rel = full.relative_to(ROOT).as_posix()
                        norm = rel[3:] if rel.startswith('en/') else rel
                        if norm in cp.USER_FILES or cp.intake_config(rel) or (cp.in_user_dir(rel) and not cp.package_readme(rel)):
                            raise AssertionError('live private read: ' + rel)
                    mode = args[0] if args else kwargs.get('mode', 'r')
                    if any(c in mode for c in 'wax+') and not (cls.base == full or cls.base in full.parents):
                        raise AssertionError('write outside scratch: ' + str(path))
                return fn(path, *args, **kwargs)
            return opened

        with mock.patch('builtins.open', side_effect=guard(original_open)), \
             mock.patch('io.open', side_effect=guard(original_io_open)), \
             mock.patch('shutil.copytree', side_effect=AssertionError('copytree forbidden')):
            cp.materialize(str(cls.pkg), branding=False)
        print('SCRATCH=' + str(cls.base), flush=True)

    def clone(self, name, source=None):
        source = source or self.pkg
        dest = self.base / name
        dest.mkdir()
        for p in source.rglob('*'):
            if p.is_file():
                target = dest / p.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(p.read_bytes())
        self.roots.append(dest)
        return dest

    def put(self, root, rel, data=b'{malformed DATAMOCK private choices\r\n'):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def run_tool(self, source, tool, *args, expected=0):
        # Guard all config reads/writes inside the actual CLI process as well as
        # confining explicit open writes to this one bounded scratch tree.
        wrapper = r'''
import builtins, io, ntpath, os, pathlib, runpy, sys
base = pathlib.Path(sys.argv[1]).absolute()
source = pathlib.Path(sys.argv[2]).absolute()
tool = sys.argv[3]
args = sys.argv[4:]
def config(path):
    if not isinstance(path, (str, os.PathLike)): return False
    full = pathlib.Path(path).absolute()
    if base not in full.parents: return False
    rel = full.relative_to(base).as_posix()
    parts = rel.split('/')
    return any(ntpath.normpath('/'.join(parts[i:])).replace('\\', '/').casefold()
               in ('.agent/source_intake.json', 'en/.agent/source_intake.json') for i in range(len(parts)))
def guard(fn):
    def opened(path, *a, **kw):
        if config(path): raise AssertionError('CLI private config access: ' + str(path))
        if isinstance(path, (str, os.PathLike)):
            full = pathlib.Path(path).absolute()
            mode = a[0] if a else kw.get('mode', 'r')
            if any(c in mode for c in 'wax+') and full != base and base not in full.parents:
                raise AssertionError('CLI write outside scratch: ' + str(path))
        return fn(path, *a, **kw)
    return opened
builtins.open, io.open = guard(builtins.open), guard(io.open)
sys.path.insert(0, str(source / 'tools'))
sys.argv = [str(source / 'tools' / tool)] + args
runpy.run_path(sys.argv[0], run_name='__main__')
'''
        result = subprocess.run([sys.executable, '-B', '-c', wrapper, str(self.base), str(source), tool, *map(str, args)],
                                cwd=str(source), env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
                                                         PYTHONDONTWRITEBYTECODE='1'),
                                capture_output=True, encoding='utf-8', timeout=120)
        print('CLI %s %s EXIT=%d' % (tool, ' '.join(map(str, args)), result.returncode), flush=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_01_identity_constants_and_unrelated_paths(self):
        tree = ast.parse((ROOT / 'tools/library_intake.py').read_text(encoding='utf-8'))
        literal = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'CONFIG' for t in n.targets))
        self.assertEqual((cp.INTAKE_CONFIG_REL, init.INTAKE_CONFIG_REL), (literal, literal))
        for rel in ALIASES:
            with self.subTest(rel=rel):
                self.assertTrue(cp.intake_config(rel))
                self.assertTrue(init.intake_config(rel))
                self.assertTrue(cp.user_owned(rel))
                self.assertFalse(cp.in_manifest(rel))
                with mock.patch.object(cp, 'all_files', return_value=[rel]), \
                     mock.patch.object(cp, 'source_state', return_value='clean'):
                    self.assertNotIn(rel, cp.delivery_selection(branding=False))
                with mock.patch.object(cp, 'source_state', side_effect=AssertionError('state/read before refusal')):
                    with self.assertRaises(cp.ProjectionError) as exc:
                        cp.delivery_bytes(rel)
                    self.assertEqual(exc.exception.code, 'EXCLUDED_FILE')
        for rel in UNRELATED:
            self.assertFalse(cp.intake_config(rel), rel)
            self.assertFalse(init.intake_config(rel), rel)
            self.assertTrue(cp.in_manifest(rel), rel)
        self.assertTrue(cp.user_owned('references/custom/SOURCE_INTAKE.json'))

    def test_02_clean_and_synthetic_maintainer_materialize(self):
        for maintainer in (False, True):
            source = self.clone('projection-' + str(maintainer))
            if maintainer:
                for rel in set(cp.TEMPLATE_OVERLAYS.values()) | set(cp.CVF_OVERLAY.values()) | {cp.PROFILE_TEMPLATE}:
                    self.put(source, rel, (ROOT / rel).read_bytes())
            for rel in (CONFIG, 'en/' + CONFIG):
                self.put(source, rel)
            self.put(source, 'docs/SOURCE_INTAKE.json', b'{"DATAMOCK": "ordinary package content"}\n')
            # Include the unrelated package file in the clean manifest.
            if not maintainer:
                with mock.patch.object(cp, 'ROOT', str(source)), no_config_io():
                    cp.write_manifest()
            before = snapshot(source)
            dest = self.base / ('projection-output-' + str(maintainer))
            with mock.patch.object(cp, 'ROOT', str(source)), no_config_io(), \
                 mock.patch('shutil.copytree', side_effect=AssertionError('copytree forbidden')):
                self.assertEqual(cp.source_package_problems(str(source)), [])
                shipped = cp.materialize(str(dest), branding=False)
            self.assertEqual(snapshot(source), before)
            self.assertFalse(any(cp.intake_config(r) for r in shipped))
            self.assertFalse(any('SOURCE_INTAKE' in r for r in shipped if r.startswith('release_templates/')))
            self.assertEqual((dest / 'docs/SOURCE_INTAKE.json').read_bytes(), b'{"DATAMOCK": "ordinary package content"}\n')
            self.assertFalse(any(cp.intake_config(line.split('  ', 1)[1])
                                 for line in (dest / 'MANIFEST.sha256').read_text().splitlines()))

    def test_03_manifest_source_guard_and_plan_before_guard(self):
        for i, rel in enumerate(ALIASES):
            source = self.clone('crafted-' + str(i))
            target = self.base / ('crafted-target-' + str(i))
            target.mkdir()
            self.roots.append(target)
            self.put(target, 'MANIFEST.sha256', ('0' * 64 + '  ' + rel + '\n').encode())
            self.put(target, CONFIG)
            self.put(source, CONFIG)
            with (source / 'MANIFEST.sha256').open('ab') as f:
                f.write(('0' * 64 + '  ' + rel + '\n').encode())
            before = snapshot(target)
            original_isfile = os.path.isfile
            def stat(path):
                if config_path(path):
                    raise AssertionError('target config stat before plan skip')
                return original_isfile(path)
            with no_config_io(), mock.patch('os.path.isfile', side_effect=stat):
                plan = up.plan(str(target), str(source), 'en')
                self.assertFalse(any(plan[k] for k in ('user_missing', 'obsolete') if k == 'obsolete'))
                self.assertFalse(any(cp.intake_config(r[0] if isinstance(r, tuple) else r)
                                     for k in ('add', 'update', 'conflict', 'kept', 'user_missing', 'user_changed', 'obsolete')
                                     for r in plan[k]))
                self.assertIn('SOURCE_MANIFEST_USER_DATA', [c for c, _ in cp.source_package_problems(str(source))])
            with mock.patch.object(cp, 'ROOT', str(source)), no_config_io():
                dest = self.base / ('blocked-output-' + str(i))
                with self.assertRaises(cp.ProjectionError):
                    cp.materialize(str(dest), branding=False)
                self.assertFalse(dest.exists())
            self.assertEqual(snapshot(target), before)

    def test_04_manifest_writer_and_old_verify_never_hash_config(self):
        source = self.clone('manifest-verify')
        for rel in (CONFIG, 'en/' + CONFIG):
            self.put(source, rel)
        with mock.patch.object(cp, 'ROOT', str(source)), no_config_io():
            cp.write_manifest()
        text = (source / 'MANIFEST.sha256').read_text()
        self.assertNotIn('SOURCE_INTAKE', text)
        with (source / 'MANIFEST.sha256').open('a', encoding='utf-8') as f:
            f.write(''.join('0' * 64 + '  ' + rel + '\n' for rel in ALIASES))
        with mock.patch.object(cp, 'ROOT', str(source)), no_config_io():
            self.assertEqual(cp.verify(), 0)

    def test_05_check_all_release_diagnoses_without_read(self):
        for maintainer in (False, True):
            source = self.clone('check-all-' + str(maintainer))
            if maintainer:
                for rel in set(cp.TEMPLATE_OVERLAYS.values()) | set(cp.CVF_OVERLAY.values()) | {cp.PROFILE_TEMPLATE}:
                    self.put(source, rel, (ROOT / rel).read_bytes())
            for rel in ('.AGENT/source_intake.JSON', 'en/.agent/SOURCE_INTAKE.json'):
                self.put(source, rel)
            with mock.patch.object(cp, 'ROOT', str(source)), no_config_io():
                for release in (False, True):
                    errs, warns = cp.check_all(release=release)
                    private = [e for e in errs if 'source_intake' in e.casefold()]
                    if release and not maintainer:
                        self.assertEqual(len(private), 2, errs)
                        self.assertTrue(all('Có file người dùng' in e for e in private))
                    else:
                        self.assertEqual(private, [], errs)

    def test_06_init_overlay_excludes_before_pristine(self):
        for state in ('missing', 'pristine', 'malformed'):
            source = self.clone('init-' + state)
            if state != 'missing':
                self.put(source, CONFIG, b'{}\n' if state == 'pristine' else b'{DATAMOCK broken\xff')
            self.put(source, 'en/' + CONFIG)
            if state == 'pristine':
                with (source / 'MANIFEST.sha256').open('a', encoding='utf-8') as f:
                    f.write(cp.sha_bytes(CONFIG, b'{}\n') + '  ' + CONFIG + '\n')
            configs = {rel: (source / rel).read_bytes() for rel in (CONFIG, 'en/' + CONFIG) if (source / rel).exists()}
            with mock.patch.object(init, 'ROOT', str(source)), no_config_io():
                self.assertFalse(any(cp.intake_config(src) or cp.intake_config(dst) for src, dst in init.overlay_pairs()))
            before = snapshot(source)
            self.run_tool(source, 'init_project.py', '--name', 'DATAMOCK', '--lang', 'en', '--dry-run')
            self.assertEqual(snapshot(source), before)
            self.run_tool(source, 'init_project.py', '--name', 'DATAMOCK', '--lang', 'en')
            self.run_tool(source, 'init_project.py', '--name', 'DATAMOCK force', '--lang', 'en', '--force')
            for rel in (CONFIG, 'en/' + CONFIG):
                self.assertEqual((source / rel).read_bytes() if (source / rel).exists() else None, configs.get(rel))
            self.assertFalse(any(cp.intake_config(p.relative_to(source).as_posix().split('.bak-', 1)[0])
                                 for p in source.rglob('*.bak-*')))

    def test_07_new_adopt_upgrade_and_unmanifested_source(self):
        source = self.clone('lifecycle-source')
        self.put(source, CONFIG)
        self.put(source, 'en/' + CONFIG)
        source_before = snapshot(source)
        for lang in ('vi', 'en'):
            before = snapshot(self.base)
            self.run_tool(source, 'new_project.py', '--name', 'New-' + lang, '--dest', self.base, '--lang', lang)
            self.assertEqual(snapshot(self.base), before)
            self.run_tool(source, 'new_project.py', '--name', 'New-' + lang, '--dest', self.base, '--lang', lang, '--apply')
            project = self.base / ('New-' + lang)
            self.roots.append(project)
            self.assertFalse((project / CONFIG).exists())
            self.assertFalse((project / ('en/' + CONFIG)).exists())
            for existing in (False, True):
                target = self.base / ('Adopt-' + lang + '-' + str(existing))
                target.mkdir()
                self.roots.append(target)
                if existing:
                    self.put(target, CONFIG, b'{DATAMOCK malformed existing\xff')
                    self.put(target, 'en/' + CONFIG, b'{"DATAMOCK": "private mirror"}\n')
                saved = {rel: (target / rel).read_bytes() if (target / rel).exists() else None for rel in (CONFIG, 'en/' + CONFIG)}
                before = snapshot(target)
                args = ('--project', target, '--name', 'DATAMOCK', '--lang', lang)
                self.run_tool(source, 'adopt_project.py', *args)
                self.assertEqual(snapshot(target), before)
                self.run_tool(source, 'adopt_project.py', *args, '--apply')
                before = snapshot(target)
                self.run_tool(source, 'upgrade_package.py', '--project', target)
                self.assertEqual(snapshot(target), before)
                self.run_tool(source, 'upgrade_package.py', '--project', target, '--apply')
                for rel, raw in saved.items():
                    self.assertEqual((target / rel).read_bytes() if (target / rel).exists() else None, raw)
                    self.assertFalse((target / (rel + '.new')).exists())
                    self.assertFalse(list((target / rel).parent.glob(Path(rel).name + '.bak-*')))
        self.assertEqual(snapshot(source), source_before)

    def test_08_upgrade_crafted_source_cli_no_writes(self):
        source = self.clone('blocked-upgrade-source')
        self.put(source, CONFIG)
        with (source / 'MANIFEST.sha256').open('a', encoding='utf-8') as f:
            f.write('0' * 64 + '  en/a/../' + CONFIG + '\n')
        target = self.clone('blocked-upgrade-target')
        for existing in (False, True):
            if existing:
                self.put(target, CONFIG)
            before = snapshot(target)
            result = self.run_tool(source, 'upgrade_package.py', '--project', target, '--allow-uninitialized', '--apply', '--force', expected=1)
            self.assertIn('SOURCE_MANIFEST_USER_DATA', result.stdout)
            self.assertEqual(snapshot(target), before)

    def test_09_upgrade_old_manifest_config_not_obsolete(self):
        target = self.clone('old-manifest-target')
        self.put(target, CONFIG)
        with (target / 'MANIFEST.sha256').open('a', encoding='utf-8') as f:
            f.write('0' * 64 + '  ' + CONFIG + '\n')
        with no_config_io():
            plan = up.plan(str(target), str(self.pkg), 'vi')
        self.assertNotIn(CONFIG, plan['obsolete'])
        saved = (target / CONFIG).read_bytes()
        self.run_tool(self.pkg, 'upgrade_package.py', '--project', target, '--allow-uninitialized', '--apply')
        self.assertEqual((target / CONFIG).read_bytes(), saved)

    def test_10_no_config_default_consumer_and_standalone_init(self):
        self.run_tool(self.pkg, 'check_package.py', '--release')
        source = self.clone('standalone-init')
        # Legacy init's optional is_original import already catches absence;
        # adding config filtering must not introduce a mandatory package import.
        (source / 'tools/check_package.py').rename(source / 'tools/check_package.saved')
        self.run_tool(source, 'init_project.py', '--name', 'DATAMOCK standalone', '--lang', 'en')

    def test_11_cli_guard_direct_open_controls(self):
        source = self.clone('guard-control')
        for rel in (CONFIG, 'en/' + CONFIG):
            self.put(source, rel)
        self.put(source, 'tools/guard_probe.py', b'import builtins, io, sys\ngetattr(builtins if sys.argv[1] == "builtins" else io, "open")(sys.argv[2], sys.argv[3])\n')
        before = snapshot(source)
        for api in ('builtins', 'io'):
            for mode in ('r', 'w'):
                for rel in (CONFIG, 'en/' + CONFIG):
                    with self.subTest(api=api, mode=mode, rel=rel):
                        result = self.run_tool(source, 'guard_probe.py', api, source / rel, mode, expected=1)
                        self.assertIn('CLI private config access:', result.stderr)
                        self.assertEqual(snapshot(source), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
