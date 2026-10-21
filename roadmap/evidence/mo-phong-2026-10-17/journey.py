"""Simulated run of the three scenario tasks (KICH_BAN section 3) through the real panel, with mock data.

Scratch script, not part of the repo. Uses the test harness only to start tools/app.py and stop it.
"""
import json
import re
import shutil
import sys
import traceback
import zipfile
from pathlib import Path

S = Path(r'C:\Users\DELL\AppData\Local\Temp\claude\d--UNG-DUNG-AI-TOOL-AI-2026-Controlled-Vibe-Framework-CVF'
         r'\c10e50f7-d8b3-4ff6-9cec-4f49b976eb5e\scratchpad')
REPO = Path(r'D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\local-agent-workspace')
ZIP = S / 'ktnd' / 'zip' / 'local-agent-workspace-v1.8.0-rc1.zip'
NEW_PKG = S / 'ktnd' / 'goi-moi' / 'local-agent-workspace-v1.8.0'
BIEN_BAN = S / 'ktnd' / 'du-lieu-gia' / 'bien-ban-thu.txt'
UI = S / 'ui'
LOG = UI / 'logs'
TMO = 60000
OBSERVER_LINE = 'Ghi chú của người thử: dòng này do tôi tự viết (dữ liệu giả).'
PKG_LINE = 'Dòng mới từ gói phát hành (dữ liệu giả).'

sys.path.insert(0, str(REPO / 'tests'))
import test_ui_browser as T  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402

REC = {'steps': [], 'console_errors': []}


def rec(name, **kw):
    REC['steps'].append(dict(step=name, **kw))
    print('>>', name, json.dumps(kw, ensure_ascii=False)[:600], flush=True)


def open_page(browser, url):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 860})
    page = ctx.new_page()
    page.on('pageerror', lambda exc: REC['console_errors'].append('pageerror: %s' % exc))
    page.on('console', lambda m: REC['console_errors'].append(m.text) if m.type == 'error' else None)
    page.goto(url)
    page.wait_for_function("document.getElementById('sb-st').textContent.length > 0", timeout=TMO)
    return page, ctx


def nav(page, pid):
    if not page.is_visible('.nav [data-page="%s"]' % pid) and page.is_visible('#nav-more'):
        page.click('#nav-more')
    page.click('.nav [data-page="%s"]' % pid)


def wait_result(page):
    page.wait_for_selector('#sheet.on', timeout=TMO)
    page.wait_for_function(
        "(() => { const t = document.getElementById('sh-tag').textContent.trim();"
        " return t.length > 0 && !/Đang/.test(t); })()", timeout=TMO)
    return {'tag': page.inner_text('#sh-tag'), 'msg': page.inner_text('#sh-msg'),
            'out': page.inner_text('#sh-out')[:900]}


def close_sheet(page):
    page.click('#sh-x')
    expect(page.locator('#sheet')).not_to_have_class(re.compile(r'\bon\b'), timeout=TMO)


def task1(browser, tpl_pkg, proj):
    panel = T.Panel(tpl_pkg, str(LOG))
    panel.start()
    try:
        page, ctx = open_page(browser, panel.url)
        expect(page.locator('#home-tpl')).to_be_visible(timeout=TMO)
        page.fill('#np-name', 'Du an thu 01')
        page.click('#np-run')
        rec('t1_preview', **wait_result(page))
        page.click('#sh-apply')
        rec('t1_apply', **wait_result(page))
        close_sheet(page)
        expect(page.locator('#np-done')).to_contain_text('Du an thu 01', timeout=TMO)
        rec('t1_done_text', text=page.inner_text('#np-done')[:300])
        rec('t1_project_files', PACKAGE_INFO=(proj / '.agent' / 'PACKAGE_INFO.json').is_file(),
            template_untouched=not (tpl_pkg / '.agent' / 'PACKAGE_INFO.json').exists())
        page.screenshot(path=str(UI / 'shot1-template-home.png'))
        # lỗi giả lập: đặt lại đúng tên project đã có / simulated error: same name again
        page.fill('#np-name', 'Du an thu 01')
        page.click('#np-run')
        try:
            rec('t1_error_duplicate_name', **wait_result(page))
        except Exception as e:  # keep going: the outcome itself is what we want to see
            rec('t1_error_duplicate_name', no_sheet=str(e).splitlines()[0][:200],
                np_done=page.inner_text('#np-done')[:300])
        page.keyboard.press('Escape')
        ctx.close()
    finally:
        panel.stop()


