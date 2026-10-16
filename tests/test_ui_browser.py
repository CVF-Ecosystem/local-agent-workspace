"""Browser tests for the panel's main flows, plus keyboard, focus, live-region and layout checks.

Needs the Python package `playwright` and a Chromium that it can launch. Without them the whole module is skipped
(CI does not install them; that is expected and the other test modules still run there).
Local setup: python -m pip install playwright && python -m playwright install chromium

Each test copies the package to a temporary folder, runs tools/app.py from that copy on a free port, drives headless
Chromium and stops the server through /api/quit. The real repository is never written. One browser is shared by the
tests of a class; every test gets its own server and browser context.

The panel serves no favicon, so the favicon 404 that Chromium requests is ignored. Every other JavaScript error or
console error fails the test.
"""
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAULT = 'LOCAL_AGENT_WORKSPACE_TEST_FAULT'
PKG_IGNORE = shutil.ignore_patterns('.git', '__pycache__', 'dist', 'roadmap', 'tests', 'feedback')
URL_RE = re.compile(r'http://127\.0\.0\.1:(\d+)/\?t=([A-Za-z0-9_\-]+)')

try:
    from playwright.sync_api import expect, sync_playwright
except ImportError:  # playwright is not installed: every browser class below is skipped
    expect = sync_playwright = None


def _probe_browser():
    if sync_playwright is None:
        return False, 'playwright is not installed'
    try:
        with sync_playwright() as p:
            p.chromium.launch(headless=True).close()
        return True, ''
    except Exception as e:  # Chromium missing or not runnable on this machine
        return False, 'Chromium cannot launch here (%s)' % type(e).__name__


HAVE_BROWSER, SKIP_REASON = _probe_browser()


def copy_package(dst, src=ROOT):
    """Temporary copy of a package; runtime data is never copied."""
    shutil.copytree(str(src), str(dst), ignore=PKG_IGNORE)
    shutil.rmtree(str(dst / '.agent' / 'runtime'), ignore_errors=True)
    return dst


def run_tool(pkg, script, *args, env=None):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    e.pop(FAULT, None)
    e.update(env or {})
    return subprocess.run([sys.executable, '-B', str(pkg / 'tools' / script)] + [str(a) for a in args],
                          cwd=str(pkg), env=e, capture_output=True, timeout=300)


def init_project(pkg):
    r = run_tool(pkg, 'init_project.py', '--name', 'Test', '--lang', 'vi')
    assert r.returncode == 0, r.stdout + r.stderr


def make_version(base, name, extra, src=ROOT):
    """A package version whose .agent/README.md has one more line; its MANIFEST is written by the package tool."""
    dst = copy_package(base / name, src)
    readme = dst / '.agent' / 'README.md'
    readme.write_text(readme.read_text(encoding='utf-8') + extra, encoding='utf-8')
    r = run_tool(dst, 'check_package.py', '--write-manifest')
    assert r.returncode == 0, r.stdout + r.stderr
    return dst


def interrupted_upgrade(pkg, new):
    """An upgrade into pkg that stops after its first committed write (test-only fault variable)."""
    r = run_tool(pkg, 'upgrade_package.py', '--project', pkg, '--from', new, '--apply', env={FAULT: 'commit:1'})
    assert r.returncode == 1, r.stdout + r.stderr
    assert has_unfinished(pkg), 'the interrupted upgrade left no unfinished transaction'


def has_unfinished(pkg):
    return run_tool(pkg, 'transaction.py', 'status', '--project', pkg).returncode == 1


