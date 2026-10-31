"""V1-A office foundation: the method catalog, the six contracts, the read-only helper, the TASK/checkpoint guard and delivery.

What these tests prove: the catalog and contracts are well-formed and coherent with each other and with the native exporter table; the helper
composes ONE brief for the method Main named, binds raw bytes, keeps the four capability dimensions apart, refuses anything outside its scope and
writes nothing; the real checkpoint recipe of roles/README.md (the real v3 loader, binding and owners) blocks every marker/context mismatch while a
legacy task runs unchanged; and the package projection, a new project and an upgrade carry the files without touching the user's data.

What they do NOT prove: that Main chooses well, that a core role ever read a contract, that a host invoked anything, or the quality of any method.
`PREPARED` is a prepared hand-over only. Contracts are judged by a reviewer's reading; the machine checks here are structural.
Everything runs on fake data in temporary folders.
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
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import artifacts  # noqa: E402
import check_package as cp  # noqa: E402
import execution_profile as ep  # noqa: E402
import native_agents  # noqa: E402
import office  # noqa: E402
import publish_new as pn  # noqa: E402
import test_task_result_flow as tf  # noqa: E402  (FlowBase and the helpers only; its own test classes are not imported here)

HAVE_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
METHODS = ('research-assistant', 'executive-secretary', 'correspondence', 'market-analyst', 'data-analyst', 'evidence-reviewer')
BASE = {'research-assistant': 'scout', 'executive-secretary': 'worker', 'correspondence': 'worker', 'market-analyst': 'worker',
        'data-analyst': 'worker', 'evidence-reviewer': 'reviewer'}
SKILL_HTML = 'skills/local/shared/html-reports/SKILL.md'
SKILL_MINUTES = 'skills/local/shared/meeting-minutes/SKILL.md'
SOURCE = 'references/source-documents/team/ghi-chu-tuan.txt'


def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def tree(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(Path(root).rglob('*'))
            if '__pycache__' not in p.parts}


def office_root(base, with_source=True):
    """A project-shaped folder that holds only the office files, two skills and one source: all the helper reads."""
    root = Path(base)
    shutil.copytree(str(ROOT / 'roles' / 'office'), str(root / 'roles' / 'office'))
    for rel in (SKILL_HTML, SKILL_MINUTES):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(ROOT / rel), str(root / rel))
    if with_source:
        (root / SOURCE).parent.mkdir(parents=True, exist_ok=True)
        (root / SOURCE).write_bytes('ghi chú tuần 1: họp giao ban\n'.encode('utf-8'))
    return root


def request(method='executive-secretary', **over):
    req = {'method': method, 'reason': 'Cần tổng hợp ghi chú các cuộc họp trong tuần thành một báo cáo cho trưởng phòng.',
           'request': 'Báo cáo tuần 1 gửi trưởng phòng: tách quyết định, đề xuất, việc chờ.', 'sources': [{'path': SOURCE, 'note': 'ghi chú họp'}],
           'resources_used': [SKILL_MINUTES] if method == 'executive-secretary' else []}
    req.update(over)
    return req


def run_office(*args, stdin=None, cwd=ROOT):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, '-B', str(Path(cwd) / 'tools' / 'office.py')] + [str(a) for a in args], cwd=str(cwd), env=e,
                          input=stdin, capture_output=True, timeout=120)


def make_link(link, target):
    """A directory link (symlink, else a Windows junction); None when neither can be made here."""
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return True
    except (OSError, NotImplementedError, AttributeError):
        pass
    if os.name == 'nt':
        done = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)], capture_output=True)
        return done.returncode == 0
    return False


class Catalog(unittest.TestCase):
    """The shipped catalog and contracts, and what the validators refuse."""

    def test_shipped_catalog_and_every_contract_validate_with_coherent_content(self):
        info = office.load(ROOT)
        self.assertTrue(info['ok'], info['problems'])
        self.assertEqual(info['problems'], [])
        self.assertEqual(tuple(info['methods']), METHODS)
        seen = set()
        for mid, m in info['methods'].items():
            version = 2 if mid in ('data-analyst', 'market-analyst') else 1
            self.assertEqual((m['base_role'], m['method_version'], m['preset_mode']), (BASE[mid], version, 'INHERIT_CORE_PROFILE'))
            self.assertEqual(m['contract'], 'roles/office/%s.md' % mid)
            self.assertEqual(tuple(m['sections']) and list(office.sections(m['contract_bytes'].decode('utf-8'))[0]), list(office.SECTION_KEYS))
            for key in office.SECTION_KEYS:  # Vietnamese body and an English line in every section
                self.assertTrue(office.part(m['sections'][key], 'vi') and office.part(m['sections'][key], 'en'), (mid, key))
            for res in m['resources']:
                self.assertTrue((ROOT / res).is_file(), res)  # every optional resource exists in the package
            self.assertTrue(set(m['required_capabilities']) <= {'read_local', 'search_local', 'write_text', 'write_html', 'compute', 'office_files'})
            seen.add((m['base_role'], tuple(m['required_capabilities']), tuple(m['optional_capabilities'])))
        self.assertEqual(len(seen), len(METHODS), 'no two methods may share the same role and capability shape')
        bodies = [m['sections']['method'] for m in info['methods'].values()]
        self.assertEqual(len(set(bodies)), len(METHODS), 'the method sections must differ')

    def test_methods_state_their_own_trade_rules(self):
        """A coarse content guard on the contracts a reviewer reads in full: each method carries the rule that defines it."""
        text = {m: (ROOT / 'roles' / 'office' / (m + '.md')).read_text(encoding='utf-8') for m in METHODS}
        needles = {'research-assistant': ('nguồn chính', 'chưa đọc được', 'mâu thuẫn'),
                   'executive-secretary': ('quyết định', 'đề xuất', 'việc chờ', 'cần xác nhận'),
                   'correspondence': ('trích dẫn', 'Không gửi', 'To/Cc'),
                   'market-analyst': ('quan sát', 'ước lượng', 'dự báo', 'độ bao phủ', 'NEEDS_CAPABILITY'),
                   'data-analyst': ('0**, **thiếu', 'làm tròn', 'NEEDS_CAPABILITY', 'ngoại lai'),
                   'evidence-reviewer': ('mở nguồn', 'Không viết lại', 'chưa kiểm', 'PASSED')}
        for mid, words in needles.items():
            for w in words:
                self.assertIn(w, text[mid], (mid, w))
        main = (ROOT / 'roles' / 'office' / 'MAIN.md').read_text(encoding='utf-8')
        for w in ('Việc nhỏ làm trực tiếp', 'OFFICE-METHOD:', 'task_revision', 'không phải dấu vết chạy thật', 'PREPARED'):
            self.assertIn(w, main)

    def catalog_bytes(self, edit):
        doc = json.loads((ROOT / 'roles' / 'office' / 'catalog.json').read_text(encoding='utf-8'))
        edit(doc)
        return json.dumps(doc, ensure_ascii=False, indent=2).encode('utf-8')

    def test_catalog_validator_refuses_unknown_version_field_id_role_and_paths(self):
        def top(k, v):
            return lambda d: d.__setitem__(k, v)

        def meth(k, v, i=1):
            return lambda d: d['methods'][i].__setitem__(k, v)
        cases = [
            ('unknown schema version', self.catalog_bytes(top('schema', 'law.office-methods/2')), 'UNKNOWN_VERSION'),
            ('foreign schema', self.catalog_bytes(top('schema', 'something/1')), 'CATALOG_INVALID:SCHEMA'),
            ('unknown top field', self.catalog_bytes(top('plugin', 'x')), 'UNKNOWN_FIELD:catalog.plugin'),
            ('unknown method field', self.catalog_bytes(meth('model', 'claude-x')), 'UNKNOWN_FIELD:executive-secretary.model'),
            ('grant-like field', self.catalog_bytes(meth('grants', [])), 'UNKNOWN_FIELD:executive-secretary.grants'),
            ('bad id', self.catalog_bytes(meth('id', 'Executive Secretary')), 'CATALOG_INVALID:methods[1].id'),
            ('duplicate id', self.catalog_bytes(meth('id', 'research-assistant')), 'CATALOG_INVALID:DUPLICATE_ID=research-assistant'),
            ('unknown base role', self.catalog_bytes(meth('base_role', 'domain_role')), 'CATALOG_INVALID:executive-secretary.base_role'),
            ('bool version', self.catalog_bytes(meth('method_version', True)), 'CATALOG_INVALID:executive-secretary.method_version'),
            ('version zero', self.catalog_bytes(meth('method_version', 0)), 'CATALOG_INVALID:executive-secretary.method_version'),
            ('contract outside the method tree', self.catalog_bytes(meth('contract', 'roles/worker/agent.md')), 'CATALOG_INVALID:executive-secretary.contract'),
            ('contract with dotdot', self.catalog_bytes(meth('contract', 'roles/office/../worker/agent.md')), 'CATALOG_INVALID:executive-secretary.contract'),
            ('contract with backslash', self.catalog_bytes(meth('contract', 'roles\\office\\executive-secretary.md')), 'CATALOG_INVALID:executive-secretary.contract'),
            ('contract of another method', self.catalog_bytes(meth('contract', 'roles/office/correspondence.md')), 'CATALOG_INVALID:executive-secretary.contract'),
            ('unknown capability', self.catalog_bytes(meth('required_capabilities', ['read_local', 'shell'])), 'CATALOG_INVALID:executive-secretary.required_capabilities'),
            ('required and optional overlap', self.catalog_bytes(meth('optional_capabilities', ['read_local'])), 'CATALOG_INVALID:executive-secretary.capabilities'),
            ('no required capability', self.catalog_bytes(meth('required_capabilities', [])), 'CATALOG_INVALID:executive-secretary.capabilities'),
            ('resource outside skills', self.catalog_bytes(meth('resources', ['references/x/SKILL.md'])), 'CATALOG_INVALID:executive-secretary.resources'),
            ('resource script', self.catalog_bytes(meth('resources', ['skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py'])), 'CATALOG_INVALID:executive-secretary.resources'),
            ('per-method preset', self.catalog_bytes(meth('preset_mode', 'OWN_MODEL')), 'CATALOG_INVALID:executive-secretary.preset_mode'),
            ('missing field', self.catalog_bytes(lambda d: d['methods'][1].pop('label')), 'CATALOG_INVALID:executive-secretary.label.MISSING'),
            ('label without english', self.catalog_bytes(meth('label', {'vi': 'x'})), 'CATALOG_INVALID:executive-secretary.label'),
            ('empty methods', self.catalog_bytes(top('methods', [])), 'CATALOG_INVALID:METHODS'),
            ('oversize', b'{"schema":"law.office-methods/1","methods":[]}' + b' ' * (office.MAX_CATALOG + 1), 'CATALOG_INVALID:TOO_LARGE'),
            ('duplicate json key', b'{"schema":"law.office-methods/1","schema":"law.office-methods/1","methods":[]}', 'CATALOG_INVALID:DUPLICATE_KEY'),
            ('NaN', b'{"schema":"law.office-methods/1","methods":[NaN]}', 'CATALOG_INVALID:NOT_JSON'),
            ('byte order mark', b'\xef\xbb\xbf{"schema":"law.office-methods/1","methods":[]}', 'CATALOG_INVALID:NOT_JSON'),
            ('not utf-8', b'\xff\xfe{}', 'CATALOG_INVALID:NOT_UTF8'),
            ('not an object', b'[1,2]', 'CATALOG_INVALID:NOT_OBJECT'),
        ]
        for label, data, code in cases:
            with self.subTest(label):
                catalog, problems = office.validate_catalog(data)
                self.assertIsNone(catalog)
                self.assertIn(code, problems)

    def test_catalog_validator_refuses_unhashable_capability_elements(self):
        for field in ('required_capabilities', 'optional_capabilities'):
            for value in ({'capability': 'read_local'}, ['read_local']):
                with self.subTest(field=field, value=value):
                    data = self.catalog_bytes(lambda d: d['methods'][1].__setitem__(field, [value]))
                    catalog, problems = office.validate_catalog(data)
                    self.assertIsNone(catalog)
                    self.assertIn('CATALOG_INVALID:executive-secretary.' + field, problems)

    def test_contract_validator_refuses_a_header_section_or_coherence_problem(self):
        info = office.load(ROOT)
        entry = info['methods']['data-analyst']
        good = entry['contract_bytes'].decode('utf-8')
        self.assertEqual(office.validate_contract(entry, good.encode('utf-8')), [])
        self.assertEqual(office.validate_contract(entry, good.replace('\n', '\r\n').encode('utf-8')), [], 'a CRLF copy edited on Windows still validates')
        first = good.split('\n', 1)[0]
        cases = {
            'header version': good.replace(first, first.replace('version=%d' % entry['method_version'],
                                                              'version=%d' % (entry['method_version'] + 1)), 1),
            'header id': good.replace(first, first.replace('id=data-analyst', 'id=market-analyst'), 1),
            'header role': good.replace(first, first.replace('base_role=worker', 'base_role=reviewer'), 1),
            'no header': good.split('\n', 1)[1],
            'section removed': good.replace('{#missing}', '{#other}'),
            'order changed': good.replace('{#input}', '{#TMP}').replace('{#method}', '{#input}').replace('{#TMP}', '{#method}'),
            'no english line': re.sub(r'^EN:.*$', '', good, flags=re.M),
            'capability not stated': good.replace('`compute`', 'compute'),
            'resource not stated': good.replace('`excel-workbooks`', 'excel-workbooks'),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertTrue(office.validate_contract(entry, text.encode('utf-8')), label)
        self.assertTrue(office.validate_contract(entry, b'\xff\xfe'))
        self.assertTrue(office.validate_contract(entry, good.encode('utf-8') + b'x' * office.MAX_CONTRACT))

    def test_a_broken_contract_breaks_only_its_own_method_and_a_broken_catalog_breaks_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = office_root(tmp)
            (root / 'roles' / 'office' / 'correspondence.md').write_text('# not a contract\n', encoding='utf-8')
            info = office.load(root)
            self.assertTrue(info['ok'])
            self.assertTrue(info['methods']['correspondence']['problems'])
            self.assertEqual(info['methods']['market-analyst']['problems'], [])
            self.assertEqual(office.status(root)['methods'], 5)
            self.assertEqual(office.compose(request('correspondence'), root)['reason'], 'CONTRACT_INVALID')
            (root / 'roles' / 'office' / 'research-assistant.md').unlink()
            self.assertIn('CONTRACT_INVALID:research-assistant:MISSING_OR_NOT_REGULAR', office.load(root)['problems'])
            (root / 'roles' / 'office' / 'catalog.json').write_text('{', encoding='utf-8')
            info = office.load(root)
            self.assertFalse(info['ok'])
            self.assertEqual(office.compose(request(), root)['reason'], 'CATALOG_INVALID')
            self.assertEqual(office.status(root), {'available': False, 'methods': 0, 'problems': info['problems'][:5]})

    def test_links_and_unreadable_paths_are_refused_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = office_root(Path(tmp) / 'a')
            elsewhere = Path(tmp) / 'elsewhere'
            shutil.copytree(str(root / 'roles' / 'office'), str(elsewhere))
            shutil.rmtree(str(root / 'roles' / 'office'))
            if not make_link(root / 'roles' / 'office', elsewhere):
                self.skipTest('NOT_CHECKED: no symlink or junction can be created here')
            info = office.load(root)
            self.assertFalse(info['ok'])
            self.assertEqual(info['problems'], ['CATALOG_UNREADABLE:MISSING_OR_NOT_REGULAR'])
            self.assertEqual(office.compose(request(), root)['reason'], 'CATALOG_INVALID')
        with tempfile.TemporaryDirectory() as tmp:
            root = office_root(tmp)
            shutil.rmtree(str(root / 'skills' / 'local' / 'shared'))
            self.assertTrue(make_link(root / 'skills' / 'local' / 'shared', ROOT / 'skills' / 'local' / 'shared'))
            out = office.compose(request(), root)
            self.assertEqual(out['reason'], 'CONTEXT_INVALID')
            self.assertTrue(any(p.startswith('RESOURCE_UNAVAILABLE:' + SKILL_MINUTES) for p in out['problems']), out['problems'])

    def test_capability_rows_follow_the_exporter_table_and_keep_four_dimensions(self):
        for role, tools in native_agents.TOOLS_BY_ROLE.items():
            rows = {r['capability']: r for r in office.capability_rows(role, list(office.CAPABILITIES), [])}
            self.assertEqual(rows['read_local']['exporter'], 'PRESENT')
            self.assertEqual(rows['write_text']['exporter'], 'PRESENT' if 'Write' in tools else 'ABSENT', role)
            self.assertEqual(rows['write_html']['exporter'], rows['write_text']['exporter'])
            self.assertEqual((rows['compute']['exporter'], rows['office_files']['exporter']), ('ABSENT', 'ABSENT'))
            for r in rows.values():
                self.assertEqual((r['grant'], r['host']), ('NOT_INSPECTED', 'NOT_INSPECTED'))
                self.assertEqual(r['status'], {'PRESENT': 'PREPARED_UNVERIFIED', 'ABSENT': 'NEEDS_CAPABILITY'}[r['exporter']])
        with mock.patch.object(office, 'exporter_tools', return_value=None):
            rows = {r['capability']: r for r in office.capability_rows('worker', ['read_local', 'compute'], ['write_html'])}
        self.assertEqual((rows['read_local']['exporter'], rows['read_local']['status']), ('NOT_INSPECTED', 'NOT_VERIFIED'))
        self.assertEqual((rows['compute']['exporter'], rows['compute']['status']), ('ABSENT', 'NEEDS_CAPABILITY'))
        self.assertEqual(rows['write_html']['status'], 'OPTIONAL_UNAVAILABLE')


class Compose(unittest.TestCase):
    """One brief for the method Main chose, from an explicit request, read only."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='law-office-')
        self.addCleanup(self.tmp.cleanup)
        self.root = office_root(self.tmp.name)

    def compose(self, method='executive-secretary', **over):
        return office.compose(request(method, **over), self.root)

    def test_weekly_report_brief_is_concrete_binds_exact_bytes_and_keeps_roles_apart(self):
        out = self.compose()
        self.assertEqual((out['outcome'], out['state'], out['problems'], out['writes']), ('COMPOSED', 'PREPARED', [], []))
        self.assertEqual(out['claims'], {'prepared': True, 'invoked': False, 'content_checked': False})
        self.assertEqual((out['method']['id'], out['method']['base_role'], out['method']['method_version'], out['method']['preset_mode']),
                         ('executive-secretary', 'worker', 1, 'INHERIT_CORE_PROFILE'))
        refs = {r['path']: r['digest'] for r in out['context_refs']}
        self.assertEqual(refs, {'roles/office/catalog.json': sha((self.root / 'roles/office/catalog.json').read_bytes()),
                                'roles/office/executive-secretary.md': sha((self.root / 'roles/office/executive-secretary.md').read_bytes()),
                                SKILL_MINUTES: sha((self.root / SKILL_MINUTES).read_bytes())})
        self.assertEqual(out['inputs_proposal'], [{'path': SOURCE, 'digest': sha((self.root / SOURCE).read_bytes())}])
        brief = out['brief']
        for needle in ('executive-secretary', 'Báo cáo tuần 1 gửi trưởng phòng', SOURCE, 'roles/office/executive-secretary.md', SKILL_MINUTES,
                       'CANDIDATE', 'cần xác nhận', 'không chứng minh vai đã được gọi'):
            self.assertIn(needle, brief)
        method_vi = office.part(office.load(self.root)['methods']['executive-secretary']['sections']['method'], 'vi')
        self.assertIn(method_vi, brief, 'the method section is quoted verbatim from the bound contract')
        frag = out['task_fragment']
        self.assertEqual(frag['acceptance_requirement']['req_id'], 'OFFICE-METHOD:executive-secretary:v1')
        self.assertTrue(frag['acceptance_requirement']['mandatory'])
        self.assertEqual(set(frag['acceptance_requirement']), {'req_id', 'statement', 'mandatory'})
        self.assertEqual(frag['context_refs'], out['context_refs'])
        caps = {c['capability']: c for c in out['capabilities']}
        self.assertEqual(out['held'], [])
        self.assertEqual({k: caps['write_text'][k] for k in ('required', 'exporter', 'grant', 'host', 'status')},
                         {'required': True, 'exporter': 'PRESENT', 'grant': 'NOT_INSPECTED', 'host': 'NOT_INSPECTED', 'status': 'PREPARED_UNVERIFIED'})
        self.assertEqual(out['profile']['profile_state'], 'PROFILE_ABSENT')  # no profile: no model, no grant is invented
        self.assertIsNone(out['profile']['requested'])
        self.assertEqual((out['profile']['applied'], out['profile']['registration']), ('NOT_INSPECTED', 'NOT_INSPECTED'))
        self.assertNotIn('model', json.dumps(out['task_fragment']).lower())

    def test_english_brief_uses_the_english_lines_of_the_contract(self):
        out = self.compose(lang='en', output_format='html')
        self.assertEqual(out['state'], 'PREPARED')
        info = office.load(self.root)['methods']['executive-secretary']
        self.assertIn(office.part(info['sections']['checks'], 'en'), out['brief'])
        self.assertIn('BEFORE YOU START', out['brief'])
        self.assertIn('This brief only prepares a hand-over', out['brief'])
        self.assertIn('write_html', [c['capability'] for c in out['capabilities'] if c['required']])

    def test_report_loop_contracts_reach_the_worker_and_reviewer_briefs_in_both_languages(self):
        """The claim table, the keep-decisions revision pass and the finding codes are part of the bound method text, not Main-only advice."""
        decisions = 'Quyết định giữ nguyên chữ: D1 chọn phương án B.'
        for lang in ('vi', 'en'):
            sec = self.compose(lang=lang, request=decisions + ' Sửa mục 2 theo phát hiện P1 (claim C3).')
            rev = self.compose('evidence-reviewer', lang=lang, request=decisions + ' Review bản sửa.')
            for out in (sec, rev):
                self.assertEqual((out['outcome'], out['state']), ('COMPOSED', 'PREPARED'), lang)
                self.assertIn(decisions, out['brief'], 'the keep-verbatim list in the request reaches the assignee untouched')
            words = {'vi': (('`C1`', 'bảng căn cứ', 'CẦN XÁC NHẬN', 'Thay đổi so với bản trước', 'không tự đổi', 'trả Main'),
                            ('`P1`', 'mã claim', 'Review lần sửa', 'còn nguyên chữ', 'không suy từ review bản trước')),
                     'en': (('`C1`', 'evidence table', 'revision pass', 'keeps its wording', 'returned to Main'),
                            ('`P1`', 'claim code', 'For a revision', 'keep their wording', 'never inferred from the earlier review'))}[lang]
            for w in words[0]:
                self.assertIn(w, sec['brief'], (lang, w))
            for w in words[1]:
                self.assertIn(w, rev['brief'], (lang, w))
        self.assertEqual(self.compose()['state'], 'PREPARED', 'a plain first report is unchanged by the revision pass')

    def test_compute_dependent_data_analysis_keeps_the_missing_tool_held_not_ready(self):
        out = self.compose('data-analyst', request='Tổng hợp doanh thu theo tháng và so cùng kỳ từ bảng bán hàng.')
        self.assertEqual((out['outcome'], out['state']), ('COMPOSED', 'NEEDS_CAPABILITY'))
        self.assertEqual(out['held'], ['compute'])
        compute = [c for c in out['capabilities'] if c['capability'] == 'compute'][0]
        self.assertEqual((compute['required'], compute['exporter'], compute['status']), (True, 'ABSENT', 'NEEDS_CAPABILITY'))
        self.assertIn('compute: NEEDS_CAPABILITY', out['brief'])
        self.assertFalse(any('shell' in json.dumps(c) for c in out['capabilities']), 'no shell is offered')
        self.assertTrue(out['claims']['prepared'] and not out['claims']['invoked'])

    def test_format_and_declared_compute_raise_the_requirement_of_other_methods(self):
        out = self.compose('market-analyst', needs_compute=True)
        self.assertEqual((out['state'], out['held']), ('NEEDS_CAPABILITY', ['compute']))
        self.assertEqual(self.compose('market-analyst')['state'], 'PREPARED')
        docx = self.compose(output_format='docx')
        self.assertEqual((docx['state'], docx['held']), ('NEEDS_CAPABILITY', ['office_files']))
        rev = office.compose(request('evidence-reviewer', output_format='html', resources_used=[]), self.root)  # a core Reviewer cannot Write
        self.assertEqual((rev['state'], rev['held']), ('NEEDS_CAPABILITY', ['write_html']))
        scout = office.compose(request('research-assistant', resources_used=[]), self.root)
        self.assertEqual(scout['state'], 'PREPARED')
        self.assertIn('trả trong phản hồi, không ghi file', scout['brief'])
        # hand-over duties differ by role: only the Worker is told to write a RESULT; Scout and Reviewer return a ROLE_REPORT and write nothing
        for read_only in (scout, rev):
            self.assertIn('ROLE_REPORT', read_only['brief'])
            self.assertNotIn('RESULT.json', read_only['brief'])
        worker = self.compose()['brief']
        self.assertIn('RESULT.json', worker)
        self.assertIn('chưa phải gói giao đã hoàn thiện', worker)
        self.assertIn('Không khai đã băm hoặc tự điền digest', worker)
        self.assertIn('not a completed hand-over package', self.compose(lang='en')['brief'])
        # V2-B: the Worker writes the RESULT only from a digest observation Main passes; it has no hashing tool and Main does not write the RESULT for it
        self.assertIn('Bạn không có công cụ băm', worker)
        self.assertIn('quan sát công cụ', worker)
        self.assertIn('role: ACTUAL_BYTES', worker)
        self.assertIn('không viết RESULT thay Worker', worker)
        en = self.compose(lang='en')['brief']
        for needle in ('You have no hashing tool', 'digest observation', 'ACTUAL_BYTES', 'does not write the RESULT in your place'):
            self.assertIn(needle, en)

    def test_missing_unsupported_or_misplaced_sources_are_held_as_missing_input(self):
        out = self.compose(sources=[{'path': 'references/khong-co.txt'}, {'path': '../ngoai.txt'}, {'path': '.agent/STATE.md'}, {'path': 'working'}])
        self.assertEqual((out['outcome'], out['state']), ('COMPOSED', 'NEEDS_INPUT'))
        codes = {(m['code'], m['path']) for m in out['missing']}
        self.assertEqual(codes, {('SOURCE_MISSING', 'references/khong-co.txt'), ('SOURCE_PATH_UNSUPPORTED', '../ngoai.txt'),
                                 ('SOURCE_ZONE_NOT_ALLOWED', '.agent/STATE.md'), ('SOURCE_ZONE_NOT_ALLOWED', 'working')})
        self.assertEqual(out['inputs_proposal'], [])
        self.assertIn('PHẦN ĐANG CHỜ', out['brief'])
        none = self.compose(sources=[])
        self.assertEqual((none['state'], none['missing']), ('NEEDS_INPUT', [{'code': 'NO_SOURCES'}]))
        big = self.compose()
        self.assertEqual(big['state'], 'PREPARED')
        with mock.patch.object(office, 'MAX_SOURCE', 4):
            self.assertEqual(self.compose()['missing'][0]['code'], 'SOURCE_TOO_LARGE')

    def test_refusals_return_no_brief_and_no_binding(self):
        before = tree(self.root)
        cases = [
            ('not an object', ['x'], 'REQUEST_INVALID'),
            ('unknown field', request(model='claude-x'), 'REQUEST_INVALID'),
            ('missing reason', {k: v for k, v in request().items() if k != 'reason'}, 'REQUEST_INVALID'),
            ('empty request', request(request='   '), 'REQUEST_INVALID'),
            ('control character', request(request='a\x00b'), 'REQUEST_INVALID'),
            ('bad format', request(output_format='exe'), 'REQUEST_INVALID'),
            ('format list', request(output_format=[]), 'REQUEST_INVALID'),
            ('format dict', request(output_format={}), 'REQUEST_INVALID'),
            ('format null', request(output_format=None), 'REQUEST_INVALID'),
            ('format int', request(output_format=1), 'REQUEST_INVALID'),
            ('format bool', request(output_format=True), 'REQUEST_INVALID'),
            ('bool as string', request(needs_compute='yes'), 'REQUEST_INVALID'),
            ('bad language', request(lang='fr'), 'REQUEST_INVALID'),
            ('source extra key', request(sources=[{'path': SOURCE, 'cmd': 'x'}]), 'REQUEST_INVALID'),
            ('too many sources', request(sources=[{'path': SOURCE}] * 51), 'REQUEST_INVALID'),
            ('duplicate resource', request(resources_used=[SKILL_HTML, SKILL_HTML]), 'REQUEST_INVALID'),
            ('unknown method', request('market-oracle'), 'UNKNOWN_METHOD'),
            ('resource of another method', request(resources_used=['skills/local/shared/excel-workbooks/SKILL.md']), 'CONTEXT_INVALID'),
            ('resource outside the listing', request(resources_used=['PROJECT.md']), 'CONTEXT_INVALID'),
        ]
        for label, req, reason in cases:
            with self.subTest(label):
                out = office.compose(req, self.root)
                self.assertEqual((out['outcome'], out['state'], out['reason']), ('REFUSED', 'REFUSED', reason), out)
                self.assertTrue(out['problems'])
                self.assertNotIn('brief', out)
                self.assertNotIn('context_refs', out)
                self.assertEqual((out['writes'], out['claims']['prepared']), ([], False))
        self.assertEqual(tree(self.root), before)
        (self.root / SKILL_MINUTES).unlink()  # a listed resource that is gone is reported, nothing else happens
        out = self.compose()
        self.assertEqual((out['reason'], out['problems']), ('CONTEXT_INVALID', ['RESOURCE_UNAVAILABLE:%s:MISSING_OR_NOT_REGULAR' % SKILL_MINUTES]))

    def test_composing_writes_nothing_uses_no_network_and_imports_nothing_from_project_data(self):
        trap = self.root / 'tools'
        trap.mkdir()
        (trap / 'execution_profile.py').write_text("open(r'%s', 'w').write('imported')\n" % (self.root / 'TRAP.txt'), encoding='utf-8')
        (trap / 'office.py').write_text("raise SystemExit('project data was imported')\n", encoding='utf-8')
        before = tree(self.root)

        def no_network(*a, **k):
            raise AssertionError('the helper must not use the network')
        with mock.patch.object(socket.socket, 'connect', no_network), mock.patch.object(socket, 'create_connection', no_network):
            self.assertEqual(self.compose()['state'], 'PREPARED')
            self.assertEqual(office.describe(self.root)['ok'], True)
            self.assertEqual(office.status(self.root)['available'], True)
            self.assertEqual(self.compose(output_format='bogus')['outcome'], 'REFUSED')
        self.assertEqual(tree(self.root), before)
        self.assertFalse((self.root / 'TRAP.txt').exists())
        self.assertNotIn(str(self.root), [os.path.dirname(getattr(m, '__file__', '') or '') for m in sys.modules.values()])

    def test_profile_choices_are_reported_as_requested_only(self):
        if not HAVE_JSONSCHEMA:
            self.skipTest('NOT_CHECKED: the profile owner needs jsonschema')
        import test_execution_profile as tep  # fixture builder only
        doc = tep.profile_doc('PROFILE')
        doc['host'] = 'claude-code'
        doc['roles']['worker'].update(model='claude-sonnet-5-5', effort='high')
        proj = tep.make_project(self.tmp.name, name='with-profile', profile=doc, line=ep.POINTERS['vi'])
        shutil.copytree(str(self.root / 'roles' / 'office'), str(proj / 'roles' / 'office'))
        (proj / SOURCE).parent.mkdir(parents=True, exist_ok=True)
        (proj / SOURCE).write_bytes((self.root / SOURCE).read_bytes())
        before = tree(proj)
        out = office.compose(request(resources_used=[]), proj)
        view = out['profile']
        self.assertEqual(out['outcome'], 'COMPOSED', out)
        self.assertEqual(view['profile_state'], 'OK')
        self.assertEqual(view['requested']['model'], 'claude-sonnet-5-5')
        self.assertEqual((view['applied'], view['registration']), ('NOT_INSPECTED', 'NOT_INSPECTED'))
        self.assertNotEqual(view['permission'], 'GRANTED')
        self.assertEqual(tree(proj), before)
        self.assertNotIn('claude-sonnet-5-5', out['brief'], 'the model choice is not part of the hand-over text')
        self.assertEqual(out['state'], 'PREPARED', 'a requested model neither grants nor blocks the hand-over preparation')

    def test_cli_list_validate_compose_and_refusals(self):
        done = run_office('list', '--json')
        self.assertEqual(done.returncode, 0, done.stderr)
        rows = json.loads(done.stdout.decode('utf-8'))
        self.assertEqual([m['id'] for m in rows['methods']], list(METHODS))
        self.assertTrue(all(m['ok'] for m in rows['methods']))
        self.assertEqual(run_office('list', '--lang', 'en').returncode, 0)
        self.assertIn('OK', run_office('validate').stdout.decode('utf-8'))
        payload = json.dumps(request(sources=[], resources_used=[]), ensure_ascii=False).encode('utf-8')
        done = run_office('compose', '--input', '-', '--json', stdin=payload)
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout.decode('utf-8'))
        self.assertEqual((out['outcome'], out['state']), ('COMPOSED', 'NEEDS_INPUT'))
        text = run_office('compose', '--input', '-', stdin=payload).stdout.decode('utf-8')
        self.assertIn('prepared=True invoked=False content_checked=False', text)
        for label, data in (('duplicate key', b'{"method":"a","method":"b"}'), ('NaN', b'{"x":NaN}'), ('not json', b'{'),
                            ('oversize', b' ' * (office.MAX_REQUEST + 1)), ('not utf-8', b'\xff'), ('unknown field', b'{"method":"executive-secretary","x":1}')):
            with self.subTest(label):
                done = run_office('compose', '--input', '-', '--json', stdin=data)
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertEqual(json.loads(done.stdout.decode('utf-8'))['outcome'], 'REFUSED')
        for value in ([], {}, None, 1, True):
            with self.subTest(output_format=value):
                data = json.dumps(request(output_format=value), ensure_ascii=False).encode('utf-8')
                done = run_office('compose', '--input', '-', '--json', stdin=data)
                self.assertEqual(done.returncode, 1, done.stderr)
                self.assertEqual(done.stderr, b'', 'invalid JSON fields must not raise a traceback')
                out = json.loads(done.stdout.decode('utf-8'))
                self.assertEqual((out['outcome'], out['reason'], out['writes']), ('REFUSED', 'REQUEST_INVALID', []))
                self.assertIn('REQUEST_INVALID:output_format', out['problems'])
        self.assertEqual(run_office('compose', '--input', str(Path(self.tmp.name) / 'missing.json'), '--json').returncode, 1)
        self.assertEqual(run_office().returncode, 2)

    def test_the_three_representative_requests_are_walkthroughs_not_recorded_routing(self):
        main = (ROOT / 'roles' / 'office' / 'MAIN.md').read_text(encoding='utf-8')
        section = main[main.index('## 8.'):main.index('## 9.')]
        self.assertIn('không phải dấu vết chạy thật', section)
        self.assertIn('việc nhỏ: Main sửa trực tiếp', section)
        self.assertIn('`executive-secretary`', section)
        self.assertIn('`evidence-reviewer`', section)
        self.assertIn('`data-analyst`', section)
        self.assertIn('NEEDS_CAPABILITY', section)
        self.assertIn('không tính nhẩm', section)


