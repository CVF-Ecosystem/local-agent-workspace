"""Synthetic observable DOCX checks; optional render deps never affect stdlib checks."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_output as co
import vn_legal_docx as render

W = co.W
HAS_DEPS = importlib.util.find_spec('docx') is not None and importlib.util.find_spec('bs4') is not None


def run(*args):
    return subprocess.run([sys.executable] + list(map(str, args)), capture_output=True, text=True, encoding='utf-8')


class Layout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def fixture(self, name='test.docx', title=False, dims=(11906, 16838), margin=1134,
                font='Times New Roman', size=26):
        p = self.root / name
        text = (co.QUOC_HIEU + ' ') if title else ''
        text += 'Nội dung tổng hợp dùng kiểm tra cơ học.'
        doc = '<w:document xmlns:w="%s"><w:body><w:p><w:pPr><w:pStyle w:val="Body"/></w:pPr><w:r><w:t>%s</w:t></w:r></w:p><w:sectPr><w:pgSz w:w="%s" w:h="%s"/><w:pgMar w:top="%s" w:bottom="1134" w:left="1701" w:right="1134"/></w:sectPr></w:body></w:document>' % (W[1:-1], text, dims[0], dims[1], margin)
        styles = '<w:styles xmlns:w="%s"><w:style w:styleId="Base"><w:rPr><w:rFonts w:ascii="%s"/><w:sz w:val="%s"/></w:rPr></w:style><w:style w:styleId="Body"><w:basedOn w:val="Base"/></w:style></w:styles>' % (W[1:-1], font, size)
        with zipfile.ZipFile(p, 'w') as z:
            z.writestr('word/document.xml', doc)
            z.writestr('word/styles.xml', styles)
        return p

    def test_valid_auto_and_forced_inherited_style(self):
        for title, profile in ((True, 'auto'), (False, 'nd30')):
            self.assertEqual(co.check_docx_layout(self.fixture(title=title), profile), ([], []))

    def test_wrong_paper_margins_font_size(self):
        p = self.fixture(title=True, dims=(12240, 15840), margin=200, font='Arial', size=20)
        must, note = co.check_docx_layout(p)
        self.assertEqual(len(must), 4, (must, note))
        self.assertEqual(co.check_docx_layout(p, 'none'), ([], []))

    def test_generic_letter_is_valid(self):
        p = self.fixture(dims=(12240, 15840), font='Arial', size=22)
        self.assertEqual(co.check_docx_layout(p), ([], []))
        self.assertEqual(run(ROOT / 'tools/check_output.py', p, '--lang', 'en').returncode, 0)

    def test_long_document_page_warning(self):
        p = self.fixture(title=True)
        with zipfile.ZipFile(p) as z:
            doc = z.read('word/document.xml').decode('utf-8')
            styles = z.read('word/styles.xml')
        start, end = doc.index('<w:p>'), doc.index('</w:p>') + len('</w:p>')
        doc = doc[:start] + doc[start:end] * 41 + doc[end:]
        with zipfile.ZipFile(p, 'w') as z:
            z.writestr('word/document.xml', doc)
            z.writestr('word/styles.xml', styles)
        must, note = co.check_docx_layout(p)
        self.assertEqual(must, []); self.assertEqual(len(note), 1)
        self.assertEqual(co.check_docx_layout(p, 'none'), ([], []))
        for field, expected_notes in (
                ('<w:r><w:t>PAGE</w:t></w:r>', 1),
                ('<w:fldSimple w:instr=" PAGE "/>', 0),
                ('<w:r><w:instrText> PAGE </w:instrText></w:r>', 0)):
            with self.subTest(field=field):
                with zipfile.ZipFile(p, 'w') as z:
                    z.writestr('word/document.xml', doc)
                    z.writestr('word/styles.xml', styles)
                    z.writestr('word/header1.xml', '<w:hdr xmlns:w="%s"><w:p>%s</w:p></w:hdr>' % (W[1:-1], field))
                self.assertEqual(len(co.check_docx_layout(p)[1]), expected_notes)

    def test_missing_corrupt_unsupported_not_pass(self):
        bad = self.root / 'bad.docx'; bad.write_bytes(b'not a zip')
        other = self.root / 'file.bin'; other.write_bytes(b'x')
        for p in (bad, other, self.root / 'missing.docx'):
            self.assertEqual(run(ROOT / 'tools/check_output.py', p).returncode, 2)

    def test_stdlib_without_site_and_import_side_effects(self):
        p = self.fixture(title=True)
        md = self.root / 'note.md'; md.write_text('A completed note with ordinary content.', encoding='utf-8')
        for file in (md, p):
            self.assertEqual(run('-S', ROOT / 'tools/check_output.py', file).returncode, 0)
        code = "import sys;sys.path.insert(0,sys.argv[1]);old=sys.stdout.encoding;import check_output;assert 'docx' not in sys.modules and 'bs4' not in sys.modules and 'vn_legal_docx' not in sys.modules;assert sys.stdout.encoding==old"
        self.assertEqual(run('-S', '-c', code, ROOT / 'tools').returncode, 0)

    def test_missing_render_dependencies_no_output(self):
        src = self.root / 'in.html'; src.write_text('<p>Supported text.</p>', encoding='utf-8')
        out = self.root / 'new' / 'out.docx'
        res = run('-S', ROOT / 'tools/vn_legal_docx.py', src, out)
        self.assertEqual(res.returncode, 2)
        self.assertIn('beautifulsoup4', res.stderr)
        self.assertFalse(out.parent.exists())


@unittest.skipUnless(HAS_DEPS, 'optional beautifulsoup4/python-docx unavailable')
class Renderer(unittest.TestCase):
    setUp = Layout.setUp
    def test_constants_match_reference(self):
        errors, found = render.spec_check()
        self.assertTrue(found); self.assertEqual(errors, [])
        for key, value in co.ND30_RULES.items():
            self.assertEqual(render.ND30_RULES[key], value)

    def test_header_signature_amendments_and_table_spans(self):
        source = '<div id="toanvancontent"><table><tr><td>ĐƠN VỊ THỬ</td><td>' + co.QUOC_HIEU + '<br>Độc lập - Tự do - Hạnh phúc</td></tr></table><p>Điều 1. Nội dung thử.</p><p>Chương II được sửa đổi như sau:</p><p>Mục 2 Chương III được bãi bỏ.</p><table><tr><th colspan="2">Hai cột</th></tr><tr><td rowspan="2">Gộp hàng</td><td>Ô A</td></tr><tr><td>Ô B</td></tr></table><table><tr><td>Nơi nhận:</td><td>KT. BỘ TRƯỞNG THỨ TRƯỞNG Người Thử</td></tr><tr><td>Lưu: VT.</td><td>TL. BỘ TRƯỞNG VỤ TRƯỞNG Người Mẫu</td></tr></table></div>'
        p = self.root / 'render.docx'; render.html_to_docx(source, p, quiet=True)
        with zipfile.ZipFile(p) as z:
            doc = ET.fromstring(z.read('word/document.xml'))
            text = ''.join(doc.itertext())
            self.assertEqual(text.count(co.QUOC_HIEU), 1)
            for value in ('Hai cột', 'Gộp hàng', 'Ô A', 'Ô B', 'KT. BỘ TRƯỞNG', 'THỨ TRƯỞNG', 'Người Thử', 'TL. BỘ TRƯỞNG', 'VỤ TRƯỞNG', 'Người Mẫu'):
                self.assertEqual(text.count(value), 1, value)
            tables = list(doc.iter(W + 'tbl')); self.assertEqual(len(tables), 3)
            self.assertIsNone(tables[0].find('.//' + W + 'tblBorders'))
            self.assertIsNotNone(tables[1].find('.//' + W + 'gridSpan'))
            self.assertIsNotNone(tables[1].find('.//' + W + 'vMerge'))
            self.assertIsNone(tables[2].find('.//' + W + 'tblStyle'))
            for para in doc.iter(W + 'p'):
                if co._ptext(para).startswith(('Chương II', 'Mục 2')):
                    self.assertIsNone(para.find('.//' + W + 'outlineLvl'))
                    self.assertIsNone(para.find('.//' + W + 'b'))
            self.assertIn('PAGE', z.read('word/header1.xml').decode('utf-8'))
            self.assertNotIn('Văn bản quy phạm pháp luật', z.read('docProps/core.xml').decode('utf-8'))

    def test_known_loss_refused_before_write(self):
        cases = ['<p>Image<img src="x"/></p>', '<table><tr><td>Outer<table><tr><td>Inner</td></tr></table></td></tr></table>', '<table><tr><td colspan="x">Text</td></tr></table>', '<table><tr><td colspan="65">Text</td></tr></table>', '<table><tr><td rowspan="2">Text</td></tr></table>', '<ol><li>Automatic number</li></ol>', '<p>x<sup>2</sup></p>', '<div id="toanvancontent" style="display:none"><p>Hidden content.</p></div>', '<div id="toanvancontent" hidden><p>Hidden content.</p></div>']
        cases.append('<p style="text-decoration:line-through">Withdrawn text.</p>')
        for i, source in enumerate(cases):
            out = self.root / ('missing%d' % i) / 'out.docx'
            with self.subTest(source=source), self.assertRaises(render.UnsupportedHTML):
                render.html_to_docx(source, out, quiet=True)
            self.assertFalse(out.parent.exists())
            existing = self.root / 'preserved.docx'; existing.write_bytes(b'preserve unsupported')
            with self.assertRaises(render.UnsupportedHTML):
                render.html_to_docx(source, existing, quiet=True, overwrite=True)
            self.assertEqual(existing.read_bytes(), b'preserve unsupported')

    def test_selected_content_ignores_external_logo(self):
        p = self.root / 'selected.docx'
        render.html_to_docx('<img src="logo"><div id="toanvancontent"><p>Selected text remains.</p></div>', p, quiet=True)
        self.assertEqual(co.text_of(p).strip().splitlines()[0], 'Selected text remains.')

    def test_existing_output_and_source_preserved_api_cli(self):
        out = self.root / 'out.docx'; out.write_bytes(b'keep existing')
        src = self.root / 'in.html'; src.write_text('<p>Supported text.</p>', encoding='utf-8'); before = src.read_bytes()
        with self.assertRaises(FileExistsError):
            render.html_to_docx(src.read_text(), out, quiet=True)
        self.assertEqual(run(ROOT / 'tools/vn_legal_docx.py', src, out).returncode, 2)
        self.assertEqual(out.read_bytes(), b'keep existing'); self.assertEqual(src.read_bytes(), before)
        self.assertEqual(run(ROOT / 'tools/vn_legal_docx.py', src, src, '--overwrite').returncode, 2)
        self.assertEqual(src.read_bytes(), before)

    def test_helper_copy_portable_and_nd30_workspace_only(self):
        helper = ROOT / 'skills/local/shared/office-documents/scripts/docx_helpers.py'
        copied = self.root / 'docx_helpers.py'; shutil.copyfile(helper, copied)
        code = """import sys
sys.path.insert(0, sys.argv[1])
import docx_helpers as h
d = h.new_document()
h.add_table(d, ['Header'], [['Text']])
d.save(sys.argv[2])
assert len(d.tables) == 1
try:
    h.new_nd30_document()
except FileNotFoundError:
    pass
else:
    raise AssertionError('ND30 unexpectedly available outside LAW')
"""
        out = self.root / 'portable.docx'
        result = run('-c', code, self.root, out)
        self.assertEqual(result.returncode, 0, result.stderr); self.assertTrue(out.exists())
        spec = importlib.util.spec_from_file_location('law_docx_helper', helper)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        d = module.new_nd30_document('Synthetic')
        self.assertEqual(d.core_properties.subject, '')


if __name__ == '__main__':
    unittest.main()