class Panel(object):
    """tools/app.py started from a package copy on a free port; stopped through /api/quit."""

    def __init__(self, pkg, log_dir):
        self.pkg, self.log_dir, self.env = pkg, log_dir, {}
        self.proc = self.url = self.base = self.token = None

    def start(self):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        log = os.path.join(self.log_dir, 'panel-%d.log' % port)
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        env.pop(FAULT, None)
        env.update(self.env)
        with open(log, 'wb') as out:
            self.proc = subprocess.Popen([sys.executable, '-B', 'tools/app.py', '--no-browser', '--port', str(port)],
                                         cwd=str(self.pkg), env=env, stdout=out, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL)
        text, deadline = '', time.time() + 30
        while time.time() < deadline:
            with open(log, 'rb') as src:
                text = src.read().decode('utf-8', 'replace')
            m = URL_RE.search(text)
            if m:
                self.base = 'http://127.0.0.1:%s' % m.group(1)
                self.token = m.group(2)
                self.url = m.group(0)
                return self.url
            if self.proc.poll() is not None:
                break
            time.sleep(0.1)
        self.stop()
        raise AssertionError('the panel did not print its address: ' + text)

    def stop(self):
        if self.proc is None:
            return
        try:
            req = urllib.request.Request(self.base + '/api/quit', data=b'{}', method='POST',
                                         headers={'Content-Type': 'application/json', 'X-Panel-Token': self.token})
            urllib.request.urlopen(req, timeout=10).read()
        except OSError:
            pass
        try:
            self.proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)
        self.proc = None


@unittest.skipUnless(HAVE_BROWSER, SKIP_REASON or 'browser tests need playwright and Chromium')
class BrowserCase(unittest.TestCase):
    """One Chromium per class; each test has its own package copy, server and browser context."""

    @classmethod
    def setUpClass(cls):
        cls._pw = sync_playwright().start()
        cls.browser = cls._pw.chromium.launch(headless=True)
        expect.set_options(timeout=20000)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls._pw.stop()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ui-browser-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.pkg = copy_package(self.base / 'package')
        self.panel = Panel(self.pkg, self.tmp.name)
        self.addCleanup(self.panel.stop)
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        self.addCleanup(self.context.close)
        self.errors = []
        self.page = None

    def tearDown(self):
        self.assertEqual(self.errors, [], 'JavaScript errors in the panel page')

    def _console(self, msg):
        url = (msg.location or {}).get('url', '')
        if msg.type == 'error' and not url.endswith('/favicon.ico'):
            self.errors.append('console: %s' % msg.text)

    def open_panel(self, width=1280, height=900):
        self.panel.start()
        self.page = self.context.new_page()
        self.page.set_viewport_size({'width': width, 'height': height})
        self.page.on('pageerror', lambda exc: self.errors.append('pageerror: %s' % exc))
        self.page.on('console', self._console)
        self.page.goto(self.panel.url)
        self.page.wait_for_function("document.getElementById('sb-st').textContent.length > 0")
        return self.page

    def close_sheet(self):
        self.page.click('#sh-x')
        expect(self.page.locator('#sheet')).not_to_have_class(re.compile(r'\bon\b'))

    def go(self, page_id):
        # các trang quản lý nằm trong nhóm thu gọn: mở nhóm nếu cần / management pages sit in a collapsed group: open it if needed
        if not self.page.is_visible('.nav [data-page="%s"]' % page_id) and self.page.is_visible('#nav-more'):
            self.page.click('#nav-more')
        self.page.click('.nav [data-page="%s"]' % page_id)


