"""V6: reuse a method across independent projects/processes, never their authority.

Fake profiles are fixtures, not dispatch grants. These tests check isolation and
current-byte binding; they do not certify natural-language selection or usability.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import execution_profile as ep
import office
import test_execution_profile as profiles
import test_office as fixtures

SOURCE = 'references/source-documents/mail/current.md'
DECISIONS = 'working/reply/decisions.md'


class Reuse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='law-reuse-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.projects = []
        for name, model, recipient in [('A', 'choice-a', 'PRIVATE_A_RECIPIENT'),
                                       ('B', 'choice-b', 'MOCK_B_RECIPIENT')]:
            doc = profiles.profile_doc('PROFILE')
            doc['roles']['worker'].update(model=model, effort='medium')
            if name == 'A':
                doc['grants'] = [profiles.fake_grant()]
            root = profiles.make_project(self.base, name=name, profile=doc, line=ep.POINTERS['vi'])
            shutil.copytree(str(ROOT / 'roles/office'), str(root / 'roles/office'))
            for rel, body in [(SOURCE, 'To: %s\nXin xác nhận đã nhận hồ sơ.\n' % recipient),
                              (DECISIONS, 'Quyết định giả lập: giọng ngắn gọn; không hứa ngày trả lời.\n')]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(body, encoding='utf-8')
            (root / 'account-ref.txt').write_text('PRIVATE_%s_ACCOUNT' % name, encoding='utf-8')
            self.projects.append(root)
        self.A, self.B = self.projects
        self.req = {'method': 'correspondence', 'reason': 'Soạn nháp trả lời từ chuỗi thư được cấp.',
                    'request': 'Trả lời như lần trước: xác nhận nhận hồ sơ, giữ giọng ngắn gọn và không hứa ngày; To/Cc theo thư hiện hành.',
                    'sources': [{'path': SOURCE}, {'path': DECISIONS}], 'resources_used': []}

    def test_reusing_the_same_method_binds_each_projects_own_inputs_and_choices(self):
        before = [fixtures.tree(p) for p in self.projects]
        a, b = [office.compose(self.req, root=p) for p in self.projects]
        for out, model in [(a, 'choice-a'), (b, 'choice-b')]:
            self.assertEqual(out['state'], 'PREPARED', out)
            self.assertEqual(out['profile']['requested']['model'], model)
            self.assertFalse(out['claims']['invoked'])
            self.assertEqual(out['writes'], [])
            self.assertEqual(out['method']['method_version'], 1)
        self.assertEqual(a['context_refs'], b['context_refs'], 'same factory method, different project data')
        self.assertNotEqual(a['inputs_proposal'][0]['digest'], b['inputs_proposal'][0]['digest'])
        self.assertEqual(b['inputs_proposal'][0]['digest'], fixtures.sha((self.B / SOURCE).read_bytes()))
        self.assertEqual(ep.inspect(self.B)['grant_claims'], 0)
        text = json.dumps(b)
        for private in ['PRIVATE_A_RECIPIENT', 'PRIVATE_A_ACCOUNT', 'choice-a', 'fake-grant-1', str(self.A)]:
            self.assertNotIn(private, text)
        self.assertEqual([fixtures.tree(p) for p in self.projects], before)

    def test_a_fresh_process_reuses_current_decisions_and_bytes_without_regeneration(self):
        before = fixtures.tree(self.B)
        code = ('import json,sys; sys.path.insert(0,sys.argv[1]); import office; '
                'print(json.dumps(office.compose(json.load(sys.stdin),root=sys.argv[2]),ensure_ascii=True))')
        done = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(ROOT / 'tools'), str(self.B)],
                              cwd=str(self.A), input=json.dumps(self.req).encode('utf-8'), capture_output=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout)
        self.assertEqual(out, office.compose(self.req, root=self.B))
        self.assertEqual(out['inputs_proposal'][1]['digest'], fixtures.sha((self.B / DECISIONS).read_bytes()))
        self.assertEqual(out['profile']['requested']['model'], 'choice-b')
        self.assertEqual(fixtures.tree(self.B), before)

    def test_reuse_rereads_changed_sources_and_never_falls_back_to_project_a(self):
        old = office.compose(self.req, root=self.B)
        (self.B / SOURCE).write_text('To: MOCK_B_NEW\nNội dung thay đổi.\n', encoding='utf-8')
        current = office.compose(self.req, root=self.B)
        self.assertNotEqual(old['inputs_proposal'][0]['digest'], current['inputs_proposal'][0]['digest'])
        (self.B / SOURCE).unlink()
        before = fixtures.tree(self.B)
        missing = office.compose(self.req, root=self.B)
        self.assertEqual(missing['state'], 'NEEDS_INPUT', missing)
        self.assertTrue(missing['missing'])
        self.assertNotIn(SOURCE, [x['path'] for x in missing['inputs_proposal']])
        self.assertTrue((self.A / SOURCE).exists())
        self.assertEqual(fixtures.tree(self.B), before)


if __name__ == '__main__':
    unittest.main()
