"""Bounded source projection and consumer lifecycle checks; no release build."""
import builtins
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp


class FactoryContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='factory-context-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name)
        cls.pkg = cls.base / 'consumer'
        original_open, original_io_open = builtins.open, io.open

        def guard(fn):
            def opened(path, *args, **kwargs):
                if isinstance(path, (str, os.PathLike)):
                    full = Path(path).resolve()
                    if ROOT in full.parents:
                        rel = full.relative_to(ROOT).as_posix()
                        norm = rel[3:] if rel.startswith('en/') else rel
                        if norm in cp.USER_FILES or (cp.in_user_dir(rel) and not cp.package_readme(rel)):
                            raise AssertionError('live user read: ' + rel)
                return fn(path, *args, **kwargs)
            return opened

        with mock.patch('builtins.open', side_effect=guard(original_open)), \
             mock.patch('io.open', side_effect=guard(original_io_open)), \
             mock.patch('shutil.copytree', side_effect=AssertionError('copytree forbidden')):
            cp.materialize(str(cls.pkg), branding=False)

    def run_tool(self, base, name, *args):
        env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, str(base / 'tools' / name), *map(str, args)],
                                cwd=str(base), env=env, capture_output=True, encoding='utf-8', timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_source_materialized_clean_context(self):
        for rel, template in cp.TEMPLATE_OVERLAYS.items():
            self.assertEqual((self.pkg / rel).read_bytes(), (ROOT / template).read_bytes(), rel)
        self.assertEqual((self.pkg / cp.PROFILE_REL).read_bytes(), cp._ep().clean_profile_bytes())
        self.assertEqual((self.pkg / '.agent/INDEX.md').read_text(encoding='utf-8'), '# Chỉ mục nguồn\n\nChưa có nguồn được ghi nhận.\n')
        self.assertEqual((self.pkg / '.agent/PENDING_LESSONS.md').read_text(encoding='utf-8'), '# Bài học chờ xem xét\n\nChưa có bài học chờ xem xét.\n\nKhi có ứng viên, ghi nguồn, phạm vi dự kiến và kết quả xử lý hoặc liên kết quyết định. Đề xuất chung/riêng hay nhãn đã xử lý không tự chứng minh đã tích hợp hoặc tiếp nhận; không tự chuyển, xóa đầu ra project.\n')
        self.assertEqual((self.pkg / 'en/.agent/INDEX.md').read_text(encoding='utf-8'), '# Source index\n\nNo sources recorded yet.\n')
        self.assertEqual((self.pkg / 'en/.agent/PENDING_LESSONS.md').read_text(encoding='utf-8'), '# Lessons awaiting review\n\nNo lessons awaiting review.\n\nFor a candidate, record its source, proposed scope and disposition or link to the decision. A proposed shared/private label or a processed label does not itself prove integration or acceptance; do not move or delete project outputs automatically.\n')
        for rel in cp._NO_DELIVERY:
            if rel != 'MANIFEST.sha256':
                self.assertFalse((self.pkg / rel).exists(), rel)
            with self.assertRaises(cp.ProjectionError):
                cp.delivery_bytes(rel)
        self.assertFalse((self.pkg / '.agent/runtime').exists())
        self.assertFalse((self.pkg / '.claude').exists())
        with mock.patch.object(cp, 'USER_FILES', cp.USER_FILES | {'.agent/UNCLASSIFIED.md'}):
            with self.assertRaises(cp.ProjectionError) as err:
                cp.delivery_selection(branding=False)
            self.assertEqual(err.exception.code, 'UNCLASSIFIED_USER_FILES')

    def test_missing_each_overlay_and_absent_live_context(self):
        root = self.base / 'synthetic-source'
        for rel, template in cp.TEMPLATE_OVERLAYS.items():
            p = root / template
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(('DATAMOCK ' + rel).encode())
        (root / 'PROJECT.md').write_bytes(b'DATAMOCK')
        (root / 'MANIFEST.sha256').write_text(cp.sha_bytes('PROJECT.md', b'DATAMOCK') + '  PROJECT.md\n')
        for rel in ('.agent/MERGE_STATUS.json', 'setup_answers.json', 'en/.agent/PACKAGE_INFO.json',
                    'en/.agent/MERGE_STATUS.json', 'en/setup_answers.json', 'en/' + cp.PROFILE_REL):
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b'DATAMOCK excluded sentinel')
        with mock.patch.object(cp, 'ROOT', str(root)):
            self.assertEqual(cp.source_state(), 'maintainer')
            selected = cp.delivery_selection(branding=False)
            self.assertFalse(set(selected) & cp._NO_DELIVERY)
            for rel in cp.TEMPLATE_OVERLAYS:
                self.assertIn(rel, selected)
                self.assertEqual(cp.delivery_bytes(rel), ('DATAMOCK ' + rel).encode())
            for rel, template in cp.TEMPLATE_OVERLAYS.items():
                path = root / template
                data = path.read_bytes()
                path.unlink()
                self.assertEqual(cp.source_state(), 'unknown', rel)
                dest = self.base / ('refused-' + str(len(rel)))
                with self.assertRaises(cp.ProjectionError):
                    cp.materialize(str(dest), branding=False)
                self.assertFalse(dest.exists())
                with self.assertRaises(cp.ProjectionError):
                    cp.delivery_bytes(rel)
                path.write_bytes(data)

        marker_root = self.base / 'bad-marker'
        marker_root.mkdir()
        (marker_root / 'PROJECT.md').write_bytes(b'DATAMOCK')
        (marker_root / 'MANIFEST.sha256').write_text(cp.sha_bytes('PROJECT.md', b'DATAMOCK') + '  PROJECT.md\n')
        (marker_root / 'release_templates').write_bytes(b'DATAMOCK not a directory')
        with mock.patch.object(cp, 'ROOT', str(marker_root)):
            self.assertEqual(cp.source_state(), 'unknown')
            with self.assertRaises(cp.ProjectionError):
                cp.delivery_bytes('.agent/INDEX.md')
            with self.assertRaises(cp.ProjectionError):
                cp.materialize(str(self.base / 'bad-marker-dest'), branding=False)
            self.assertFalse((self.base / 'bad-marker-dest').exists())

    def test_clean_consumer_new_adopt_upgrade(self):
        def snapshot(root):
            return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
                    for p in root.rglob('*') if '__pycache__' not in p.parts}

        with mock.patch.object(cp, 'ROOT', str(self.pkg)):
            self.assertEqual(cp.source_state(), 'clean')
            cp.materialize(str(self.base / 'consumer-copy'), branding=False)
        for lang in ('vi', 'en'):
            name = 'New-' + lang
            before = snapshot(self.base)
            self.run_tool(self.pkg, 'new_project.py', '--name', name, '--dest', self.base, '--lang', lang)
            self.assertEqual(snapshot(self.base), before)
            self.assertFalse((self.base / name).exists())
            self.run_tool(self.pkg, 'new_project.py', '--name', name, '--dest', self.base, '--lang', lang, '--apply')
            project = self.base / name
            for rel in ('.agent/INDEX.md', '.agent/PENDING_LESSONS.md'):
                expected = ('en/' if lang == 'en' else '') + rel
                self.assertEqual((project / rel).read_bytes(), (self.pkg / expected).read_bytes())
                (project / rel).write_bytes(b'DATAMOCK user context\n')
            before = snapshot(project)
            self.run_tool(self.pkg, 'upgrade_package.py', '--project', project)
            self.assertEqual(snapshot(project), before)
            self.run_tool(self.pkg, 'upgrade_package.py', '--project', project, '--apply')
            for rel in ('.agent/INDEX.md', '.agent/PENDING_LESSONS.md'):
                self.assertEqual((project / rel).read_bytes(), b'DATAMOCK user context\n')
            target = self.base / ('Adopt-' + lang)
            (target / '.agent').mkdir(parents=True)
            for rel in ('.agent/INDEX.md', '.agent/PENDING_LESSONS.md'):
                (target / rel).write_bytes(b'DATAMOCK existing context\n')
            before = snapshot(target)
            self.run_tool(self.pkg, 'adopt_project.py', '--project', target, '--name', name, '--lang', lang)
            self.assertEqual(snapshot(target), before)
            self.assertFalse((target / 'VERSION').exists())
            self.run_tool(self.pkg, 'adopt_project.py', '--project', target, '--name', name, '--lang', lang, '--apply')
            for rel in ('.agent/INDEX.md', '.agent/PENDING_LESSONS.md'):
                self.assertEqual((target / rel).read_bytes(), b'DATAMOCK existing context\n')

    def test_synthetic_maintainer_materializes_without_reading_private_sentinels(self):
        root = self.base / 'sentinel-source'
        # Copy only the already projected, finite consumer fixture, never source ROOT.
        for source in self.pkg.rglob('*'):
            if source.is_file():
                dest = root / source.relative_to(self.pkg)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(source.read_bytes())
        for template in set(cp.TEMPLATE_OVERLAYS.values()) | set(cp.CVF_OVERLAY.values()) | {cp.PROFILE_TEMPLATE}:
            dest = root / template
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / template).read_bytes())
        sentinels = set(cp.TEMPLATE_OVERLAYS) | {cp.PROFILE_REL} | (cp._NO_DELIVERY - {'.agent/PACKAGE_INFO.json'})
        sentinels |= {'working/private.txt', 'output/private.txt', 'archive/private.txt',
                      'references/source-documents/private.txt', '.agent/runtime/private.txt',
                      '.claude/private.txt', 'en/working/private.txt'}
        for rel in sentinels:
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b'DATAMOCK private sentinel - must not be read or shipped\n')
        forbidden = {root / rel for rel in sentinels}
        original_open, original_io_open = builtins.open, io.open

        def guard(fn):
            def opened(path, *args, **kwargs):
                if isinstance(path, (str, os.PathLike)) and Path(path).resolve() in forbidden:
                    raise AssertionError('synthetic private read: ' + str(path))
                return fn(path, *args, **kwargs)
            return opened

        dest = self.base / 'sentinel-output'
        with mock.patch.object(cp, 'ROOT', str(root)), \
             mock.patch('builtins.open', side_effect=guard(original_open)), \
             mock.patch('io.open', side_effect=guard(original_io_open)), \
             mock.patch('shutil.copytree', side_effect=AssertionError('copytree forbidden')):
            cp.materialize(str(dest), branding=False)
        for rel in cp.TEMPLATE_OVERLAYS:
            self.assertEqual((dest / rel).read_bytes(), (self.pkg / rel).read_bytes())
        self.assertEqual((dest / cp.PROFILE_REL).read_bytes(), cp._ep().clean_profile_bytes())
        for rel in sentinels - set(cp.TEMPLATE_OVERLAYS) - {cp.PROFILE_REL, 'MANIFEST.sha256'}:
            self.assertFalse((dest / rel).exists(), rel)


if __name__ == '__main__':
    unittest.main()