@unittest.skipUnless(HAVE_BROWSER, SKIP_REASON or 'browser tests need playwright and Chromium')
class MainFlows(BrowserCase):
    """The five main flows of Stage 12: set up, check, upgrade with a conflict, missing dependency, interrupted work."""

    def test_init_preview_apply_then_overview_shows_project(self):
        p = self.open_panel()
        expect(p.locator('#home-tpl')).to_be_visible()  # bộ mẫu: trang chính là tạo project mới / template: home is "new project"
        self.go('setup')  # khởi tạo tại chỗ vẫn có, trong nhóm quản lý / in-place setup still exists, in the management group
        p.fill('#f-name', 'Test UI')
        p.click('#su-run')
        expect(p.locator('#sh-tag')).to_contain_text('Đã xem trước')
        expect(p.locator('#sh-apply')).to_be_visible()
        self.assertFalse((self.pkg / '.agent' / 'PACKAGE_INFO.json').exists(), 'preview must write nothing')
        p.click('#sh-apply')
        expect(p.locator('#sh-msg')).to_contain_text('Đã ghi')
        self.close_sheet()
        self.go('home')
        expect(p.locator('#ov-name')).to_have_text('Test UI')
        expect(p.locator('#home-tpl')).to_be_hidden()
        self.assertTrue((self.pkg / '.agent' / 'PACKAGE_INFO.json').exists())

    def test_template_home_creates_a_separate_project_and_keeps_the_template(self):
        before = {rel: (self.pkg / rel).read_bytes() for rel in ('PROJECT.md', '.agent/STATE.md', 'AGENTS.md')}
        p = self.open_panel()
        expect(p.locator('#np-run')).to_be_visible()
        expect(p.locator('#nav2')).to_be_hidden()  # quản lý thu gọn / management collapsed
        p.fill('#np-name', 'Biên bản họp')
        expect(p.locator('#np-where')).to_contain_text('Biên bản họp')
        p.click('#np-run')
        expect(p.locator('#sh-tag')).to_contain_text('Đã xem trước')
        target = self.base / 'Biên bản họp'
        self.assertFalse(target.exists(), 'preview must write nothing')
        p.click('#sh-apply')
        expect(p.locator('#sh-tag')).to_contain_text('Thành công')
        self.close_sheet()
        expect(p.locator('#np-done')).to_contain_text(str(target))
        expect(p.locator('#np-done [data-po="panel"]')).to_be_visible()
        self.assertTrue((target / '.agent' / 'PACKAGE_INFO.json').is_file())
        self.assertFalse((self.pkg / '.agent' / 'PACKAGE_INFO.json').exists(), 'the template is not set up')
        self.assertEqual({rel: (self.pkg / rel).read_bytes() for rel in before}, before)
        p.fill('#np-name', 'Biên bản họp')  # trùng tên: bị chặn / same name: blocked
        p.click('#np-run')
        expect(p.locator('#sh-tag')).to_contain_text('Chưa thể thực hiện')
        self.close_sheet()

    def test_project_home_shows_the_work_sources_results_and_an_opening_message(self):
        init_project(self.pkg)
        (self.pkg / 'references' / 'source-documents' / 'ghi-chu.txt').write_text('ghi chú', encoding='utf-8')
        (self.pkg / 'output' / 'bien-ban.md').write_text('# Biên bản', encoding='utf-8')
        p = self.open_panel()
        expect(p.locator('#home-prj')).to_be_visible()
        expect(p.locator('#src-list')).to_contain_text('ghi-chu.txt')
        expect(p.locator('#out-list')).to_contain_text('bien-ban.md')
        expect(p.locator('#ag-prompt')).to_contain_text('«Test»')
        expect(p.locator('#st-box')).to_contain_text('Chưa có tiến độ được lưu')  # chưa có tiến độ thật thì nói rõ / no fake progress
        p.click('#ag-mode button[data-v="cont"]')
        expect(p.locator('#ag-prompt')).to_contain_text('Tiếp tục công việc')
        expect(p.locator('#ag-mode-h')).to_contain_text('chưa sửa file nào')  # chế độ xem lại chỉ tóm tắt / review mode only summarises
        expect(p.locator('#nav2')).to_be_hidden()
        p.click('#nav-more')
        expect(p.locator('#nav2 [data-page="packs"]')).to_be_visible()
        self.assertEqual(p.get_attribute('#nav-more', 'aria-expanded'), 'true')

    def test_install_skills_copies_only_the_chosen_accepted_skills(self):
        init_project(self.pkg)
        r = run_tool(self.pkg, 'pack.py', 'add', 'cang-logistics')  # gói chưa tiếp nhận: REVIEW / not through intake
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dest = self.base / 'app-skills'
        p = self.open_panel()
        self.go('packs')
        expect(p.locator('.pack .pk-intake').first).to_contain_text('Thử nghiệm')
        self.go('skills')
        p.click('label.opt:has(input[value="custom"])')
        p.fill('#sk-dest', str(dest))
        expect(p.locator('[data-sk="port-operations-reports"]')).to_be_disabled()
        p.click('#sk-run')  # chưa chọn gì: không chạy / nothing chosen: nothing runs
        expect(p.locator('#sheet')).not_to_have_class(re.compile(r'\bon\b'))
        p.check('[data-sk="meeting-minutes"]')
        p.click('#sk-run')
        expect(p.locator('#sh-tag')).to_contain_text('Đã xem trước')
        self.assertFalse(dest.exists(), 'preview must write nothing')
        p.click('#sh-apply')
        deadline = time.time() + 20
        while time.time() < deadline and not (dest / 'meeting-minutes' / 'SKILL.md').exists():
            time.sleep(0.2)
        self.assertEqual(sorted(x.name for x in dest.iterdir()), ['meeting-minutes'])
        self.close_sheet()

    def test_install_and_accept_a_pack_takes_one_click_and_one_dialog(self):
        import json
        init_project(self.pkg)
        pj = self.pkg / 'packs' / 'cang-logistics' / 'pack.json'
        meta = json.loads(pj.read_text(encoding='utf-8'))
        meta['intake'] = {'decision': 'ADD_MISSING_PART', 'version': meta['version'], 'relation': 'SUPPLEMENT',
                          'record': 'references/intake-record.md'}
        pj.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
        p = self.open_panel()
        dialogs = []
        p.on('dialog', lambda d: (dialogs.append(d.message), d.accept()))
        self.go('packs')
        card = p.locator('.pack', has_text='port-operations-reports')
        expect(card.locator('[data-pk="addconfirm"]')).to_be_visible()
        expect(card.locator('[data-pk="add"]')).to_be_visible()  # cài để thử vẫn còn / trial install stays
        card.locator('[data-pk="addconfirm"]').click()
        expect(p.locator('#sh-tag')).to_contain_text('Thành công')
        self.assertEqual(len(dialogs), 1, 'exactly one dialog')
        index = (self.pkg / '.agent' / 'SKILL_INDEX.md').read_text(encoding='utf-8')
        self.assertIn('| port-operations-reports | LOCAL | PACK |', index)
        row = [l for l in index.splitlines() if l.startswith('| port-operations-reports |')][0]
        self.assertEqual(row.split('|')[6].strip(), 'AVAILABLE')
        self.close_sheet()

    def test_check_flags_placeholder_and_reports_unsupported_as_not_checked(self):
        init_project(self.pkg)
        txt = self.pkg / 'output' / 'thu-dung-thu.txt'
        txt.write_text('Kính gửi [Tên khách hàng],\nSố tiền: 1.000.000 đ.\n', encoding='utf-8')
        pdf = self.pkg / 'output' / 'anh-minh-hoa.pdf'
        pdf.write_bytes(b'%PDF-1.4 synthetic test file, not a real document\n')
        p = self.open_panel()
        self.go('check')
        p.fill('#ck-path', str(txt))
        p.click('#ck-add')
        p.click('#ck-run')
        expect(p.locator('#sh-tag')).to_contain_text('Cần xem xét')
        expect(p.locator('#sh-out')).to_contain_text('Tên khách hàng')
        # có phát hiện là kiểm xong, không phải công cụ lỗi (D1) / findings mean the check finished, not a tool failure (D1)
        expect(p.locator('#sh-msg')).to_contain_text('Không file nào bị sửa')
        expect(p.locator('#sh-msg')).not_to_contain_text('Công cụ không hoàn tất')
        self.close_sheet()
        p.reload()  # the file list lives in the page only
        p.fill('#ck-path', str(pdf))
        p.click('#ck-add')
        p.click('#ck-run')
        expect(p.locator('#sh-tag')).to_contain_text('Chưa kiểm được')
        self.close_sheet()

    def test_upgrade_conflict_lists_merge_compares_and_keeps_states_after_reload(self):
        init_project(self.pkg)
        readme = self.pkg / '.agent' / 'README.md'
        user_text = readme.read_text(encoding='utf-8') + 'Ghi chú của tôi trong project.\n'
        readme.write_text(user_text, encoding='utf-8')
        new = make_version(self.base, 'new', 'Dòng mới từ gói phát hành.\n')
        p = self.open_panel()
        self.go('upgrade')
        p.fill('#u-dir', str(new))
        p.click('#u-run')
        expect(p.locator('#sh-apply')).to_be_visible()
        p.click('#sh-apply')
        expect(p.locator('#sh-tag')).to_contain_text('hợp nhất')
        self.close_sheet()
        self.assertEqual(readme.read_text(encoding='utf-8'), user_text, 'the user file must be kept')
        self.assertTrue((self.pkg / '.agent' / 'README.md.new').exists())
        self.go('merges')
        rows = p.locator('#mg-rows tr')
        expect(rows).to_have_count(1)
        expect(rows.first).to_contain_text('.agent/README.md.new')
        state = rows.first.locator('td').nth(2)
        expect(state).to_contain_text('Chưa xem')
        p.click('#mg-rows [data-md="0"]')
        expect(p.locator('#sh-diff .dr.add').first).to_contain_text('Dòng mới')
        expect(p.locator('#sh-diff .dr.del').first).to_contain_text('Ghi chú của tôi')
        self.close_sheet()
        p.click('#mg-rows [data-ms="reviewing"]')
        expect(state).to_contain_text('Đang xem')
        p.click('#mg-rows [data-ms="ready"]')
        expect(state).to_contain_text('Đã xem, chờ xử lý')
        p.reload()
        expect(p.locator('#mg-rows tr').first.locator('td').nth(2)).to_contain_text('Đã xem, chờ xử lý')

    def test_missing_openpyxl_is_shown_as_not_usable_with_pip_command(self):
        init_project(self.pkg)
        block = self.base / 'no-openpyxl'
        block.mkdir()
        (block / 'sitecustomize.py').write_text(
            "import sys\nsys.modules['openpyxl'] = None  # test only: openpyxl is treated as not installed\n",
            encoding='utf-8')
        existing = os.environ.get('PYTHONPATH')
        self.panel.env['PYTHONPATH'] = os.pathsep.join(x for x in (str(block), existing) if x)
        p = self.open_panel()
        self.go('health')
        rows = p.locator('#hl-comp .hrow')
        library = rows.filter(has_text='Thư viện nguồn')
        expect(library.locator('.tag')).to_contain_text('Chưa dùng được')
        expect(library).to_contain_text('python -m pip install openpyxl')
        expect(rows.filter(has_text='Kiểm tra file .xlsx').locator('.tag')).to_contain_text('Chưa dùng được')
        expect(rows.filter(has_text='Python 3.8').locator('.tag')).to_contain_text('Dùng được')

    def test_unfinished_transaction_resume_then_rollback_with_confirm(self):
        init_project(self.pkg)
        new1 = make_version(self.base, 'new1', 'Dòng 1 từ gói.\n')
        interrupted_upgrade(self.pkg, new1)
        p = self.open_panel()
        expect(p.locator('#bn-tx')).to_be_visible()
        p.click('#bn-tx [data-goto="health"]')
        p.click('#hl-tx [data-txa="resume"]')
        expect(p.locator('#sh-tag')).to_contain_text('Thành công')
        self.close_sheet()
        expect(p.locator('#hl-tx')).to_contain_text('Không có thao tác lưu file nào bị gián đoạn')
        self.assertFalse(has_unfinished(self.pkg))
        self.assertEqual((self.pkg / 'MANIFEST.sha256').read_bytes(), (new1 / 'MANIFEST.sha256').read_bytes())
        self.go('home')
        expect(p.locator('#bn-tx')).to_be_hidden()

        new2 = make_version(self.base, 'new2', 'Dòng 2 từ gói.\n', src=new1)
        interrupted_upgrade(self.pkg, new2)
        p.reload()
        expect(p.locator('#bn-tx')).to_be_visible()
        p.click('#bn-tx [data-goto="health"]')
        dialogs = []

        def answer(dialog):
            dialogs.append(dialog.message)
            if len(dialogs) == 1:
                dialog.dismiss()  # cancelling the confirmation must change nothing
            else:
                dialog.accept()

        p.on('dialog', answer)
        p.click('#hl-tx [data-txa="rollback"]')
        p.wait_for_timeout(500)
        self.assertEqual(len(dialogs), 1)
        self.assertIn('Phục hồi lần lưu file', dialogs[0])
        self.assertTrue(has_unfinished(self.pkg), 'cancelled rollback must keep the transaction')
        self.assertEqual(p.locator('#sheet.on').count(), 0)
        p.click('#hl-tx [data-txa="rollback"]')
        expect(p.locator('#sh-tag')).to_contain_text('Thành công')
        self.close_sheet()
        self.assertEqual(len(dialogs), 2)
        self.assertFalse(has_unfinished(self.pkg))
        # back to the state before the second upgrade: the version installed by the first one
        self.assertEqual((self.pkg / '.agent' / 'README.md').read_bytes(),
                         (new1 / '.agent' / 'README.md').read_bytes())
        expect(p.locator('#hl-tx')).to_contain_text('Không có thao tác lưu file nào bị gián đoạn')


