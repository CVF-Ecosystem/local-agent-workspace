"""Host-session declarations are preparation, never authority or observed runtime evidence."""
import argparse
import contextlib
import copy
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tests')]
import execution_profile as ep
import office
import transaction as tx
import test_execution_profile as profile_fixture
import test_office as office_fixture


class HostSession(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='law-host-session-')
        self.addCleanup(self.temp.cleanup)
        self.root = office_fixture.office_root(self.temp.name)
        self.note = self.root / 'working/host-note.txt'
        self.note.parent.mkdir(parents=True, exist_ok=True)
        self.note.write_bytes(b'Main reports native tools and a container-only Office smoke; actual model unknown.')
        self.session = {
            'host': 'cowork', 'agent_type': 'general-purpose', 'tool_names': ['Bash'],
            'capabilities': ['read_local', 'write_text', 'compute', 'office_files'],
            'requested_model': 'sonnet', 'requested_effort': 'medium',
            'execution_location': 'container', 'output_location': 'container',
            'evidence_ref': {'path': 'working/host-note.txt', 'digest': office.sha_of(self.note.read_bytes())},
        }

    def compose(self, session=None, **over):
        return office.compose(office_fixture.request('data-analyst', resources_used=[],
                              host_session=self.session if session is None else session, **over), self.root)

    def test_declared_native_compute_is_separate_from_exporter_and_observed_authority(self):
        before = office_fixture.tree(self.root)
        out = self.compose(output_format='xlsx')
        self.assertEqual(out['state'], 'PREPARED')
        caps = {c['capability']: c for c in out['capabilities']}
        self.assertEqual(caps['compute']['exporter'], 'ABSENT')
        self.assertEqual(caps['compute']['status'], 'ROUTE_READY_UNVERIFIED')
        self.assertEqual(caps['office_files']['status'], 'ROUTE_READY_UNVERIFIED')
        self.assertEqual(out['claims'], {'prepared': True, 'invoked': False, 'content_checked': False})
        for key in ('actual_model', 'actual_effort', 'grant', 'registration'):
            self.assertEqual(out['host_session'][key], 'NOT_INSPECTED')
        self.assertEqual(out['host_session']['delivery'], 'NOT_VERIFIED')
        self.assertEqual(out['host_session']['specialist_call'], 'NOT_OBSERVED')
        self.assertIn(self.session['evidence_ref'], out['context_refs'])
        self.assertEqual(out['task_fragment']['context_refs'], out['context_refs'])
        self.assertEqual(office_fixture.tree(self.root), before)

    def test_missing_native_capability_does_not_fall_back_to_code_exporter(self):
        spec = copy.deepcopy(self.session)
        spec['capabilities'] = ['compute']
        out = self.compose(spec)
        self.assertEqual(out['state'], 'NEEDS_CAPABILITY')
        self.assertIn('read_local', out['held'])
        self.assertIn('write_text', out['held'])
        caps = {c['capability']: c for c in out['capabilities']}
        self.assertEqual(caps['read_local']['exporter'], 'PRESENT')
        self.assertEqual(caps['read_local']['status'], 'NEEDS_CAPABILITY')

    def test_strict_fields_types_and_claims(self):
        variants = []
        for field in ('actual_model', 'verified', 'grants', 'registration', 'PASS'):
            spec = copy.deepcopy(self.session); spec[field] = True; variants.append(spec)
        for field, value in [('host', ''), ('tool_names', ['Bash', 'Bash']), ('tool_names', [[]]),
                             ('capabilities', ['shell']), ('capabilities', ['compute', 'compute']),
                             ('requested_effort', 3), ('evidence_ref', {'path': 'working/x', 'digest': 'sha256:no'})]:
            spec = copy.deepcopy(self.session); spec[field] = value; variants.append(spec)
        for spec in variants + [None, [], {}]:
            with self.subTest(spec=spec):
                req = office_fixture.request('data-analyst', resources_used=[], host_session=spec)
                self.assertEqual(office.compose(req, self.root)['outcome'], 'REFUSED')

    def test_missing_stale_unsafe_or_linked_evidence_refuses(self):
        for path in ['../outside', '.agent/EXECUTION_PROFILE.json', 'working/missing.txt']:
            spec = copy.deepcopy(self.session); spec['evidence_ref']['path'] = path
            self.assertEqual(self.compose(spec)['outcome'], 'REFUSED')
        self.note.write_bytes(b'changed after the brief was selected')
        self.assertIn('HOST_SESSION_EVIDENCE_CHANGED', self.compose()['problems'])
        self.note.write_bytes(b'restored but now held behind a simulated unsupported link')
        self.session['evidence_ref']['digest'] = office.sha_of(self.note.read_bytes())
        with mock.patch.object(office.transaction, 'link_free', return_value=False):
            self.assertIsNone(office._host_session(self.session, str(self.root))[0])

    def test_routes_are_explicit_and_legacy_default_is_unchanged(self):
        out = self.compose(compute_route={'probe': 'working/p.json', 'scope': 'working/s.json'})
        self.assertEqual(out['outcome'], 'REFUSED')
        req = office_fixture.request('data-analyst', resources_used=[])
        old = office.compose(req, self.root)
        self.assertNotIn('host_session', old)
        self.assertIn('compute', old['held'])
        self.assertIn('Bạn chỉ có Read/Grep/Glob/Write', old['brief'])

    def test_native_handover_does_not_invent_hash_tool_or_delivery_and_retains_checkpoint(self):
        for lang in ('vi', 'en'):
            brief = self.compose(lang=lang)['brief']
            self.assertNotIn('Bạn chỉ có Read/Grep/Glob/Write', brief)
            self.assertNotIn('Bạn không có công cụ băm', brief)
            self.assertNotIn('You only have Read/Grep/Glob/Write', brief)
            self.assertNotIn('You have no hashing tool', brief)
            for term in ('RESULT.json', 'TASK', 'binding', 'checkpoint', 'CANDIDATE', 'delivery=NOT_VERIFIED'):
                self.assertIn(term, brief)
        self.session['output_location'] = 'Windows project (declared only)'
        self.assertEqual(self.compose()['host_session']['delivery'], 'NOT_VERIFIED')

    def test_same_preparation_contract_for_other_hosts_without_assuming_support(self):
        for host in ('codex-desktop', 'antigravity'):
            self.session['host'] = host
            self.session['requested_model'] = None
            out = self.compose()
            self.assertEqual(out['state'], 'PREPARED')
            self.assertEqual(out['host_session']['actual_model'], 'NOT_INSPECTED')

    def test_office_formats_require_a_supporting_method_contract_and_declared_capability(self):
        for method in ('data-analyst', 'market-analyst', 'executive-secretary', 'correspondence',
                       'research-assistant', 'evidence-reviewer'):
            for fmt in ('docx', 'xlsx', 'pptx', 'pdf'):
                req = office_fixture.request(method, resources_used=[], host_session=self.session, output_format=fmt)
                out = office.compose(req, self.root)
                if method in ('data-analyst', 'market-analyst'):
                    self.assertEqual(out['outcome'], 'COMPOSED', out)
                    self.assertNotIn('office_files', out['held'])
                else:
                    self.assertEqual(out['outcome'], 'REFUSED', out)
                    self.assertIn('REQUEST_INVALID:host_session.OUTPUT_CONTRACT_UNSUPPORTED', out['problems'])
        spec = copy.deepcopy(self.session)
        spec['capabilities'].remove('office_files')
        self.assertIn('office_files', self.compose(spec, output_format='xlsx')['held'])

    def test_native_reviewer_requires_exact_candidate_path_and_digest(self):
        for lang in ('vi', 'en'):
            req = office_fixture.request('evidence-reviewer', resources_used=[], host_session=self.session, lang=lang)
            brief = office.compose(req, self.root)['brief']
            self.assertIn('candidate Main', brief)
            self.assertIn('digest', brief)
            self.assertIn('thiếu thì trả lại Main' if lang == 'vi' else 'if either is missing', brief)


