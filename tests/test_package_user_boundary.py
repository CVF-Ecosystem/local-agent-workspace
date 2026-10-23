"""V7: private README paths cannot become package files, including en/ overlays.

Use real materialize/new/adopt/upgrade owners in disposable folders. Old target
manifest entries are retained; a contaminated upgrade source is refused.
"""
import json
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


if __name__ == '__main__':
    unittest.main()