PAGES = ['home', 'library', 'check', 'merges', 'packs', 'skills', 'setup', 'upgrade', 'maintain', 'health']
OVERFLOW_JS = """() => {
  const vw = document.documentElement.clientWidth, sw = document.documentElement.scrollWidth, off = [];
  if (sw > vw) document.querySelectorAll('body *').forEach(el => {
    if (el.closest('.tw,.dfx,.term,.sheet:not(.on),.skip,.sr')) return;
    const r = el.getBoundingClientRect();
    if (r.width && r.right > vw + 0.5 && getComputedStyle(el).position !== 'fixed')
      off.push((el.id ? '#' + el.id : el.tagName.toLowerCase()) + ' right=' + Math.round(r.right));
  });
  return {sw: sw, vw: vw, off: off.slice(0, 5)};
}"""
# every visible control: a name, a label for text fields, and a focus ring when reached from the keyboard
CONTROLS_JS = """() => {
  const out = [];
  document.querySelectorAll('button, a[href], input, select, textarea, [tabindex]').forEach(el => {
    if (!el.getClientRects().length || el.disabled || el.type === 'hidden' || el.closest('[hidden],#sheet')) return;
    if (el.getAttribute('tabindex') === '-1' && !el.matches('button, a, input, select, textarea')) return;  // landmark targets
    const what = el.outerHTML.slice(0, 70);
    let name = el.getAttribute('aria-label') || '';
    if (!name && el.labels && el.labels.length) name = Array.prototype.map.call(el.labels, l => l.textContent).join(' ');
    if (!name) name = (el.textContent || '').trim();
    if (!name) name = el.getAttribute('title') || '';
    if (!name.trim()) out.push('no name: ' + what);
    if (el.matches('input:not([type=checkbox]):not([type=radio]), textarea, select') && !(el.labels && el.labels.length))
      out.push('no label: ' + what);
    el.focus();
    const cs = getComputedStyle(el);
    if (document.activeElement !== el) out.push('cannot take focus: ' + what);
    else if (!el.matches(':focus-visible') || cs.outlineStyle === 'none' || parseFloat(cs.outlineWidth) < 2)
      out.push('no focus ring: ' + what);
  });
  return out;
}"""


