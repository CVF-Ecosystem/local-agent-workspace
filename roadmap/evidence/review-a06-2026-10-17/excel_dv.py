"""What survives when real Excel re-saves the index and LAW then rewrites it with openpyxl? Dummy data."""
import os, re, shutil, subprocess, sys, tempfile, warnings, zipfile
sys.argv = [sys.argv[0]]
LAW = r'D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\local-agent-workspace'
SCRATCH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(LAW, 'tools'))
import library_sync  # noqa: E402
import openpyxl  # noqa: E402

TEMPLATE = os.path.join(LAW, 'skills/local/shared/source-library/assets/source-index-template.xlsx')


def dv_counts(path):
    z = zipfile.ZipFile(path)
    sheets = [n for n in z.namelist() if n.startswith('xl/worksheets/sheet')]
    classic = ext = 0
    for n in sheets:
        x = z.read(n).decode('utf-8', 'ignore')
        classic += len(re.findall(r'<dataValidation ', x))
        ext += len(re.findall(r'<x14:dataValidation ', x))
    return classic, ext


base = tempfile.mkdtemp(prefix='a06-dv-')
os.makedirs(os.path.join(base, 'references', 'source-documents', 'team'))
index = os.path.join(base, 'references', '_INDEX.xlsx')
shutil.copyfile(TEMPLATE, index)
open(os.path.join(base, 'references', 'source-documents', 'team', 'one.txt'), 'w').write('one')
print('template                  (classic, x14 ext):', dv_counts(index))
wb = openpyxl.load_workbook(index); n = wb.sheetnames.index(library_sync.library.SHEET) + 1; wb.close()
subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(SCRATCH, 'excel_ops.ps1'),
                '-Mode', 'edit', '-Path', index, '-Sheet', str(n), '-Text', 'x'], capture_output=True, timeout=120)
print('after real Excel saves   (classic, x14 ext):', dv_counts(index))
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    print('LAW preview notices on the Excel-saved file:', library_sync.plan(base)['notices'])
    library_sync.apply(base)
print('after LAW rewrites       (classic, x14 ext):', dv_counts(index), '| openpyxl warnings:', [str(x.message)[:60] for x in w])
# control: LAW rewriting the untouched template
base2 = tempfile.mkdtemp(prefix='a06-dv2-')
os.makedirs(os.path.join(base2, 'references', 'source-documents', 'team'))
shutil.copyfile(TEMPLATE, os.path.join(base2, 'references', '_INDEX.xlsx'))
open(os.path.join(base2, 'references', 'source-documents', 'team', 'one.txt'), 'w').write('one')
library_sync.apply(base2)
print('control: LAW rewrites the template directly (classic, x14 ext):', dv_counts(os.path.join(base2, 'references', '_INDEX.xlsx')))
shutil.rmtree(base, ignore_errors=True); shutil.rmtree(base2, ignore_errors=True)
subprocess.run(['taskkill', '/F', '/IM', 'EXCEL.EXE'], capture_output=True) if False else None
