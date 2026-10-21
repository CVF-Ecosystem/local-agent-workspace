"""Measure the result sheet at desktop and phone widths: is the close button inside the viewport? Scratch script."""
import json
import sys
from pathlib import Path

S = Path(r'C:\Users\DELL\AppData\Local\Temp\claude\d--UNG-DUNG-AI-TOOL-AI-2026-Controlled-Vibe-Framework-CVF'
         r'\c10e50f7-d8b3-4ff6-9cec-4f49b976eb5e\scratchpad')
sys.path.insert(0, str(S))
import errors2 as E  # noqa: E402

BIEN_BAN = E.S / 'ktnd' / 'du-lieu-gia' / 'bien-ban-thu.txt'


def measure(browser, width):
    ctx = browser.new_context(viewport={'width': width, 'height': 860})
    page = ctx.new_page()
    panel = E.T.Panel(E.PROJ, str(E.UI / 'logs'))
    panel.start()
    try:
        page.goto(panel.url)
        page.wait_for_function("document.getElementById('sb-st').textContent.length > 0", timeout=E.TMO)
        E.nav(page, 'check')
        page.fill('#ck-path', str(BIEN_BAN))
        page.click('#ck-add')
        page.click('#ck-run')
        E.wait_result(page)
        page.wait_for_timeout(800)  # cho hoạt ảnh mở xong / let the open animation finish
        box = page.locator('#sheet').bounding_box()
        xbox = page.locator('#sh-x').bounding_box()
        out = {'width': width, 'viewport_w': page.evaluate('window.innerWidth'),
               'sheet': box, 'close_btn': xbox,
               'sheet_right_edge_inside_viewport': bool(box and box['x'] + box['width'] <= width + 1),
               'close_btn_inside_viewport': bool(xbox and 0 <= xbox['x'] and xbox['x'] + xbox['width'] <= width + 1),
               'horizontal_scroll': page.evaluate('document.documentElement.scrollWidth > window.innerWidth')}
        page.screenshot(path=str(E.UI / ('shot6-sheet-open-%d.png' % width)))
        E.close_sheet(page)
        return out
    finally:
        panel.stop()
        ctx.close()


def main():
    with E.sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            results = [measure(browser, w) for w in (1280, 390)]
        finally:
            browser.close()
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
