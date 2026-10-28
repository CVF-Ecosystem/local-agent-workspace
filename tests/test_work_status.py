"""V5 exact-reference, readonly view; actual owners on isolated DATAMOCK fixtures."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import traceback
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import work_status as ws
import task_checkpoint as tc
import execution_profile as ep
import test_task_result_flow as tf
import test_execution_profile as pf


class WorkStatus(tf.FlowBase):
    def set_marker(self, task_rel, results):
        doc = {'work_id': tf.WORK, 'tasks': [{'task': task_rel, 'results': results}]}
        text = tf.STATE_FRAME + '<!-- law-work/1 ' + json.dumps(doc) + ' -->\n'
        self.write('.agent/STATE.md', text.encode())

    def ready(self):
        t, r, task = self.assignment()
        self.set_marker(t, [r])
        return t, r, task

    def assignment_view(self):
        return ws.status(self.project)['tasks'][0]['assignments'][0]

    def test_matching_result_is_not_accepted_running_or_stopped(self):
        self.ready()
        before = self.tree()
        view = ws.status(self.project)
        self.assertEqual(view['result'], 'READY', view)
        self.assertEqual(view['tasks'][0]['assignments'][0]['state'], 'MATCHED')
        self.assertEqual(view['tasks'][0]['assignments'][0]['declared_states'], ['CANDIDATE'])
        self.assertEqual(view['host_stop'], 'UNCONFIRMED')
        self.assertEqual(view['writes'], [])
        self.assertEqual(self.tree(), before)
        self.assertIn('Yêu cầu dừng chưa chứng minh host đã dừng', view['stop_prompt'])

    def test_late_result_after_revision_bump_stays_stale_and_immutable(self):
        t, r, task = self.ready()
        old = self.read(r)
        self.put_task(self.task_record('t-a', 2, 'a2'))
        before = self.tree()
        view = self.assignment_view()
        self.assertEqual(view['state'], 'STALE')
        self.assertEqual(ws.status(self.project)['result'], 'HELD')
        self.assertTrue(any('BINDING B-TASK' in p for p in view['problems']))
        self.assertEqual(self.read(r), old)
        self.assertEqual(self.tree(), before)

    def test_changed_source_bytes_and_ledger_revision_are_rechecked(self):
        self.ready()
        self.write(tf.SOURCE_REL, b'changed source\n')
        self.assertIn('INPUT_CHANGED ' + tf.SOURCE_REL, self.assignment_view()['problems'])
        self.write(tf.SOURCE_REL, self.source0)
        # Real catalog revision changes while source bytes remain identical.
        self.edit_ledger(lambda sh: setattr(sh.cell(5, 22), 'value', 2))
        view = self.assignment_view()
        self.assertEqual(view['state'], 'STALE')
        self.assertIn('LEDGER_METADATA_CHANGED SRC-000001', view['problems'])
        self.assertEqual(self.read(tf.SOURCE_REL), self.source0)

    def test_missing_result_is_not_running(self):
        t, r, task = self.ready()
        os.remove(self.abs(r))
        view = self.assignment_view()
        self.assertEqual(view['state'], 'MISSING')
        self.assertEqual(ws.status(self.project)['result'], 'HELD')
        self.assertNotIn('RUNNING', json.dumps(view))
        self.assertEqual(ws.status(self.project)['host_stop'], 'UNCONFIRMED')

    def test_marker_missing_duplicate_and_traversal_never_discover(self):
        self.ready()
        state = self.read('.agent/STATE.md')
        for data, expected in [(tf.STATE_FRAME.encode(), 'NO_WORK'),
                               (state + state, 'HELD'),
                               (state.replace(b'working/', b'../working/'), 'HELD')]:
            self.write('.agent/STATE.md', data)
            with mock.patch.object(ws.tc, 'load_v3', side_effect=AssertionError('must not load tasks')):
                self.assertEqual(ws.status(self.project)['result'], expected)

    def test_unknown_result_cannot_read_another_tasks_candidate(self):
        t, r, task = self.ready()
        result = json.loads(self.read(r))
        result['artifacts'][0]['path'] = 'working/other/secret.txt'
        result['binding']['outputs'][0]['path'] = 'working/other/secret.txt'
        self.write(r, json.dumps(result).encode())
        with mock.patch.object(tc, 'read_file', wraps=tc.read_file) as read:
            view = ws.status(self.project)
        self.assertEqual(view['tasks'][0]['assignments'][0]['state'], 'STALE')
        self.assertNotIn('working/other/secret.txt', [call.args[1] for call in read.call_args_list])

    def test_large_input_uses_scoped_digest_snapshot_and_detects_drift(self):
        path, data = 'references/large.bin', b'\x00\xff' * (1024 * 1024 + 123)
        self.write(path, data)
        t, r, _ = self.assignment(inputs=[{'path': path, 'digest': tc.sha(data)}])
        # Two tasks reuse one named input snapshot during a view.
        t2, r2, _ = self.assignment(task_id='t-b', inputs=[{'path': path, 'digest': tc.sha(data)}])
        marker = {'work_id': tf.WORK, 'tasks': [{'task': t, 'results': [r]}, {'task': t2, 'results': [r2]}]}
        self.write('.agent/STATE.md', (tf.STATE_FRAME + '<!-- law-work/1 ' + json.dumps(marker) + ' -->\n').encode())
        before = self.tree()
        real_checkpoint = tc.checkpoint
        def checked(*args, **kwargs):
            self.assertEqual(kwargs['digest_reader'](self.project, 'working/secret.bin'),
                             (None, 0, 'READ_SCOPE_UNSUPPORTED'))
            return real_checkpoint(*args, **kwargs)
        with mock.patch.object(tc, 'file_digest', wraps=tc.file_digest) as digest, \
             mock.patch.object(tc, 'checkpoint', side_effect=checked):
            view = ws.status(self.project)
        self.assertEqual(view['result'], 'READY', view)
        self.assertEqual([c.args[1] for c in digest.call_args_list], [path])
        self.assertEqual(self.tree(), before)
        self.write(path, data[:-1] + b'x')
        self.assertIn('INPUT_CHANGED ' + path, self.assignment_view()['problems'])

    def test_streamed_inputs_keep_view_budget(self):
        path, data = 'references/large.bin', b'x' * (16 * 1024 * 1024 + 1)
        self.write(path, data)
        t, r, _ = self.assignment(inputs=[{'path': path, 'digest': tc.sha(data)}])
        self.set_marker(t, [r])
        view = self.assignment_view()
        self.assertEqual(view['state'], 'STALE')
        self.assertIn('INPUT ' + path + ' VIEW_READ_BUDGET_EXCEEDED', view['problems'])

    def test_view_no_scan_writer_or_process_call(self):
        self.ready()
        os.makedirs(self.abs('.agent/runtime/transactions'), exist_ok=True)
        ws.status(self.project)  # preload schema dependency metadata outside the scan assertion
        before = self.tree()
        real_load_v3 = tc.load_v3
        load_tracebacks = []

        def traced_load_v3(*args, **kwargs):
            try:
                return real_load_v3(*args, **kwargs)
            except Exception:
                load_tracebacks.append(traceback.format_exc())
                raise

        with mock.patch.object(tc, 'load_v3', side_effect=traced_load_v3), \
             mock.patch('os.walk', side_effect=AssertionError('scan')), \
             mock.patch('os.listdir', side_effect=AssertionError('scan')), \
             mock.patch('os.scandir', side_effect=AssertionError('scan')), \
             mock.patch('subprocess.run', side_effect=AssertionError('process')):
            view = ws.status(self.project)
        self.assertEqual(view['result'], 'READY', (view, load_tracebacks))
        self.assertEqual(self.tree(), before)

    def test_current_permission_reduction_never_promotes_or_changes_draft(self):
        self.ready()
        self.write('PROJECT.md', pf.project_text(ep.POINTERS['vi']).encode('utf-8'))
        profile = ep.default_profile('PROFILE')
        profile['grants'] = [pf.fake_grant()]
        self.write(ep.PROFILE_REL, json.dumps(profile).encode())
        first = ws.status(self.project)
        self.assertEqual(first['permission']['state'], 'CLAIMS_UNVERIFIED')
        self.assertEqual(first['permission']['roles']['worker']['permission'], 'GRANT_CLAIMED', first)
        profile['grants'] = []
        self.write(ep.PROFILE_REL, json.dumps(profile).encode())
        before = self.tree()
        second = ws.status(self.project)
        self.assertEqual(second['permission']['roles']['worker']['permission'], 'NO_GRANT')
        self.assertEqual(second['permission']['grant_claim_count'], 0)
        self.assertNotEqual(first['permission']['profile_digest'], second['permission']['profile_digest'])
        self.assertEqual(second['host_stop'], 'UNCONFIRMED')
        self.assertEqual(self.tree(), before)

    def test_fresh_process_reopens_exact_refs_without_writes(self):
        self.ready()
        before = self.tree()
        completed = subprocess.run([sys.executable, '-I', '-B', str(ROOT / 'tools/work_status.py'), '--project', self.project],
                                   capture_output=True, encoding='utf-8', timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        view = json.loads(completed.stdout)
        self.assertEqual(view['tasks'][0]['task_revision'], 1, view)
        self.assertEqual(view['tasks'][0]['assignments'][0]['state'], 'MATCHED')
        self.assertEqual(self.tree(), before)

    def test_real_browser_api_reopens_and_shows_source_drift_without_mutation(self):
        import test_ui_browser as ui
        if not ui.HAVE_BROWSER:
            self.skipTest(ui.SKIP_REASON)
        import app
        self.ready()
        before = self.tree()
        with mock.patch.object(app, 'ROOT', self.project), mock.patch.object(app, 'STATE', dict(app.STATE)):
            server = app.Server(('127.0.0.1', 0), app.Handler)
            app.STATE['port'] = server.server_address[1]
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                with ui.sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True)
                    try:
                        page = browser.new_page()
                        errors, requests = [], []
                        page.on('pageerror', lambda e: errors.append(str(e)))
                        page.on('request', lambda req: requests.append(req.url) if '/api/' in req.url else None)
                        page.goto('http://127.0.0.1:%d/?t=%s&view=work' % (app.STATE['port'], app.TOKEN))
                        ui.expect(page.locator('#work-box')).to_contain_text('CANDIDATE')
                        self.assertEqual(self.tree(), before, 'real page and API are read only')
                        self.write(tf.SOURCE_REL, b'changed input after first view\n')
                        after_change = self.tree()
                        page.click('#work-refresh')
                        ui.expect(page.locator('#work-box')).to_contain_text('INPUT_CHANGED')
                        self.assertEqual(self.tree(), after_change)
                        self.assertFalse(errors, errors)
                        self.assertTrue(requests)
                        self.assertTrue(all('/api/work/status' in url for url in requests), requests)
                    finally:
                        browser.close()
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=5)


class WorkAPI(unittest.TestCase):
    def test_route_is_dedicated_and_bad_body_does_not_reach_owner(self):
        import app
        with mock.patch.object(ws, 'status', return_value={'result': 'NO_WORK', 'writes': []}) as read:
            self.assertEqual(app.work_api({})['result'], 'NO_WORK')
            self.assertEqual(app.work_api({'path': '../../secret'})['result'], 'ERROR')
        read.assert_called_once_with(app.ROOT)

    def test_checker_cannot_load_from_data_project(self):
        with self.assertRaises(RuntimeError):
            tc.load_v3(ROOT / 'working')


if __name__ == '__main__':
    unittest.main()