def task2(browser, proj):
    panel = T.Panel(proj, str(LOG))
    panel.start()
    try:
        page, ctx = open_page(browser, panel.url)
        nav(page, 'check')
        page.fill('#ck-path', str(BIEN_BAN))
        page.click('#ck-add')
        page.click('#ck-run')
        rec('t2_check', **wait_result(page))
        close_sheet(page)
        page.screenshot(path=str(UI / 'shot2-check.png'))
        ctx.close()
    finally:
        panel.stop()


def task3(browser, proj):
    # bước 2.4 của kịch bản: người quan sát thêm dòng vào file mà gói mới cũng đổi
    readme = proj / '.agent' / 'README.md'
    readme.write_text(readme.read_text(encoding='utf-8') + '\n' + OBSERVER_LINE + '\n', encoding='utf-8')
    panel = T.Panel(proj, str(LOG))
    panel.start()
    try:
        page, ctx = open_page(browser, panel.url)
        nav(page, 'upgrade')
        page.fill('#u-dir', str(NEW_PKG))
        page.click('#u-run')
        rec('t3_report', **wait_result(page))
        page.click('#sh-apply')
        rec('t3_apply', **wait_result(page))
        close_sheet(page)
        nav(page, 'merges')
        expect(page.locator('#mg-rows tr')).to_have_count(1, timeout=TMO)
        rec('t3_merges_before', rows=page.inner_text('#mg-rows')[:300])
        page.click('#mg-rows [data-md="0"]')
        rec('t3_diff', added=page.locator('#sh-diff .dr.add').first.inner_text()[:200],
            removed=page.locator('#sh-diff .dr.del').first.inner_text()[:200])
        close_sheet(page)
        page.click('#mg-rows [data-ms="reviewing"]')
        page.click('#mg-rows [data-ms="ready"]')
        page.screenshot(path=str(UI / 'shot3-merges-before.png'))
        ctx.close()
    finally:
        panel.stop()

    # người thử hợp nhất: giữ cả dòng gói mới và dòng của mình, rồi xóa .new (làm ngoài ứng dụng)
    new = proj / '.agent' / 'README.md.new'
    merged = new.read_text(encoding='utf-8').rstrip('\n') + '\n\n' + OBSERVER_LINE + '\n'
    (proj / '.agent' / 'README.md').write_text(merged, encoding='utf-8')
    new.unlink()
    rec('t3_manual_merge', merged_has_pkg_line=PKG_LINE in merged, merged_has_observer_line=OBSERVER_LINE in merged,
        new_file_left=new.exists())

    panel = T.Panel(proj, str(LOG))
    panel.start()
    try:
        page, ctx = open_page(browser, panel.url)
        nav(page, 'upgrade')
        page.fill('#u-dir', str(NEW_PKG))
        page.click('#u-run')
        rec('t3_final_report', **wait_result(page))
        close_sheet(page)
        nav(page, 'merges')
        rec('t3_merges_after', rows=page.inner_text('#mg-rows')[:300])
        page.screenshot(path=str(UI / 'shot4-merges-after.png'))
        ctx.close()
    finally:
        panel.stop()


def main():
    shutil.rmtree(UI, ignore_errors=True)
    LOG.mkdir(parents=True, exist_ok=True)
    tpl_root = UI / 'tpl'
    tpl_root.mkdir(parents=True)
    zipfile.ZipFile(ZIP).extractall(tpl_root)
    tpl_pkg = tpl_root / 'local-agent-workspace-v1.8.0'
    proj = tpl_root / 'Du an thu 01'
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for name, fn in (('task1', lambda: task1(browser, tpl_pkg, proj)),
                             ('task2', lambda: task2(browser, proj)),
                             ('task3', lambda: task3(browser, proj))):
                try:
                    fn()
                except Exception as e:
                    rec(name + '_FAILED', error=traceback.format_exc()[-900:])
        finally:
            browser.close()
    REC['console_errors'] = [c for c in REC['console_errors'] if '404' not in c]
    (UI / 'result.json').write_text(json.dumps(REC, ensure_ascii=False, indent=2), encoding='utf-8')
    print('SUMMARY steps=%d console_errors(non-404)=%d' % (len(REC['steps']), len(REC['console_errors'])))


if __name__ == '__main__':
    main()