@unittest.skipUnless(tf.CAN_RUN, tf.SKIP_RUN)
class OfficeBinding(tf.FlowBase):
    """The real checkpoint recipe of roles/README.md with office tasks. No fake checkpoint: the recipe is executed from the document."""

    def setUp(self):
        super().setUp()
        for rel in [p.relative_to(ROOT).as_posix() for p in (ROOT / 'roles' / 'office').iterdir()] + [SKILL_HTML, SKILL_MINUTES]:
            self.write(rel, (ROOT / rel).read_bytes())
        self.catalog0, self.contract0 = self.read('roles/office/catalog.json'), self.read('roles/office/executive-secretary.md')

    def office_assignment(self, task_id='t-o', rev=1, aid='a1', method='executive-secretary', edit=None, **req):
        """Compose with the real helper, build the TASK from its fragment, let `edit` tamper with the task, then the role returns a RESULT."""
        out = office.compose(request(method, sources=[{'path': tf.SOURCE_REL}], resources_used=req.pop('resources_used', [SKILL_MINUTES]), **req), self.project)
        self.assertEqual(out['outcome'], 'COMPOSED', out)
        self.assertEqual(out['state'], 'PREPARED', out)
        task = self.task_record(task_id, rev, aid)
        task['acceptance']['requirements'].append(copy.deepcopy(out['task_fragment']['acceptance_requirement']))
        task['context_refs'] = copy.deepcopy(out['task_fragment']['context_refs'])
        if edit:
            edit(task)
        task_rel = self.put_task(task)
        result = self.result_record(task, aid, b'ban nhap bao cao tuan\n')
        result_rel = self.slot(task_id, aid) + '/RESULT.json'
        self.write(result_rel, json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
        return task_rel, result_rel, task, out

    def office_problems(self, cp):
        return [p for p in cp['problems'] if p.startswith('OFFICE_')]

    def test_a_valid_office_candidate_passes_and_publishes_the_checked_bytes(self):
        task_rel, result_rel, task, out = self.office_assignment()
        self.assertEqual({r['path'] for r in task['context_refs']}, {'roles/office/catalog.json', 'roles/office/executive-secretary.md', SKILL_MINUTES})
        before = self.tree()
        cp = self.checkpoint(task_rel, result_rel)
        self.assertEqual(cp['problems'], [])
        self.assertEqual(self.tree(), before, 'the checkpoint with the office guard only reads')
        self.assertEqual(cp['result']['acceptance_states'], ['CANDIDATE'])
        rid = self.new_rid()
        res = pn.publish(self.project, self.publish_request(cp, task_rel, result_rel), cp['candidate'], request_id=rid)
        self.assertEqual(res['outcome'], 'PUBLISHED', res)
        pub = pn.cj_loads(self.read('.agent/runtime/publish/%s.prepared.json' % rid))
        bound = {i['path'] for i in pub['task']['inputs']}
        self.assertTrue({'roles/office/catalog.json', 'roles/office/executive-secretary.md', SKILL_MINUTES} <= bound,
                        'the method context travels into the publish request with the other bound bytes')

    def test_changing_the_catalog_the_contract_a_skill_or_the_source_blocks_the_old_result(self):
        task_rel, result_rel, _, _ = self.office_assignment()
        self.assertEqual(self.checkpoint(task_rel, result_rel)['problems'], [])
        cases = [('contract', 'roles/office/executive-secretary.md', self.contract0 + '\nthêm một dòng\n'.encode('utf-8'), 'OFFICE_CONTRACT_BYTES_CHANGED'),
                 ('catalog', 'roles/office/catalog.json', self.catalog0 + b'\n', 'OFFICE_CATALOG_BYTES_CHANGED'),
                 ('skill', SKILL_MINUTES, self.read(SKILL_MINUTES) + b'\nx\n', None),
                 ('source', tf.SOURCE_REL, b'nguon da doi\n', None)]
        for label, rel, new, code in cases:
            with self.subTest(label):
                original = self.read(rel)
                self.write(rel, new)
                problems = self.checkpoint(task_rel, result_rel)['problems']
                self.assertIn('INPUT_CHANGED ' + rel, problems)
                if code:
                    self.assertIn(code, problems)
                self.write(rel, original)
                self.assertEqual(self.checkpoint(task_rel, result_rel)['problems'], [], 'restoring the bound bytes restores the match')

    def test_task_changes_void_the_old_result_which_keeps_its_bytes(self):
        task_rel, result_rel, task, out = self.office_assignment()
        old_result, old_candidate = self.read(result_rel), self.read(self.slot('t-o', 'a1') + '/candidate/draft.txt')
        changed = copy.deepcopy(task)
        changed['acceptance']['requirements'][-1]['statement'] += ' Thêm điều kiện mới.'
        self.put_task(changed)  # same revision: the binding of the old RESULT no longer matches
        problems = self.checkpoint(task_rel, result_rel)['problems']
        self.assertTrue(any(p.startswith('BINDING B-') for p in problems), problems)
        changed['task_revision'] = 2
        self.put_task(changed)
        self.assertTrue(any(p.startswith('BINDING B-REF') for p in self.checkpoint(task_rel, result_rel)['problems']))
        self.assertEqual((self.read(result_rel), self.read(self.slot('t-o', 'a1') + '/candidate/draft.txt')), (old_result, old_candidate))

    def test_every_marker_and_context_mismatch_blocks_with_an_office_reason_and_never_falls_back_to_legacy(self):
        cat_ref = {'path': 'roles/office/catalog.json', 'digest': sha(self.catalog0)}
        other_contract = {'path': 'roles/office/correspondence.md', 'digest': sha(self.read('roles/office/correspondence.md'))}
        main_guide = {'path': 'roles/office/MAIN.md', 'digest': sha(self.read('roles/office/MAIN.md'))}

        def marker(task):
            return [r for r in task['acceptance']['requirements'] if r['req_id'].startswith('OFFICE-METHOD')]

        def drop_marker(t):
            t['acceptance']['requirements'] = [r for r in t['acceptance']['requirements'] if not r['req_id'].startswith('OFFICE-METHOD')]

        def set_marker(**kw):
            return lambda t: marker(t)[0].update(kw)

        def add_marker(req_id):
            return lambda t: t['acceptance']['requirements'].append({'req_id': req_id, 'statement': 'một điều kiện nghiệp vụ khác', 'mandatory': True})

        def set_roles(role):
            def edit(t):
                t['authority']['subject']['role'] = role
                t['envelope']['role'] = role
            return edit

        def swap_contract(t):
            t['context_refs'] = [cat_ref, other_contract]
        cases = [
            ('marker missing, refs remain', drop_marker, 'OFFICE_MARKER_MISSING'),
            ('refs missing, marker remains', lambda t: t.__setitem__('context_refs', []), 'OFFICE_CONTEXT_MISSING'),
            ('second marker', add_marker('OFFICE-METHOD:correspondence:v1'), 'OFFICE_MARKER_DUPLICATE'),
            ('unknown method', set_marker(req_id='OFFICE-METHOD:market-oracle:v1'), 'OFFICE_METHOD_UNKNOWN market-oracle'),
            ('wrong version', set_marker(req_id='OFFICE-METHOD:executive-secretary:v2'), 'OFFICE_METHOD_VERSION catalog=1 marker=2'),
            ('malformed id', set_marker(req_id='OFFICE-METHOD:executive-secretary'), 'OFFICE_MARKER_MALFORMED'),
            ('upper case id', set_marker(req_id='OFFICE-METHOD:Executive-Secretary:v1'), 'OFFICE_MARKER_MALFORMED'),
            ('lower case prefix', set_marker(req_id='office-method:executive-secretary:v1'), 'OFFICE_MARKER_MALFORMED'),
            ('marker not mandatory', set_marker(mandatory=False), 'OFFICE_MARKER_MALFORMED'),
            ('subject is a reviewer', set_roles('reviewer'), 'OFFICE_ROLE_MISMATCH base=worker subject=reviewer envelope=reviewer'),
            ('contract of another method', swap_contract, 'OFFICE_CONTRACT_LOCATOR roles/office/correspondence.md'),
            ('extra office context', lambda t: t['context_refs'].append(main_guide), 'OFFICE_CONTEXT_SHAPE catalog=1 contract=2'),
            ('catalog ref alone', lambda t: t.__setitem__('context_refs', [cat_ref]), 'OFFICE_CONTEXT_SHAPE catalog=1 contract=0'),
        ]
        for n, (label, edit, expected) in enumerate(cases):
            with self.subTest(label):
                task_rel, result_rel, _, _ = self.office_assignment('t-case%d' % n, edit=edit)
                problems = self.checkpoint(task_rel, result_rel)['problems']
                self.assertIn(expected, problems)
                self.assertTrue(self.office_problems({'problems': problems}), problems)
                self.assertFalse([p for p in problems if p.startswith('BINDING')], 'binding is untouched: only the office guard blocks %s' % label)
        # a catalog reference whose digest is not the bytes on disk is blocked by both the byte check and the guard
        task_rel, result_rel, _, _ = self.office_assignment('t-bad', edit=lambda t: t['context_refs'][0].update(digest='sha256:' + '0' * 64))
        problems = self.checkpoint(task_rel, result_rel)['problems']
        self.assertIn('INPUT_CHANGED roles/office/catalog.json', problems)
        self.assertIn('OFFICE_CATALOG_BYTES_CHANGED', problems)

    def test_a_catalog_that_moved_on_to_another_version_is_a_version_mismatch_not_a_pass(self):
        task_rel, result_rel, _, _ = self.office_assignment()
        doc = json.loads(self.catalog0.decode('utf-8'))
        for m in doc['methods']:
            if m['id'] == 'executive-secretary':
                m['method_version'] = 2
        self.write('roles/office/catalog.json', json.dumps(doc, ensure_ascii=False, indent=2).encode('utf-8'))
        problems = self.checkpoint(task_rel, result_rel)['problems']
        self.assertIn('OFFICE_METHOD_VERSION catalog=2 marker=1', problems)
        self.assertIn('INPUT_CHANGED roles/office/catalog.json', problems)

    def test_a_contract_that_stays_unchanged_but_whose_catalog_row_is_gone_is_blocked(self):
        task_rel, result_rel, _, _ = self.office_assignment()
        doc = json.loads(self.catalog0.decode('utf-8'))
        doc['methods'] = [m for m in doc['methods'] if m['id'] != 'executive-secretary']
        self.write('roles/office/catalog.json', json.dumps(doc, ensure_ascii=False, indent=2).encode('utf-8'))
        self.assertIn('OFFICE_METHOD_UNKNOWN executive-secretary', self.checkpoint(task_rel, result_rel)['problems'])
        self.write('roles/office/catalog.json', b'{')
        self.assertTrue([p for p in self.checkpoint(task_rel, result_rel)['problems'] if p.startswith('OFFICE_CATALOG_INVALID')])
        os.remove(self.abs('roles/office/catalog.json'))
        self.assertTrue([p for p in self.checkpoint(task_rel, result_rel)['problems'] if p.startswith('OFFICE_CATALOG_UNREADABLE')])

    def test_removing_the_marker_and_all_refs_together_leaves_the_old_result_unbound(self):
        task_rel, result_rel, task, _ = self.office_assignment()
        old = (self.read(result_rel), self.read(self.slot('t-o', 'a1') + '/candidate/draft.txt'))
        for label, rev in (('same revision', 1), ('revision raised', 2)):
            with self.subTest(label):
                plain = copy.deepcopy(task)
                plain['task_revision'] = rev
                plain['context_refs'] = []
                plain['acceptance']['requirements'] = [r for r in plain['acceptance']['requirements'] if not r['req_id'].startswith('OFFICE-METHOD')]
                self.put_task(plain)  # a rewrite by someone who can rewrite the whole record: the guard sees a legacy task
                problems = self.checkpoint(task_rel, result_rel)['problems']
                self.assertEqual(self.office_problems({'problems': problems}), [], 'no office reason: the task now looks legacy')
                self.assertTrue([p for p in problems if p.startswith('BINDING')], 'the RESULT made for the office task no longer matches the binding')
                self.assertEqual((self.read(result_rel), self.read(self.slot('t-o', 'a1') + '/candidate/draft.txt')), old)

    def test_a_legacy_task_still_runs_without_any_office_file(self):
        shutil.rmtree(self.abs('roles'))
        task_rel, result_rel, _ = self.assignment('t-legacy', 1, 'a1')
        cp = self.checkpoint(task_rel, result_rel)
        self.assertEqual(cp['problems'], [])
        self.assertEqual(self.r.load_v3(ROOT)['office'].guard_task(cp['task'], lambda rel: (None, 'MISSING')), [])

    def test_the_guard_serves_a_reviewer_task_through_the_same_marker(self):
        out = office.compose(request('evidence-reviewer', sources=[{'path': tf.SOURCE_REL}], resources_used=[]), self.project)
        self.assertEqual(out['state'], 'PREPARED')

        def task_for(role):
            return {'acceptance': {'requirements': [dict(out['task_fragment']['acceptance_requirement'])]}, 'context_refs': out['context_refs'],
                    'authority': {'subject': {'actor_id': 'rv', 'role': role}}, 'envelope': {'role': role}}
        read = lambda rel: self.r.read_file(self.project, rel)  # noqa: E731
        self.assertEqual(office.guard_task(task_for('reviewer'), read), [])
        self.assertEqual(office.guard_task(task_for('worker'), read), ['OFFICE_ROLE_MISMATCH base=reviewer subject=worker envelope=worker'])
        self.assertEqual(office.guard_task({'acceptance': {'requirements': []}, 'context_refs': [{'path': 'references/x.txt', 'digest': 'sha256:' + '1' * 64}]}, read), [])


@unittest.skipUnless(tf.CAN_RUN, tf.SKIP_RUN)
class MainAssistedDigest(tf.FlowBase):
    """V2-B: Main observes the candidate digest with the real owner (`observe_candidate` of the recipe in roles/README.md) and the Worker writes its own
    RESULT from that observation. The Worker here is a TEST DRIVER that writes files; it is not a native Worker, and no host, grant or provider is involved.
    What this proves: the real recipe/owner refuse what they must and write nothing, and a RESULT built only from the observation passes the real checkpoint
    structurally. It does not prove a native child can continue, that a host exposes the helper to Main, or any content quality."""
    BODY = 'Báo cáo tuần — dòng một\r\ndòng hai ✓\n'.encode('utf-8')

    def setUp(self):
        super().setUp()
        for rel in [p.relative_to(ROOT).as_posix() for p in (ROOT / 'roles' / 'office').iterdir()] + [SKILL_HTML, SKILL_MINUTES]:
            self.write(rel, (ROOT / rel).read_bytes())

    def dispatch(self, task_id='t-o', aid='a1', rev=1, edit=None, body=None, targets='both', method='executive-secretary'):
        """Main finalises the TASK (marker, context, targets in the new slot), keeps its raw digest and computes the binding; the driver then writes the candidate."""
        out = office.compose(request(method, sources=[{'path': tf.SOURCE_REL}], resources_used=[SKILL_MINUTES] if method == 'executive-secretary' else []), self.project)
        self.assertEqual(out['state'], 'PREPARED', out)
        slot = self.slot(task_id, aid)
        cand, res = slot + '/candidate/draft.txt', slot + '/RESULT.json'
        task = self.task_record(task_id, rev, aid, targets=[cand, res] if targets == 'both' else targets(cand, res))
        task['effects']['expected_outputs'] = [cand]  # the RESULT is metadata, not an output of its own
        task['acceptance']['requirements'].append(copy.deepcopy(out['task_fragment']['acceptance_requirement']))
        task['context_refs'] = copy.deepcopy(out['task_fragment']['context_refs'])
        if edit:
            edit(task)
        task_rel = self.put_task(task)
        d = {'task_rel': task_rel, 'task': task, 'cand': cand, 'res': res, 'aid': aid, 'raw': tf.sha(self.read(task_rel)),
             'binding': self.r.binding_stub(self.v3, task), 'marker': out['task_fragment']['acceptance_requirement']['req_id']}
        self.write(cand, self.BODY if body is None else body)  # worker phase 1
        return d

    def observe(self, d, **over):
        a = {'task_rel': d['task_rel'], 'cand': d['cand'], 'res': d['res'], 'raw': d['raw']}
        a.update(over)
        return self.r.observe_candidate(self.v3, self.project, a['task_rel'], a['cand'], a['res'], a['raw'])

    def worker_result(self, d, obs):
        """Worker phase 2 (test driver): the RESULT is built ONLY from the delivered binding and the observation passed by Main."""
        c = obs['candidate']
        outputs = [{'path': c['path'], 'digest': c['digest'], 'role': 'ACTUAL_BYTES'}]
        binding = copy.deepcopy(d['binding'])
        binding['outputs'] = outputs
        result = {'schema_version': tf.V3, 'record_type': 'result', 'evaluation_basis': tf.EB, 'result_id': 'r-%s-%s' % (d['task']['task_id'], d['aid']),
                  'binding': binding, 'produced_by': dict(tf.WORKER), 'artifacts': copy.deepcopy(outputs),
                  'evidence': [{'evidence_id': 'ev-digest-1', 'req_id': d['marker'], 'locator': 'main-observation:%s' % obs['observed_by'], 'kind': 'TOOL_OBSERVED',
                                'scope': 'sha256 of the candidate observed by Main with %s; not hashed by the Worker; no content check' % obs['observed_by']}],
                  'requirements': [{'req_id': r['req_id'], 'mandatory': r['mandatory'], 'status': 'UNKNOWN'} for r in d['task']['acceptance']['requirements']],
                  'gaps': ['No tool checked the semantic content.'], 'acceptance_states': ['CANDIDATE'], 'state_set_by': dict(tf.WORKER)}
        self.write(d['res'], json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
        return result

    def refused(self, label, d, code, spy, **kw):
        before = self.tree()
        got = self.observe(d, **kw)
        self.assertFalse(got['observed'], label)
        self.assertIsNone(got['observation'], label)
        self.assertTrue(any(p == code or p.startswith(code + ' ') or p.startswith(code) for p in got['problems']), '%s: %s' % (label, got['problems']))
        self.assertEqual(self.tree(), before, '%s: a refusal writes nothing' % label)
        spy.assert_not_called()

    def test_main_observes_the_digest_the_worker_writes_the_result_from_it_and_the_checkpoint_passes(self):
        d = self.dispatch()
        before = self.tree()
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy, \
                mock.patch.object(socket, 'socket', side_effect=AssertionError('network')), mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('subprocess')), \
                mock.patch.object(self.v3['library'], 'read_book', side_effect=AssertionError('ledger')):
            got = self.observe(d)
        self.assertEqual(self.tree(), before, 'observing reads only: no RESULT, no sidecar, no registry')
        spy.assert_called_once_with(self.project, d['cand'])
        self.assertEqual((got['observed'], got['problems']), (True, []), got)
        obs = got['observation']
        self.assertEqual(obs['candidate']['digest'], 'sha256:' + hashlib.sha256(self.BODY).hexdigest(), 'matches an independent hash of the bytes')
        self.assertEqual(obs['candidate']['size'], len(self.BODY))
        self.assertEqual((obs['task']['task_id'], obs['task']['task_revision'], obs['task']['raw_digest']), ('t-o', 1, d['raw']))
        self.assertEqual((obs['observed_by'], obs['result_path']), ('artifacts.observe_file', d['res']))
        self.assertEqual(set(got), {'observed', 'problems', 'observation'}, 'no binding, RESULT or receipt is returned')
        self.assertFalse(os.path.exists(self.abs(d['res'])))
        result = self.worker_result(d, obs)
        cp = self.checkpoint(d['task_rel'], d['res'])
        self.assertEqual(cp['problems'], [], 'structure and bytes only: not a PASS, a grant or a content check')
        self.assertEqual(cp['candidate'], self.BODY)
        self.assertEqual((result['acceptance_states'], result['produced_by']['role'], result['state_set_by']['role']), (['CANDIDATE'], 'worker', 'worker'))
        self.assertEqual(result['binding']['outputs'], result['artifacts'])
        self.assertNotIn(d['res'], {a['path'] for a in result['artifacts']}, 'the RESULT is not its own artifact')
        self.assertEqual(self.r.integration_gate(cp, {}, 'NOT_REQUIRED')['state'], 'HOLD', 'matching bytes do not meet the mandatory requirements')

    def test_without_the_dispatch_digest_or_after_the_task_changed_nothing_is_observed(self):
        d = self.dispatch()
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy:
            for label, raw, code in (('none', None, 'TASK_RAW_DIGEST_REQUIRED'), ('empty', '', 'TASK_RAW_DIGEST_REQUIRED'), ('bare hex', 'ab' * 32, 'TASK_RAW_DIGEST_REQUIRED'),
                                     ('other digest', 'sha256:' + '0' * 64, 'TASK_CHANGED_SINCE_DISPATCH')):
                with self.subTest(label):
                    before = self.tree()
                    got = self.r.observe_candidate(self.v3, self.project, d['task_rel'], d['cand'], d['res'], raw)
                    self.assertEqual((got['observed'], got['observation']), (False, None))
                    self.assertEqual(got['problems'], [code])
                    self.assertEqual(self.tree(), before)
            changed = copy.deepcopy(d['task'])
            changed['acceptance']['requirements'][0]['statement'] += ' đổi sau khi giao'
            self.put_task(changed)  # Main's digest is the one kept at dispatch: the digest just read must not stand in for it
            self.refused('task rewritten after dispatch', d, 'TASK_CHANGED_SINCE_DISPATCH', spy)
            os.remove(self.abs(d['task_rel']))
            self.refused('task missing', d, 'RECORD_TASK', spy)
            self.write(d['task_rel'], b'{not json')
            self.refused('task not a record', d, 'RECORD_', spy, raw=tf.sha(b'{not json'))
            self.assertEqual(self.r.observe_candidate({'pkg': 1}, self.project, d['task_rel'], d['cand'], d['res'], d['raw'])['problems'], ['OWNER_UNAVAILABLE'])

    def test_a_task_copy_is_not_the_current_task_path(self):
        d = self.dispatch()
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy:
            for rel in ('working/%s/t-copy/TASK.json' % tf.WORK,
                        'working/%s/t-o/assignments/a1/TASK.json' % tf.WORK):
                with self.subTest(rel):
                    self.write(rel, self.read(d['task_rel']))
                    self.refused('copied TASK', d, 'TASK_PATH_NOT_CURRENT', spy, task_rel=rel)

    def test_project_artifacts_module_is_never_imported_as_the_observer(self):
        d = self.dispatch()
        poison = 'working/poison-import.txt'
        self.write('artifacts.py', ('from pathlib import Path\nPath(%r).write_text("executed")\n' % self.abs(poison)).encode('utf-8'))
        cached = sys.modules.pop('artifacts', None)
        try:
            with mock.patch.object(sys, 'path', [self.project] + list(sys.path)):
                v3 = self.r.load_v3(ROOT)
                got = self.r.observe_candidate(v3, self.project, d['task_rel'], d['cand'], d['res'], d['raw'])
            self.assertTrue(got['observed'], got)
            self.assertFalse(os.path.exists(self.abs(poison)), 'project code must not run before the trusted-owner check')
        finally:
            sys.modules.pop('artifacts', None)
            if cached is not None:
                sys.modules['artifacts'] = cached

    def test_only_an_office_worker_task_with_both_marker_and_context_is_supported(self):
        def drop_marker(t):
            t['acceptance']['requirements'] = [r for r in t['acceptance']['requirements'] if not r['req_id'].startswith('OFFICE-METHOD')]

        def reviewer(t):
            t['authority']['subject']['role'] = 'reviewer'
            t['envelope']['role'] = 'reviewer'

        def legacy(t):
            drop_marker(t)
            t['context_refs'] = []

        def other_method(t):
            [r for r in t['acceptance']['requirements'] if r['req_id'].startswith('OFFICE-METHOD')][0]['req_id'] = 'OFFICE-METHOD:evidence-reviewer:v1'
        cases = [('legacy task: both missing, guard_task alone says []', legacy, 'OFFICE_MARKER_AND_CONTEXT_REQUIRED'),
                 ('marker without context', lambda t: t.__setitem__('context_refs', []), 'OFFICE_MARKER_AND_CONTEXT_REQUIRED'),
                 ('context without marker', drop_marker, 'OFFICE_MARKER_AND_CONTEXT_REQUIRED'),
                 ('reviewer task', reviewer, 'TASK_NOT_WORKER'),
                 ('marker of another role', other_method, 'OFFICE_ROLE_MISMATCH')]
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy:
            for n, (label, edit, code) in enumerate(cases):
                with self.subTest(label):
                    d = self.dispatch('t-case%d' % n, edit=edit)
                    if n == 0:
                        self.assertEqual(self.v3['office'].guard_task(d['task'], lambda rel: self.r.read_file(self.project, rel)), [], 'the guard alone lets a legacy task through')
                    self.refused(label, d, code, spy)

    def test_targets_must_be_exactly_the_candidate_and_the_result_of_one_slot_under_create_new_write_working(self):
        def action_edit(**kw):
            return lambda t: t['effects']['actions'][0].update(kw)
        cases = [('result not declared', dict(targets=lambda c, r: [c])),
                 ('candidate not declared', dict(targets=lambda c, r: [r])),
                 ('extra shared target', dict(targets=lambda c, r: [c, r, 'working/%s/ghi-chu.txt' % tf.WORK])),
                 ('another slot declared', dict(targets=lambda c, r: [c, self.slot('t-x', 'a9') + '/RESULT.json'])),
                 ('tool is not Write', dict(edit=action_edit(tool='Edit'))),
                 ('operation is not create_new', dict(edit=action_edit(operation='overwrite'))),
                 ('zone is not working', dict(edit=action_edit(write_zone='output_new'))),
                 ('a second action writes elsewhere', dict(edit=lambda t: t['effects']['actions'].append(
                     {'operation': 'create_new', 'tool': 'Write', 'targets': ['working/%s/ghi-chu.txt' % tf.WORK], 'write_zone': 'working'})))]
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy:
            for n, (label, kw) in enumerate(cases):
                with self.subTest(label):
                    d = self.dispatch('t-c%d' % n, **kw)
                    got = self.observe(d)
                    self.assertFalse(got['observed'])
                    self.assertTrue(got['problems'], label)
                    self.assertFalse(os.path.exists(self.abs(d['res'])), label)
                    spy.assert_not_called()
                    # a TASK rejected by the loader is also a refusal; every other case must be the targets check itself
                    self.assertTrue(got['problems'][0].startswith(('TARGETS_NOT_CANDIDATE_AND_RESULT', 'RECORD_TASK')), got['problems'])
        self.assertEqual(self.observe(self.dispatch('t-ok'))['problems'], [], 'the same builder with the exact targets is accepted')

    def test_paths_and_slot_layout_are_checked_by_the_owner_forms_and_not_normalised(self):
        d = self.dispatch()
        slot = self.slot('t-o', 'a1')
        other_slot = self.slot('t-o', 'a2')
        self.write(other_slot + '/candidate/draft.txt', self.BODY)
        cases = [('traversal', dict(cand=slot + '/candidate/../candidate/draft.txt'), 'PATH_UNSUPPORTED_FORM'),
                 ('backslash', dict(cand=slot.replace('/', '\\') + '\\candidate\\draft.txt'), 'PATH_UNSUPPORTED_FORM'),
                 ('absolute', dict(cand=self.abs(d['cand'])), 'PATH_UNSUPPORTED_FORM'),
                 ('drive alias', dict(cand='C:/x/draft.txt'), 'PATH_UNSUPPORTED_FORM'),
                 ('result with traversal', dict(res=slot + '/../a1/RESULT.json'), 'PATH_UNSUPPORTED_FORM'),
                 ('not a string', dict(res=None), 'PATH_UNSUPPORTED_FORM'),
                 ('candidate list', dict(cand=[]), 'PATH_UNSUPPORTED_FORM'),
                 ('result dict', dict(res={}), 'PATH_UNSUPPORTED_FORM'),
                 ('candidate in another slot', dict(cand=other_slot + '/candidate/draft.txt'), 'SLOT_LAYOUT'),
                 ('result in another slot', dict(res=other_slot + '/RESULT.json'), 'SLOT_LAYOUT'),
                 ('result under another name', dict(res=slot + '/RESULT2.json'), 'SLOT_LAYOUT'),
                 ('candidate outside candidate/', dict(cand=slot + '/draft.txt'), 'SLOT_LAYOUT'),
                 ('candidate one level deeper', dict(cand=slot + '/candidate/sub/draft.txt'), 'SLOT_LAYOUT'),
                 ('shared output', dict(cand='output/%s/draft.txt' % tf.WORK), 'SLOT_LAYOUT')]
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy:
            for label, kw, code in cases:
                with self.subTest(label):
                    self.refused(label, d, code, spy, **kw)

    def test_result_that_exists_a_missing_candidate_and_owner_errors_hold_without_a_digest(self):
        d = self.dispatch()
        with mock.patch.object(artifacts, 'observe_file', wraps=artifacts.observe_file) as spy:
            self.write(d['res'], b'{}')
            self.refused('RESULT already exists', d, 'RESULT_ALREADY_EXISTS', spy)
            os.remove(self.abs(d['res']))
        with mock.patch.object(artifacts, 'observe_file', side_effect=OSError('boom')):
            got = self.observe(d)
            self.assertEqual((got['observed'], got['observation'], got['problems']), (False, None, ['OBSERVER_ERROR OSError']))
        with mock.patch.object(artifacts, 'observe_file', return_value=(None, 'changed')):
            self.assertEqual(self.observe(d)['problems'], ['CANDIDATE_CHANGED'])
        os.remove(self.abs(d['cand']))
        got = self.observe(d)
        self.assertEqual((got['observed'], got['problems']), (False, ['CANDIDATE_MISSING']))
        os.makedirs(self.abs(d['cand']))
        self.assertEqual(self.observe(d)['problems'], ['CANDIDATE_NOT_REGULAR'])

    def test_a_hardlinked_candidate_is_refused(self):
        d = self.dispatch()
        try:
            os.link(self.abs(d['cand']), self.abs('working/%s/kopija.txt' % tf.WORK))
        except OSError:
            self.skipTest('hard links cannot be made here: SKIPPED, not passed')
        before = self.tree()
        self.assertEqual(self.observe(d)['problems'], ['CANDIDATE_HARDLINK'])
        self.assertEqual(self.tree(), before)

    def test_a_candidate_or_a_result_slot_behind_a_link_is_refused(self):
        d = self.dispatch()
        cand_dir, moved = os.path.dirname(self.abs(d['cand'])), self.abs('working/%s/moved-candidate' % tf.WORK)
        os.rename(cand_dir, moved)
        if not make_link(cand_dir, moved):
            os.rename(moved, cand_dir)
            self.skipTest('directory links cannot be made here: SKIPPED, not passed')
        self.addCleanup(lambda: os.path.isdir(cand_dir) and os.rmdir(cand_dir))  # removes the link, never its target
        before = self.tree()
        self.assertEqual(self.observe(d)['problems'], ['CANDIDATE_LINK'])
        self.assertEqual(self.tree(), before)
        d2 = self.dispatch('t-slot')
        slot_dir, parked = os.path.dirname(self.abs(d2['res'])), self.abs('working/%s/parked-slot' % tf.WORK)
        os.rename(slot_dir, parked)
        self.assertTrue(make_link(slot_dir, parked))
        self.addCleanup(lambda: os.path.isdir(slot_dir) and os.rmdir(slot_dir))
        self.assertEqual(self.observe(d2)['problems'], ['RESULT_PATH_LINK'])

    def test_a_candidate_changed_after_the_observation_or_a_changed_task_or_input_is_caught_and_never_re_bound(self):
        d = self.dispatch()
        obs = self.observe(d)['observation']
        self.worker_result(d, obs)
        self.assertEqual(self.checkpoint(d['task_rel'], d['res'])['problems'], [])
        old_result = self.read(d['res'])
        # 1. the candidate changes after the observation: the RESULT keeps the old digest and the checkpoint stops it
        self.write(d['cand'], self.BODY + b'them mot dong\n')
        self.assertIn('CANDIDATE_CHANGED', self.checkpoint(d['task_rel'], d['res'])['problems'])
        self.assertEqual(self.read(d['res']), old_result, 'the RESULT digest is not edited to fit')
        self.write(d['cand'], self.BODY)
        self.assertEqual(self.checkpoint(d['task_rel'], d['res'])['problems'], [])
        # 2. an accepted input or its ledger row changes: the current checkpoint reports it, whatever the observation said
        self.write(tf.SOURCE_REL, b'nguon da doi\n')
        self.assertIn('INPUT_CHANGED ' + tf.SOURCE_REL, self.checkpoint(d['task_rel'], d['res'])['problems'])
        self.write(tf.SOURCE_REL, self.source0)
        self.edit_ledger(lambda ws: setattr(ws.cell(5, 22), 'value', 2))
        self.assertIn('LEDGER_METADATA_CHANGED SRC-000001', self.checkpoint(d['task_rel'], d['res'])['problems'])
        self.write('references/_INDEX.xlsx', self.ledger0)
        self.assertEqual(self.checkpoint(d['task_rel'], d['res'])['problems'], [])
        # 3. the TASK is revised: the old binding and the old observation are not reusable and the old RESULT is not re-bound
        revised = copy.deepcopy(d['task'])
        revised['task_revision'] = 2
        self.put_task(revised)
        self.assertTrue(any(p.startswith('BINDING B-REF') for p in self.checkpoint(d['task_rel'], d['res'])['problems']))
        self.assertEqual(self.observe(d)['problems'], ['TASK_CHANGED_SINCE_DISPATCH'], 'the digest Main kept at dispatch no longer matches the current TASK')
        again = self.r.observe_candidate(self.v3, self.project, d['task_rel'], d['cand'], d['res'], tf.sha(self.read(d['task_rel'])))
        self.assertEqual(again['problems'], ['RESULT_ALREADY_EXISTS'], 'a new revision needs a new slot: the old RESULT is neither reused nor overwritten')
        self.assertEqual(self.read(d['res']), old_result)

    def test_the_worker_tool_table_is_unchanged_and_a_reviewer_brief_asks_for_no_result(self):
        self.assertEqual(native_agents.TOOLS_BY_ROLE, {'scout': ('Read', 'Grep', 'Glob'), 'worker': ('Read', 'Grep', 'Glob', 'Write'), 'reviewer': ('Read', 'Grep', 'Glob')})
        rev = office.compose(request('evidence-reviewer', sources=[{'path': tf.SOURCE_REL}], resources_used=[]), self.project)
        self.assertNotIn('RESULT.json', rev['brief'])
        rows = {c['capability']: c['required'] for c in office.compose(request(sources=[{'path': tf.SOURCE_REL}]), self.project)['capabilities']}
        self.assertFalse({'compute', 'shell', 'bash'} & set(rows), 'the capability rows of the Worker method are unchanged: no compute or shell is added')
        self.assertTrue(rows['write_text'])


FRAGMENT_RE = re.compile(r'```json\n(.*?)\n```', re.S)


@unittest.skipUnless(tf.CAN_RUN, tf.SKIP_RUN)
class WorkerBriefResultShape(tf.FlowBase):
    """V2-E: the nested evidence[]/requirements[] shape of the Worker brief. The JSON fragment is taken from the brief that `compose` really renders (VI and EN),
    its VALUES are replaced by the TASK and the observation of this fixture, and the RESULT built that way goes through the real strict loader and checkpoint.
    The Worker is a TEST DRIVER that writes files; it is not a native Worker, and nothing here shows a native Worker follows the brief.
    The object keys come from the fragment only: a key the brief loses is not re-added by the driver, so the owner schema rejects the RESULT."""
    BODY = MainAssistedDigest.BODY
    dispatch = MainAssistedDigest.dispatch
    observe = MainAssistedDigest.observe
    SCHEMA = json.loads((ROOT / '.cvf' / 'contracts' / 'v3' / 'control.schema.json').read_text(encoding='utf-8'))['$defs']['result']

    def setUp(self):
        super().setUp()
        for rel in [p.relative_to(ROOT).as_posix() for p in (ROOT / 'roles' / 'office').iterdir()] + [SKILL_HTML, SKILL_MINUTES]:
            self.write(rel, (ROOT / rel).read_bytes())
        self.count = 0

    def brief(self, method='executive-secretary', **over):
        over.setdefault('sources', [{'path': tf.SOURCE_REL}])
        over.setdefault('resources_used', [SKILL_MINUTES] if method == 'executive-secretary' else [])
        return office.compose(request(method, **over), self.project)

    def fragment(self, lang):
        """The one JSON fragment of the rendered Worker brief, parsed (not re-built from anything in this test)."""
        brief = self.brief(lang=lang)['brief']
        found = FRAGMENT_RE.findall(brief)
        self.assertEqual(len(found), 1, 'one fenced JSON fragment in the %s brief' % lang)
        return json.loads(found[0])

    def dispatch_mixed(self):
        """A TASK with mandatory and optional requirements besides the office marker, so no flag can be taken from the illustrative sample."""
        self.count += 1
        extra = {'req_id': 'REQ-OPT-2', 'statement': 'Điều kiện không bắt buộc của lần giao', 'mandatory': False}
        d = self.dispatch(task_id='t-v2e%d' % self.count, edit=lambda t: t['acceptance']['requirements'].append(copy.deepcopy(extra)))
        self.assertEqual([r['mandatory'] for r in d['task']['acceptance']['requirements']], [True, True, False])
        return d

    def sub_objects(self, frag, d, obs):
        """evidence/requirements objects: structure from the fragment, VALUES from the TASK and the observation. A key missing from the fragment stays missing."""
        values = {'evidence_id': 'ev-digest-1', 'req_id': d['marker'], 'locator': 'main-observation:%s' % obs['observed_by'],
                  'scope': 'sha256 of the candidate observed by Main with %s; not hashed by the Worker; no content check' % obs['observed_by']}
        ev = copy.deepcopy(frag['evidence'][0])
        for key, val in values.items():
            if key in ev:
                ev[key] = val
        reqs, templates = [], frag['requirements']
        for i, task_req in enumerate(d['task']['acceptance']['requirements']):
            obj = copy.deepcopy(templates[i % len(templates)])
            for key in ('req_id', 'mandatory'):
                if key in obj:
                    obj[key] = task_req[key]
            reqs.append(obj)
        return [ev], reqs

    def write_result(self, d, obs, evidence, requirements):
        """Header and binding as the owner fixture builds them (worker_result of MainAssistedDigest); only the two sub-arrays are passed in."""
        c = obs['candidate']
        outputs = [{'path': c['path'], 'digest': c['digest'], 'role': 'ACTUAL_BYTES'}]
        binding = copy.deepcopy(d['binding'])
        binding['outputs'] = outputs
        result = {'schema_version': tf.V3, 'record_type': 'result', 'evaluation_basis': tf.EB, 'result_id': 'r-%s-%s' % (d['task']['task_id'], d['aid']),
                  'binding': binding, 'produced_by': dict(tf.WORKER), 'artifacts': copy.deepcopy(outputs), 'evidence': evidence, 'requirements': requirements,
                  'gaps': ['No tool checked the semantic content.'], 'acceptance_states': ['CANDIDATE'], 'state_set_by': dict(tf.WORKER)}
        self.write(d['res'], json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
        return result

    def problems_for(self, frag):
        """Fresh assignment in the temp project → Main's real observation → RESULT from `frag` → the real checkpoint. Returns (problems, result, checkpoint, d)."""
        d = self.dispatch_mixed()
        got = self.observe(d)
        self.assertEqual((got['observed'], got['problems']), (True, []), got)
        evidence, requirements = self.sub_objects(frag, d, got['observation'])
        result = self.write_result(d, got['observation'], evidence, requirements)
        cp = self.checkpoint(d['task_rel'], d['res'])
        return cp['problems'], result, cp, d

    def test_the_rendered_brief_states_the_schema_the_fields_and_the_return_when_missing_in_both_languages(self):
        required_ev = set(self.SCHEMA['properties']['evidence']['items']['required'])
        item_req = self.SCHEMA['properties']['requirements']['items']
        for lang, words in (('vi', ('.cvf/contracts/v3/control.schema.json#/$defs/result', 'CHỈ minh họa cấu trúc', 'trả lại Main trước khi Write', 'không đoán tên trường',
                                    'Read/Grep/Glob/Write', 'không mặc định mọi mandatory=true', 'TASK cuối cùng', 'không state, không note', 'không là quyền để Write')),
                            ('en', ('.cvf/contracts/v3/control.schema.json#/$defs/result', 'ONLY illustrates the structure', 'return to Main before writing', 'guess field names',
                                    'Read/Grep/Glob/Write', 'do not default every mandatory to true', 'final TASK', 'no state, no note', 'not authority to Write'))):
            with self.subTest(lang):
                before = self.tree()
                out = self.brief(lang=lang)
                self.assertEqual((out['state'], out['writes'], out['claims']), ('PREPARED', [], {'prepared': True, 'invoked': False, 'content_checked': False}))
                self.assertEqual(self.tree(), before, 'compose stays read only')
                for w in words:
                    self.assertIn(w, out['brief'])
                for field in self.SCHEMA['required'] + ['schema_version', 'record_type', 'evaluation_basis']:
                    self.assertIn(field, out['brief'], 'the twelve top-level fields stay named')
                frag = self.fragment(lang)
                self.assertEqual(set(frag), {'evidence', 'requirements'})
                self.assertEqual(set(frag['evidence'][0]), required_ev, 'the sample evidence object has exactly the fields the owner schema requires')
                self.assertEqual({tuple(sorted(o)) for o in frag['requirements']}, {tuple(sorted(item_req['required']))})
                self.assertTrue(set(frag['evidence'][0]) <= set(self.SCHEMA['properties']['evidence']['items']['properties']))
                self.assertEqual({o['status'] for o in frag['requirements']} | {frag['evidence'][0]['kind']}, {'UNKNOWN', 'TOOL_OBSERVED'})
                self.assertEqual({o['mandatory'] for o in frag['requirements']}, {True, False}, 'the sample shows both flags: it is not a reason to set every flag to true')
                text = json.dumps(frag)
                for banned in ('sha256', 'USER_CONFIRMATION', '"MET"', 'PASS', '"state"', '"note"', 'binding'):
                    self.assertNotIn(banned, text)

    def test_both_languages_carry_the_same_fragment_and_scout_and_reviewer_briefs_get_no_result_shape(self):
        self.assertEqual(self.fragment('vi'), self.fragment('en'))
        for method in ('research-assistant', 'evidence-reviewer'):
            for lang in ('vi', 'en'):
                with self.subTest((method, lang)):
                    brief = self.brief(method, lang=lang)['brief']
                    for needle in ('```', 'evidence_id', 'RESULT.json', 'control.schema.json', 'requirements[]'):
                        self.assertNotIn(needle, brief)
        held = self.brief(sources=[])
        self.assertEqual(held['state'], 'NEEDS_INPUT', 'a brief with the sample is still not permission to dispatch')
        self.assertIn('NO_SOURCES', held['brief'])

    def test_fragment_from_the_rendered_brief_builds_a_result_the_strict_loader_and_checkpoint_accept(self):
        for lang in ('vi', 'en'):
            with self.subTest(lang):
                frag = self.fragment(lang)
                problems, result, cp, d = self.problems_for(frag)
                self.assertEqual(problems, [], 'structure and bytes only: not a PASS, a grant or a content check')
                record, _, why = self.r.read_record(self.v3, self.project, d['res'], 'result')
                self.assertIsNone(why)
                self.assertEqual(record['record_type'], 'result')
                task_reqs = d['task']['acceptance']['requirements']
                self.assertEqual([(r['req_id'], r['mandatory']) for r in result['requirements']], [(r['req_id'], r['mandatory']) for r in task_reqs])
                self.assertEqual({r['mandatory'] for r in result['requirements']}, {True, False}, 'flags follow the TASK, not the sample')
                self.assertEqual({r['status'] for r in result['requirements']}, {'UNKNOWN'})
                self.assertFalse({'state', 'note'} & {k for r in result['requirements'] for k in r})
                self.assertEqual([(e['evidence_id'], e['req_id'], e['kind']) for e in result['evidence']], [('ev-digest-1', d['marker'], 'TOOL_OBSERVED')])
                self.assertFalse(any('EXAMPLE' in json.dumps(result[k]) for k in ('evidence', 'requirements')), 'no illustrative ID travels into the delivered file')
                self.assertEqual(result['acceptance_states'], ['CANDIDATE'])
                self.assertEqual(result['binding']['outputs'], result['artifacts'])
                self.assertNotIn(d['res'], {a['path'] for a in result['artifacts']}, 'the RESULT is not its own artifact')
                self.assertEqual(self.r.integration_gate(cp, {}, 'NOT_REQUIRED')['state'], 'HOLD', 'UNKNOWN requirements and a CANDIDATE are not integrated')

    def test_the_d_shaped_result_is_refused_by_the_owner_schema(self):
        d = self.dispatch_mixed()
        obs = self.observe(d)['observation']
        wrong_evidence = [{'locator': 'main-observation:%s' % obs['observed_by'], 'kind': 'TOOL_OBSERVED', 'scope': 'sha256 observed by Main'}]
        wrong_reqs = [{'req_id': r['req_id'], 'state': 'UNKNOWN', 'note': 'chưa kiểm'} for r in d['task']['acceptance']['requirements']]
        self.write_result(d, obs, wrong_evidence, wrong_reqs)
        problems = self.checkpoint(d['task_rel'], d['res'])['problems']
        self.assertTrue(problems and problems[0].startswith('RECORD_REJECTED result'), problems)
        record, _, why = self.r.read_record(self.v3, self.project, d['res'], 'result')
        self.assertIsNone(record)
        self.assertTrue(why.startswith('RECORD_REJECTED result'), why)

    def test_losing_or_adding_a_nested_key_in_the_fragment_of_the_rendered_brief_is_caught(self):
        base = self.fragment('vi')
        self.assertEqual(self.problems_for(base)[0], [], 'the unmutated fragment is the passing baseline')
        mutations = [('evidence_id removed', lambda f: f['evidence'][0].pop('evidence_id')), ('evidence req_id removed', lambda f: f['evidence'][0].pop('req_id')),
                     ('mandatory removed', lambda f: [o.pop('mandatory') for o in f['requirements']]), ('status removed', lambda f: [o.pop('status') for o in f['requirements']]),
                     ('state added', lambda f: [o.update(state='UNKNOWN') for o in f['requirements']]), ('note added', lambda f: f['requirements'][0].update(note='x'))]
        for label, mutate in mutations:
            with self.subTest(label):
                frag = copy.deepcopy(base)  # in memory only: no source, schema or artifact is touched
                mutate(frag)
                problems = self.problems_for(frag)[0]
                self.assertTrue(problems and problems[0].startswith('RECORD_REJECTED result'), problems)

    def test_a_brief_that_loses_a_nested_field_is_caught_end_to_end(self):
        """The same check through the renderer: the module sample is changed in memory, `compose` renders it, the fixture reads the new brief."""
        base = json.loads(office.RESULT_FRAGMENT)
        for label, mutate in (('evidence_id', lambda f: f['evidence'][0].pop('evidence_id')), ('mandatory', lambda f: [o.pop('mandatory') for o in f['requirements']])):
            with self.subTest(label):
                frag = copy.deepcopy(base)
                mutate(frag)
                with mock.patch.object(office, 'RESULT_FRAGMENT', json.dumps(frag, indent=2)):
                    problems = self.problems_for(self.fragment('en'))[0]
                self.assertTrue(problems and problems[0].startswith('RECORD_REJECTED result'), problems)
        self.assertEqual(office.RESULT_FRAGMENT, json.dumps(base, ensure_ascii=False, indent=2), 'the patch was in memory only')

    def test_main_guide_names_the_full_package_the_return_when_missing_and_the_corrected_limits_in_both_languages(self):
        main = (ROOT / 'roles' / 'office' / 'MAIN.md').read_text(encoding='utf-8')
        for w in ('Gói giao đủ cho Worker', '.cvf/contracts/v3/control.schema.json', 'tách khỏi nguồn nghiệp vụ', 'không đoán root kho nguồn',
                  'không mở rộng Read', 'kỳ và người đọc bắt buộc do bên giao xác định', 'không tự miễn vì chỉ là smoke', 'hai invocation',
                  'checkpoint schema giữ HOLD', 'chưa có RESULT native hợp lệ', 'lưu hash và bản source driver trước khi gọi', 'không bị buộc lập driver',
                  'evidence thiếu `evidence_id`/`req_id`'):
            self.assertIn(w, main)
        for w in ('A complete Worker package', 'protocol contract, kept apart from business sources', 'does not guess the source-repo root', 'does not widen Read',
                  'period and reader are set by the party handing over', 'do not waive it because it is only a smoke run', 'two invocations',
                  'held by the schema checkpoint', 'no valid native RESULT', 'save the hash and source of the driver before the call', 'not required to build a driver',
                  'evidence missing `evidence_id`/`req_id`'):
            self.assertIn(w, main)
        for w in ('Xử lý phát hiện của Reviewer và giao bản', '`SỬA`', '`GIỮ-CÓ-LÝ-DO`', '`CHỜ`', '`CHƯA KIỂM`', 'không tự hạ mức', 'không lập sổ nghiệp vụ riêng',
                  'Giao bản không là `USER_ACCEPTED`', 'Sửa báo cáo giữ quyết định', 'ghi vào mục "Decisions" của STATE', 'Mở tiếp ở phiên khác',
                  'artifacts.py find', 'current_draft.py status', 'không chạy lại Worker', 'không tạo TASK, slot hay candidate mới'):
            self.assertIn(w, main)
        for w in ('Reviewer findings arrive as `P1`', 'no parallel business ledger', 'it is not `USER_ACCEPTED`', 'Revising a report while keeping decisions',
                  'Reopening in another session', 'replaces none of the steps above', 'no new TASK, slot or candidate'):
            self.assertIn(w, main)
        self.assertNotIn('chưa chạy ở host thật', main)
        self.assertNotIn('not on a real host', main)
        self.assertNotIn('is not proven here', main)


class HttpAndPanel(unittest.TestCase):
    """The panel status carries the helper's summary and exposes no route that takes or stores a task description."""

    def test_status_summary_available_missing_and_broken(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import app
        with mock.patch.object(app, 'ROOT', str(ROOT)):
            self.assertEqual(app.office_info(), {'available': True, 'methods': 6, 'problems': []})
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(app, 'ROOT', tmp):
                info = app.office_info()
                self.assertEqual((info['available'], info['methods']), (False, 0))
            with mock.patch.object(office, 'status', side_effect=RuntimeError('boom')):
                self.assertEqual(app.office_info(), {'available': False, 'methods': 0, 'problems': ['OFFICE_UNREADABLE']})

    def test_status_requires_a_readable_main_guide_and_keeps_the_valid_method_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = office_root(Path(tmp))
            guide = root / 'roles' / 'office' / 'MAIN.md'
            cases = [
                ('missing', None, 'OFFICE_GUIDE_UNREADABLE:MISSING_OR_NOT_REGULAR'),
                ('not utf-8', b'\xff', 'OFFICE_GUIDE_INVALID:NOT_UTF8'),
                ('too large', b'x' * (office.MAX_CONTRACT + 1), 'OFFICE_GUIDE_UNREADABLE:TOO_LARGE'),
            ]
            for label, data, problem in cases:
                with self.subTest(label=label):
                    if guide.exists():
                        guide.unlink()
                    if data is not None:
                        guide.write_bytes(data)
                    info = office.status(root)
                    self.assertEqual((info['available'], info['methods']), (False, 6))
                    self.assertIn(problem, info['problems'])


NEED_PACKAGE = unittest.skipUnless(HAVE_JSONSCHEMA, 'NOT_CHECKED: package pins and the profile need jsonschema')


def run_in(base, script, *args):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, str(Path(base) / 'tools' / script), *map(str, args)], cwd=str(base), env=e, capture_output=True,
                          encoding='utf-8', timeout=300)


@NEED_PACKAGE
class Delivery(unittest.TestCase):
    """Package projection, new project (VI and EN) and upgrade through the real owners. Not a release, not a gate."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-office-delivery-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name)
        cls.A, cls.B, cls.A0 = cls.base / 'A', cls.base / 'B', cls.base / 'A0'
        cp.materialize(str(cls.A), branding=False)
        (cls.A / 'VERSION').write_text('90.0.1\n', encoding='utf-8')
        shutil.copytree(str(cls.A), str(cls.B))
        (cls.B / 'VERSION').write_text('90.0.2\n', encoding='utf-8')
        cls.contract = 'roles/office/executive-secretary.md'
        (cls.B / cls.contract).write_bytes((cls.B / cls.contract).read_bytes() + '\nDòng thêm của bản B\n'.encode('utf-8'))
        shutil.copytree(str(cls.A), str(cls.A0))  # a package that predates the office files
        (cls.A0 / 'VERSION').write_text('90.0.0\n', encoding='utf-8')
        shutil.rmtree(str(cls.A0 / 'roles' / 'office'))
        (cls.A0 / 'tools' / 'office.py').unlink()
        for pkg in (cls.A, cls.B, cls.A0):
            done = run_in(pkg, 'check_package.py', '--write-manifest')
            assert done.returncode == 0, done.stdout + done.stderr

    def new_project(self, pkg, name, lang):
        done = run_in(pkg, 'new_project.py', '--name', name, '--dest', self.base, '--lang', lang, '--apply', '--result-json')
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return self.base / name

    def test_the_projection_carries_the_office_files_with_the_exact_source_bytes_and_a_clean_profile(self):
        files = ['roles/office/' + p.name for p in (ROOT / 'roles' / 'office').iterdir()] + ['tools/office.py']
        self.assertEqual(len(files), 9)
        manifest = (self.A / 'MANIFEST.sha256').read_text(encoding='utf-8')
        for rel in files:
            self.assertEqual((self.A / rel).read_bytes().replace(b'\r\n', b'\n'), (ROOT / rel).read_bytes().replace(b'\r\n', b'\n'), rel)
            self.assertIn('  ' + rel + '\n', manifest, rel)
        self.assertEqual(cp.source_package_problems(str(self.A)), [])
        self.assertEqual((self.A / ep.PROFILE_REL).read_bytes(), ep.clean_profile_bytes())
        self.assertEqual(run_in(self.A, 'office.py', 'validate').returncode, 0)

    def test_new_projects_in_both_languages_have_a_working_method_tool_guide_and_clean_profile(self):
        for lang in ('vi', 'en'):
            with self.subTest(lang):
                proj = self.new_project(self.A, 'P-' + lang, lang)
                self.assertTrue((proj / 'roles/office/MAIN.md').is_file())
                self.assertEqual(run_in(proj, 'office.py', 'validate').stdout.strip(), 'OK')
                self.assertEqual(run_in(proj, 'check_package.py', '--verify').returncode, 0)
                self.assertEqual((proj / ep.PROFILE_REL).read_bytes(), ep.clean_profile_bytes())
                rep = ep.inspect(proj)
                self.assertEqual(rep['grant_claims'], 0)
                self.assertTrue(all(r['permission'] != 'GRANTED' for r in rep['roles'].values()))
                src = proj / 'references' / 'source-documents' / 'tuan.txt'
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text('ghi chú', encoding='utf-8')
                payload = json.dumps(request(sources=[{'path': 'references/source-documents/tuan.txt'}], resources_used=[]), ensure_ascii=False)
                done = subprocess.run([sys.executable, '-B', str(proj / 'tools' / 'office.py'), 'compose', '--input', '-', '--json'], cwd=str(proj), input=payload,
                                      capture_output=True, encoding='utf-8', env=dict(os.environ, PYTHONUTF8='1'))
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(json.loads(done.stdout)['state'], 'PREPARED')
                guide = (proj / 'AGENTS.md').read_text(encoding='utf-8')
                self.assertIn('roles/office/MAIN.md', guide)
                self.assertNotIn('roadmap', json.dumps(sorted(p.name for p in proj.iterdir())))

    def test_upgrade_of_an_older_project_adds_the_office_files_and_keeps_every_user_file_and_the_profile(self):
        proj = self.new_project(self.A0, 'P-old', 'vi')
        self.assertFalse((proj / 'roles/office').exists())
        choices = {'host': 'claude-code', 'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}}}
        plan = ep.plan_config(str(proj), choices)
        self.assertEqual(plan['status'], 'PREVIEW', plan)
        self.assertEqual(ep.apply_config(str(proj), choices, plan['plan']['plan_sha256'])['status'], 'WRITTEN')
        mine = {'output/ket-qua.md': 'kết quả giả\n', 'working/nhap.md': 'nháp giả\n', 'references/quy-che.txt': 'quy chế giả\n'}
        for rel, text in mine.items():
            (proj / rel).parent.mkdir(parents=True, exist_ok=True)
            (proj / rel).write_text(text, encoding='utf-8')
        keep = ['PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', ep.PROFILE_REL] + list(mine)
        before = {rel: (proj / rel).read_bytes() for rel in keep}
        tree0 = tree(proj)
        pv = run_in(self.A, 'upgrade_package.py', '--project', proj, '--result-json')
        self.assertEqual(pv.returncode, 0, pv.stdout + pv.stderr)
        self.assertEqual(tree(proj), tree0, 'the preview writes nothing')
        done = run_in(self.A, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        for rel in ['tools/office.py'] + ['roles/office/' + p.name for p in (self.A / 'roles' / 'office').iterdir()]:
            self.assertEqual((proj / rel).read_bytes(), (self.A / rel).read_bytes(), rel)
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, before, 'user files and the profile keep their bytes')
        profile = json.loads((proj / ep.PROFILE_REL).read_text(encoding='utf-8'))
        self.assertEqual(profile['roles']['worker']['model'], 'claude-sonnet-5-5')
        self.assertEqual(ep.inspect(proj)['grant_claims'], 0, 'the upgrade adds no grant')
        self.assertFalse([p for p in tree(proj) if p.endswith('.new') and p.startswith('roles/')], 'new package files need no pending copy')
        self.assertEqual(run_in(proj, 'office.py', 'validate').stdout.strip(), 'OK')

    def test_a_customised_contract_is_kept_and_the_package_change_waits_as_a_pending_copy(self):
        proj = self.new_project(self.A, 'P-edit', 'vi')
        mine = (proj / self.contract).read_bytes() + '\nGhi chú riêng của người dùng\n'.encode('utf-8')
        (proj / self.contract).write_bytes(mine)
        profile0 = (proj / ep.PROFILE_REL).read_bytes()
        tree0 = tree(proj)
        pv = run_in(self.B, 'upgrade_package.py', '--project', proj, '--result-json')
        self.assertEqual(pv.returncode, 0, pv.stdout + pv.stderr)
        self.assertEqual(tree(proj), tree0)
        done = run_in(self.B, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual((proj / self.contract).read_bytes(), mine, 'the user contract is not overwritten')
        self.assertEqual((proj / (self.contract + '.new')).read_bytes(), (self.B / self.contract).read_bytes())
        for rel in ('roles/office/catalog.json', 'roles/office/MAIN.md', 'tools/office.py'):
            self.assertEqual((proj / rel).read_bytes(), (self.B / rel).read_bytes(), rel)
        self.assertEqual((proj / ep.PROFILE_REL).read_bytes(), profile0)
        verdict = office.load(proj)
        self.assertTrue(verdict['ok'] and not verdict['methods']['executive-secretary']['problems'], 'the customised contract still validates')


if __name__ == '__main__':
    unittest.main()
