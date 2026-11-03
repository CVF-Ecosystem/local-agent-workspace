import hashlib
import json
import re
import unittest
from pathlib import Path

try:
    from playwright.sync_api import Error as PlaywrightError, sync_playwright
except ImportError:
    sync_playwright = None

HTML = Path(__file__).resolve().parents[1] / 'skills/local/shared/data-charts/assets/basic-charts.html'
PATTERN = r'(<script id="report-data" type="application/json">)(.*?)(</script>)'
BASELINE = {'c-line': 'd87f248c13551d453b41f87366c68354deb429bedd2ffe5c4168705fc4bfd227', 'c-bar': '3ccbc944560164e06e8e86efd3073cc4b31f47e9bd63141cdff49627bee814af', 'c-stack': 'adb9411aa3dc2ce315a7640dfe358fa4c8213e1b295d82e82390985de6ccc3d1', 'c-donut': '6f5c66fc0eb7fb04b91e5436a9e95103d4a4e24fc69acc637ce403783eb15dc4', 'c-table': 'a206ad4593d8a58006aaebf87a656ec48965f2a6895e88b51ef6de8d705d5810'}

@unittest.skipUnless(sync_playwright, "playwright unavailable; no installation attempted")
class DataChartsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding='utf-8')
        cls.data = json.loads(re.search(PATTERN, cls.html, re.S).group(2))
        cls.pw = sync_playwright().start()
        cls.addClassCleanup(cls.pw.stop)
        try:
            cls.browser = cls.pw.chromium.launch(headless=True)
        except PlaywrightError as error:
            if "Executable doesn't exist" in str(error):
                raise unittest.SkipTest("Chromium executable unavailable; no download attempted")
            raise
        cls.addClassCleanup(cls.browser.close)
        cls.page = cls.browser.new_page()
        cls.page.route('**/*', lambda route: route.abort())

    def render(self, values=None, sparse=False):
        data = json.loads(json.dumps(self.data))
        if values is not None:
            items = [{'name': name, 'value': value} for name, value in zip('ABC', values)]
            data['bar']['categories'] = items
            data['table']['rows'] = items
            data['donut']['parts'] = items
        if sparse:
            data['months'] = ['one', 'two', 'three']
            data['line']['series'] = [{'name': '<unsafe>', 'values': [10, None, 0]}]
            data['source'] = '<source>'
            data['isDemo'] = False
        content = re.sub(PATTERN, lambda m: m.group(1) + json.dumps(data, ensure_ascii=False) + m.group(3), self.html, flags=re.S)
        self.page.set_content(content, wait_until='load')

    def test_default_dom(self):
        self.render()
        for key, expected in BASELINE.items():
            html = self.page.locator('#' + key).inner_html()
            self.assertEqual(hashlib.sha256(html.encode()).hexdigest(), expected, key)

    def test_partial(self):
        self.render([12, None, 0])
        table = self.page.locator('#c-table')
        self.assertIn('Tổng phần đã biết (2/3)', table.inner_text())
        self.assertEqual(table.locator('tfoot td').all_inner_texts(), ['12', '—'])
        self.assertEqual(table.locator('tbody tr').nth(1).locator('td').all_inner_texts(), ['—', '—'])
        self.assertEqual(table.locator('tbody tr').nth(1).locator('.inbar').count(), 0)
        self.assertEqual(self.page.locator('#c-bar svg rect').count(), 2)
        self.assertNotIn('%', self.page.locator('#c-bar').inner_text())
        self.assertEqual(self.page.locator('#c-donut svg').count(), 0)
        self.assertIn('Chưa đủ dữ liệu', self.page.locator('#u-donut').inner_text())
        self.assertEqual(self.page.locator('#c-donut tbody tr').nth(1).locator('td').all_text_contents(), ['—', '—'])

    def test_all_missing(self):
        self.render([None, None, None])
        self.assertEqual(self.page.locator('#c-bar svg rect').count(), 0)
        self.assertIn('Chưa có dữ liệu', self.page.locator('#c-table').inner_text())
        self.assertNotIn('100%', self.page.locator('#c-table').inner_text())
        self.assertEqual(self.page.locator('#c-table tfoot td').all_inner_texts(), ['—', '—'])

    def test_all_zero(self):
        self.render([0, 0, 0])
        for key in ['c-donut', 'c-table']:
            html = self.page.locator('#' + key).inner_html()
            for bad in ['NaN', 'Infinity', '100%']:
                self.assertNotIn(bad, html)
        self.assertEqual(self.page.locator('#c-donut svg').count(), 0)
        self.assertEqual(self.page.locator('#c-donut tbody tr').count(), 3)

    def test_sparse_line_and_metadata(self):
        self.render(sparse=True)
        path = self.page.locator('#c-line svg path').get_attribute('d')
        self.assertEqual(path.count('M'), 2)
        self.assertNotIn('L', path)
        self.assertEqual(self.page.locator('#c-line svg circle').count(), 2)
        self.assertIn('—', self.page.locator('#c-line').text_content())
        self.assertIn('0', self.page.locator('#c-line').text_content())
        self.assertEqual(self.page.locator('#source').inner_text(), '<source>')
        self.assertEqual(self.page.locator('#demo').inner_text(), '')
        self.assertEqual(self.page.locator('#lg-line span').inner_text(), '<unsafe>')
        self.assertEqual(self.page.locator('#lg-line unsafe').count(), 0)

if __name__ == '__main__':
    unittest.main()