@unittest.skipUnless(HAVE_BROWSER, SKIP_REASON or 'browser tests need playwright and Chromium')
class Accessibility(BrowserCase):
    """Keyboard use, focus, live status, busy state and narrow screens (technical part of Stage 13)."""

    def focus_in_sheet(self):
        return self.page.evaluate("() => document.getElementById('sheet').contains(document.activeElement)")

    def active_id(self):
        return self.page.evaluate("() => document.activeElement ? (document.activeElement.id || document.activeElement.tagName) : ''")

    def app_inert(self):
        return self.page.evaluate("() => document.querySelector('.app').hasAttribute('inert')")

    def assert_no_overflow(self, where):
        r = self.page.evaluate(OVERFLOW_JS)
        self.assertLessEqual(r['sw'], r['vw'], '%s: horizontal overflow %s' % (where, r['off']))

    def test_result_sheet_is_a_dialog_that_traps_focus_and_returns_it(self):
        init_project(self.pkg)
        (self.pkg / 'output' / 'bang-kiem.txt').write_text('Kính gửi [Tên khách hàng].\n', encoding='utf-8')
        p = self.open_panel()
        self.go('check')
        p.fill('#ck-path', str(self.pkg / 'output' / 'bang-kiem.txt'))
        p.click('#ck-add')
        p.focus('#ck-run')
        p.keyboard.press('Enter')  # keyboard only from here on
        expect(p.locator('#sheet')).to_have_class(re.compile(r'\bon\b'))
        p.wait_for_function("document.getElementById('sheet').contains(document.activeElement)")
        self.assertEqual(p.get_attribute('#sheet', 'role'), 'dialog')
        self.assertEqual(p.get_attribute('#sheet', 'aria-modal'), 'true')
        self.assertEqual(p.get_attribute('#sh-tag', 'aria-live'), 'polite')
        self.assertTrue(self.app_inert(), 'the page behind the dialog must be inert while it is open')
        for _ in range(14):
            p.keyboard.press('Tab')
            self.assertTrue(self.focus_in_sheet(), 'Tab moved focus out of the dialog')
        for _ in range(6):
            p.keyboard.press('Shift+Tab')
            self.assertTrue(self.focus_in_sheet(), 'Shift+Tab moved focus out of the dialog')
        p.keyboard.press('Escape')
        expect(p.locator('#sheet')).not_to_have_class(re.compile(r'\bon\b'))
        self.assertEqual(self.active_id(), 'ck-run', 'focus must return to the control that opened the dialog')
        self.assertFalse(self.app_inert())

    def test_closed_dialog_is_not_in_the_tab_order(self):
        init_project(self.pkg)  # trang Kiểm tra thuộc project, không có ở bộ mẫu / the check page belongs to a project
        p = self.open_panel()
        self.go('check')
        p.focus('#ck-path')
        reached = set()
        for _ in range(70):
            p.keyboard.press('Tab')
            reached.add(self.active_id())
        self.assertNotIn('sh-x', reached)
        self.assertNotIn('sh-close', reached)
        self.assertNotIn('sh-out', reached)

    def test_running_action_is_disabled_until_its_result_arrives(self):
        init_project(self.pkg)
        p = self.open_panel()
        held, calls = [], []

        def hold(route):  # the request stays in flight until the test releases it
            calls.append(1)
            held.append(route)

        p.route('**/api/run', hold)
        self.go('setup')
        p.fill('#f-name', 'Dang chay')
        p.focus('#su-run')
        p.keyboard.press('Enter')
        expect(p.locator('#sh-tag .spin')).to_have_count(1)
        self.assertEqual(p.get_attribute('#sheet', 'aria-busy'), 'true')
        self.assertTrue(p.is_disabled('#su-run'), 'the action button must be disabled while it runs')
        self.assertTrue(p.is_disabled('#sh-apply'))
        p.dispatch_event('#su-run', 'click')  # a second submit must do nothing
        p.wait_for_timeout(300)
        self.assertEqual(len(calls), 1)
        held[0].continue_()
        expect(p.locator('#sh-tag .spin')).to_have_count(0)
        expect(p.locator('#sh-tag')).to_contain_text('Đã xem trước')
        self.assertFalse(p.is_disabled('#su-run'))
        self.assertEqual(p.get_attribute('#sheet', 'aria-busy'), 'false')

    def test_no_horizontal_overflow_at_360_and_390_px_on_every_page(self):
        init_project(self.pkg)
        (self.pkg / 'output' / 'bang-kiem.txt').write_text('Ghi chú dài để thử bố cục.\n', encoding='utf-8')
        p = self.open_panel()
        for width in (360, 390):
            p.set_viewport_size({'width': width, 'height': 800})
            for page_id in PAGES:
                self.go(page_id)
                self.assert_no_overflow('%s at %dpx' % (page_id, width))
            self.go('check')
            p.fill('#ck-path', str(self.pkg / 'output' / 'bang-kiem.txt'))
            p.click('#ck-add')
            p.click('#ck-run')
            expect(p.locator('#sheet')).to_have_class(re.compile(r'\bon\b'))
            self.assert_no_overflow('result sheet at %dpx' % width)
            p.keyboard.press('Escape')
            expect(p.locator('#sheet')).not_to_have_class(re.compile(r'\bon\b'))

    def test_every_control_has_a_name_a_label_and_a_visible_focus_ring_in_both_languages(self):
        init_project(self.pkg)
        p = self.open_panel()
        for lang in ('vi', 'en'):
            p.click('.lang button[data-lang="%s"]' % lang)
            problems = {}
            for page_id in PAGES:
                self.go(page_id)
                p.keyboard.press('Tab')  # keyboard mode, so :focus-visible applies to programmatic focus
                found = p.evaluate(CONTROLS_JS)
                if found:
                    problems[page_id] = found
            self.assertEqual(problems, {}, 'language %s' % lang)
            self.go('home')


