"""V7: private README paths cannot become package files, including en/ overlays.

Use real materialize/new/adopt/upgrade owners in disposable folders. Old target
manifest entries are retained; a contaminated upgrade source is refused.
"""
import json
import os
import subprocess
import zipfile
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import check_package as cp
import upgrade_package as upgrade
import test_package_v3 as fixture

PRIVATE = ('working/private/project/references/README.md',
           'en/working/private/project/references/README.md',
           'references/customer/README.md', 'en/references/customer/README.md')


class UserBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-user-boundary-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name)
        cls.pkg = cls.base / 'pkg'
        cp.materialize(str(cls.pkg), branding=False)

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(dir=self.base))
        self.addCleanup(shutil.rmtree, str(self.work))

    def add_private(self, root):
        for rel in PRIVATE:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(b'PRIVATE PROJECT DATA; not a package template\n')

    def run_ok(self, source, script, *args):
        result = fixture.run(source, script, *args, '--result-json')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_exact_factory_paths_and_mirrors_do_not_depend_on_project_manifest(self):
        self.assertEqual(len(cp.SCAFFOLD_READMES), 14)
        with mock.patch.object(cp, 'ROOT', str(self.work)):
            (self.work / '.agent').mkdir()
            (self.work / '.agent/PACKAGE_INFO.json').write_text('{}')
            (self.work / 'MANIFEST.sha256').write_text('0' * 64 + '  ' + PRIVATE[0] + '\n')
            for rel in cp.SCAFFOLD_READMES:
                for path in (rel, 'en/' + rel):
                    self.assertTrue(cp.package_readme(path), path)
                    self.assertTrue(cp.in_manifest(path), path)
            for rel in PRIVATE:
                self.assertFalse(cp.package_readme(rel), rel)
                self.assertFalse(cp.in_manifest(rel), rel)
                self.assertTrue(cp.user_owned(rel), rel)

    def test_projection_excludes_nested_readmes_but_preserves_all_factory_readmes(self):
        source = self.work / 'source'
        shutil.copytree(self.pkg, source)
        self.add_private(source)
        before = fixture.tree(source)
        with mock.patch.object(cp, 'ROOT', str(source)):
            selected = set(cp.delivery_selection(branding=False))
            self.assertFalse(selected.intersection(PRIVATE))
            dest = self.work / 'delivery'
            cp.materialize(str(dest), branding=False)
        self.assertEqual(fixture.tree(source), before)
        delivered = fixture.files(dest)
        for rel in cp.SCAFFOLD_READMES:
            self.assertTrue({rel, 'en/' + rel} <= delivered, rel)
        self.assertFalse(delivered.intersection(PRIVATE))
        manifest = (dest / 'MANIFEST.sha256').read_text(encoding='utf-8')
        self.assertTrue(all(rel not in manifest for rel in PRIVATE))
        self.assertEqual({p for p in delivered if p.startswith('.cvf/')}, set(cp.CVF_CLOSURE))
        self.assertEqual(json.loads((dest / cp.PROFILE_REL).read_text(encoding='utf-8'))['grants'], [])

    def test_staged_release_rejects_private_english_and_root_readmes(self):
        stage = self.work / 'stage'
        shutil.copytree(self.pkg, stage)
        self.add_private(stage)
        with mock.patch.object(cp, 'ROOT', str(stage)):
            errors, _ = cp.check_all(release=True)
        for rel in PRIVATE:
            self.assertTrue(any(rel in e and 'file người dùng' in e for e in errors), (rel, errors))

    def test_new_adopt_and_upgrade_keep_target_data_choices_and_native_configuration(self):
        self.run_ok(self.pkg, 'new_project.py', '--name', 'B', '--dest', self.work, '--apply')
        target = self.work / 'B'
        self.add_private(target)
        (target / '.claude').mkdir()
        (target / '.claude/settings.json').write_bytes(b'{"private":"NATIVE_B"}\n')
        profile = json.loads((target / cp.PROFILE_REL).read_text(encoding='utf-8'))
        profile['roles']['worker']['model'] = 'USER_CHOICE_B'
        (target / cp.PROFILE_REL).write_text(json.dumps(profile), encoding='utf-8')
        # A legacy package wrongly tracked a user's nested README; a newer
        # manifest must never turn that old entry into an instruction to delete.
        with (target / 'MANIFEST.sha256').open('a', encoding='utf-8') as f:
            f.write(cp.sha_bytes(PRIVATE[0], (target / PRIVATE[0]).read_bytes()) + '  ' + PRIVATE[0] + '\n')
        keep = list(PRIVATE) + [cp.PROFILE_REL, '.claude/settings.json']
        before = {rel: (target / rel).read_bytes() for rel in keep}
        self.run_ok(self.pkg, 'upgrade_package.py', '--project', target, '--apply')
        self.assertEqual({rel: (target / rel).read_bytes() for rel in keep}, before)
        adopted = self.work / 'existing'
        adopted.mkdir()
        self.add_private(adopted)
        old = {rel: (adopted / rel).read_bytes() for rel in PRIVATE}
        self.run_ok(self.pkg, 'adopt_project.py', '--project', adopted, '--name', 'Existing', '--apply')
        self.assertEqual({rel: (adopted / rel).read_bytes() for rel in PRIVATE}, old)

    def test_hash_valid_source_manifest_with_private_entry_is_refused_even_with_force(self):
        source = self.work / 'bad-source'
        shutil.copytree(self.pkg, source)
        self.add_private(source)
        with (source / 'MANIFEST.sha256').open('a', encoding='utf-8') as f:
            for rel in PRIVATE:
                f.write(cp.sha_bytes(rel, (source / rel).read_bytes()) + '  ' + rel + '\n')
        self.assertIn('SOURCE_MANIFEST_USER_DATA', [c for c, _ in cp.source_package_problems(str(source))])
        self.run_ok(self.pkg, 'new_project.py', '--name', 'Target', '--dest', self.work, '--apply')
        target = self.work / 'Target'
        before = fixture.tree(target)
        result = fixture.run(source, 'upgrade_package.py', '--project', target, '--apply', '--force', '--result-json')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('SOURCE_MANIFEST_USER_DATA', result.stdout)
        self.assertTrue(any('ZIP phát hành' in step for step in upgrade.block_steps(['SOURCE_MANIFEST_USER_DATA'])))
        self.assertEqual(fixture.tree(target), before)


