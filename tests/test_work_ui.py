"""Focused browser coverage for the read-only Work page."""
import json
import unittest
from urllib.parse import urlparse

try:
    from . import test_ui_browser as panel_tests
except ImportError:
    import test_ui_browser as panel_tests


FIXTURE = {
    'result': 'READY',
    'work_id': 'work-demo',
    'state_digest': 'sha256:' + 'a' * 64,
    'tasks': [{
        'task_path': 'working/work-demo/task-1/TASK.json',
        'task_id': 'task-1',
        'task_revision': 2,
        'actor': 'worker',
        'method': 'correspondence',
        'intent': '</dd><img src=x onerror="window.__workInjected=true">',
        'requirements': [{'req_id': 'OFFICE-METHOD:correspondence:v1', 'status': 'UNKNOWN'}],
        'problems': ['Needs content review'],
        'assignments': [{
            'result_path': 'working/work-demo/task-1/assignments/a1/RESULT.json',
            'state': 'MATCHED',
            'problems': [],
            'candidate': {'path': 'working/work-demo/task-1/assignments/a1/candidate/reply.md',
                          'digest': 'sha256:' + 'b' * 64},
            'declared_states': ['CANDIDATE'],
            'gaps': ['Reviewer decision is pending'],
        }],
    }],
    'decisions': ['Keep the current subject line'],
    'waiting': ['Reviewer decision is pending'],
    'permission': {
        'roles': {'worker': {'permission': 'UNKNOWN', 'applied': 'NOT_INSPECTED', 'registration': 'UNKNOWN'}},
        'state': 'CLAIMS_UNVERIFIED',
        'problem': 'TRANSACTIONS_AND_HOST_NOT_INSPECTED',
    },
    'host_stop': 'UNCONFIRMED',
    'writes': [],
    'scan': False,
    'ai_calls': False,
    'reopen_prompt': 'Ask Main to reopen work-demo at task-1 revision 2.',
    'stop_prompt': 'Ask Main to stop work-demo; host stop is unconfirmed.',
    'limits': ['A matching binding is not content acceptance.'],
}


@unittest.skipUnless(panel_tests.HAVE_BROWSER, panel_tests.SKIP_REASON or 'Playwright and Chromium are required')
class WorkPage(panel_tests.BrowserCase):
    def open_work(self):
        self.panel.start()
        self.page = self.context.new_page()
        self.page.on('pageerror', lambda exc: self.errors.append('pageerror: %s' % exc))
        self.page.on('console', self._console)
        self.api_requests = []

        def api_route(route):
            request = route.request
            path = urlparse(request.url).path
            self.api_requests.append((request.method, path))
            if path == '/api/work/status':
                route.fulfill(status=200, content_type='application/json', body=json.dumps(FIXTURE))
            else:
                route.fulfill(status=418, content_type='application/json', body='{}')

        self.page.route('**/api/**', api_route)
        self.page.add_init_script("""
          window.__workCopied = [];
          Object.defineProperty(navigator, 'clipboard', {configurable:true,
            value:{writeText:function(value){window.__workCopied.push(String(value));return Promise.resolve();}}});
        """)
        self.page.goto(self.panel.url + '&view=work')
        self.page.wait_for_function("document.querySelector('#work-box #work-result-note') !== null")
        return self.page

    def test_direct_work_view_reads_only_work_status_and_escapes_records(self):
        page = self.open_work()
        self.assertEqual(set(path for _, path in self.api_requests), {'/api/work/status'})
        self.assertTrue(all(method == 'POST' for method, _ in self.api_requests))
        self.assertEqual(page.locator('#work-box img').count(), 0)
        self.assertFalse(page.evaluate('window.__workInjected === true'))
        panel_tests.expect(page.locator('#work-box')).to_contain_text('CANDIDATE')
        panel_tests.expect(page.locator('#work-box')).to_contain_text('Chưa kiểm tra')
        panel_tests.expect(page.locator('#work-box')).to_contain_text('Chỉ có khai báo, chưa xác minh quyền')
        panel_tests.expect(page.locator('#work-box')).to_contain_text('Chưa xác nhận host đã dừng')
        panel_tests.expect(page.locator('#work-box')).to_contain_text('Keep the current subject line')

        before = len(self.api_requests)
        page.click('#work-refresh')
        page.wait_for_function('window.__workCopied.length === 0')
        self.assertEqual(len(self.api_requests), before + 1)
        self.assertEqual(set(path for _, path in self.api_requests), {'/api/work/status'})

    def test_continue_and_stop_buttons_only_copy_main_requests(self):
        page = self.open_work()
        before = list(self.api_requests)
        storage_before = page.evaluate('JSON.stringify(Object.assign({}, localStorage))')

        page.click('[data-work-copy="resume"]')
        page.wait_for_function('window.__workCopied.length === 1')
        self.assertIn('Ask Main to reopen', page.evaluate('window.__workCopied[0]'))
        panel_tests.expect(page.locator('#toast')).to_contain_text('Chưa gửi cho Main')

        page.click('[data-work-copy="stop"]')
        page.wait_for_function('window.__workCopied.length === 2')
        self.assertIn('host stop is unconfirmed', page.evaluate('window.__workCopied[1]'))
        self.assertEqual(self.api_requests, before, 'copying a prompt must not call an API')
        self.assertEqual(page.evaluate('JSON.stringify(Object.assign({}, localStorage))'), storage_before)


if __name__ == '__main__':
    unittest.main()
