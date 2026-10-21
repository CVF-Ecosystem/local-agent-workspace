"""Simulated error cases through the panel (criterion C2). Scratch script, standalone helpers."""
import json
import re
import sys
import traceback
from pathlib import Path

S = Path(r'C:\Users\DELL\AppData\Local\Temp\claude\d--UNG-DUNG-AI-TOOL-AI-2026-Controlled-Vibe-Framework-CVF'
         r'\c10e50f7-d8b3-4ff6-9cec-4f49b976eb5e\scratchpad')
REPO = Path(r'D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\local-agent-workspace')
UI = S / 'ui'
PROJ = UI / 'tpl' / 'Du an thu 01'
MISSING_PKG = UI / 'khong-co-goi'
MISSING_FILE = UI / 'khong-co' / 'bien-ban.txt'
TMO = 60000
REC = {'steps': []}

sys.path.insert(0, str(REPO / 'tests'))
import test_ui_browser as T  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402


def rec(name, **kw):
    REC['steps'].append(dict(step=name, **kw))
    print('>>', name, json.dumps(kw, ensure_ascii=False)[:700], flush=True)


def open_page(browser, url):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 860})
    page = ctx.new_page()
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


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        panel = T.Panel(PROJ, str(UI / 'logs'))
        panel.start()
        try:
            page, ctx = open_page(browser, panel.url)
            nav(page, 'upgrade')
            page.fill('#u-dir', str(MISSING_PKG))
            page.click('#u-run')
            try:
                rec('e1_upgrade_missing_package', **wait_result(page))
                close_sheet(page)
            except Exception:
                rec('e1_upgrade_missing_package', error=traceback.format_exc()[-400:])
            nav(page, 'check')
            page.fill('#ck-path', str(MISSING_FILE))
            try:
                page.click('#ck-add')
                page.click('#ck-run')
                rec('e2_check_missing_file', **wait_result(page))
                close_sheet(page)
            except Exception:
                rec('e2_check_missing_file', error=traceback.format_exc()[-400:])
            page.screenshot(path=str(UI / 'shot5-error-check.png'))
            ctx.close()
        finally:
            panel.stop()
            browser.close()
    (UI / 'errors.json').write_text(json.dumps(REC, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
