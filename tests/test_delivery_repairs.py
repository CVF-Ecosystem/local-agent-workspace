"""AN C2 delivery repairs: disposable fixtures, no release or host activation."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp
import pack


class DeliveryRepairs(unittest.TestCase):
    def test_clean_index_overlays_preserve_shared_rows_and_live_source(self):
        for rel in ('.agent/SKILL_INDEX.md', 'en/.agent/SKILL_INDEX.md'):
            live = (ROOT / rel).read_bytes()
            clean = cp.delivery_bytes(rel).decode('utf-8')
            self.assertNotIn('| PACK |', clean)
            expected = [line for line in live.decode('utf-8').splitlines() if '| PACK |' not in line]
            self.assertEqual(clean.splitlines(), expected)
            self.assertEqual((ROOT / rel).read_bytes(), live)

    def test_pack_index_targets_and_templates_are_checked(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(cp, 'ROOT', td):
            root = Path(td)
            rel = '.agent/SKILL_INDEX.md'
            (root / '.agent').mkdir()
            row = '| sample | LOCAL | PACK | skills/local/packs/demo/skills/sample/SKILL.md | use | REVIEW | demo |\n'
            (root / rel).write_text(row, encoding='utf-8')
            self.assertTrue(cp.pack_index_problems())
            target = root / 'skills/local/packs/demo/skills/sample/SKILL.md'
            target.parent.mkdir(parents=True)
            target.write_text('skill', encoding='utf-8')
            self.assertEqual(cp.pack_index_problems(), [])
            template = root / 'release_templates' / rel
            template.parent.mkdir(parents=True)
            template.write_text(row, encoding='utf-8')
            self.assertTrue(any('release_templates' in p for p in cp.pack_index_problems()))

    def test_no_git_literal_raw_paths_only_and_ordinary_crlf_warns(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(cp, 'ROOT', td):
            root = Path(td)
            (root / '.gitattributes').write_text('raw.py -text\n*.md -text\n*.py -text\n', encoding='utf-8')
            for rel in ('raw.py', 'ordinary.py', 'notes.md'):
                (root / rel).write_bytes(b'# ordinary text\r\n')
            with mock.patch.object(cp.subprocess, 'run', side_effect=AssertionError('no Git needed')):
                self.assertEqual(cp.crlf_warning_paths(['raw.py', 'ordinary.py', 'notes.md']), ['ordinary.py', 'notes.md'])

    def test_pytest_cache_is_excluded_from_walk_selection_and_manifest_without_deletion(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(cp, 'ROOT', td):
            root = Path(td)
            cache = root / '.pytest_cache/README.md'
            cache.parent.mkdir()
            cache.write_bytes(b'local cache\r\n')
            (root / 'README.md').write_bytes(b'package\n')
            # Unknown sources still fail closed; cache selection needs a coherent clean fixture.
            with self.assertRaises(cp.ProjectionError) as refused:
                cp.delivery_manifest(['README.md'], branding=False)
            self.assertEqual(refused.exception.code, 'SOURCE_STATE_INVALID')
            (root / 'PROJECT.md').write_bytes(b'DATAMOCK project\n')
            rels = ['PROJECT.md', 'README.md']
            manifest = ''.join(cp.sha_bytes(rel, (root / rel).read_bytes()) + '  ' + rel + '\n' for rel in rels)
            (root / 'MANIFEST.sha256').write_text(manifest, encoding='utf-8')
            self.assertEqual(cp.source_state(), 'clean')
            self.assertNotIn('.pytest_cache/README.md', cp.all_files())
            self.assertNotIn('.pytest_cache/README.md', cp.delivery_selection(branding=False))
            self.assertNotIn(b'.pytest_cache', cp.delivery_manifest(rels, branding=False))
            self.assertEqual(cache.read_bytes(), b'local cache\r\n')

    def test_long_pack_description_is_rejected_and_fallback_keeps_words(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(pack, 'ROOT', td):
            root = Path(td)
            base = root / 'packs/demo'
            skill = base / 'skills/sample/SKILL.md'
            skill.parent.mkdir(parents=True)
            meta = {'name': 'demo', 'version': '1.0.0', 'requires_core': '1.0',
                    'title': {'en': 'Demo'}, 'description': {'en': 'Demo pack'}, 'skills': ['sample']}
            (base / 'pack.json').write_text(json.dumps(meta), encoding='utf-8')
            description = ('completeword ' * 30).strip()
            skill.write_text('---\nname: sample\ndescription: ' + description + '\nmetadata:\n  version: 1.0.0\n---\n', encoding='utf-8')
            self.assertTrue(any('220' in e for e in pack.validate_pack(str(base), 'demo')))
            rendered = pack.index_rows('demo', meta, pack.intake_state(meta))[0][2] % 'REVIEW'
            use = rendered.split('|')[5].strip()
            self.assertLessEqual(len(use), 220)
            self.assertTrue(use.endswith('completeword…'), use)

    def test_new_vi_en_then_add_pack_delivers_resolvable_complete_rows(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            for lang in ('vi', 'en'):
                result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(ROOT / 'tools/new_project.py'),
                                         '--name', lang, '--dest', td, '--lang', lang, '--apply'],
                                        capture_output=True, text=True, encoding='utf-8', timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                project = base / lang
                index = project / '.agent/SKILL_INDEX.md'
                self.assertNotIn('| PACK |', index.read_text(encoding='utf-8'))
                self.assertFalse((project / '.pytest_cache').exists())
                self.assertNotIn('.pytest_cache', (project / 'MANIFEST.sha256').read_text(encoding='utf-8'))
                result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(project / 'tools/pack.py'),
                                         'add', 'cang-logistics'], capture_output=True, text=True,
                                        encoding='utf-8', timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                rows = [line for line in index.read_text(encoding='utf-8').splitlines() if '| PACK |' in line]
                self.assertEqual(len(rows), 2)
                for row in rows:
                    cells = [cell.strip() for cell in row.split('|')]
                    self.assertTrue((project / cells[4]).is_file(), row)
                    self.assertTrue(cells[5].endswith('.'), cells[5])
                with mock.patch.object(cp, 'ROOT', str(project)):
                    self.assertEqual(cp.pack_index_problems(), [])
                    self.assertEqual(cp.crlf_warning_paths(cp.all_files()), [])

    def test_adopt_and_upgrade_preserve_installed_index_and_private_choices(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / 'package'
            cp.materialize(str(source), branding=False)
            target = Path(td) / 'existing'
            index = target / '.agent/SKILL_INDEX.md'
            installed = target / 'skills/local/packs/private/skills/own/SKILL.md'
            private = target / 'references/customer/README.md'
            for path, data in ((index, cp.delivery_bytes('.agent/SKILL_INDEX.md') + b'\n| own | LOCAL | PACK | skills/local/packs/private/skills/own/SKILL.md | private choice | DISABLED | user |\n'),
                               (installed, b'PRIVATE INSTALLED SKILL\n'), (private, b'PRIVATE CUSTOMER SOURCE\n')):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            before = {path: path.read_bytes() for path in (index, installed, private)}
            for script, arguments in (('adopt_project.py', ['--name', 'Existing']), ('upgrade_package.py', [])):
                result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(source / 'tools' / script),
                                         '--project', str(target), *arguments, '--apply'],
                                        capture_output=True, text=True, encoding='utf-8', timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual({path: path.read_bytes() for path in before}, before)


if __name__ == '__main__':
    unittest.main()
