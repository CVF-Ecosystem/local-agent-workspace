"""I3 checks: the one-runtime v3 package, its lifecycle (new / adopt / upgrade) and the controlled-flow readiness.

Everything runs on fake data in temporary folders. The package under test is a real RC archive built by tools/build_release.py (no --skip-check;
the nested marker only keeps the suite from re-running itself, exactly like test_workflows) and then extracted: projects are made from THAT
extracted package, not from the source tree. Nothing here activates a policy, migrates a record or touches a host, the global Python or CVF.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp  # noqa: E402
import result_schema  # noqa: E402

WINDOWS = os.name == 'nt'
HAVE_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
NEED = unittest.skipUnless(WINDOWS and HAVE_JSONSCHEMA, 'the controlled flow needs Windows NTFS and jsonschema (the pin check)')
CLOSURE = set(cp.CVF_CLOSURE)
V1_V2_MARKERS = ('/v2/', 'control_check_v2', 'control_check.py', 'ROUTING_POLICY.json', 'vectors', 'examples', 'EXPECTED', 'PROVENANCE', 'evidence')


def tree(root):
    """Every file and folder with bytes, runtime data included: proof that a refusal or preview changed nothing."""
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(Path(root).rglob('*'))
            if '__pycache__' not in p.parts}


def files(root):
    """Only the files (relative paths), for comparing sets of shipped files."""
    return {p.relative_to(root).as_posix() for p in Path(root).rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def norm(rel, data):
    """The archive stores text with LF; the source tree on this machine has CRLF. Compare text modulo that, but never the pinned owners."""
    if data is not None and rel not in cp.BYTE_EXACT + cp.CVF_MACHINE + cp.CVF_DEPENDENCIES and os.path.splitext(rel)[1] in cp.TEXT_EXT:
        return data.replace(b'\r\n', b'\n')
    return data


def unit_branding(rel):
    """The development machine's own logo, name and fonts ride along only from the source tree (the archive was built with --no-branding)."""
    return rel.startswith('assets/') and not rel.endswith('README.md')


def run(base, script, *args, env=None):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    e.update(env or {})
    return subprocess.run([sys.executable, str(Path(base) / 'tools' / script), *map(str, args)], cwd=str(base), env=e,
                          capture_output=True, encoding='utf-8', timeout=240)