T1_PRIVATE = (
    '.agent/demo_credentials.json',
    '.ENV',
    'tools/.env',
    'tools/.env.Local',
    'tools/nested/CLIENT_CREDENTIALS.TEST.JSON',
    'tools/secrets/fake.PEM',
    'tools/secrets/fake.KEY',
)
T1_EXAMPLES = (
    '.agent/demo_credentials.example.json',
    'tools/templates/sample_credentials.example.JSON',
    'tools/templates/.env.example',
    'tools/templates/.env.stage.EXAMPLE',
    'tools/templates/.env.stage.EXAMPLE.JSON',
    '.env.example.json',
    '.ENV.Example',
)
T1_DOC_TARGET = '.agent/demo_credentials.json'


def run_t1_tool(base, script, *args):
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run(
        [sys.executable, str(Path(base) / 'tools' / script), *map(str, args)],
        cwd=str(base), env=env, capture_output=True, encoding='utf-8', errors='replace', timeout=600,
    )


def manifest_paths_from_bytes(data):
    return {line.split('  ', 1)[1] for line in data.decode('utf-8').splitlines() if '  ' in line}


class CredentialBoundaryT1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean_temp = tempfile.TemporaryDirectory(prefix='law-t1-clean-package-')
        cls.addClassCleanup(cls.clean_temp.cleanup)
        cls.clean_package = Path(cls.clean_temp.name) / 'package'
        cp.materialize(str(cls.clean_package), branding=False)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='law-t1-package-boundary-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.package = self.base / 'package'
        shutil.copytree(str(self.clean_package), str(self.package))
        for rel in T1_PRIVATE + T1_EXAMPLES:
            path = self.package / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'FAKE_FIXTURE_ONLY\n')
        readme = self.package / 'tools' / 'README.md'
        with readme.open('a', encoding='utf-8', newline='') as f:
            f.write('\nReference example: ' + chr(96) + T1_DOC_TARGET + chr(96) + '.\n')
        result = run_t1_tool(self.package, 'check_package.py', '--write-manifest')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.source_snapshot = {
            rel: (self.package / rel).read_bytes()
            for rel in T1_PRIVATE + T1_EXAMPLES + ('tools/README.md', 'MANIFEST.sha256')
        }

    def assert_no_fixture_private_files(self, root, allowed=()):
        for rel in T1_PRIVATE:
            if rel not in allowed:
                self.assertFalse((Path(root) / rel).exists(), rel)

    def test_gitignore_matches_private_policy_and_keeps_examples(self):
        repo = self.base / 'ignore-repo'
        repo.mkdir()
        shutil.copyfile(str(ROOT / '.gitignore'), str(repo / '.gitignore'))
        empty_config = self.base / 'empty-gitconfig'
        empty_config.write_text('', encoding='utf-8')
        git_env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=str(empty_config))
        initialized = subprocess.run(['git', 'init', '--quiet', str(repo)], env=git_env,
                                     capture_output=True, text=True, timeout=30)
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        configured = subprocess.run(['git', '-C', str(repo), 'config', 'core.ignorecase', 'false'],
                                      env=git_env, capture_output=True, text=True, timeout=30)
        self.assertEqual(configured.returncode, 0, configured.stdout + configured.stderr)
        ignored = T1_PRIVATE + ('tools/nested/MIXED_CREDENTIALS.JSON',)
        public = T1_EXAMPLES + ('tools/credentials.SAMPLE.EXAMPLE.JSON',)
        for rel in ignored + public:
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'FAKE_IGNORE_FIXTURE_ONLY\n')
        for rel in ignored:
            result = subprocess.run(['git', '-C', str(repo), 'check-ignore', '--quiet', '--', rel],
                                    env=git_env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, rel)
        for rel in public:
            result = subprocess.run(['git', '-C', str(repo), 'check-ignore', '--quiet', '--', rel],
                                    env=git_env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1, rel)

    def test_shared_selection_and_manifest_filter_names_but_keep_examples(self):
        excluded = self.package / 'tests' / 'hidden.key'
        excluded.parent.mkdir()
        excluded.write_bytes(b'FAKE_EXCLUDED_FIXTURE_ONLY\n')
        with mock.patch.object(cp, 'ROOT', str(self.package)):
            files = set(cp.all_files())
            private = set(cp.private_files())
            self.assertEqual(set(cp.private_files(self.package)), private)
            self.assertEqual(cp._walk(self.package), cp._walk(str(self.package)))
            selected = set(cp.delivery_selection(branding=False))
            manifest = set(manifest_paths_from_bytes((self.package / 'MANIFEST.sha256').read_bytes()))
            projected_manifest = set(manifest_paths_from_bytes(
                cp.delivery_manifest(cp.delivery_selection(branding=False), branding=False)
            ))
        self.assertEqual(private, set(T1_PRIVATE))
        for rel in T1_PRIVATE:
            self.assertNotIn(rel, files)
            self.assertNotIn(rel, selected)
            self.assertNotIn(rel, manifest)
            self.assertNotIn(rel, projected_manifest)
        for rel in T1_EXAMPLES:
            self.assertIn(rel, files)
            self.assertIn(rel, selected)
            self.assertIn(rel, manifest)
            self.assertIn(rel, projected_manifest)

    def test_release_tree_refuses_private_files_even_if_manifest_omits_them(self):
        result = run_t1_tool(self.package, 'check_package.py', '--release')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for rel in T1_PRIVATE:
            self.assertIn(rel, result.stdout)
        path_error = 'đường dẫn ' + chr(96) + T1_DOC_TARGET + chr(96) + ' không tồn tại'
        self.assertNotIn(path_error, result.stdout)
        verified = run_t1_tool(self.package, 'check_package.py', '--verify')
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

    def test_doc_exception_requires_a_matching_example_json(self):
        doc_package = self.base / 'doc-package'
        shutil.copytree(str(self.package), str(doc_package))
        for rel in T1_PRIVATE:
            (doc_package / rel).unlink()
        path_error = 'đường dẫn ' + chr(96) + T1_DOC_TARGET + chr(96) + ' không tồn tại'
        with_example = run_t1_tool(doc_package, 'check_package.py', '--release')
        self.assertNotIn(path_error, with_example.stdout + with_example.stderr)
        self.assertEqual(with_example.returncode, 0, with_example.stdout + with_example.stderr)
        (doc_package / '.agent' / 'demo_credentials.example.json').unlink()
        without_example = run_t1_tool(doc_package, 'check_package.py', '--release')
        self.assertEqual(without_example.returncode, 1, without_example.stdout + without_example.stderr)
        self.assertIn(path_error, without_example.stdout)

    def test_zip_new_project_and_adopt_share_filtered_selection(self):
        out = self.base / 'release-out'
        out.mkdir()
        built = run_t1_tool(self.package, 'build_release.py', '--rc', '91', '--skip-check',
                            '--no-branding', '--out', out)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        archive = next(out.glob('*.zip'))
        with zipfile.ZipFile(str(archive)) as z:
            names = set(z.namelist())
            members = {name.split('/', 1)[1] for name in names if '/' in name}
            shipped_manifest = next(name for name in names if name.endswith('/MANIFEST.sha256'))
            archive_manifest = set(manifest_paths_from_bytes(z.read(shipped_manifest)))
        for rel in T1_PRIVATE:
            self.assertNotIn(rel, members)
            self.assertNotIn(rel, archive_manifest)
        for rel in T1_EXAMPLES:
            self.assertIn(rel, members)
            self.assertIn(rel, archive_manifest)

        extracted = self.base / 'extracted'
        extracted.mkdir()
        with zipfile.ZipFile(str(archive)) as z:
            z.extractall(str(extracted))
        release_package = next(p for p in extracted.iterdir() if p.is_dir())
        verified = run_t1_tool(release_package, 'check_package.py', '--verify')
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

        new_parent = self.base / 'new-projects'
        new_parent.mkdir()
        created = run_t1_tool(self.package, 'new_project.py', '--name', 'Boundary fixture',
                              '--dest', new_parent, '--apply')
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        new_project = new_parent / 'Boundary fixture'
        self.assert_no_fixture_private_files(new_project)
        for rel in T1_EXAMPLES:
            self.assertTrue((new_project / rel).is_file(), rel)
        self.assertEqual(run_t1_tool(new_project, 'check_package.py', '--verify').returncode, 0)

        existing = self.base / 'existing-project'
        existing.mkdir()
        user_note = b'FAKE_USER_DATA_ONLY\n'
        (existing / 'user-note.txt').write_bytes(user_note)
        adopted = run_t1_tool(self.package, 'adopt_project.py', '--project', existing,
                              '--name', 'Existing fixture', '--apply')
        self.assertEqual(adopted.returncode, 0, adopted.stdout + adopted.stderr)
        self.assertEqual((existing / 'user-note.txt').read_bytes(), user_note)
        self.assert_no_fixture_private_files(existing)
        for rel in T1_EXAMPLES:
            self.assertTrue((existing / rel).is_file(), rel)
        self.assertEqual(run_t1_tool(existing, 'check_package.py', '--verify').returncode, 0)

        for rel, before in self.source_snapshot.items():
            self.assertEqual((self.package / rel).read_bytes(), before, rel)

if __name__ == '__main__':
    unittest.main()