# Text checks that need no browser: they run in every environment, including CI without playwright.
def _css_tokens(text, pattern):
    m = re.search(pattern, text, re.S)
    assert m, 'token block not found: ' + pattern
    return dict(re.findall(r'--([a-z0-9-]+):(#[0-9a-fA-F]{3,6})', m.group(1)))


def _luminance(hex_color):
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    channels = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


# (text colour token or literal, background token, minimum ratio). Icons use 3:1 (WCAG 1.4.11), text 4.5:1.
CONTRAST_PAIRS = [
    ('ink', 'bg', 4.5), ('ink', 'panel', 4.5), ('ink', 'sunken', 4.5),
    ('ink-2', 'panel', 4.5), ('ink-2', 'panel-2', 4.5), ('ink-2', 'sunken', 4.5),
    ('ink-2', 'accent-soft', 4.5), ('ink-2', 'warn-soft', 4.5), ('ink-2', 'info-soft', 4.5),
    ('muted', 'bg', 4.5), ('muted', 'panel', 4.5), ('muted', 'panel-2', 4.5), ('muted', 'sunken', 4.5),
    ('faint', 'panel', 3.0), ('faint', 'sunken', 3.0),  # icons only
    ('accent', 'panel', 4.5), ('accent', 'accent-soft', 4.5), ('accent-ink', 'accent', 4.5),
    ('ok', 'panel', 4.5), ('ok', 'ok-soft', 4.5), ('warn', 'panel', 4.5), ('warn', 'warn-soft', 4.5),
    ('err', 'panel', 4.5), ('err', 'err-soft', 4.5), ('info', 'info-soft', 4.5), ('info', 'panel', 4.5),
    ('term-ink', 'term', 4.5), ('term-muted', 'term', 4.5),
]