def envelope(result):
    return result_schema.split_output(result.stdout)[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Rc(unittest.TestCase):
    """One real RC archive per class, extracted once; tests copy the extracted package before changing anything."""
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-i3-')
        cls.base = Path(cls.tmp.name)
        out = cls.base / 'out'
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', LOCAL_AGENT_WORKSPACE_GATE_NESTED='1')
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_release.py'), '--out', str(out), '--rc', '1', '--no-branding', '--result-json'],
                           cwd=str(ROOT), env=env, capture_output=True, encoding='utf-8', timeout=600)
        if r.returncode != 0:
            raise AssertionError('RC build failed: ' + r.stdout[-3000:] + r.stderr[-1000:])
        cls.archive = next(out.glob('*.zip'))
        cls.pkg = cls.base / 'pkg'
        with zipfile.ZipFile(cls.archive) as z:
            cls.names = z.namelist()
            z.extractall(str(cls.base / 'x'))
        (top,) = [p for p in (cls.base / 'x').iterdir()]
        shutil.move(str(top), str(cls.pkg))
        cls.tpl_tree = tree(cls.pkg)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-i3-w-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)

    def copy_pkg(self, name='pkg2'):
        dst = self.work / name
        shutil.copytree(str(self.pkg), str(dst))
        return dst

    def new_project(self, name='Demo', lang='vi', src=None):
        src = src or self.pkg
        r = run(src, 'new_project.py', '--name', name, '--dest', self.work, '--lang', lang, '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return self.work / name

    def old_project_without_cvf(self):
        """A project as an older package left it: no .cvf at all, and a MANIFEST that does not list it."""
        proj = self.new_project('Old')
        shutil.rmtree(str(proj / '.cvf'))
        lines = [l for l in (proj / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines() if ' .cvf/' not in l]
        (proj / 'MANIFEST.sha256').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return proj


class Archive(Rc):
    def test_archive_holds_exactly_the_v3_closure(self):
        inside = {n.split('/', 1)[1] for n in self.names if '/' in n and not n.endswith('/')}
        cvf = {n for n in inside if n.startswith('.cvf/')}
        self.assertEqual(cvf, CLOSURE)
        for n in cvf:
            self.assertFalse(any(m in n for m in V1_V2_MARKERS if m != 'ROUTING_POLICY.json'), n)
        self.assertFalse([n for n in inside if n.startswith(('.agent/runtime', 'tests/', 'roadmap/', 'release_templates/', 'feedback/', '.github/'))])
        self.assertNotIn('.cvf/rules/ROUTING_POLICY.json', inside)
        self.assertNotIn('.cvf/checks/control_check.py', inside)
        self.assertNotIn('.cvf/PROVENANCE.md', inside)

    def test_the_archive_carries_the_projected_references_not_the_v1_ones(self):
        for rel in ('AGENTS.md', 'en/AGENTS.md', 'roles/README.md', 'roles/scout/agent.md', 'roles/worker/agent.md', 'roles/reviewer/agent.md'):
            text = (self.pkg / rel).read_text(encoding='utf-8')
            self.assertNotIn('`.cvf/rules/CONTROL_RULES.md`', text, rel)
            self.assertNotIn('`.cvf/rules/ROUTING_POLICY.json`', text, rel)
            self.assertNotIn('`.cvf/contracts/`', text, rel)
            self.assertIn('.cvf/rules/v3/CONTROL_RULES.md', text, rel)
        self.assertIn('.cvf/contracts/v3/', (self.pkg / 'AGENTS.md').read_text(encoding='utf-8'))

    def test_pinned_owners_ship_byte_for_byte_and_match_the_policy_pins(self):
        policy = json.loads((self.pkg / '.cvf/rules/v3/ROUTING_POLICY.json').read_text(encoding='utf-8'))
        pins = {p['entrypoint']: p['entrypoint_sha256'] for p in policy['owner_protocols']}
        pins[policy['operational_context_protocol']['entrypoint']] = policy['operational_context_protocol']['entrypoint_sha256']
        self.assertEqual(set(pins), set(cp.BYTE_EXACT))
        for rel, want in pins.items():
            self.assertEqual('sha256:' + sha(self.pkg / rel), want, rel)
            self.assertEqual((self.pkg / rel).read_bytes(), (ROOT / rel).read_bytes(), rel + ' must not be re-encoded by the archive')

    def test_machine_bytes_equal_the_source_bytes(self):
        for rel in cp.CVF_MACHINE:
            self.assertEqual((self.pkg / rel).read_bytes(), (ROOT / rel).read_bytes(), rel)

    def test_manifest_is_computed_from_the_shipped_bytes_not_copied_from_the_source(self):
        shipped = (self.pkg / 'MANIFEST.sha256').read_bytes()
        self.assertEqual(shipped, cp.delivery_manifest(cp.delivery_selection(branding=False), branding=False))
        self.assertNotEqual(shipped, (ROOT / 'MANIFEST.sha256').read_bytes())
        lines = dict((line.split('  ', 1)[1], line.split('  ', 1)[0]) for line in shipped.decode('utf-8').splitlines())
        self.assertEqual(lines['AGENTS.md'], cp.sha_bytes('AGENTS.md', (self.pkg / 'AGENTS.md').read_bytes()))
        self.assertNotEqual(lines['AGENTS.md'], cp.sha('AGENTS.md'))  # the source AGENTS.md differs from what ships
        again = self.work / 'again'
        shutil.copytree(str(self.pkg), str(again))
        (again / 'MANIFEST.sha256').unlink()
        r = run(again, 'check_package.py', '--write-manifest')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((again / 'MANIFEST.sha256').read_bytes(), shipped)

    def test_extracted_package_passes_release_check_and_verify(self):
        for args in (('--release',), ('--verify',)):
            r = run(self.pkg, 'check_package.py', *args)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_template_is_recognised_by_contents_not_by_folder_name_or_marker(self):
        import app
        with mock.patch.object(app, 'ROOT', str(self.pkg)):
            self.assertEqual(app.workspace_kind({}), 'template')
        odd = self.copy_pkg('local-agent-workspace-maintainer')
        (odd / 'PROJECT.md').write_text((odd / 'PROJECT.md').read_text(encoding='utf-8') + '\nsửa tay\n', encoding='utf-8')
        with mock.patch.object(app, 'ROOT', str(odd)):
            self.assertEqual(app.workspace_kind({}), 'unknown')  # the name does not make it a template

    def test_the_release_check_turns_red_for_extras_runtime_and_changed_pins(self):
        def add(rel, text='{}'):
            def f(p):
                (p / rel).parent.mkdir(parents=True, exist_ok=True)
                (p / rel).write_text(text)
            return f

        def lf(rel):
            return lambda p: (p / rel).write_bytes((p / rel).read_bytes().replace(b'\r\n', b'\n'))

        def stray_reference(p):
            doc = p / 'roles/README.md'
            doc.write_text(doc.read_text(encoding='utf-8') + '\nxem `.cvf/rules/CONTROL_RULES.md`\n', encoding='utf-8')
        # (label, mutation, whether `--verify` alone stays green: an unlisted extra is invisible to a MANIFEST verify)
        cases = [('a v2 file', add('.cvf/rules/v2/ROUTING_POLICY.json'), True), ('a v1 owner', add('.cvf/rules/ROUTING_POLICY.json'), True),
                 ('a v2 checker', add('.cvf/checks/control_check_v2.py', 'x = 1\n'), True), ('a vectors file', add('.cvf/contracts/v3/vectors.json'), True),
                 ('a fixture', add('.cvf/contracts/v3/examples/ex01.json'), True), ('runtime data', add('.agent/runtime/transactions/x.json'), True),
                 ('a missing closure file', lambda p: (p / '.cvf/checks/v3/workflow.py').unlink(), False),
                 ('an LF pinned owner', lf('tools/publish_new.py'), False), ('a stray reference', stray_reference, False)]
        for label, mutate, verify_green in cases:
            with self.subTest(label):
                p = self.copy_pkg('red-' + re.sub(r'\W+', '-', label))
                mutate(p)
                r = run(p, 'check_package.py', '--release')
                self.assertEqual(r.returncode, 1, label + '\n' + r.stdout)
                if verify_green:
                    self.assertEqual(run(p, 'check_package.py', '--verify').returncode, 0, label)
        self.assertEqual(run(self.pkg, 'check_package.py', '--release').returncode, 0)


class Projection(unittest.TestCase):
    def test_idempotent_exact_replacement_and_eol_kept(self):
        for rel in cp.REF_REPLACEMENTS:
            with self.subTest(rel):
                raw = (ROOT / rel).read_bytes()
                once = cp.project_refs(rel, raw)
                self.assertEqual(cp.project_refs(rel, once), once)  # idempotent
                self.assertEqual(b'\r\n' in raw, b'\r\n' in once)
                self.assertNotEqual(once, raw)
                self.assertEqual(len(re.findall(rb'(?<!\r)\n', once)) == 0, len(re.findall(rb'(?<!\r)\n', raw)) == 0)

    def test_abnormal_anchors_are_refused_before_any_write(self):
        raw = (ROOT / 'roles/scout/agent.md').read_bytes()
        with self.assertRaises(cp.ProjectionError):
            cp.project_refs('roles/scout/agent.md', raw + b'\r\nthem `.cvf/rules/CONTROL_RULES.md`\r\n')  # one more occurrence than expected
        with self.assertRaises(cp.ProjectionError):
            cp.project_refs('roles/scout/agent.md', raw.replace(b'`.cvf/rules/CONTROL_RULES.md`', b'`.cvf/rules/KHAC.md`'))  # anchor gone
        lf = raw.replace(b'\r\n', b'\n')
        for valid in (lf, lf.replace(b'\n', b'\r\n')):
            with self.subTest(eol='CRLF' if b'\r\n' in valid else 'LF'):
                cp.project_refs('roles/scout/agent.md', valid)
        mixed = lf.replace(b'\n', b'\r\n', 1)
        self.assertNotEqual(mixed, lf)
        self.assertIn(b'\r\n', mixed)
        self.assertIn(b'\n', mixed.replace(b'\r\n', b''))
        with self.assertRaises(cp.ProjectionError) as caught:
            cp.project_refs('roles/scout/agent.md', mixed)
        self.assertEqual(caught.exception.code, 'MIXED_LINE_ENDINGS')
        with self.assertRaises(cp.ProjectionError):
            cp.project_refs('roles/scout/agent.md', b'\xff\xfe' + raw)  # not UTF-8

    def test_source_selection_never_ships_maintainer_or_older_runtime_files(self):
        sel = set(cp.delivery_selection(branding=False))
        self.assertEqual({r for r in sel if r.startswith('.cvf/')}, CLOSURE)
        self.assertFalse([r for r in sel if r.startswith(('tests/', 'roadmap/', 'release_templates/', 'feedback/', '.github/', '.agent/runtime'))])
        self.assertEqual(cp.delivery_problems(), [])
        # the source tree keeps v1/v2 for comparison
        self.assertTrue((ROOT / '.cvf/rules/ROUTING_POLICY.json').is_file() and (ROOT / '.cvf/checks/control_check_v2.py').is_file())

    def test_the_clean_templates_are_the_only_context_files_and_the_en_state_keeps_the_frame(self):
        import context_update
        for rel in ('.agent/STATE.md', 'en/.agent/STATE.md'):
            self.assertIsNone(context_update.state_problem(cp.delivery_bytes(rel).decode('utf-8')), rel)
        for rel in ('PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', 'en/PROJECT.md', 'en/.agent/STATE.md', 'en/.agent/HANDOFF.md'):
            self.assertEqual(cp.delivery_bytes(rel), (ROOT / cp.TEMPLATE_OVERLAYS[rel]).read_bytes(), rel)
        self.assertNotIn(b'maintainer-state', cp.delivery_bytes('.agent/STATE.md'))


class Lifecycle(Rc):
    def test_new_project_in_both_languages_uses_the_same_bytes_as_the_package(self):
        for lang in ('vi', 'en'):
            with self.subTest(lang):
                proj = self.new_project('P-' + lang, lang)
                self.assertEqual({r for r in files(proj) if r.startswith('.cvf/')}, CLOSURE)
                self.assertEqual((proj / '.agent/PACKAGE_INFO.json').is_file(), True)
                self.assertFalse([r for r in tree(proj) if r.startswith(('release_templates/', 'tests/', 'roadmap/', 'feedback/', '.github/'))])
                for rel in cp.CVF_CLOSURE:
                    self.assertEqual((proj / rel).read_bytes(), (self.pkg / rel).read_bytes(), rel)
                for rel in cp.BYTE_EXACT:
                    self.assertEqual((proj / rel).read_bytes(), (self.pkg / rel).read_bytes(), rel)
                self.assertEqual((proj / '.agent/HANDOFF.md').read_bytes(), (self.pkg / ('en/' if lang == 'en' else '') / '.agent/HANDOFF.md').read_bytes())
                v = run(proj, 'check_package.py', '--verify')
                self.assertEqual(v.returncode, 0, v.stdout + v.stderr)
                self.assertTrue((proj / '.agent/runtime').is_dir(), 'init bootstrap leaves the runtime parents the owners need')

    def test_new_project_from_the_source_and_from_the_package_are_byte_identical(self):
        (self.work / 'a').mkdir()
        (self.work / 'b').mkdir()
        a = run(self.pkg, 'new_project.py', '--name', 'Same', '--dest', self.work / 'a', '--apply')
        b = run(ROOT, 'new_project.py', '--name', 'Same', '--dest', self.work / 'b', '--apply')
        self.assertEqual((a.returncode, b.returncode), (0, 0), a.stdout + b.stdout + a.stderr + b.stderr)

        def snap(root):
            out = tree(root)
            out.pop('.agent/PACKAGE_INFO.json', None)  # initialized date only
            return {k: norm(k, v) for k, v in out.items() if not k.startswith('.agent/runtime/') and not unit_branding(k)}
        self.assertEqual(snap(self.work / 'a' / 'Same'), snap(self.work / 'b' / 'Same'))

    def test_adopt_keeps_user_files_adds_the_candidate_and_leaves_maintainer_files_out(self):
        for lang in ('vi', 'en'):
            with self.subTest(lang):
                target = self.work / ('old-' + lang)
                user = {'PROJECT.md': 'Của tôi\n', '.agent/STATE.md': 'Trạng thái của tôi\n', '.agent/HANDOFF.md': 'Bàn giao của tôi\n',
                        'references/policies/quy-che.md': 'quy chế\n', 'skills/local/project/rieng/SKILL.md': '---\nname: rieng\ndescription: Kỹ năng riêng của dự án để thử\n---\n',
                        'assets/branding.json': '{"title": "Của tôi"}\n', 'output/ket-qua.md': 'kết quả\n'}
                for rel, text in user.items():
                    f = target / rel
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_bytes(text.encode('utf-8'))
                before = tree(target)
                pv = run(self.pkg, 'adopt_project.py', '--project', target, '--name', 'Cũ', '--lang', lang, '--result-json')
                self.assertEqual(pv.returncode, 0, pv.stdout + pv.stderr)
                self.assertEqual(tree(target), before)  # preview writes nothing
                ap = run(self.pkg, 'adopt_project.py', '--project', target, '--name', 'Cũ', '--lang', lang, '--apply')
                self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
                after = tree(target)
                for rel, text in user.items():
                    self.assertEqual(after[rel], text.encode('utf-8'), rel)
                self.assertEqual({r for r in files(target) if r.startswith('.cvf/')}, CLOSURE)
                self.assertFalse([r for r in after if r.startswith(('release_templates/', 'tests/', 'roadmap/', 'feedback/', '.github/'))])
                self.assertTrue(CLOSURE <= {r for r in after})
                for rel in cp.BYTE_EXACT:
                    self.assertEqual(after[rel], (self.pkg / rel).read_bytes(), rel)

    def test_adopt_from_the_source_tree_and_from_the_package_give_the_same_project(self):
        out = []
        for label, src in (('pkg', self.pkg), ('src', ROOT)):
            target = self.work / label
            (target / 'working').mkdir(parents=True)
            r = run(src, 'adopt_project.py', '--project', target, '--name', 'Same', '--apply')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            snap = tree(target)
            snap.pop('.agent/PACKAGE_INFO.json', None)
            out.append({k: norm(k, v) for k, v in snap.items() if not k.startswith('.agent/runtime/') and not unit_branding(k)})
        self.assertEqual(out[0], out[1])

    def test_adopt_refuses_a_target_with_another_cvf_and_leaves_the_whole_tree(self):
        cases = {
            'v1 owner': {'.cvf/rules/ROUTING_POLICY.json': '{}'},
            'v2 tree': {'.cvf/rules/v2/ROUTING_POLICY.json': '{}'},
            'unknown version': {'.cvf/rules/v4/ROUTING_POLICY.json': '{}'},
        }
        for label, files in cases.items():
            with self.subTest(label):
                target = self.work / re.sub(r'\W+', '-', label)
                (target / '.agent' / 'runtime').mkdir(parents=True)
                for rel, text in files.items():
                    (target / rel).parent.mkdir(parents=True, exist_ok=True)
                    (target / rel).write_text(text)
                before = tree(target)
                for extra in ((), ('--apply',)):
                    r = run(self.pkg, 'adopt_project.py', '--project', target, '--name', 'X', *extra, '--result-json')
                    self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                    self.assertEqual(envelope(r)['status'], 'blocked')
                    self.assertEqual(tree(target), before)

    def test_adopt_and_new_refuse_an_initialized_project_as_the_source(self):
        proj = self.new_project('Src')
        target = self.work / 'dest'
        target.mkdir()
        r = run(proj, 'adopt_project.py', '--project', target, '--name', 'X', '--apply', '--result-json')
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(tree(target), {})
        r = run(proj, 'new_project.py', '--name', 'Y', '--dest', self.work, '--apply', '--result-json')
        self.assertEqual(r.returncode, 1)
        self.assertFalse((self.work / 'Y').exists())

    def test_a_template_with_an_unsupported_cvf_cannot_make_projects(self):
        tpl = self.copy_pkg('tpl-bad')
        (tpl / '.cvf/rules/v2').mkdir(parents=True)
        (tpl / '.cvf/rules/v2/ROUTING_POLICY.json').write_text('{}')
        before = tree(tpl)
        for extra in ((), ('--apply',)):
            r = run(tpl, 'new_project.py', '--name', 'Z', '--dest', self.work, *extra, '--result-json')
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertFalse((self.work / 'Z').exists())
            self.assertEqual(tree(tpl), before)
        self.assertEqual([p.name for p in self.work.iterdir() if p.name.startswith('.')], [])

    # ---------------------------------------------------------------- upgrade
    def upgrade(self, proj, src=None, *extra):
        return run(src or self.pkg, 'upgrade_package.py', '--project', proj, *extra, '--result-json')

    def test_upgrade_adds_the_candidate_to_a_project_without_cvf_and_keeps_the_rest(self):
        proj = self.old_project_without_cvf()
        (proj / 'working').mkdir(exist_ok=True)
        (proj / 'working' / 'nhap.md').write_text('nháp của tôi\n', encoding='utf-8')
        before = tree(proj)
        pv = self.upgrade(proj)
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertEqual(tree(proj), before)
        ap = self.upgrade(proj, None, '--apply')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        after = tree(proj)
        self.assertEqual({r for r in files(proj) if r.startswith('.cvf/')}, CLOSURE)
        for rel in CLOSURE:
            self.assertEqual(after[rel], (self.pkg / rel).read_bytes(), rel)
        for rel, data in before.items():
            if data is not None and not rel.startswith(('.agent/runtime/', '.cvf/')) and rel not in ('MANIFEST.sha256', '.agent/PACKAGE_INFO.json'):
                self.assertEqual(after[rel], data, rel)
        self.assertEqual(run(proj, 'check_package.py', '--verify').returncode, 0)

    def test_upgrade_of_a_coherent_v3_project_is_a_no_op_and_takes_readable_changes_by_three_way(self):
        proj = self.new_project('Same')
        before = tree(proj)
        r = self.upgrade(proj, None, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        expected = {k: v for k, v in before.items() if not k.startswith('.agent/runtime/')}
        expected.update({'.agent/PACKAGE_INFO.json': (proj / '.agent/PACKAGE_INFO.json').read_bytes(), 'MANIFEST.sha256': before['MANIFEST.sha256']})
        self.assertEqual({k: v for k, v in tree(proj).items() if not k.startswith('.agent/runtime/')}, expected)
        newer = self.copy_pkg('newer')
        rules = newer / '.cvf/rules/v3/CONTROL_RULES.md'
        rules.write_bytes(rules.read_bytes() + '\nGhi chú bản mới.\n'.encode('utf-8'))
        self.assertEqual(run(newer, 'check_package.py', '--write-manifest').returncode, 0)
        r = self.upgrade(proj, newer, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((proj / '.cvf/rules/v3/CONTROL_RULES.md').read_bytes(), rules.read_bytes())
        for rel in cp.CVF_MACHINE:
            self.assertEqual((proj / rel).read_bytes(), (self.pkg / rel).read_bytes(), rel)  # machine bytes untouched

    def block_cases(self):
        """(label, mutate(project)): every target state the guard has to refuse, each also with --apply --force."""
        def add(rel, text='{}'):
            def f(p):
                (p / rel).parent.mkdir(parents=True, exist_ok=True)
                (p / rel).write_text(text)
            return f

        def edit(rel):
            def f(p):
                (p / rel).write_bytes((p / rel).read_bytes() + b'\n ')
            return f

        def partial(p):
            (p / '.cvf/checks/v3/workflow.py').unlink()

        def cvf_is_a_file(p):
            shutil.rmtree(str(p / '.cvf'))
            (p / '.cvf').write_text('không phải thư mục', encoding='utf-8')

        def only_readable(p):
            for rel in cp.CVF_MACHINE:
                (p / rel).unlink()
        return [('v1 owner', add('.cvf/rules/ROUTING_POLICY.json')), ('v2 tree', add('.cvf/rules/v2/ROUTING_POLICY.json')),
                ('mixed v2 beside v3', add('.cvf/checks/control_check_v2.py', 'x = 1\n')), ('unknown version', add('.cvf/rules/v4/ROUTING_POLICY.json')),
                ('partial closure', partial), ('only readable docs', only_readable), ('changed canonical policy', edit('.cvf/rules/v3/ROUTING_POLICY.json')),
                ('changed schema', edit('.cvf/contracts/v3/control.schema.json')), ('changed checker module', edit('.cvf/checks/v3/loader.py')),
                ('changed entry', edit('.cvf/checks/control_check_v3.py')), ('.cvf is a file', cvf_is_a_file),
                ('user-edited owner dependency', edit('tools/publish_new.py')), ('user-edited context owner', edit('tools/context_update.py')),
                ('user-edited transaction', edit('tools/transaction.py')), ('user-edited current_draft', edit('tools/current_draft.py'))]

    def test_upgrade_refuses_every_unsupported_target_even_with_force_and_changes_nothing(self):
        for label, mutate in self.block_cases():
            with self.subTest(label):
                proj = self.new_project('B-' + re.sub(r'\W+', '-', label))
                mutate(proj)
                (proj / '.agent' / 'runtime' / 'transactions' / 'keep.txt').write_text('runtime data')
                before = tree(proj)
                for extra in ((), ('--apply',), ('--apply', '--force')):
                    r = self.upgrade(proj, None, *extra)
                    self.assertEqual(r.returncode, 1, label + ' ' + str(extra) + '\n' + r.stdout + r.stderr)
                    self.assertEqual(envelope(r)['status'], 'blocked', label)
                    self.assertEqual(tree(proj), before, label)  # whole tree incl. runtime, no .new, no backup, no MANIFEST change

    def test_a_user_edited_cvf_doc_that_the_package_also_changed_blocks_instead_of_making_a_new_file(self):
        proj = self.new_project('Edit')
        doc = proj / '.cvf/rules/v3/CONTROL_RULES.md'
        doc.write_bytes(doc.read_bytes() + 'dòng của tôi\n'.encode('utf-8'))
        newer = self.copy_pkg('newer2')
        n = newer / '.cvf/rules/v3/CONTROL_RULES.md'
        n.write_bytes(n.read_bytes() + 'dòng của bản mới\n'.encode('utf-8'))
        self.assertEqual(run(newer, 'check_package.py', '--write-manifest').returncode, 0)
        before = tree(proj)
        for extra in ((), ('--apply', '--force')):
            r = self.upgrade(proj, newer, *extra)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertEqual(tree(proj), before)
        self.assertFalse(list(proj.rglob('*.new')))

    def test_upgrade_refuses_a_source_that_is_not_a_consistent_v3_package(self):
        proj = self.new_project('Dest')
        before = tree(proj)
        stale = self.copy_pkg('stale')
        (stale / 'README.md').write_text('đã sửa sau khi lập MANIFEST\n', encoding='utf-8')
        extra = self.copy_pkg('extra')
        (extra / '.cvf/rules/v2').mkdir(parents=True)
        (extra / '.cvf/rules/v2/ROUTING_POLICY.json').write_text('{}')
        missing = self.copy_pkg('missing')
        (missing / '.cvf/checks/v3/routing.py').unlink()
        for label, src in (('stale MANIFEST', stale), ('v2 extra', extra), ('missing closure file', missing), ('maintainer source', ROOT)):
            with self.subTest(label):
                r = self.upgrade(proj, src, '--apply', '--force')
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertEqual(tree(proj), before)
        self.assertEqual([x for x in (ROOT / '.agent').glob('*.new')], [])

    def test_upgrade_of_an_older_package_without_cvf_to_a_package_without_cvf_still_works(self):
        old, new = self.work / 'o', self.work / 'n'
        for root in (old, new):
            (root / '.agent').mkdir(parents=True)
            (root / 'VERSION').write_text('1.6.0\n')
            (root / 'a.txt').write_text('old\n')
            (root / 'PROJECT.md').write_text('mine\n')
        (old / '.agent/PACKAGE_INFO.json').write_text(json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0', 'language': 'vi'}))
        (new / 'a.txt').write_text('new\n')
        for root in (old, new):
            lines = ['%s  %s' % (hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest(), p.relative_to(root).as_posix()) for p in sorted(root.rglob('*'))
                     if p.is_file() and p.name not in ('MANIFEST.sha256', 'PACKAGE_INFO.json')]
            (root / 'MANIFEST.sha256').write_text('\n'.join(lines) + '\n')
        r = run(self.pkg, 'upgrade_package.py', '--project', old, '--from', new, '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((old / 'a.txt').read_bytes().replace(b'\r\n', b'\n'), b'new\n')


@NEED
class Journey(Rc):
    """The demo from the extracted archive: a new project, the readiness, a P-CN1 draft, the Current draft selection and a P-CTX1 STATE update."""

    def test_extracted_package_to_selected_draft(self):
        import publish_new as pn
        proj = self.new_project('Hanh trinh')
        status = run(proj, 'current_draft.py', 'status', '--project', proj, '--result-json')
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(envelope(status)['pointer']['state'], 'NONE')
        (proj / 'references' / 'source-documents').mkdir(parents=True, exist_ok=True)
        src = proj / 'references' / 'source-documents' / 'quy-che.pdf'
        src.write_bytes(b'%PDF fake source')
        att = {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:msg/0012', 'recorded_by': {'actor_id': 'main', 'role': 'main'}}
        request = {'work_id': 'w-1', 'target': 'working/w-1/bao-cao.docx',
                   'intent_ref': {'ref_id': 'intent-1', 'locator': 'host:msg/0012', 'digest': 'sha256:' + '5' * 64, 'attribution': att},
                   'main_interpretation': 'Báo cáo ngắn', 'requirements': [{'req_id': 'REQ-1', 'statement': 'Tóm tắt', 'mandatory': True}],
                   'grant_refs': [{'ref_id': 'grant-1', 'locator': 'PROJECT.md#pham-vi', 'digest': 'sha256:' + '1' * 64, 'attribution': att}],
                   'subject': {'actor_id': 'main', 'role': 'main'},
                   'inputs': [{'path': 'references/source-documents/quy-che.pdf', 'digest': pn._sha_bytes(b'%PDF fake source')}]}
        (self.work / 'request.json').write_text(json.dumps(request), encoding='utf-8')
        (self.work / 'draft.bin').write_bytes('PK bản nháp'.encode('utf-8'))
        rid = 'a' * 32
        pub = run(proj, 'publish_new.py', 'publish', '--request', self.work / 'request.json', '--staged', self.work / 'draft.bin', '--rid', rid, '--project', proj, '--result-json')
        self.assertEqual(pub.returncode, 0, pub.stdout + pub.stderr)
        pv = envelope(run(proj, 'current_draft.py', 'select', '--rid', rid, '--project', proj, '--result-json'))
        self.assertEqual(pv['result'], 'PREVIEW', pv)
        ap = run(proj, 'current_draft.py', 'select', '--rid', rid, '--apply', '--expected-state', pv['state_sha256'],
                 '--expected-selection', pv['selection_fingerprint'], '--project', proj, '--result-json')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        final = envelope(run(proj, 'current_draft.py', 'status', '--project', proj, '--result-json'))
        self.assertEqual((final['pointer']['state'], final['selected']['state']), ('SET', 'matched'))
        self.assertEqual(run(proj, 'check_package.py', '--verify').returncode, 0)  # STATE is the user's file; the package bytes are untouched
        entry = subprocess.run([sys.executable, '-B', '-I', str(proj / '.cvf/checks/control_check_v3.py'), '--help'], cwd=str(proj), capture_output=True, encoding='utf-8')
        self.assertEqual(entry.returncode, 0, entry.stdout + entry.stderr)



    def test_adopted_and_upgraded_projects_are_ready_for_the_same_flow(self):
        target = self.work / 'adopted'
        (target / 'references').mkdir(parents=True)
        r = run(self.pkg, 'adopt_project.py', '--project', target, '--name', 'Adopted', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        runtime = target / '.agent' / 'runtime'
        self.assertTrue(runtime.is_dir() and not os.path.islink(str(runtime)), 'the transaction bootstrap leaves plain runtime parents')
        s = run(target, 'current_draft.py', 'status', '--project', target, '--result-json')
        self.assertEqual((s.returncode, envelope(s)['result']), (0, 'OK'), s.stdout + s.stderr)
        old = self.old_project_without_cvf()
        r = run(self.pkg, 'upgrade_package.py', '--project', old, '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        s = run(old, 'current_draft.py', 'status', '--project', old, '--result-json')
        self.assertEqual((s.returncode, envelope(s)['result']), (0, 'OK'), s.stdout + s.stderr)

    def test_a_changed_pinned_owner_makes_the_card_unavailable_and_nothing_falls_back(self):
        proj = self.new_project('Pin')
        owner = proj / 'tools' / 'publish_new.py'
        owner.write_bytes(owner.read_bytes().replace(b'\r\n', b'\n'))  # same text, other line endings: the pin is over raw bytes
        before = tree(proj)
        r = run(proj, 'current_draft.py', 'status', '--project', proj, '--result-json')
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertEqual((envelope(r)['result'], envelope(r)['reason']), ('UNAVAILABLE', 'OWNER_UNAVAILABLE'))
        ready = subprocess.run([sys.executable, '-B', '-c', 'import sys, json; sys.path.insert(0, "tools"); import current_draft; print(json.dumps(current_draft.readiness(".")))'],
                               cwd=str(proj), capture_output=True, encoding='utf-8', env=dict(os.environ, PYTHONUTF8='1'))
        self.assertEqual(ready.returncode, 0, ready.stdout + ready.stderr)
        got = json.loads(ready.stdout.strip().splitlines()[-1])
        self.assertEqual((got['usable'], got['reason']), (False, 'OWNER_UNAVAILABLE'))
        self.assertEqual(tree(proj), before)


class Readiness(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-i3-r-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)

    def project(self):
        p = self.work / 'p'
        (p / '.agent' / 'runtime').mkdir(parents=True)
        (p / '.agent' / 'STATE.md').write_text('# PROJECT STATE\n', encoding='utf-8')
        return p

    @NEED
    def test_usable_here_reads_only_and_never_installs(self):
        import current_draft
        p = self.project()
        before = tree(p)
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('no subprocess')), mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('no subprocess')):
            r = current_draft.readiness(str(p))
        self.assertEqual((r['usable'], r['reason'], r['python']), (True, None, sys.executable), r)
        self.assertEqual(r['fs'], 'NTFS')
        self.assertEqual(tree(p), before)

    def run_with(self, snippet):
        code = ('import sys, json\nsys.path.insert(0, %r)\n%s\nimport current_draft\nprint(json.dumps(current_draft.readiness(sys.argv[1])))\n'
                % (str(ROOT / 'tools'), snippet))
        r = subprocess.run([sys.executable, '-B', '-c', code, str(self.project())], capture_output=True, encoding='utf-8', env=dict(os.environ, PYTHONUTF8='1'))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout.strip().splitlines()[-1])

    @unittest.skipUnless(WINDOWS, 'the controlled flow is Windows only')
    def test_missing_jsonschema_makes_the_card_unavailable_and_the_rest_keep_working(self):
        r = self.run_with("sys.modules['jsonschema'] = None")
        self.assertEqual((r['usable'], r['reason']), (False, 'DEPENDENCY_MISSING'))
        import app
        code = ('import sys, json\nsys.path.insert(0, %r)\nsys.modules["jsonschema"] = None\nimport app\n'
                'print(json.dumps({c["feature"]: [c["usable"], c.get("reason")] for c in app.components()}))\n' % str(ROOT / 'tools'))
        out = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, encoding='utf-8', env=dict(os.environ, PYTHONUTF8='1'))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        feats = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(feats['controlled'], [False, 'DEPENDENCY_MISSING'])
        self.assertEqual(feats['python'][0], True)  # the other features keep their own conditions
        self.assertIn('controlled', {c['feature'] for c in app.components()})

    @unittest.skipUnless(WINDOWS, 'the controlled flow is Windows only')
    def test_an_old_jsonschema_is_not_enough(self):
        r = self.run_with("import importlib.metadata as m\n_v = m.version\nm.version = lambda name: '4.17.3' if name == 'jsonschema' else _v(name)")
        self.assertEqual((r['usable'], r['reason'], r['jsonschema']), (False, 'DEPENDENCY_MISSING', '4.17.3'))

    @NEED
    def test_an_unsupported_filesystem_is_unavailable_not_a_fallback(self):
        import current_draft
        p = self.project()
        pn = current_draft.Env(str(p)).pn
        with mock.patch.object(pn, 'volume_supported', return_value=(False, {'fs': 'FAT32', 'local': True, 'drive_type': 3, 'cloud_attributes': False})):
            r = current_draft.readiness(str(p))
            card = current_draft.status(str(p))
        self.assertEqual((r['usable'], r['reason'], r['fs']), (False, 'FS_UNSUPPORTED', 'FAT32'))
        self.assertEqual(card['result'], 'OK')  # the card itself still goes through the owner's own volume check when it writes; readiness reports the condition

    def test_other_platforms_are_unsupported(self):
        import current_draft
        with mock.patch.object(os, 'name', 'posix'):
            r = current_draft.readiness(str(self.project()))
        self.assertEqual((r['usable'], r['reason']), (False, 'PLATFORM_UNSUPPORTED'))

    def test_the_launcher_does_not_pick_another_python_or_install_anything(self):
        text = (ROOT / 'APP.bat').read_text(encoding='utf-8', errors='replace').lower()
        self.assertNotIn('pip', text)
        self.assertNotIn('venv', text)
        self.assertEqual(len(re.findall(r'py -3', text)), 1)


class GuardReview(unittest.TestCase):
    """Focused review regressions: no target code executes and every refusal precedes mutation."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='law-i3-review-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / 'source'
        cp.materialize(str(self.source), branding=False)
        self.target = self.base / 'target'
        shutil.copytree(self.source, self.target)
        (self.target / '.agent/PACKAGE_INFO.json').write_text(json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0', 'language': 'vi'}))
        (self.target / '.agent/runtime').mkdir()
        (self.target / '.agent/runtime/keep.txt').write_bytes(b'keep runtime')

    def refused_upgrade(self):
        before = tree(self.target)
        for extra in ((), ('--apply',), ('--apply', '--force')):
            r = run(ROOT, 'upgrade_package.py', '--project', self.target, '--from', self.source, '--result-json', *extra)
            self.assertEqual((r.returncode, envelope(r)['status']), (1, 'blocked'), r.stdout + r.stderr)
            self.assertEqual(tree(self.target), before)

    def test_empty_or_readable_partial_cvf_is_not_absent(self):
        shutil.rmtree(self.target / '.cvf')
        (self.target / '.cvf').mkdir()
        self.refused_upgrade()

    def test_a_package_without_cvf_cannot_upgrade_a_target_with_cvf(self):
        shutil.rmtree(self.source / '.cvf')
        mf = self.source / 'MANIFEST.sha256'
        mf.write_text('\n'.join(l for l in mf.read_text().splitlines() if '  .cvf/' not in l) + '\n')
        self.refused_upgrade()

    def test_leaf_links_are_outside_the_runtime_closure(self):
        leaf = self.target / '.cvf/rules/v3/ROUTING_POLICY.json'
        real = cp._is_link
        with mock.patch.object(cp, '_is_link', side_effect=lambda p: Path(p) == leaf or real(p)):
            kind, found = cp.cvf_inventory(str(self.target))
            self.assertEqual(kind, 'DIR')
            self.assertIn('.cvf/rules/v3/ROUTING_POLICY.json@link', found)
            errors = cp.cvf_target_problems(str(self.target), lambda rel: (self.source / rel).read_bytes())
        self.assertTrue(errors)

    def test_raw_owner_eol_change_blocks_even_when_manifest_hash_still_matches(self):
        owner = self.target / 'tools/publish_new.py'
        raw = owner.read_bytes()
        self.assertIn(b'\r\n', raw)
        owner.write_bytes(raw.replace(b'\r\n', b'\n'))
        self.assertEqual(cp.sha_bytes('tools/publish_new.py', raw), cp.sha_bytes('tools/publish_new.py', owner.read_bytes()))
        self.refused_upgrade()

    def test_source_manifest_must_declare_the_runtime_it_carries(self):
        mf = self.source / 'MANIFEST.sha256'
        mf.write_text('\n'.join(l for l in mf.read_text().splitlines() if '  .cvf/' not in l) + '\n')
        self.assertIn('SOURCE_MANIFEST_INCOMPLETE', [code for code, _ in cp.source_package_problems(str(self.source))])
        self.refused_upgrade()

    def test_clean_template_stale_bytes_or_raw_pin_are_refused_before_copy(self):
        for rel, content in (('README.md', b'stale manifest\n'), ('tools/publish_new.py', (self.source / 'tools/publish_new.py').read_bytes().replace(b'\r\n', b'\n'))):
            path = self.source / rel
            old = path.read_bytes()
            path.write_bytes(content)
            with mock.patch.object(cp, 'ROOT', str(self.source)):
                self.assertTrue(cp.delivery_problems())
            before = tree(self.source)
            for apply in ((), ('--apply',)):
                r = run(self.source, 'new_project.py', '--name', 'Never', '--dest', self.base, '--result-json', *apply)
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assertFalse((self.base / 'Never').exists())
            self.assertEqual(tree(self.source), before)
            path.write_bytes(old)

    def test_adopt_never_runs_foreign_bootstrap_code(self):
        for name in ('init_project.py', 'check_package.py', 'transaction.py', 'result_schema.py'):
            target = self.base / ('adopt-' + name)
            (target / 'tools').mkdir(parents=True)
            sentinel = target / 'EXECUTED'
            (target / 'tools' / name).write_text('from pathlib import Path\nPath(%r).write_text("executed")\n' % str(sentinel))
            before = tree(target)
            for apply in ((), ('--apply',)):
                r = run(self.source, 'adopt_project.py', '--project', target, '--name', 'Mine', '--result-json', *apply)
                self.assertEqual((r.returncode, envelope(r)['status']), (1, 'blocked'), r.stdout + r.stderr)
                self.assertEqual(tree(target), before)
                self.assertFalse(sentinel.exists())

    def test_git_clean_filters_preserve_the_four_raw_owner_files(self):
        if shutil.which('git') is None:
            self.skipTest('git unavailable')
        repo = self.base / 'raw-owner-git'
        repo.mkdir()
        # The contract belongs to the versioned attributes, not an ancestor repo
        # or a developer's global Git attributes/configuration.
        env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM='1')

        def git(*args, raw=None):
            return subprocess.run(['git', '-c', 'core.attributesFile=' + os.devnull, *args],
                                  input=raw, cwd=str(repo), env=env, capture_output=True)

        initialized = git('init', '--quiet')
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        top = git('rev-parse', '--show-toplevel')
        self.assertEqual(top.returncode, 0, top.stderr)
        self.assertEqual(Path(os.fsdecode(top.stdout).strip()).resolve(), repo.resolve())
        (repo / '.gitattributes').write_bytes((ROOT / '.gitattributes').read_bytes())
        probe = b'raw-owner-probe\r\nsecond-line\r\n'
        for rel in ('tools/publish_new.py', 'tools/context_update.py', '.cvf/checks/v3/observer.py', '.cvf/checks/v3/workflow.py'):
            raw = (ROOT / rel).read_bytes()
            filtered = git('hash-object', '--stdin', '--path=' + rel, raw=raw)
            exact = git('hash-object', '--stdin', '--no-filters', raw=raw)
            self.assertEqual((filtered.returncode, exact.returncode), (0, 0), rel)
            self.assertEqual(filtered.stdout, exact.stdout, rel)
            filtered_probe = git('hash-object', '--stdin', '--path=' + rel, raw=probe)
            exact_probe = git('hash-object', '--stdin', '--no-filters', raw=probe)
            self.assertEqual((filtered_probe.returncode, exact_probe.returncode), (0, 0), rel)
            self.assertEqual(filtered_probe.stdout, exact_probe.stdout, rel)
        filtered = git('hash-object', '--stdin', '--path=unprotected-probe.py', raw=probe)
        exact = git('hash-object', '--stdin', '--no-filters', raw=probe)
        normalized = git('hash-object', '--stdin', '--no-filters', raw=probe.replace(b'\r\n', b'\n'))
        self.assertEqual((filtered.returncode, exact.returncode, normalized.returncode), (0, 0, 0))
        self.assertNotEqual(filtered.stdout, exact.stdout)
        self.assertEqual(filtered.stdout, normalized.stdout)


if __name__ == '__main__':
    unittest.main()