@unittest.skipUnless(office_fixture.tf.CAN_RUN, office_fixture.tf.SKIP_RUN)
class NativeCheckpoint(office_fixture.tf.FlowBase):
    def setUp(self):
        super().setUp()
        for path in (ROOT / 'roles/office').iterdir():
            self.write(path.relative_to(ROOT).as_posix(), path.read_bytes())
        for rel in (office_fixture.SKILL_HTML, office_fixture.SKILL_MINUTES):
            self.write(rel, (ROOT / rel).read_bytes())

    def test_evidence_changed_after_compose_blocks_the_actual_checkpoint(self):
        note = 'working/host-note.txt'
        self.write(note, b'Main-declared native session; not runtime proof')
        session = {'host': 'cowork', 'agent_type': 'general-purpose', 'tool_names': ['Bash'],
                   'capabilities': ['read_local', 'search_local', 'write_text'],
                   'requested_model': None, 'requested_effort': None,
                   'execution_location': 'container', 'output_location': 'container',
                   'evidence_ref': {'path': note, 'digest': office.sha_of(self.read(note))}}
        task_rel, result_rel, _, _ = office_fixture.OfficeBinding.office_assignment(self, host_session=session)
        self.assertEqual(self.checkpoint(task_rel, result_rel)['problems'], [])
        self.write(note, b'changed after compose and after the bound RESULT')
        before = self.tree()
        self.assertIn('INPUT_CHANGED ' + note, self.checkpoint(task_rel, result_rel)['problems'])
        self.assertEqual(self.tree(), before, 'checkpoint must only read')


