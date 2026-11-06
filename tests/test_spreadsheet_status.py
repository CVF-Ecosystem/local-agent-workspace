import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py'
CALLER = ROOT / 'tools/check_output.py'

class StatusCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='datamock-')
        self.d = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def run_cli(self, script, *args, isolated=False):
        cmd = [sys.executable] + (['-S'] if isolated else []) + [str(script)] + [str(x) for x in args]
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10, cwd=str(ROOT))
    def csv(self, name, contents):
        p = self.d / name
        p.write_text(contents, encoding='utf-8')
        return p
    def check(self, p, *args, expected=0):
        before = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        r = self.run_cli(CHECK, p, '--status-exit', '--lang', 'en', *args)
        self.assertEqual(r.returncode, expected, r.stdout + r.stderr)
        if before: self.assertEqual(before, hashlib.sha256(p.read_bytes()).hexdigest())
        return r
    def test_clean_finding_and_default_aliases(self):
        p = self.csv('clean.csv', 'Name,Amount\nA,10\nB,20\n')
        r = self.check(p, '--key', 'Name', '--max-examples', '2')
        self.assertIn('INFO:', r.stdout)
        self.assertIn('Trace:', r.stdout)
        self.assertEqual(self.run_cli(CHECK, p).returncode, 0)
        r = self.run_cli(CHECK, p, '--status-exit', '--lang', 'vi', '--khoa', 'Name', '--toi-da-vi-du', '2')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        q = self.csv('total.csv', 'Name,Amount\nA,10\nB,20\nTotal,40\n')
        self.assertEqual(self.run_cli(CHECK, q).returncode, 0)
        r = self.check(q, expected=1)
        self.assertIn('difference 10', r.stdout)
        self.check(q, '--key', 'Absent', expected=2)
    def test_requested_coverage(self):
        p = self.csv('clean.csv', 'Name,Amount\nA,10\nB,20\n')
        self.assertIn('--sheet is ignored', self.check(p, '--sheet', 'CSV', expected=2).stdout)
        self.check(p, '--key', 'Absent', expected=2)
        self.check(p, '--key', 'Name,Absent', expected=2)
        vi = self.run_cli(CHECK, p, '--status-exit', '--lang', 'vi', '--key', 'Absent')
        self.assertEqual(vi.returncode, 2, vi.stdout + vi.stderr)
        self.assertIn('khóa được yêu cầu', vi.stdout)
        self.assertNotIn('requested key', vi.stdout)
        self.check(self.csv('empty.csv', ''), expected=2)
        self.check(self.csv('form.csv', 'Guide,,,\n,,,\nValue,,,\n'), expected=2)
        self.check(self.d / 'missing.csv', expected=2)
        self.check(self.csv('old.xls', 'data'), expected=2)
        fake = self.csv('book.xlsx', 'data')
        r = self.run_cli(CHECK, fake, '--status-exit', '--lang', 'en', isolated=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn('openpyxl', r.stderr)
    def test_formula_and_missing_sheet(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest('openpyxl unavailable')
        book = self.d / 'formula.xlsx'
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Data'
        ws.append(['Name', 'Amount']); ws.append(['A', '=10+20']); ws.append(['B', 20]); wb.save(str(book))
        r = self.check(book, expected=2)
        self.assertIn('not recalculated', r.stdout)
        self.check(book, '--sheet', 'missing', expected=2)
        cached = self.d / 'cached.xlsx'
        with zipfile.ZipFile(str(book)) as src, zipfile.ZipFile(str(cached), 'w') as dst:
            for item in src.infolist():
                data = src.read(item.filename)
                if item.filename == 'xl/worksheets/sheet1.xml':
                    data = data.replace(b'<f>10+20</f><v></v>', b'<f>10+20</f><v>30</v>')
                dst.writestr(item, data)
        values = openpyxl.load_workbook(str(cached), data_only=True)
        formulas = openpyxl.load_workbook(str(cached), data_only=False)
        self.assertEqual(values['Data']['B2'].value, 30)
        self.assertEqual(formulas['Data']['B2'].value, '=10+20')
        values.close(); formulas.close()
        r = self.check(cached)
        self.assertIn('not engine-verified', r.stdout)
    def test_no_data_worksheets_is_incomplete(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest('openpyxl unavailable')
        from openpyxl.chart import BarChart
        book = self.d / 'chart-only.xlsx'
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        chart = wb.create_chartsheet('Chart')
        chart.add_chart(BarChart())
        wb.save(str(book)); wb.close()
        loaded = openpyxl.load_workbook(str(book))
        self.assertEqual(loaded.worksheets, [])
        self.assertEqual(loaded.sheetnames, ['Chart'])
        loaded.close()
        result = self.check(book, expected=2)
        self.assertIn('no data worksheets to check', result.stdout)
        self.assertEqual(self.run_cli(CHECK, book).returncode, 0)
        vi = self.run_cli(CHECK, book, '--status-exit', '--lang', 'vi')
        self.assertEqual(vi.returncode, 2, vi.stdout + vi.stderr)
        self.assertIn('không có worksheet dữ liệu để kiểm', vi.stdout)
        before = hashlib.sha256(book.read_bytes()).hexdigest()
        caller = self.run_cli(CALLER, book, '--lang', 'en', '--result-json')
        self.assertEqual(caller.returncode, 2, caller.stdout + caller.stderr)
        result = json.loads(caller.stdout.split('@@RESULT_JSON@@', 1)[1].strip())
        self.assertEqual(result['files'][0]['status'], 'not_checked')
        self.assertNotIn('TOOL ERROR', caller.stdout)
        self.assertEqual(before, hashlib.sha256(book.read_bytes()).hexdigest())
    def test_caller_status_and_json(self):
        clean = self.csv('clean.csv', 'Name,Amount\nA,10\nB,20\n')
        finding = self.csv('finding.csv', 'Name,Amount\nA,10\nB,20\nTotal,40\n')
        empty = self.csv('empty.csv', '')
        missing = self.d / 'missing.csv'
        for p, code, status in [(clean,0,'success'), (finding,1,'issues'), (empty,2,'not_checked'), (missing,2,'not_checked')]:
            with self.subTest(p=p):
                before = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
                r = self.run_cli(CALLER, p, '--lang', 'en', '--result-json')
                self.assertEqual(r.returncode, code, r.stdout + r.stderr)
                result = json.loads(r.stdout.split('@@RESULT_JSON@@', 1)[1].strip())
                self.assertEqual((result['status'], result['code']), (status, code))
                self.assertEqual(result['files'][0]['status'], ('pass', 'issues', 'not_checked')[code])
                if before: self.assertEqual(before, hashlib.sha256(p.read_bytes()).hexdigest())
                if p == empty:
                    self.assertIn('INCOMPLETE', r.stdout)
                    self.assertNotIn('TOOL ERROR', r.stdout)
        r = self.run_cli(CALLER, finding, empty, '--lang', 'en', '--result-json')
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

# Import the module, not its test classes, to avoid collecting the existing suite.
from tests import test_current_draft as continuity

class CanonicalRevision(continuity.Base):
    def test_older_revision_and_copy_with_newer_mtime_do_not_replace_selection(self):
        self.select(self.r2)
        older = Path(self.path('working/w-1/bao-cao-v1.docx'))
        current = Path(self.path('working/w-1/bao-cao-v2.docx'))
        copied = older.with_name('copied-old.docx')
        copied.write_bytes(older.read_bytes())
        newer_ns = current.stat().st_mtime_ns + 60_000_000_000
        os.utime(older, ns=(newer_ns, newer_ns))
        os.utime(copied, ns=(newer_ns, newer_ns))
        self.assertGreater(older.stat().st_mtime_ns, current.stat().st_mtime_ns)
        self.assertGreater(copied.stat().st_mtime_ns, current.stat().st_mtime_ns)
        before = continuity.tree(self.project)
        status = continuity.cd.status(self.project)
        self.assertEqual(status['selected']['rid'], self.r2)
        self.assertEqual(status['selected']['state'], 'matched')
        self.assertEqual(continuity.tree(self.project), before)
        self.assertEqual(self.opened, [])

if __name__ == '__main__': unittest.main()
