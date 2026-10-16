"""Behavior checks on synthetic files in disposable directories. No real project writes."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_output as co
import check_package as cp
import adopt_project as adopt
import transaction as tx
import app
import library
import merge_center
import result_schema


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return p


def run(script, *args, base=ROOT, nested=False):
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    if nested:  # đang ở trong bộ kiểm thử: build lồng không chạy lại cả bộ / already inside the suite
        env['LOCAL_AGENT_WORKSPACE_GATE_NESTED'] = '1'
    return subprocess.run([sys.executable, str(base / 'tools' / script), *map(str, args)],
                          cwd=base, env=env, capture_output=True, encoding='utf-8', timeout=60)


def manifest(root):
    lines = []
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name != 'MANIFEST.sha256':
            lines.append(hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest() + '  ' + p.relative_to(root).as_posix())
    write(root, 'MANIFEST.sha256', '\n'.join(lines) + '\n')


class Workflows(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='workspace-check-')
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def package(self, name='package'):
        dst = self.root / name
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist', 'roadmap', 'tests', 'feedback'))
        shutil.rmtree(str(dst / '.agent' / 'runtime'), ignore_errors=True)  # dữ liệu vận hành của máy phát triển không vào bản sao / dev-machine runtime data never enters the copy
        [f.unlink() for f in (dst / 'assets').glob('*') if f.is_file() and f.name != 'README.md']  # logo/nhận diện của máy phát triển / dev-machine branding
        return dst

    def test_adopt_preserves_instructions_both_languages_and_rerun(self):
        for lang in ('vi', 'en'):
            with self.subTest(lang=lang):
                target = self.root / lang
                for name in adopt.ADAPTERS:
                    write(target, name, 'PRIVATE INSTRUCTION ' + name)
                before = snapshot(target)
                preview = run('adopt_project.py', '--project', target, '--name', 'Example', '--lang', lang)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                self.assertEqual(snapshot(target), before)
                result = run('adopt_project.py', '--project', target, '--name', 'Example', '--lang', lang, '--apply')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('MERGE REQUIRED', result.stdout)
                for name in adopt.ADAPTERS:
                    self.assertEqual((target / name).read_bytes(), before[name])
                    src = ROOT / ('en' if lang == 'en' else '') / name
                    self.assertEqual((target / (name + '.new')).read_bytes(), src.read_bytes())
                after = snapshot(target)
                rerun = run('adopt_project.py', '--project', target, '--name', 'Example', '--apply')
                self.assertNotEqual(rerun.returncode, 0)
                self.assertEqual(snapshot(target), after)

    def test_adopt_conflicting_pending_file_blocks_all_writes(self):
        target = self.root / 'project'
        write(target, 'AGENTS.md', 'own instructions')
        write(target, 'AGENTS.md.new', 'merge in progress')
        before = snapshot(target)
        for args in ([], ['--apply']):
            r = run('adopt_project.py', '--project', target, '--name', 'Example', *args)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(snapshot(target), before)

    def test_adopt_identical_instruction_has_no_pending_copy(self):
        target = self.root / 'project'
        target.mkdir()
        shutil.copy2(ROOT / 'AGENTS.md', target / 'AGENTS.md')
        r = run('adopt_project.py', '--project', target, '--name', 'Example', '--apply')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((target / 'AGENTS.md.new').exists())

    def test_adopt_and_upgrade_emit_structured_results(self):
        target = self.root / 'adopt-structured'
        write(target, 'AGENTS.md', 'private')
        result = run('adopt_project.py', '--project', target, '--name', 'Example', '--result-json')
        human, data = result_schema.split_output(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data['status'], 'preview')
        self.assertTrue(data['changes'])
        self.assertTrue(data['merge_required'])
        self.assertNotIn(result_schema.MARKER, human)

        old, new = self.upgrade_fixture()
        result = run('upgrade_package.py', '--project', old, '--from', new, '--result-json')
        _, data = result_schema.split_output(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data['status'], 'preview')
        self.assertTrue(data['merge_required'])
        self.assertTrue(any(x['action'] == 'merge' for x in data['files']))

    def test_init_partial_context_and_private_instructions_survive_english(self):
        pkg = self.package()
        p = pkg / 'PROJECT.md'
        original = p.read_text(encoding='utf-8')
        p.write_text(original + '\nPRIVATE CONTEXT\n', encoding='utf-8')
        write(pkg, 'AGENTS.md', 'PRIVATE RULES')
        before = snapshot(pkg)
        r = run('init_project.py', '--name', 'Example', '--lang', 'en', '--dry-run', base=pkg)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(pkg), before)
        r = run('init_project.py', '--name', 'Example', '--lang', 'en', base=pkg)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('PRIVATE CONTEXT', p.read_text(encoding='utf-8'))
        self.assertIn('Example', p.read_text(encoding='utf-8'))
        self.assertEqual((pkg / 'AGENTS.md').read_text(), 'PRIVATE RULES')
        before = snapshot(pkg)
        r = run('init_project.py', '--name', 'Other', '--lang', 'en', '--force', base=pkg)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((pkg / 'PROJECT.md').read_bytes(), before['PROJECT.md'])
        self.assertEqual((pkg / '.agent/STATE.md').read_bytes(), before['.agent/STATE.md'])

    def test_init_clean_template(self):
        pkg = self.package()
        r = run('init_project.py', '--name', 'Example', base=pkg)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Example', (pkg / 'PROJECT.md').read_text(encoding='utf-8'))

    def upgrade_fixture(self):
        old, new = self.root / 'old', self.root / 'new'
        for root in (old, new):
            write(root, 'VERSION', '1.6.0\n')
            write(root, 'untouched.txt', 'old package')
            write(root, 'conflict.txt', 'old package')
            write(root, 'kept.txt', 'old package')
            write(root, 'PROJECT.md', 'private context')
            manifest(root)
        write(old, '.agent/PACKAGE_INFO.json', json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0', 'language': 'vi'}))
        write(old, 'conflict.txt', 'user change')
        write(old, 'kept.txt', 'user change')
        write(new, 'untouched.txt', 'new package')
        write(new, 'conflict.txt', 'new package')
        write(new, 'added.txt', 'new file')
        manifest(new)
        return old, new

    def test_upgrade_preview_apply_and_repeat(self):
        old, new = self.upgrade_fixture()
        before = snapshot(old)
        args = ('--project', old, '--from', new)
        r = run('upgrade_package.py', *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(old), before)
        r = run('upgrade_package.py', *args, '--apply')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((old / 'untouched.txt').read_text(), 'new package')
        self.assertEqual((old / 'conflict.txt').read_text(), 'user change')
        self.assertEqual((old / 'conflict.txt.new').read_text(), 'new package')
        self.assertEqual((old / 'kept.txt').read_text(), 'user change')
        self.assertEqual((old / 'PROJECT.md').read_bytes(), before['PROJECT.md'])
        after = snapshot(old)
        r = run('upgrade_package.py', *args, '--apply')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(old), after)

    def test_upgrade_preserves_pending_merge(self):
        old, new = self.upgrade_fixture()
        write(old, 'conflict.txt.new', 'work in progress')
        before = snapshot(old)
        r = run('upgrade_package.py', '--project', old, '--from', new, '--apply')
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(snapshot(old), before)

    def test_adopt_child_failure_is_not_reported_as_complete(self):
        target = self.root / 'project'
        write(target, 'tools/init_project.py', 'raise SystemExit(2)\n')
        r = run('adopt_project.py', '--project', target, '--name', 'Example', '--apply')
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn('Package added.', r.stdout)

    def test_adopt_write_failure_keeps_original(self):
        target = self.root / 'project'
        write(target, 'AGENTS.md', 'PRIVATE')
        with patch.dict(os.environ, {tx.FAULT_ENV: 'commit:1'}), \
                patch.object(sys, 'argv', ['adopt', '--project', str(target), '--name', 'Test', '--apply']), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(OSError):
                adopt.main()
        self.assertEqual((target / 'AGENTS.md').read_text(), 'PRIVATE')
        self.assertNotIn('Package added.', out.getvalue())
        self.assertEqual([x['status'] for x in tx.incomplete(str(target))], ['committing'])

    def test_output_mixed_unsupported_missing_and_review(self):
        good = write(self.root, 'good.txt', 'A complete text with enough content.')
        issue = write(self.root, 'issue.txt', 'The owner is [Person name] and needs review.')
        unknown = write(self.root, 'file.pdf', 'synthetic unsupported content')
        for files, code in [([good], 0), ([issue], 1), ([unknown], 2),
                            ([self.root / 'missing.txt'], 2), ([good, issue, unknown], 2)]:
            with self.subTest(files=files):
                r = run('check_output.py', *files)
                self.assertEqual(r.returncode, code, r.stdout + r.stderr)

    def test_docx_all_supported_parts_split_runs_and_corrupt_xml(self):
        for part in ('document', 'header1', 'footer1', 'footnotes', 'endnotes'):
            with self.subTest(part=part):
                path = self.root / (part + '.docx')
                def xml(text):
                    return '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p>' + text + '</w:p></w:document>'
                good = xml('<w:r><w:t>Complete document with enough content.</w:t></w:r>')
                placeholder = xml('<w:r><w:t>[Person </w:t></w:r><w:r><w:t>name]</w:t></w:r>')
                with zipfile.ZipFile(path, 'w') as z:
                    z.writestr('word/document.xml', placeholder if part == 'document' else good)
                    if part != 'document':
                        z.writestr('word/' + part + '.xml', placeholder)
                r = run('check_output.py', path)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        path = self.root / 'broken.docx'
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('word/document.xml', '<broken>')
        self.assertEqual(run('check_output.py', path).returncode, 2)

    def test_spreadsheet_findings_not_pass(self):
        r = run('check_output.py', ROOT / 'examples/demo-project/data/weekly_log.csv')
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        broken = write(self.root, 'broken.xlsx', 'not an Excel archive')
        self.assertEqual(run('check_output.py', broken).returncode, 2)

    def test_missing_excel_dependency(self):
        path = write(self.root, 'sample.xlsx', 'synthetic')
        with patch.object(sys, 'argv', ['check_output', str(path)]), \
                patch.object(importlib.util, 'find_spec', return_value=None), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as cm:
                co.main()
        self.assertEqual(cm.exception.code, 2)
        self.assertIn('python -m pip install openpyxl', out.getvalue())

    def test_app_propagates_checker_status(self):
        path = write(self.root, 'unknown.pdf', 'synthetic')
        result = app.action('check_output', {'files': [str(path)]})
        self.assertEqual(result['result']['status'], 'not_checked')
        result = app.action('check_output', {'files': [str(self.root / 'missing.txt')]})
        self.assertEqual(result['result']['status'], 'not_checked')

    def test_result_schema_roundtrip_and_invalid_data(self):
        value = result_schema.make('preview', changes=False, files=[{'path': 'a.txt'}])
        text_value = 'human output\n' + result_schema.MARKER + json.dumps(value)
        human, parsed = result_schema.split_output(text_value)
        self.assertEqual(human, 'human output')
        self.assertEqual(parsed, value)
        human, parsed = result_schema.split_output('text\n' + result_schema.MARKER + '{broken')
        self.assertIsNone(parsed)
        self.assertIn(result_schema.MARKER, human)

    def test_structured_tool_results_drive_panel(self):
        good = write(self.root, 'good.txt', 'A complete text with enough content.')
        result = app.action('check_output', {'files': [str(good)]})
        self.assertEqual(result['result']['schema'], result_schema.SCHEMA)
        self.assertEqual(result['result']['status'], 'success')
        self.assertFalse(result['result']['changes'])
        self.assertNotIn(result_schema.MARKER, result['out'])

    def test_merge_center_only_tracks_managed_files_and_persists_state(self):
        root = self.root / 'merge-project'
        write(root, 'managed.txt', 'current')
        write(root, 'managed.txt.new', 'new package')
        write(root, 'user-note.txt.new', 'user content')
        digest = hashlib.sha256(b'current').hexdigest()
        write(root, 'MANIFEST.sha256', digest + '  managed.txt\n')
        items = merge_center.scan(str(root))
        self.assertEqual([x['pending'] for x in items], ['managed.txt.new'])
        merge_center.set_state(str(root), 'managed.txt.new', 'reviewing')
        self.assertEqual(merge_center.scan(str(root))[0]['state'], 'reviewing')
        write(root, 'managed.txt.new', 'different package version')
        self.assertEqual(merge_center.scan(str(root))[0]['state'], 'unseen')
        with self.assertRaises(ValueError):
            merge_center.set_state(str(root), 'user-note.txt.new', 'ready')

    def test_release_uses_clean_templates_without_changing_worktree(self):
        before_state = (ROOT / '.agent/STATE.md').read_bytes()
        before_manifest = (ROOT / 'MANIFEST.sha256').read_bytes()
        out = self.root / 'release-out'
        result = run('build_release.py', '--out', out, '--result-json', nested=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((ROOT / '.agent/STATE.md').read_bytes(), before_state)
        self.assertEqual((ROOT / 'MANIFEST.sha256').read_bytes(), before_manifest)
        archive = next(out.glob('*.zip'))
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            state_name = next(n for n in names if n.endswith('/.agent/STATE.md') and '/en/' not in n)
            state = z.read(state_name).decode('utf-8')
            self.assertIn('[Phase/trạng thái hiện tại]', state)
            self.assertNotIn('15 kiểm thử', state)
            self.assertFalse(any('/release_templates/' in n or '/tests/' in n or '/roadmap/' in n for n in names))
        first_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
        result = run('build_release.py', '--out', out, '--result-json', nested=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), first_hash)

    def test_status_uses_evidence_not_folder_name(self):
        fake = self.root / 'local-agent-workspace'
        fake.mkdir()
        with patch.object(app, 'ROOT', str(fake)), patch.object(app, 'pack_info', return_value={'items': []}):
            self.assertEqual(app.status()['workspace_kind'], 'unknown')
            write(fake, 'PROJECT.md', 'Template')
            manifest(fake)
            self.assertEqual(app.status()['workspace_kind'], 'template')
            write(fake, '.agent/PACKAGE_INFO.json', '[]')
            self.assertEqual(app.status()['workspace_kind'], 'unknown')
            write(fake, '.agent/PACKAGE_INFO.json', json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0'}))
            self.assertEqual(app.status()['workspace_kind'], 'project')


if __name__ == '__main__':
    unittest.main()
