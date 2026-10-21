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
import upgrade_package as up


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
        [f.unlink() for f in (dst / 'assets').rglob('*') if f.is_file() and f.name != 'README.md']  # logo, font của máy phát triển / dev-machine branding and fonts
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
                    # bản package đi vào project là bytes đã projection (tham chiếu .cvf sang v3), không phải bytes thô của kho nguồn
                    self.assertEqual((target / (name + '.new')).read_bytes(), cp.delivery_bytes(('en/' if lang == 'en' else '') + name))
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
        (target / 'AGENTS.md').write_bytes(cp.delivery_bytes('AGENTS.md'))  # đúng bytes package sẽ giao / exactly the bytes the package ships
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


class UpgradeIdentity(unittest.TestCase):
    """D-01a: nhãn phiên bản tách khỏi baseline nội dung gói. Chỉ fixture trong thư mục tạm; kế hoạch giữ/cập nhật/xung đột vẫn do upgrade_package quyết định.
    The version label is told apart from the package content baseline. Fixtures only; the plan itself is still decided by upgrade_package."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='workspace-identity-')
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def pair(self, old_label='1.6.0', new_label='1.6.0'):
        old, new = self.root / 'old', self.root / 'new'
        for root, label in ((old, old_label), (new, new_label)):
            write(root, 'VERSION', label + '\n')
            write(root, 'untouched.txt', 'package one')
            write(root, 'kept.txt', 'package one')
            write(root, 'PROJECT.md', 'private context')
            manifest(root)
        write(old, '.agent/PACKAGE_INFO.json', json.dumps({'package': 'local-agent-workspace', 'version': old_label, 'language': 'vi'}))
        return old, new

    def rewrite_manifest(self, root, keep=lambda rel: True, reverse=False, eol=b'\n'):
        lines = [l for l in (root / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines() if l.strip() and keep(l.split('  ', 1)[1])]
        (root / 'MANIFEST.sha256').write_bytes(eol.join(x.encode('utf-8') for x in (lines[::-1] if reverse else lines)) + eol)

    def upgrade(self, old, new, *extra):
        r = run('upgrade_package.py', '--project', old, '--from', new, *extra, '--result-json')
        human, data = result_schema.split_output(r.stdout)
        return r, human, data

    def test_same_label_different_baseline_is_told_apart_and_apply_updates_by_plan(self):
        old, new = self.pair()
        write(new, 'untouched.txt', 'package two')
        manifest(new)
        before = snapshot(old)
        r, human, data = self.upgrade(old, new)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        pi = data['package_identity']
        self.assertEqual((data['status'], data['from_version'], data['to_version']), ('preview', '1.6.0', '1.6.0'))
        self.assertEqual(pi['relation'], 'SAME_LABEL_DIFFERENT_BASELINE')
        self.assertEqual((pi['version']['same'], pi['baseline']['same']), (True, False))
        self.assertEqual({pi['baseline'][k]['state'] for k in ('installed', 'source')}, {'KNOWN'})
        self.assertNotEqual(pi['baseline']['installed']['digest'], pi['baseline']['source']['digest'])
        self.assertIn('[SAME_LABEL_DIFFERENT_BASELINE]', human)
        self.assertEqual(snapshot(old), before)  # xem trước không ghi, không tạo runtime / the preview writes nothing, no runtime
        self.assertFalse((old / '.agent' / 'runtime').exists())
        r, human, data = self.upgrade(old, new, '--apply')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), r.stdout + r.stderr)
        self.assertEqual(data['package_identity']['relation'], 'SAME_LABEL_DIFFERENT_BASELINE')
        self.assertEqual((old / 'untouched.txt').read_text(), 'package two')
        self.assertEqual((old / 'VERSION').read_bytes(), before['VERSION'])  # nhãn không bị tăng giả / the label is not bumped
        self.assertEqual(json.loads((old / '.agent/PACKAGE_INFO.json').read_text())['version'], '1.6.0')
        r, human, data = self.upgrade(old, new)
        self.assertEqual(data['package_identity']['relation'], 'SAME_LABEL_SAME_BASELINE')
        self.assertFalse(data['changes'])

    def test_same_baseline_ignores_manifest_order_and_eol(self):
        old, new = self.pair()
        self.rewrite_manifest(old, eol=b'\n')
        self.rewrite_manifest(new, reverse=True, eol=b'\r\n')
        a, b = up.manifest_identity(str(old)), up.manifest_identity(str(new))
        self.assertEqual(a['state'], 'KNOWN')
        self.assertEqual(a, b)
        r, human, data = self.upgrade(old, new)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(data['package_identity']['relation'], 'SAME_LABEL_SAME_BASELINE')
        self.assertEqual((data['package_identity']['baseline']['same'], data['changes']), (True, False))
        # đổi nội dung một entry thì identity khác / one changed entry changes the identity
        write(new, 'untouched.txt', 'package two')
        manifest(new)
        self.assertNotEqual(up.manifest_identity(str(new))['digest'], a['digest'])

    def test_same_baseline_with_own_edits_keeps_them_and_still_does_the_remaining_work(self):
        old, new = self.pair()
        for root in (old, new):
            write(root, 'extra.txt', 'package one')
            write(root, '.agent/INDEX.md', 'template index')
            manifest(root)
        self.rewrite_manifest(old, keep=lambda rel: rel != '.agent/PACKAGE_INFO.json')  # manifest() đã nuốt PACKAGE_INFO của project / manifest() swept up the project's PACKAGE_INFO
        (old / 'extra.txt').unlink()  # file của package mà project thiếu / a package file the project lacks
        (old / '.agent' / 'INDEX.md').unlink()  # file mẫu của người dùng còn thiếu / a missing starter file
        write(old, 'kept.txt', 'user change')
        r, human, data = self.upgrade(old, new)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(data['package_identity']['relation'], 'SAME_LABEL_SAME_BASELINE')
        self.assertTrue(data['changes'])  # cùng baseline không short-circuit kế hoạch / the plan is not short-circuited by identity
        self.assertEqual({(f['path'], f['action']) for f in data['files']}, {('extra.txt', 'add'), ('.agent/INDEX.md', 'user_missing')})
        self.assertIn('kept.txt', human)
        kept = (old / 'kept.txt').read_bytes()
        r, human, data = self.upgrade(old, new, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((old / 'kept.txt').read_bytes(), kept)
        self.assertEqual((old / 'extra.txt').read_text(), 'package one')
        self.assertTrue((old / '.agent' / 'INDEX.md').is_file())
        self.assertFalse(list(old.rglob('*.new')))
        self.assertFalse(self.upgrade(old, new)[2]['changes'])

    def test_different_label_is_shown_with_its_own_baseline_relation(self):
        old, new = self.pair('1.6.0', '1.7.0')
        write(new, 'untouched.txt', 'package two')
        manifest(new)
        r, human, data = self.upgrade(old, new)
        self.assertEqual((data['from_version'], data['to_version']), ('1.6.0', '1.7.0'))
        self.assertEqual(data['package_identity']['relation'], 'DIFFERENT_LABEL_DIFFERENT_BASELINE')
        self.assertIn('[DIFFERENT_LABEL_DIFFERENT_BASELINE]', human)
        # nhãn đổi mà MANIFEST không ghi VERSION: cùng baseline, vẫn do kế hoạch quyết định việc làm / label bumped but the MANIFEST does not list VERSION
        old, new = self.root / 'o2', self.root / 'n2'
        for root, label in ((old, '1.6.0'), (new, '1.6.1')):
            write(root, 'VERSION', label + '\n')
            write(root, 'a.txt', 'package one')
            manifest(root)
            self.rewrite_manifest(root, keep=lambda rel: rel != 'VERSION')
        write(old, '.agent/PACKAGE_INFO.json', json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0', 'language': 'vi'}))
        r, human, data = self.upgrade(old, new)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(data['package_identity']['relation'], 'DIFFERENT_LABEL_SAME_BASELINE')
        self.assertEqual((data['package_identity']['version']['same'], data['package_identity']['baseline']['same']), (False, True))

    def test_a_missing_or_damaged_manifest_has_no_identity_whatever_the_label_says(self):
        base = self.root / 'm'
        good = 'a' * 64
        cases = {
            'MANIFEST_MALFORMED_LINE': (good + '  a.txt\nnot a manifest line\n').encode(),
            'MANIFEST_DUPLICATE_PATH': (good + '  a.txt\n' + good + '  a.txt\n').encode(),
            'MANIFEST_EMPTY': b'\n  \n',
            'MANIFEST_UNREADABLE': b'\xff\xfe\x00bad',
            'MANIFEST_AMBIGUOUS': (good + '  a\x0cb.txt\n').encode(),  # read_manifest tách ở \x0c / read_manifest splits at \x0c
        }
        for reason, raw in cases.items():
            with self.subTest(reason):
                base.mkdir(exist_ok=True)
                (base / 'MANIFEST.sha256').write_bytes(raw)
                got = up.manifest_identity(str(base))
                self.assertEqual((got['state'], got['reason'], got['digest'], got['entries']), ('UNKNOWN', reason, None, None))
        shutil.rmtree(str(base))
        base.mkdir()
        self.assertEqual(up.manifest_identity(str(base))['reason'], 'MANIFEST_MISSING')
        # cùng VERSION cũng không cứu được: relation UNKNOWN, baseline.same là null / the same VERSION does not rescue it
        old, new = self.pair()
        raw = (new / 'MANIFEST.sha256').read_bytes()
        line = raw.splitlines()[0] + b'\n'
        (new / 'MANIFEST.sha256').write_bytes(raw + line)  # entry trùng nhau từng byte: owner hiện vẫn cho chạy / a byte-identical duplicate: the owner still lets it run
        r, human, data = self.upgrade(old, new)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        pi = data['package_identity']
        self.assertEqual((pi['relation'], pi['version']['same'], pi['baseline']['same']), ('UNKNOWN', True, None))
        self.assertEqual(pi['baseline']['source']['reason'], 'MANIFEST_DUPLICATE_PATH')
        self.assertIn('[UNKNOWN]', human)
        (new / 'MANIFEST.sha256').write_bytes(raw)
        self.assertEqual(self.upgrade(old, new)[2]['files'], data['files'])  # kế hoạch không đổi vì identity / the plan does not depend on identity

    def test_refusals_for_a_missing_or_malformed_manifest_are_kept_and_nothing_is_written(self):
        for side in ('old', 'new'):
            for label, mutate in (('missing', lambda p: p.unlink()),
                                  ('malformed', lambda p: p.write_bytes(p.read_bytes() + b'khong phai dong manifest\n'))):
                with self.subTest(side=side, case=label):
                    shutil.rmtree(str(self.root), ignore_errors=True)
                    self.root.mkdir(exist_ok=True)
                    old, new = self.pair()
                    mutate((old if side == 'old' else new) / 'MANIFEST.sha256')
                    before = snapshot(old)
                    for extra in ((), ('--apply',)):
                        r = run('upgrade_package.py', '--project', old, '--from', new, *extra, '--result-json')
                        self.assertNotEqual(r.returncode, 0, r.stdout)
                        self.assertNotIn('package_identity', r.stdout)
                        self.assertEqual(snapshot(old), before)

    def test_real_upgrade_keeps_user_material_byte_for_byte(self):
        old, new = self.pair()
        for root in (old, new):
            write(root, 'conflict.txt', 'package one')
            write(root, '.agent/STATE.md', 'template state')
            write(root, '.agent/HANDOFF.md', 'template handoff')
            write(root, '.agent/INDEX.md', 'template index')
            write(root, '.agent/SKILL_INDEX.md', '| x | LOCAL | SHARED | skills/local/shared/x/SKILL.md |')
        for name in ('retired-plain', 'retired-edited'):
            write(old, 'skills/local/shared/%s/SKILL.md' % name, 'shared skill that the new package dropped')
        manifest(old)
        write(old, 'skills/local/shared/retired-edited/SKILL.md', 'edited shared skill')
        write(new, 'untouched.txt', 'package two')
        write(new, 'conflict.txt', 'package two')
        write(new, '.agent/STATE.md', 'newer template state')
        manifest(new)
        write(old, 'conflict.txt', 'user change')
        write(old, '.agent/STATE.md', 'real state')
        write(old, '.agent/HANDOFF.md', 'real handoff')
        write(old, '.agent/INDEX.md', 'real index with sources')
        write(old, '.agent/SKILL_INDEX.md', '| x | LOCAL | SHARED | skills/local/shared/x/SKILL.md |\n| retired-edited | LOCAL | SHARED | skills/local/shared/retired-edited/SKILL.md |')
        # tài liệu opaque: profile hỏng/phiên bản lạ, sổ nguồn không phải xlsx thật, đầu ra nhị phân, marker runtime, skill riêng
        opaque = {
            '.agent/EXECUTION_PROFILE.json': b'{"schema": "future/99", "owner": [',
            'references/_INDEX.xlsx': b'PK\x03\x04 not a real workbook',
            'references/source-documents/nguon.md': 'nguồn của tôi\n'.encode('utf-8'),
            'working/nhap.md': 'nháp\n'.encode('utf-8'),
            'output/ket-qua.docx': b'\x00\x01binary output\xff',
            'archive/cu.md': b'old',
            'skills/local/project/rieng/SKILL.md': 'kỹ năng riêng\n'.encode('utf-8'),
            '.agent/runtime/marker.txt': b'runtime marker',
        }
        for rel, raw in opaque.items():
            (old / rel).parent.mkdir(parents=True, exist_ok=True)
            (old / rel).write_bytes(raw)
        before = snapshot(old)
        r, human, data = self.upgrade(old, new)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(snapshot(old), before)
        self.assertIn('skills/local/shared/retired-edited/SKILL.md', human)  # liệt kê obsolete, không xóa / listed as obsolete, not deleted
        r, human, data = self.upgrade(old, new, '--apply')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), r.stdout + r.stderr)
        after = snapshot(old)
        changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        self.assertEqual({k for k in changed if not k.startswith('.agent/runtime/transactions/')},
                         {'untouched.txt', 'conflict.txt.new', 'MANIFEST.sha256', '.agent/PACKAGE_INFO.json'})
        for rel, raw in opaque.items():
            self.assertEqual(after[rel], raw, rel)
        for rel in ('.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md', '.agent/SKILL_INDEX.md', 'conflict.txt', 'kept.txt', 'PROJECT.md',
                    'skills/local/shared/retired-plain/SKILL.md', 'skills/local/shared/retired-edited/SKILL.md'):
            self.assertEqual(after[rel], before[rel], rel)
        self.assertEqual((old / 'conflict.txt.new').read_text(), 'package two')
        self.assertEqual([p.name for p in old.rglob('*.new')], ['conflict.txt.new'])

    def test_pending_merge_and_cvf_refusals_keep_their_behaviour_and_report_identity(self):
        old, new = self.pair()
        write(new, 'untouched.txt', 'package two')
        write(new, 'kept.txt', 'package two')
        manifest(new)
        write(old, 'kept.txt', 'user change')
        write(old, 'kept.txt.new', 'work in progress')
        before = snapshot(old)
        r, human, data = self.upgrade(old, new, '--apply')
        self.assertEqual((r.returncode, data['status']), (1, 'blocked'), r.stdout + r.stderr)
        self.assertTrue(data['merge_required'])
        self.assertEqual(data['package_identity']['relation'], 'SAME_LABEL_DIFFERENT_BASELINE')
        self.assertEqual(snapshot(old), before)
        write(old, 'kept.txt.new', 'package two')  # .new đã đúng bản package: không ghi đè, không báo lỗi / already the package version: kept
        r, human, data = self.upgrade(old, new, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(((old / 'kept.txt').read_text(), (old / 'kept.txt.new').read_text()), ('user change', 'package two'))
        # .cvf không hỗ trợ ở project: chặn cả --apply --force, giữ nguyên toàn cây / an unsupported .cvf stays refused even with --force
        old, new = self.root / 'o2', self.root / 'n2'
        for root in (old, new):
            write(root, 'VERSION', '1.6.0\n')
            write(root, 'a.txt', 'package one')
        write(old, '.agent/PACKAGE_INFO.json', json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0', 'language': 'vi'}))
        write(old, '.cvf/rules/v2/ROUTING_POLICY.json', '{}')
        manifest(old)
        manifest(new)
        before = snapshot(old)
        for extra in ((), ('--apply',), ('--apply', '--force')):
            r, human, data = self.upgrade(old, new, *extra)
            self.assertEqual((r.returncode, data['status']), (1, 'blocked'), r.stdout + r.stderr)
            self.assertIn('SOURCE_CVF_MISSING_FOR_TARGET', human)
            self.assertIn('package_identity', data)
            self.assertEqual(snapshot(old), before)


if __name__ == '__main__':
    unittest.main()
