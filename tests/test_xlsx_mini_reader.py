import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / 'skills/local/shared/excel-html-viewer/assets/xlsx-mini-reader.js'
TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet'
NODE = r'''const fs = require('fs');
const {readXlsx} = require(process.argv[1]);
const b = fs.readFileSync(process.argv[2]);
readXlsx(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)).then(x => console.log(JSON.stringify({ok:true, sheets:x}))).catch(e => console.log(JSON.stringify({ok:false,error:String(e.message)})));'''

class ReaderCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='datamock-xlsx-')
        self.file = Path(self.tmp.name) / 'input.xlsx'
    def tearDown(self): self.tmp.cleanup()
    def run_book(self, files, compression=zipfile.ZIP_STORED, duplicate=None):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(str(self.file), 'w', compression) as z:
                for name, content in files.items(): z.writestr(name, content)
                if duplicate: z.writestr(duplicate, files[duplicate])
        before = hashlib.sha256(self.file.read_bytes()).hexdigest()
        r = subprocess.run(['node', '-e', NODE, str(READER), str(self.file)], cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(before, hashlib.sha256(self.file.read_bytes()).hexdigest())
        return json.loads(r.stdout)
    def files(self, props='', sheets=None, rels=None, sheet1=None, second=False):
        sheets = sheets if sheets is not None else '<sheet name="Dữ liệu" sheetId="1" r:id="rId1"/>'
        rels = rels if rels is not None else '<Relationship Id="rId1" Type="%s" Target="worksheets/sheet1.xml"/>' % TYPE
        sheet1 = sheet1 if sheet1 is not None else '<worksheet><sheetData/></worksheet>'
        f = {'xl/workbook.xml':'<workbook xmlns:r="rel">%s<sheets>%s</sheets></workbook>' % (props,sheets),
             'xl/_rels/workbook.xml.rels':'<Relationships>%s</Relationships>' % rels,
             'xl/worksheets/sheet1.xml':sheet1}
        if second: f['xl/worksheets/sheet2.xml'] = '<worksheet><sheetData/></worksheet>'
        return f
    def rejected(self, files, contains=None, **kw):
        r = self.run_book(files, **kw)
        self.assertFalse(r['ok'], r)
        self.assertNotIn('sheets', r)
        if contains: self.assertIn(contains, r['error'])
    def test_stored_deflate_empty_multisheet_and_typed_sparse(self):
        sheet = '''<worksheet><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Việt</t></is></c><c r="C1"><v>45000</v></c><c r="D1"><v>0</v></c><c r="E1" t="b"><v>0</v></c><c r="F1"><f>1+1</f><v>2</v></c><c r="G1"><f>1+2</f><v></v></c><c r="H1" t="s"><v>0</v></c></row><row r="3"><c r="B3" t="b"><v>1</v></c></row></sheetData></worksheet>'''
        sheets = '<sheet name="Dữ liệu" r:id="rId1"/><sheet name="Trống" r:id="rId2" state="hidden"/>'
        rels = '<Relationship Id="rId1" Type="%s" Target="./worksheets/sheet1.xml"/><Relationship Id="rId2" Type="%s" Target="/xl/worksheets/sheet2.xml"/>' % (TYPE,TYPE)
        f = self.files(sheets=sheets, rels=rels, sheet1=sheet, second=True)
        f['xl/sharedStrings.xml'] = '<sst><si><t>Chuỗi</t></si></sst>'
        expected = [{'name':'Dữ liệu','rows':[['Việt',None,45000,0,False,2,None,'Chuỗi'],[],[None,True]],'formulas':2,'nocache':1,'state':'visible'}, {'name':'Trống','rows':[],'formulas':0,'nocache':0,'state':'hidden'}]
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            with self.subTest(method=method): self.assertEqual(self.run_book(f, method), {'ok':True,'sheets':expected})
    def test_missing_relationship_target_and_second_part(self):
        f = self.files(); del f['xl/_rels/workbook.xml.rels']; self.rejected(f)
        self.rejected(self.files(rels=''))
        self.rejected(self.files(rels='<Relationship Id="rId1" Type="%s"/>' % TYPE))
        self.rejected(self.files(rels='<Relationship Id="rId1" Type="%s" Target="https://example.com/x"/>' % TYPE))
        sheets='<sheet name="one" r:id="rId1"/><sheet name="two" r:id="rId2"/>'
        rels='<Relationship Id="rId1" Type="%s" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="%s" Target="worksheets/sheet2.xml"/>' % (TYPE,TYPE)
        self.rejected(self.files(sheets=sheets,rels=rels))
    def test_bad_type_external_duplicate_and_garbage(self):
        self.rejected(self.files(rels='<Relationship Id="rId1" Type="%s" Target="worksheets/sheet1.xml" TargetMode="External"/>' % TYPE))
        self.rejected(self.files(rels='<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chartsheet" Target="worksheets/sheet1.xml"/>'))
        self.rejected(self.files(sheet1='<chartsheet><sheetData/></chartsheet>'))
        self.rejected(self.files(sheet1='garbage'))
        self.rejected(self.files(sheet1='<worksheet><sheetData>garbage</sheetData></worksheet>'))
        self.rejected(self.files(sheet1='<worksheet><sheetData></worksheet>'))
        self.rejected(self.files(sheet1='<worksheet><sheetData><row></sheetData></worksheet>'))
        self.rejected(self.files(), duplicate='xl/worksheets/sheet1.xml')
        rel='<Relationship Id="rId1" Type="%s" Target="worksheets/sheet1.xml"/>' % TYPE
        self.rejected(self.files(rels=rel+rel))
        self.rejected(self.files(sheets='<sheet name="x" r:id="rId1" r:id="rId1"/>'))
        self.rejected(self.files(sheets='<sheet name="x" r:id="rId1"/><sheet name="y" r:id="rId2"/>', rels=rel+'<Relationship Id="rId2" Type="%s" Target="./worksheets/sheet1.xml"/>' % TYPE))
    def test_date_metadata(self):
        for prop in ('', '<workbookPr/>', '<workbookPr date1904="false"/>', "<workbookPr date1904='0'/>"):
            with self.subTest(prop=prop): self.assertTrue(self.run_book(self.files(props=prop))['ok'])
        for prop in ('<workbookPr date1904="true"/>', "<workbookPr date1904='1'/>", '<workbookPr date1904="yes"/>', '<workbookPr date1904="0" date1904="1"/>', '<workbookPr/><workbookPr/>', '<x:workbookPr date1904="true"/>', '<workbookPr x:date1904="true"/>'):
            with self.subTest(prop=prop): self.rejected(self.files(props=prop))
        self.assertTrue(self.run_book(self.files(props='<!-- <workbookPr date1904="true"/> --><workbookPr date1904="0"/>'))['ok'])
        self.rejected(self.files(props='<!-- ignored --><workbookPr date1904="true"/>', sheet1='<worksheet><sheetData><row><c><v>45000</v></c></row></sheetData></worksheet>'))
    def test_legal_tag_whitespace_preserves_nonempty_values(self):
        sheet = '<worksheet><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t >Việt</t ></is ></c ><c r="B1"><f >1+1</f ><v >2</v ></c ><c r="C1" t="s"><v >0</v ></c ><c r="D1" t="b"><v >0</v ></c ></row ></sheetData ></worksheet >'
        f = self.files(sheet1=sheet)
        f['xl/sharedStrings.xml'] = '<sst><si ><t >Chuỗi</t ></si ></sst >'
        expected = [{'name':'Dữ liệu','rows':[['Việt',2,'Chuỗi',False]],'formulas':1,'nocache':0,'state':'visible'}]
        self.assertEqual(self.run_book(f), {'ok':True,'sheets':expected})
    def test_single_quoted_critical_attributes(self):
        f=self.files(sheets="<sheet name='Một' r:id='rId1'/>", rels="<Relationship Id='rId1' Type='%s' Target='../xl/worksheets/sheet1.xml'/>" % TYPE)
        self.assertEqual(self.run_book(f)['sheets'][0]['name'], 'Một')

if __name__ == '__main__': unittest.main()