class ProfileDiagnostics(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='law-host-write-')
        self.addCleanup(self.temp.cleanup)
        self.root = profile_fixture.make_project(self.temp.name, line=ep.POINTERS['vi'],
                                                 profile=profile_fixture.profile_doc('PROFILE'))

    def test_delete_denial_explains_phase_without_changing_profile_or_old_probe(self):
        runtime = self.root / '.agent/runtime'; runtime.mkdir()
        old = runtime / '.probe-existing'; old.write_bytes(b'not this transaction')
        profile = self.root / ep.PROFILE_REL; before = profile.read_bytes()
        remove = os.remove
        def deny(path, *args, **kw):
            if Path(path).name.startswith('.probe-'):
                raise PermissionError(errno.EPERM, 'host deletion not allowed', str(path))
            return remove(path, *args, **kw)
        with mock.patch.object(tx.os, 'remove', side_effect=deny):
            result = ep.apply_config(str(self.root), {'host': 'cowork'})
        self.assertEqual((result['status'], result['reasons']), ('REFUSED', ['WRITE_REFUSED']))
        for term in ('WRITE_PROBE_FAILED', 'phase=remove', 'errno=1', '.agent/runtime/.probe-'):
            self.assertIn(term, result['detail'])
        self.assertEqual(profile.read_bytes(), before)
        self.assertEqual(old.read_bytes(), b'not this transaction')
        self.assertFalse((runtime / 'transactions').exists())

    def test_create_denial_has_a_different_phase(self):
        with mock.patch('builtins.open', side_effect=PermissionError(errno.EACCES, 'creation denied')):
            with self.assertRaises(OSError) as caught:
                tx.probe_writable(str(self.root))
        self.assertIn('phase=create', str(caught.exception))

    def test_cli_text_and_json_retain_detail_and_exit_in_both_locales(self):
        previous = ep.LANG
        self.addCleanup(setattr, ep, 'LANG', previous)
        for lang in ('vi', 'en'):
            ep.LANG = lang
            for detail in ('WRITE_PROBE_FAILED phase=remove errno=1', [{'path': '/roles/worker', 'rule': 'required'}]):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = ep._emit(ep._result('REFUSED', ['WRITE_REFUSED'], detail=detail),
                                    argparse.Namespace(result_json=True), 'test refusal')
                self.assertEqual(code, 1)
                self.assertIn('detail:', out.getvalue())
                self.assertIn('phase=remove' if isinstance(detail, str) else '/roles/worker', out.getvalue())

    def test_ordinary_profile_write_still_works_without_grant_or_native_registration(self):
        result = ep.apply_config(str(self.root), {'host': 'cowork'})
        self.assertEqual(result['status'], 'WRITTEN', result)
        doc = json.loads((self.root / ep.PROFILE_REL).read_bytes())
        self.assertEqual((doc['host'], doc['grants']), ('cowork', []))
        self.assertFalse((self.root / '.claude').exists())


if __name__ == '__main__':
    unittest.main()