class ContrastAndWording(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / 'tools' / 'app_ui.html').read_text(encoding='utf-8')
        cls.light = _css_tokens(cls.text, r':root\{(.*?)\}\s*@media')
        cls.dark_media = dict(cls.light, **_css_tokens(cls.text, r'prefers-color-scheme:dark\)\{:root:not\(\[data-theme="light"\]\)\{(.*?)\}\}'))
        cls.dark = dict(cls.light, **_css_tokens(cls.text, r':root\[data-theme="dark"\]\{(.*?)\}'))

    def test_dark_theme_is_defined_the_same_way_in_both_blocks(self):
        self.assertEqual(self.dark_media, self.dark)

    def test_text_and_tag_colours_meet_contrast_in_both_themes(self):
        failures = []
        for name, tokens in (('light', self.light), ('dark', self.dark)):
            for fg, bg, need in CONTRAST_PAIRS:
                ratio = _contrast(tokens[fg], tokens[bg])
                if ratio < need:
                    failures.append('%s: %s on %s = %.2f (needs %.1f)' % (name, fg, bg, ratio, need))
        self.assertEqual(failures, [])

    def test_error_and_result_messages_say_what_happened_whether_data_is_safe_and_the_next_step(self):
        block = self.text[self.text.index('var D={'):self.text.index('\n};', self.text.index('var D={'))]
        entries = {}
        for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*\[\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*\]", block):
            entries[m.group(1)] = (m.group(2), m.group(3))
        keys = ['err_conn', 'err_tool', 'err_blocked', 'm_issues_ro', 'tx_partial', 'tx_partial_rb', 'merge_msg',
                'ck_not_checked_next', 'merge_state_fail', 'diff_fail', 'pick_fail']
        vi_safe = ('Chưa ghi', 'chưa biết', 'chưa rõ', 'Chưa rõ', 'không bị thay đổi', 'Không có gì bị', 'Không file',
                   'được giữ', 'giữa hai trạng thái', 'giữa bản cũ và bản mới', 'không phải kết quả đạt')
        en_safe = ('Nothing was', 'not known', 'not yet clear', 'No document', 'kept', 'between two states', 'between the old and the new', 'not a pass')
        problems = []
        for key in keys:
            if key not in entries:
                problems.append('missing key ' + key)
                continue
            vi, en = entries[key]
            if 'Bước tiếp' not in vi:
                problems.append(key + ': vi has no next step')
            if 'Next step' not in en:
                problems.append(key + ': en has no next step')
            if not any(s in vi for s in vi_safe):
                problems.append(key + ': vi does not say whether data is safe')
            if not any(s in en for s in en_safe):
                problems.append(key + ': en does not say whether data is safe')
        self.assertEqual(problems, [])


if __name__ == '__main__':
    unittest.main()
