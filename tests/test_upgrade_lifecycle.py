"""D-01d checks: same-schema upgrade and forced downgrade of a projected-v3 project that holds real data (D01D_INTEGRATION_ONLY).

Everything runs on fake data in temporary folders. The packages are the real shipped bytes after projection (check_package.materialize, no branding;
NOT an official release or ZIP and not evidence of a full gate), copied into A and B whose only difference is a fake VERSION and one VI/EN pair of
ordinary guides. Projects are made by the real new_project.py of A; the library workbook, the content entry, the artifact registry, the execution
profile and the D-01b / D-01c merge archives are written by their real owners before the first upgrade. The upgrade and downgrade run through the
real upgrade_package.py CLI of the clean source package. This is a SAME-SCHEMA version change only: no migration, no T39 as a whole, no host, no
release. Native files here are opaque markers kept as bytes; they prove nothing about registration, usability or R4.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import artifacts  # noqa: E402
import check_package as cp  # noqa: E402
import execution_profile as ep  # noqa: E402
import library  # noqa: E402
import library_sync  # noqa: E402
import merge_center  # noqa: E402
import native_agents  # noqa: E402
import result_schema  # noqa: E402
import transaction  # noqa: E402
import upgrade_package  # noqa: E402

try:
    import openpyxl
except ImportError:
    openpyxl = None
HAVE_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
NEED = unittest.skipUnless(os.name == 'nt' and openpyxl is not None and HAVE_JSONSCHEMA,
                           'NOT_CHECKED: needs Windows (the D-01c finish), openpyxl (the workbook) and jsonschema (the profile and pin checks)')
TEMPLATE = ROOT / 'skills/local/shared/source-library/assets/source-index-template.xlsx'
PROFILE = ep.PROFILE_REL
VERSION_A, VERSION_B, VERSION_C = '90.0.0', '90.0.1', '90.0.2'
# (main guide the user edits, the other guide B changes, guide for the seeded D-01b archive, guide for the seeded D-01c archive)
GUIDES = {'vi': ('docs/HUONG_DAN_SKILLS_VI.md', 'docs/en/SKILLS_GUIDE.md', 'docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md', 'docs/HUONG_DAN_SU_DUNG_VI.md'),
          'en': ('docs/en/SKILLS_GUIDE.md', 'docs/HUONG_DAN_SKILLS_VI.md', 'docs/en/NEW_PROJECT_GUIDE.md', 'docs/en/DAILY_USE_GUIDE.md')}
CHANGED_BY_B = ('docs/HUONG_DAN_SKILLS_VI.md', 'docs/en/SKILLS_GUIDE.md')
REPORT = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tree(root):
    """Every file and folder with bytes, runtime data included: proof that a preview or a refusal changed nothing."""
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(Path(root).rglob('*'))
            if '__pycache__' not in p.parts}


def changed(before, after):
    """Paths whose bytes differ, appear or vanish between two trees (folders ignored)."""
    keys = {k for k in set(before) | set(after) if before.get(k) is not None or after.get(k) is not None}
    return {k for k in keys if before.get(k) != after.get(k)}


def run(base, script, *args):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, str(Path(base) / 'tools' / script), *map(str, args)], cwd=str(base), env=e,
                          capture_output=True, encoding='utf-8', timeout=300)


def envelope(result):
    return result_schema.split_output(result.stdout)[1]


def write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def archive_files(project):
    base = Path(project) / '.agent' / 'merge-backups'
    return {p.relative_to(project).as_posix(): sha(p.read_bytes()) for p in sorted(base.rglob('*')) if p.is_file()} if base.is_dir() else {}


def projection(project):
    """What the real readers say about the workbook: sources, content entries, artifact revisions and their dependencies. Read-only."""
    root = str(project)
    book = artifacts.load_book(root)
    catalog = {sid: [{k: r.get(k) for k in ('id', 'file', 'law_revision', 'law_sha', 'law_state', 'status')} for r in rows]
               for sid, rows in sorted(book['catalog'].items())}
    content = library.content_find(root)
    items = artifacts.find(root)
    return json.loads(json.dumps({'catalog': catalog, 'content_sheet': content['content_sheet'], 'entries': content['entries'],
                                  'registry': items['registry'], 'artifacts': items['items'], 'edges': book['registry']['edges']},
                                 ensure_ascii=False, sort_keys=True, default=str))


@NEED
class UpgradeLifecycle(unittest.TestCase):
    """One fixture per class: packages A and B, and one seeded project per language. Every test works on its own copy."""

    @classmethod
    def setUpClass(cls):
        warning_guard = warnings.catch_warnings()
        warning_guard.__enter__()
        cls.addClassCleanup(warning_guard.__exit__, None, None, None)
        cls.addClassCleanup(setattr, ep, 'LANG', ep.LANG)
        warnings.simplefilter('ignore')
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-d01d-')
        cls.base = Path(cls.tmp.name)
        cls.A, cls.B = cls.base / 'A', cls.base / 'B'
        cp.materialize(str(cls.A), branding=False)
        shutil.copytree(str(cls.A), str(cls.B))
        write_bytes(cls.A / 'VERSION', (VERSION_A + '\n').encode('utf-8'))
        write_bytes(cls.B / 'VERSION', (VERSION_B + '\n').encode('utf-8'))
        for rel in CHANGED_BY_B:
            raw = (cls.B / rel).read_bytes()
            assert b'\r\n' not in raw, rel
            (cls.B / rel).write_bytes(raw + '\nDòng thêm của bản B / line added in B\n'.encode('utf-8'))
        for pkg in (cls.A, cls.B):
            done = run(pkg, 'check_package.py', '--write-manifest')
            assert done.returncode == 0, done.stdout + done.stderr
        cls.seeded = {lang: cls.make_project(lang) for lang in ('vi', 'en')}

    @classmethod
    def tearDownClass(cls):
        if REPORT:
            sys.stderr.write('\nD01D-REPORT ' + json.dumps(REPORT, ensure_ascii=False, sort_keys=True) + '\n')
        cls.tmp.cleanup()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-d01d-w-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)

    # ---------------------------------------------------------------- fixture
    @classmethod
    def make_project(cls, lang):
        """A real project of A, then data written by the real owners. Returns the paths and everything later tests compare against."""
        r = run(cls.A, 'new_project.py', '--name', 'P-' + lang, '--dest', cls.base, '--lang', lang, '--apply', '--result-json')
        assert r.returncode == 0, r.stdout + r.stderr
        proj = cls.base / ('P-' + lang)
        root = str(proj)
        main, other, guide2, guide3 = GUIDES[lang]
        # the profile, through the owner: a valid file with explicit choices
        choices = {'host': 'claude-code', 'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}}}
        ep.LANG = lang
        plan = ep.plan_config(root, choices)
        assert plan['status'] == 'PREVIEW', plan
        done = ep.apply_config(root, choices, plan['plan']['plan_sha256'])
        assert done['status'] == 'WRITTEN', done
        # the library workbook from the template of package A, sources, one revision bump, one content entry, two artifact revisions
        folder = proj / 'references' / 'source-documents' / 'team'
        shutil.copyfile(str(cls.A / 'skills/local/shared/source-library/assets/source-index-template.xlsx'), str(proj / 'references' / '_INDEX.xlsx'))
        write_bytes(folder / 'a.txt', b'alpha v1')
        write_bytes(folder / 'b.txt', b'beta v1')
        library_sync.apply(root)
        write_bytes(folder / 'a.txt', b'alpha v2 after a change')
        library_sync.apply(root)
        book = artifacts.load_book(root)

        def source_dep(sid):
            rec = book['catalog'][sid][0]
            return {'kind': 'SOURCE', 'id': sid, 'revision': library.revision_of(rec['law_revision']), 'sha256': rec['law_sha']}
        rec_b = book['catalog']['SRC-000002'][0]
        entry = {'entry_id': 'E-001', 'source_id': 'SRC-000002', 'source_revision': rec_b['law_revision'], 'source_sha256': rec_b['law_sha'],
                 'locator': 'đoạn 1', 'read_scope': 'đoạn 1 đã đọc', 'kind': 'EXTRACT', 'text': 'nội dung giả của fixture',
                 'limits': 'chỉ đọc đoạn 1; dữ liệu giả phục vụ kiểm', 'recorded_by': 'tester'}
        library_sync.content_apply(root, entry, library_sync.content_plan(root, entry)['plan_token'])

        def register(aid, deps, kind):
            path = 'working/w/%s-v1.txt' % aid.lower()
            write_bytes(proj / path, ('nội dung ' + aid).encode('utf-8'))
            req = {'artifact_id': aid, 'revision': 1, 'path': path, 'title': 'Kết quả ' + aid, 'kind': kind, 'limits': 'chỉ đọc đoạn đã khai',
                   'origin': 'USER_FILE', 'recorded_by': 'tester', 'dependencies': deps}
            res = artifacts.register_apply(root, req, artifacts.register_plan(root, req)['plan_token'])
            assert res['action'] == 'record', res
            return artifacts.load_book(root)['registry']['by_key'][(aid, 1)]['sha256']
        appendix_sha = register('ART-000001', [source_dep('SRC-000001')], 'APPENDIX')
        register('ART-000002', [{'kind': 'ARTIFACT', 'id': 'ART-000001', 'revision': 1, 'sha256': appendix_sha}], 'REPORT')
        # files the user owns: context, skills, sources, drafts, output, archive and runtime/native markers (opaque bytes)
        for rel in ('.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md'):
            raw = (proj / rel).read_bytes()
            (proj / rel).write_bytes(raw + '\nDòng của người dùng trong fixture D-01d\n'.encode('utf-8'))
        write_bytes(proj / 'skills/local/project/rieng/SKILL.md', '---\nname: rieng\ndescription: Kỹ năng riêng của dự án để thử\n---\n'.encode('utf-8'))
        write_bytes(proj / 'skills/local/shared/dung-chung-rieng/SKILL.md', '---\nname: dung-chung-rieng\ndescription: Kỹ năng dùng chung do người dùng thêm\n---\n'.encode('utf-8'))
        write_bytes(proj / 'references/policies/quy-che.md', 'quy chế giả\n'.encode('utf-8'))
        write_bytes(proj / 'output/ket-qua.md', 'kết quả giả\n'.encode('utf-8'))
        write_bytes(proj / 'working/nhap.md', 'nháp giả\n'.encode('utf-8'))
        write_bytes(proj / 'archive/cu.md', 'bản lưu giả\n'.encode('utf-8'))
        write_bytes(proj / '.agent/runtime/marker.txt', b'RUNTIME MARKER')
        write_bytes(proj / native_agents.NATIVE_REL, b'OPAQUE NATIVE MARKER: not a registered agent\n')
        write_bytes(proj / native_agents.RECEIPT_REL, b'OPAQUE RECEIPT MARKER: not a receipt\n')
        # guides: the user edits the main one; the others are seeded pairs that the upgrade did NOT create
        edited = (proj / main).read_bytes() + 'Dòng sửa của người dùng\n'.encode('utf-8')
        (proj / main).write_bytes(edited)
        seeds = {}
        for rel, text in ((guide2, 'SEEDED CANDIDATE FOR THE D-01b ARCHIVE\n'), (guide3, 'SEEDED CANDIDATE FOR THE D-01c ARCHIVE\n')):
            (proj / rel).write_bytes((proj / rel).read_bytes() + 'Dòng sửa của người dùng ở guide khác\n'.encode('utf-8'))
            write_bytes(proj / (rel + '.new'), text.encode('utf-8'))
        pv = merge_center.preview_replace(root, guide2 + '.new')
        rep = merge_center.apply_replace(root, guide2 + '.new', pv['current_sha256'], pv['candidate_sha256'])
        assert rep['outcome'] == 'replaced', rep
        fp = merge_center.preview_finish(root, guide3 + '.new')
        fin = merge_center.apply_finish(root, guide3 + '.new', fp['current_sha256'], fp['candidate_sha256'], fp['finish_id'])
        assert fin['outcome'] == 'finished', fin
        for rel in (guide2, guide3):  # what the seeded pairs look like now: replaced (pending kept) and finished (pending archived)
            pending = proj / (rel + '.new')
            seeds[rel] = ((proj / rel).read_bytes(), pending.read_bytes() if pending.exists() else None)
        return {'path': proj, 'lang': lang, 'edited': edited, 'seeds': seeds, 'finish3': (guide3, fp['current_sha256'], fp['candidate_sha256'], fp['finish_id'])}

    def clone(self, lang, name):
        dst = self.work / name
        shutil.copytree(str(self.seeded[lang]['path']), str(dst))
        return dst

    def upgrade(self, proj, source, *extra):
        return run(source, 'upgrade_package.py', '--project', proj, *extra, '--result-json')

    def workbook(self, proj):
        raw = (Path(proj) / 'references' / '_INDEX.xlsx').read_bytes()
        view = projection(proj)
        self.assertEqual((Path(proj) / 'references' / '_INDEX.xlsx').read_bytes(), raw, 'reading the workbook must not change its bytes')
        return sha(raw), view

    def changed_by_verify(self, proj):
        out = run(proj, 'check_package.py', '--verify').stdout
        return {m.group(1).strip() for m in re.finditer(r'ĐÃ SỬA\s*:\s*(.+)', out)}

    def observe(self, proj, guide, finish):
        _, cur, cand, fid = finish
        return merge_center.observe_finish(str(proj), guide + '.new', cur, cand, fid)

    # ---------------------------------------------------------------- the fixture itself
    def test_fixture_is_projected_v3_with_real_data_and_pins_that_hold(self):
        for pkg in (self.A, self.B):
            self.assertEqual(cp.source_package_problems(str(pkg)), [], pkg)
            self.assertEqual(cp.pin_problems(str(pkg)), [], pkg)
            self.assertEqual({r for r in tree(pkg) if r.startswith('.cvf/') and tree(pkg)[r] is not None}, set(cp.CVF_CLOSURE))
            self.assertFalse([r for r in tree(pkg) if r.startswith(('release_templates/', 'tests/', 'roadmap/', 'feedback/', '.agent/runtime'))])
            self.assertFalse([f for f in (pkg / 'assets').rglob('*') if f.is_file() and f.name != 'README.md'], 'no logo or private font in a fixture')
        a, b = tree(self.A), tree(self.B)
        self.assertEqual(changed(a, b), {'VERSION', 'MANIFEST.sha256', *CHANGED_BY_B})  # B differs from A in exactly these files
        for rel in (*cp.CVF_MACHINE, *cp.CVF_DEPENDENCIES):
            self.assertEqual(a[rel], b[rel], rel)
        self.assertEqual((self.A / 'VERSION').read_text().strip(), VERSION_A)
        self.assertEqual((self.B / 'VERSION').read_text().strip(), VERSION_B)
        for lang, seed in self.seeded.items():
            proj = seed['path']
            info = json.loads((proj / '.agent/PACKAGE_INFO.json').read_text(encoding='utf-8'))
            self.assertEqual((info['language'], info['version']), (lang, VERSION_A))
            files = {r for r, d in tree(proj).items() if r.startswith('.cvf/') and d is not None}
            self.assertEqual(files, set(cp.CVF_CLOSURE))
            for rel in (*cp.CVF_CLOSURE, *cp.BYTE_EXACT):
                self.assertEqual((proj / rel).read_bytes(), (self.A / rel).read_bytes(), rel)
            self.assertEqual(cp.pin_problems(str(proj)), [])
            self.assertEqual(ep.inspect(proj)['state'], 'OK')  # a valid profile with explicit choices
            self.assertEqual(json.loads((proj / PROFILE).read_bytes())['host'], 'claude-code')
            self.assertEqual(self.changed_by_verify(proj) - set(GUIDES[lang][2:]), {GUIDES[lang][0]})  # only the user's own guide edits differ from the MANIFEST

    def test_the_workbook_holds_real_data_read_back_by_the_owner_readers(self):
        for lang, seed in self.seeded.items():
            with self.subTest(lang=lang):
                _, view = self.workbook(seed['path'])
                self.assertEqual(sorted(view['catalog']), ['SRC-000001', 'SRC-000002'])
                source_a = view['catalog']['SRC-000001'][0]
                source_b = view['catalog']['SRC-000002'][0]
                self.assertEqual((source_a['law_revision'], source_a['law_sha']), (2, sha(b'alpha v2 after a change')))
                self.assertEqual((source_b['law_revision'], source_b['law_sha']), (1, sha(b'beta v1')))
                self.assertEqual([e['entry_id'] for e in view['entries']], ['E-001'])
                entry = view['entries'][0]
                self.assertEqual((entry['source_id'], entry['source_revision'], entry['source_sha256']),
                                 ('SRC-000002', 1, sha(b'beta v1')))
                self.assertEqual((entry['read_scope'], entry['limits']), ('đoạn 1 đã đọc', 'chỉ đọc đoạn 1; dữ liệu giả phục vụ kiểm'))
                self.assertEqual(sorted((i['artifact_id'], i['revision']) for i in view['artifacts']), [('ART-000001', 1), ('ART-000002', 1)])
                self.assertEqual({i['artifact_id']: i['kind'] for i in view['artifacts']},
                                 {'ART-000001': 'APPENDIX', 'ART-000002': 'REPORT'})
                edge_keys = ('from_kind', 'from_id', 'from_revision', 'to_kind', 'to_id', 'to_revision', 'to_sha256')
                self.assertEqual({tuple(e[k] for k in edge_keys) for e in view['edges']}, {
                    ('ARTIFACT', 'ART-000001', 1, 'SOURCE', 'SRC-000001', 2, sha(b'alpha v2 after a change')),
                    ('ARTIFACT', 'ART-000002', 1, 'ARTIFACT', 'ART-000001', 1, sha('nội dung ART-000001'.encode('utf-8')))})
                snap = archive_files(seed['path'])
                self.assertEqual(sorted(n.rsplit('/', 1)[1] for n in snap), ['current.txt', 'current.txt', 'incoming.txt', 'incoming.txt',
                                                                            'pending-retired.txt', 'record.json', 'record.json'])
                guide3, cur, cand, fid = seed['finish3']
                self.assertEqual(self.observe(seed['path'], guide3, seed['finish3'])['state'], 'finished')

    # ---------------------------------------------------------------- A -> B, then B -> A, in both languages
    def roundtrip(self, lang, plan):
        seed = self.seeded[lang]
        proj = self.clone(lang, 'rt-' + lang)
        main, other, guide2, guide3 = GUIDES[lang]
        raw_a = {rel: (self.A / rel).read_bytes() for rel in CHANGED_BY_B}
        raw_b = {rel: (self.B / rel).read_bytes() for rel in CHANGED_BY_B}
        wb0, view0 = self.workbook(proj)
        archive0 = archive_files(proj)
        native0 = native_agents.inspect(str(proj))['state']
        keep_rel = ('PROJECT.md', PROFILE, '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md', '.agent/SKILL_INDEX.md', 'skills/local/project/rieng/SKILL.md',
                    'skills/local/shared/dung-chung-rieng/SKILL.md', 'references/policies/quy-che.md', 'output/ket-qua.md', 'working/nhap.md', 'archive/cu.md',
                    '.agent/runtime/marker.txt', native_agents.NATIVE_REL, native_agents.RECEIPT_REL, 'references/_INDEX.xlsx', 'working/w/art-000001-v1.txt',
                    'working/w/art-000002-v1.txt', 'references/source-documents/team/a.txt', 'references/source-documents/team/b.txt')
        user0 = {rel: (proj / rel).read_bytes() for rel in keep_rel}

        def assert_data_kept(label):
            self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep_rel}, user0, label)
            self.assertEqual(self.workbook(proj), (wb0, view0), label)  # raw bytes AND what the readers see
            self.assertEqual({k: v for k, v in archive_files(proj).items() if k in archive0}, archive0, label)
            for rel in (*cp.CVF_CLOSURE, *cp.BYTE_EXACT):
                self.assertEqual((proj / rel).read_bytes(), (self.A / rel).read_bytes(), label + ' ' + rel)
            self.assertEqual(cp.pin_problems(str(proj)), [], label)
            for rel, (cur, cand) in seed['seeds'].items():  # seeded pairs: current and pending untouched (the finished one has no pending)
                self.assertEqual((proj / rel).read_bytes(), cur, label)
                self.assertEqual((proj / (rel + '.new')).read_bytes() if (proj / (rel + '.new')).exists() else None, cand, label)
        # ---- A -> B: the preview writes nothing, the apply goes through the real compatibility guard
        before = tree(proj)
        pv = self.upgrade(proj, self.B)
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertEqual(tree(proj), before)  # the whole tree, runtime included
        ap = self.upgrade(proj, self.B, '--apply')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        after = tree(proj)
        delta = changed(before, after)
        journals = {k for k in delta if k.startswith('.agent/runtime/transactions/')}
        self.assertEqual(len(journals), 1, delta)
        self.assertEqual(delta - journals, {'VERSION', 'MANIFEST.sha256', '.agent/PACKAGE_INFO.json', other, main + '.new'})  # the plan, nothing else
        self.assertEqual((proj / 'VERSION').read_text().strip(), VERSION_B)
        self.assertEqual(json.loads((proj / '.agent/PACKAGE_INFO.json').read_text(encoding='utf-8'))['version'], VERSION_B)
        self.assertEqual((proj / 'MANIFEST.sha256').read_bytes(), (self.B / 'MANIFEST.sha256').read_bytes())
        self.assertEqual((proj / main).read_bytes(), seed['edited'])  # the user's edit is not overwritten
        self.assertEqual((proj / (main + '.new')).read_bytes(), raw_b[main])  # the package change arrives as a .new, byte for byte
        self.assertEqual((proj / other).read_bytes(), raw_b[other])  # untouched by the user, so the package version is taken
        assert_data_kept('after A -> B')
        verify_after_b = self.changed_by_verify(proj)
        self.assertEqual(verify_after_b, {main, guide2, guide3})  # diagnostic only: the user's own pending/edited files
        native1 = native_agents.inspect(str(proj))['state']
        # ---- the guide in conflict: D-01b replace + D-01c finish (VI) or D-01c finish keeping my file (EN)
        if plan == 'replace':
            pv1 = merge_center.preview_replace(str(proj), main + '.new')
            rep = merge_center.apply_replace(str(proj), main + '.new', pv1['current_sha256'], pv1['candidate_sha256'])
            self.assertEqual(rep['outcome'], 'replaced', rep)
            self.assertEqual((proj / main).read_bytes(), raw_b[main])
            self.assertEqual((proj / rep['archive']['current']).read_bytes(), seed['edited'])
            self.assertEqual((proj / rep['archive']['incoming']).read_bytes(), raw_b[main])
        fp = merge_center.preview_finish(str(proj), main + '.new')  # a NEW preview of the pair as it is now
        self.assertTrue(fp['eligible'], fp)
        self.assertEqual(fp['identical'], plan == 'replace')
        fin = merge_center.apply_finish(str(proj), main + '.new', fp['current_sha256'], fp['candidate_sha256'], fp['finish_id'])
        self.assertEqual(fin['outcome'], 'finished', fin)
        self.assertFalse((proj / (main + '.new')).exists())
        self.assertEqual((proj / fin['archive']['retired']).read_bytes(), raw_b[main])  # the pending moved out with its bytes
        self.assertEqual((proj / fin['archive']['current']).read_bytes(), (raw_b[main] if plan == 'replace' else seed['edited']))
        chosen = (main, fp['current_sha256'], fp['candidate_sha256'], fp['finish_id'])
        self.assertEqual((proj / main).read_bytes(), raw_b[main] if plan == 'replace' else seed['edited'])
        self.assertEqual(self.observe(proj, main, chosen)['state'], 'finished')
        self.assertEqual(self.changed_by_verify(proj), {guide2, guide3} | (set() if plan == 'replace' else {main}))
        assert_data_kept('after replace/finish')
        archive1 = archive_files(proj)
        # ---- B -> A, same schema: refused without --force (preview and apply), the whole tree kept
        mid = tree(proj)
        for extra in ((), ('--apply',)):
            refused = self.upgrade(proj, self.A, *extra)
            self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
            self.assertTrue('thấp hơn' in refused.stdout + refused.stderr or 'older than' in refused.stdout + refused.stderr)
            self.assertEqual(tree(proj), mid)
        pv2 = self.upgrade(proj, self.A, '--force')
        self.assertEqual((pv2.returncode, envelope(pv2)['status']), (0, 'preview'), pv2.stdout + pv2.stderr)
        self.assertEqual(tree(proj), mid)  # the forced preview writes nothing
        down = self.upgrade(proj, self.A, '--apply', '--force')
        self.assertEqual(down.returncode, 0, down.stdout + down.stderr)
        end = tree(proj)
        delta = changed(mid, end)
        journals = {k for k in delta if k.startswith('.agent/runtime/transactions/')}
        self.assertEqual(len(journals), 1, delta)
        expected = {'VERSION', 'MANIFEST.sha256', '.agent/PACKAGE_INFO.json', other}
        if plan == 'replace':
            expected.add(main)  # my file now equals the B baseline, so it takes the A version
            self.assertEqual((proj / main).read_bytes(), raw_a[main])
            self.assertFalse((proj / (main + '.new')).exists())
        else:
            expected.add(main + '.new')  # my file differs from the B baseline: the A version waits as a .new, my file is kept
            self.assertEqual((proj / main).read_bytes(), seed['edited'])
            self.assertEqual((proj / (main + '.new')).read_bytes(), raw_a[main])
        self.assertEqual(delta - journals, expected)
        self.assertEqual((proj / other).read_bytes(), raw_a[other])
        self.assertEqual((proj / 'VERSION').read_text().strip(), VERSION_A)
        self.assertEqual(json.loads((proj / '.agent/PACKAGE_INFO.json').read_text(encoding='utf-8'))['version'], VERSION_A)
        self.assertEqual((proj / 'MANIFEST.sha256').read_bytes(), (self.A / 'MANIFEST.sha256').read_bytes())
        assert_data_kept('after B -> A')
        self.assertEqual({k: v for k, v in archive_files(proj).items() if k in archive1}, archive1)  # every archive, including the new ones
        # old observations stay conservative: bound to the current bytes, never a permanent "done"
        self.assertEqual(self.observe(proj, seed['finish3'][0], seed['finish3'])['state'], 'finished')
        late = self.observe(proj, main, chosen)
        self.assertNotEqual(late['state'], 'finished')
        self.assertEqual(late['reason'], 'current_changed' if plan == 'replace' else 'both_present')
        native2 = native_agents.inspect(str(proj))['state']
        REPORT['roundtrip-' + lang] = {'plan': plan, 'native_status_before_after_B_after_A': [native0, native1, native2],
                                       'workbook_sha256': wb0, 'archive_files_kept': len(archive1), 'late_observation': [late['state'], late['reason']],
                                       'projection_sha256': sha(json.dumps(view0, sort_keys=True).encode('utf-8')),
                                       'projection_counts': {'sources': len(view0['catalog']), 'entries': len(view0['entries']), 'artifacts': len(view0['artifacts']),
                                                             'edges': len(view0['edges'])},
                                       'source_revisions': {k: v[0]['law_revision'] for k, v in view0['catalog'].items()},
                                       'verify_changed_after_B': sorted(verify_after_b)}

    def test_vi_project_a_to_b_replace_finish_then_forced_downgrade_takes_the_update_branch(self):
        self.roundtrip('vi', 'replace')

    def test_en_project_a_to_b_keep_finish_then_forced_downgrade_makes_a_new_pending(self):
        self.roundtrip('en', 'keep')

    # ---------------------------------------------------------------- two negative clones
    def test_a_future_user_profile_is_kept_opaque_and_refused_by_the_profile_owner(self):
        proj = self.clone('vi', 'future')
        doc = json.loads((proj / PROFILE).read_bytes())
        doc['schema_version'] = 'law.execution-profile/2'
        future = ep.serialize(doc)
        (proj / PROFILE).write_bytes(future)
        wb0, view0 = self.workbook(proj)
        ap = self.upgrade(proj, self.B, '--apply')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)  # an upgrade of the same v3 is not refused because one user file has another schema
        self.assertEqual((proj / PROFILE).read_bytes(), future)
        self.assertEqual(list(proj.rglob('EXECUTION_PROFILE*.new')), [])
        self.assertEqual(sorted(p.name for p in (proj / '.agent').glob('EXECUTION_PROFILE*')), ['EXECUTION_PROFILE.json', 'EXECUTION_PROFILE.schema.json'])
        self.assertEqual(self.workbook(proj), (wb0, view0))
        choices = write_bytes(self.work / 'choices.json', json.dumps({'host': 'claude-code'}).encode('utf-8'))
        before = tree(proj)
        status = run(proj, 'execution_profile.py', 'status', '--result-json')
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertEqual(envelope(status)['outcome']['state'], 'UNSUPPORTED')
        self.assertFalse(envelope(status)['outcome']['authority_usable'])
        for cmd in ('preview-config', 'apply-config'):
            res = run(proj, 'execution_profile.py', cmd, '--choices', choices, '--result-json')
            self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
            outcome = envelope(res)['outcome']
            self.assertEqual(outcome['status'], 'REFUSED')
            self.assertIn('CONFIG_BLOCKED_STATE', outcome['reasons'])
            self.assertIn('PROFILE_UNSUPPORTED_VERSION', outcome['reasons'])
        outcome = ep.apply_config(str(proj), {'host': 'claude-code'})
        self.assertEqual(outcome['status'], 'REFUSED')
        self.assertIn('CONFIG_BLOCKED_STATE', outcome['reasons'])
        self.assertIn('PROFILE_UNSUPPORTED_VERSION', outcome['reasons'])
        self.assertEqual(tree(proj), before)  # status and refusals write nothing
        self.assertNotEqual(ep.inspect(proj)['state'], 'OK')  # kept bytes are not proof that the schema is read or migrated
        REPORT['future-profile'] = {'profile_state': ep.inspect(proj)['state'], 'upgrade_rc': ap.returncode}

    def test_an_unsupported_cvf_refuses_even_with_force_and_the_pending_agents_file_stays_outside_replace(self):
        proj = self.clone('en', 'bad-cvf')
        loader = proj / '.cvf/checks/v3/loader.py'
        loader.write_bytes(loader.read_bytes() + b'\n ')
        write_bytes(proj / 'AGENTS.md.new', 'AGENTS pending text made by hand\n'.encode('utf-8'))
        before = tree(proj)
        for extra in ((), ('--apply',), ('--apply', '--force')):
            r = self.upgrade(proj, self.B, *extra)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertEqual(envelope(r)['status'], 'blocked')
            self.assertEqual(tree(proj), before)  # the whole tree, runtime and workbook included
        root = str(proj)
        # D-01e: AGENTS.md vẫn không được replace; finish mở riêng cho nó nên ca finish-ngoài-scope dùng một file role / replace still refuses AGENTS.md; finish covers it since D-01e, so the finish out-of-scope case uses a role file
        self.assertEqual((merge_center.preview_replace(root, 'AGENTS.md.new')['eligible'], merge_center.preview_replace(root, 'AGENTS.md.new')['reason']), (False, 'unsupported'))
        self.assertEqual(merge_center.apply_replace(root, 'AGENTS.md.new', 'a' * 64, 'b' * 64)['outcome'], 'blocked')
        self.assertEqual((merge_center.preview_finish(root, 'roles/scout/agent.md.new')['eligible'], merge_center.preview_finish(root, 'roles/scout/agent.md.new')['reason']), (False, 'unsupported'))
        self.assertEqual(merge_center.apply_finish(root, 'roles/scout/agent.md.new', 'a' * 64, 'b' * 64, 'finish-' + 'a' * 32)['reason'], 'unsupported')
        self.assertEqual(tree(proj), before)  # current and pending are as they were; nothing in the allowlist moved
        self.assertTrue(cp.cvf_target_problems(str(proj), lambda rel: (self.B / rel).read_bytes()))


@unittest.skipUnless(HAVE_JSONSCHEMA, 'NOT_CHECKED: needs jsonschema (the profile and pin checks)')
class OlderCoreDependency(unittest.TestCase):
    """M3/E03: a project whose core dependency still holds the untouched bytes of an older package is upgraded (this very transaction replaces them);
    a user-edited one still stops everything. Found when a real 1.8.0 project could not be upgraded at all. Fake data, temporary folders, same schema."""
    DEP = 'tools/transaction.py'
    OUTSIDE = 'tools/check_output.py'  # a package file that no replace or finish route covers

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-m3-dep-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name)
        cls.A, cls.B, cls.C = cls.base / 'A', cls.base / 'B', cls.base / 'C'
        cp.materialize(str(cls.A), branding=False)
        shutil.copytree(str(cls.A), str(cls.B))
        write_bytes(cls.A / 'VERSION', (VERSION_A + '\n').encode('utf-8'))
        write_bytes(cls.B / 'VERSION', (VERSION_B + '\n').encode('utf-8'))
        write_bytes(cls.B / cls.DEP, (cls.B / cls.DEP).read_bytes() + b'\n# newer core dependency, test only\n')
        # a package file outside every merge allowlist (M3-C1/F5): B changes it once, C (later) changes it again
        write_bytes(cls.B / cls.OUTSIDE, (cls.B / cls.OUTSIDE).read_bytes() + b'\n# newer, test only (B)\n')
        shutil.copytree(str(cls.B), str(cls.C))
        write_bytes(cls.C / 'VERSION', (VERSION_C + '\n').encode('utf-8'))
        write_bytes(cls.C / cls.OUTSIDE, (cls.C / cls.OUTSIDE).read_bytes() + b'\n# newer still, test only (C)\n')
        for pkg in (cls.A, cls.B, cls.C):
            done = run(pkg, 'check_package.py', '--write-manifest')
            assert done.returncode == 0, done.stdout + done.stderr
        made = run(cls.A, 'new_project.py', '--name', 'P-dep', '--dest', cls.base, '--lang', 'vi', '--apply', '--result-json')
        assert made.returncode == 0, made.stdout + made.stderr
        cls.seed = cls.base / 'P-dep'

    def setUp(self):
        self.proj = Path(tempfile.mkdtemp(prefix='law-m3-dep-w-')) / 'P'
        self.addCleanup(shutil.rmtree, str(self.proj.parent), True)
        shutil.copytree(str(self.seed), str(self.proj))

    def upgrade(self, *extra):
        return run(self.B, 'upgrade_package.py', '--project', self.proj, *extra, '--result-json')

    def test_untouched_older_core_dependency_is_replaced_not_blocked(self):
        old = (self.proj / self.DEP).read_bytes()
        self.assertEqual(old, (self.A / self.DEP).read_bytes())
        self.assertNotEqual(old, (self.B / self.DEP).read_bytes())
        before = tree(self.proj)
        pv = self.upgrade()
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertIn({'path': self.DEP, 'action': 'update'}, envelope(pv)['files'])
        self.assertEqual(tree(self.proj), before)
        ap = self.upgrade('--apply')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        self.assertEqual((self.proj / self.DEP).read_bytes(), (self.B / self.DEP).read_bytes())
        self.assertEqual((self.proj / 'VERSION').read_text().strip(), VERSION_B)
        self.assertEqual(cp.pin_problems(str(self.proj)), [])

    def test_a_user_edited_core_dependency_still_blocks_even_with_force(self):
        path = self.proj / self.DEP
        path.write_bytes(path.read_bytes() + b'\n# user edit\n')
        before = tree(self.proj)
        for extra in ((), ('--apply',), ('--apply', '--force')):
            r = self.upgrade(*extra)
            self.assertEqual((r.returncode, envelope(r)['status']), (1, 'blocked'), r.stdout + r.stderr)
            self.assertIn('CVF_OWNER_DEPENDENCY_CONFLICT', r.stdout)
            self.assertEqual(tree(self.proj), before)


    def upgrade_with_edit_between_plan_and_add(self, rel, save):
        """M3-C1/F1 controlled interleaving, NOT a kernel race: the real main() runs in this process and `save` fires exactly once, at the
        Transaction.add boundary of `rel` (after plan() classified it, before add() took its snapshot). Returns (exit code, stdout, hits, result)."""
        hits = []
        original = transaction.Transaction.add

        def add(txn, path, data, action='write', *a, **kw):
            if path == rel and not hits:
                hits.append(path)
                save()
            return original(txn, path, data, action, *a, **kw)

        out = io.StringIO()
        upgrade_package.LAST_RESULT = None
        argv = ['upgrade_package.py', '--from', str(self.B), '--project', str(self.proj), '--apply']
        with mock.patch.object(transaction.Transaction, 'add', add), mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(out):
            try:
                upgrade_package.main()
                code = 0
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return code, out.getvalue(), hits, upgrade_package.LAST_RESULT

    def test_a_core_dependency_saved_after_the_plan_and_before_add_keeps_the_user_save(self):
        path = self.proj / self.DEP
        saved = path.read_bytes() + b'\n# USER SAVED after the plan, before add\n'
        before = tree(self.proj)
        code, out, hits, result = self.upgrade_with_edit_between_plan_and_add(self.DEP, lambda: path.write_bytes(saved))
        self.assertEqual(hits, [self.DEP], 'the interleaving did not fire: this would prove nothing')
        self.assertNotEqual(code, 0, out)
        self.assertEqual(path.read_bytes(), saved)  # the user save survives, it is not the incoming bytes and not the old bytes
        self.assertNotEqual(path.read_bytes(), (self.B / self.DEP).read_bytes())
        self.assertEqual(result['status'], 'blocked')  # no success claim
        self.assertEqual((self.proj / 'VERSION').read_text().strip(), VERSION_A)
        self.assertEqual(transaction.incomplete(str(self.proj)), [])  # nothing was started, so there is nothing to resume
        after = tree(self.proj)
        after[self.DEP] = before[self.DEP]  # the only change is the user's own save
        self.assertEqual(changed(before, after), set())

    def test_a_package_file_created_by_the_user_after_the_plan_is_not_overwritten(self):
        rel = 'docs/HUONG_DAN_SKILLS_VI.md'
        path = self.proj / rel
        path.unlink()  # in the plan this file is an `add`
        mine = 'file của tôi, tạo sau khi xem trước\n'.encode('utf-8')
        code, out, hits, result = self.upgrade_with_edit_between_plan_and_add(rel, lambda: path.write_bytes(mine))
        self.assertEqual(hits, [rel])
        self.assertNotEqual(code, 0, out)
        self.assertEqual(path.read_bytes(), mine)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual((self.proj / 'VERSION').read_text().strip(), VERSION_A)

    # ---- M3-C1/F5: a package file outside every allowlist, kept by a measured manual route
    def set_aside_by_hand(self, rel, stamp):
        """The manual route of the upgrade guide ("Other toolkit files"), with the standard library instead of PowerShell: a NEW numbered folder
        under archive/, both copies in it, byte checks, the .new MOVED (never deleted), the current file untouched. Returns (folder, hashes)."""
        cur, new = self.proj / rel, self.proj / (rel + '.new')
        folder = self.proj / 'archive' / 'nang-cap' / ('%s-%s' % (stamp, Path(rel).stem))
        folder.mkdir(parents=True)  # exist_ok stays False: an existing folder is never reused or overwritten
        h_cur, h_new = sha(cur.read_bytes()), sha(new.read_bytes())
        shutil.copyfile(str(cur), str(folder / (Path(rel).name + '.hien-hanh')))
        shutil.copyfile(str(new), str(folder / (Path(rel).name + '.new')))
        self.assertEqual((sha((folder / (Path(rel).name + '.hien-hanh')).read_bytes()), sha((folder / (Path(rel).name + '.new')).read_bytes())), (h_cur, h_new))
        os.replace(str(new), str(folder / (Path(rel).name + '.new.da-chuyen')))  # a move: the bytes are the same ones, nothing is deleted
        self.assertEqual(sha((folder / (Path(rel).name + '.new.da-chuyen')).read_bytes()), h_new)
        self.assertEqual(sha(cur.read_bytes()), h_cur)  # keeping yours means yours is exactly as it was
        self.assertFalse(new.exists())
        return folder, (h_cur, h_new)

    def test_a_file_outside_the_allowlists_is_kept_by_a_manual_route_that_keeps_both_copies_and_a_pending_that_differs_names_it(self):
        rel = self.OUTSIDE
        mine = (self.proj / rel).read_bytes() + b'\n# my own change\n'
        (self.proj / rel).write_bytes(mine)
        ap = self.upgrade('--apply')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        env = envelope(ap)
        self.assertIn({'path': rel + '.new', 'action': 'merge'}, env['files'])
        self.assertEqual((self.proj / rel).read_bytes(), mine)  # yours is kept
        self.assertEqual((self.proj / (rel + '.new')).read_bytes(), (self.B / rel).read_bytes())  # the incoming copy, as pending
        self.assertTrue(env['next_actions'])
        for line in env['next_actions']:
            self.assertNotRegex(line, r'(?i)(rồi xóa|then delete|resolve or remove)')  # never "delete the .new" as the way out
        self.assertIn('không xóa .new', ' '.join(env['next_actions']))
        # the product has no replace/finish for it, and this route does not pretend to be one
        root = str(self.proj)
        for preview in (merge_center.preview_replace(root, rel + '.new'), merge_center.preview_finish(root, rel + '.new')):
            self.assertEqual((preview['eligible'], preview['reason']), (False, 'unsupported'))
        # a later package changes the file again while a .new that differs is still pending: stopped before any write, with the way out named
        before = tree(self.proj)
        blocked = run(self.C, 'upgrade_package.py', '--project', self.proj, '--apply', '--result-json')
        self.assertEqual((blocked.returncode, envelope(blocked)['status']), (1, 'blocked'), blocked.stdout + blocked.stderr)
        self.assertEqual(tree(self.proj), before)
        said = ' '.join(envelope(blocked)['next_actions'])
        self.assertIn('archive/', said)
        self.assertIn('Không xóa .new', said)
        self.assertNotRegex(said, r'(?i)(rồi xóa|then delete|resolve or remove)')
        # the route: both copies, byte checks, the .new moved, the current file as it was
        folder, (h_cur, h_new) = self.set_aside_by_hand(rel, '20261021-120000')
        self.assertEqual(sha((self.proj / rel).read_bytes()), sha(mine))
        # same package again: the file is simply "kept", no new .new
        again = run(self.B, 'upgrade_package.py', '--project', self.proj, '--result-json')
        self.assertEqual((again.returncode, envelope(again)['status']), (0, 'preview'), again.stdout + again.stderr)
        self.assertNotIn({'path': rel + '.new', 'action': 'merge'}, envelope(again)['files'])
        self.assertFalse((self.proj / (rel + '.new')).exists())
        # a later package that changes the file once more gives a fresh pending next to the kept file, and nothing of the archive moves
        ap2 = run(self.C, 'upgrade_package.py', '--project', self.proj, '--apply', '--result-json')
        self.assertEqual(ap2.returncode, 0, ap2.stdout + ap2.stderr)
        self.assertEqual((self.proj / (rel + '.new')).read_bytes(), (self.C / rel).read_bytes())
        self.assertEqual((self.proj / rel).read_bytes(), mine)
        archived = sorted(p.name for p in folder.iterdir())
        self.assertEqual(archived, ['check_output.py.hien-hanh', 'check_output.py.new', 'check_output.py.new.da-chuyen'])
        # getting the archived .new back as a NEW file: while another .new sits there the guide's guard stops (never overwrite); after it is set
        # aside too (a second numbered folder), the first archived copy comes back as a new file with the bytes it had
        self.assertTrue((self.proj / (rel + '.new')).exists())
        folder2, (_, h_new2) = self.set_aside_by_hand(rel, '20261021-120100')
        self.assertNotEqual(folder2, folder)
        self.assertEqual(h_new2, sha((self.C / rel).read_bytes()))
        self.assertFalse((self.proj / (rel + '.new')).exists())
        shutil.copyfile(str(folder / 'check_output.py.new'), str(self.proj / (rel + '.new')))
        self.assertEqual(sha((self.proj / (rel + '.new')).read_bytes()), h_new)
        self.assertEqual(sha((self.proj / rel).read_bytes()), sha(mine))  # through all of it the current file stayed exactly yours

    def test_a_downgrade_is_refused_before_any_write_with_a_next_step_and_no_force_advice(self):
        self.assertEqual(self.upgrade('--apply').returncode, 0)
        before = tree(self.proj)
        down = run(self.A, 'upgrade_package.py', '--project', self.proj, '--apply', '--result-json')
        self.assertEqual((down.returncode, envelope(down)['status']), (1, 'blocked'), down.stdout + down.stderr)
        self.assertEqual(tree(self.proj), before)
        said = ' '.join(envelope(down)['next_actions']) + ' ' + down.stdout
        self.assertIn('bản sao lưu', said)
        self.assertNotRegex(said, r'(?i)(thêm --force|add --force)')  # --force is never the suggested way out

    def test_every_kind_of_block_names_a_concrete_step_and_never_force_or_a_manifest_edit_as_the_way_out(self):
        for code in ('SOURCE_MANIFEST_INCONSISTENT', 'SOURCE_CVF_NOT_V3_CLOSURE', 'SOURCE_CVF_MISSING_FOR_TARGET', 'CVF_PARTIAL', 'CVF_MACHINE_DIFFERS',
                     'CVF_OWNER_DEPENDENCY_DIFFERS', 'CVF_OWNER_DEPENDENCY_CONFLICT', 'CVF_USER_EDIT_CONFLICT', 'SOMETHING_NEW'):
            with self.subTest(code=code):
                steps = upgrade_package.block_steps([code])
                self.assertGreaterEqual(len(steps), 2)  # the specific step + the standing "not --force" line
                self.assertIn('--force', steps[-1])
                self.assertRegex(steps[-1], r'(?i)(không dùng --force|do not use --force)')
                for line in steps:
                    self.assertNotRegex(line, r'(?i)(thêm --force|add --force|sửa MANIFEST cho khớp(?!\.)|rồi xóa)')
        self.assertIn('hạ xuống schema cũ không được hỗ trợ', ' '.join(upgrade_package.block_steps(['SOURCE_CVF_MISSING_FOR_TARGET'])))


if __name__ == '__main__':
    unittest.main()
