"""Optional, bounded, read-only source indicators; no legal verification."""
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

BYTE_LIMIT = 20 * 1024 * 1024
PAGE_LIMIT = 100
TIME_LIMIT = 15
ZIP_ENTRIES = 2000
ZIP_EXPANDED = 40 * 1024 * 1024
XML_LIMIT = 1024 * 1024


def pdf_worker():
    counts = []
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer
        raw = sys.stdin.buffer.read(BYTE_LIMIT + 1)
        if len(raw) > BYTE_LIMIT:
            print(json.dumps({'pages': [], 'reason': 'byte_limit'}))
            return
        for page in extract_pages(io.BytesIO(raw), maxpages=PAGE_LIMIT):
            counts.append(sum(sum(1 for c in item.get_text() if c.isprintable() and not c.isspace())
                              for item in page if isinstance(item, LTTextContainer)))
        reason = 'page_limit' if len(counts) == PAGE_LIMIT else ('' if counts else 'no_pages')
        print(json.dumps({'pages': counts, 'reason': reason}))
    except ImportError:
        print(json.dumps({'pages': [], 'reason': 'engine_missing'}))
    except Exception as exc:
        print(json.dumps({'pages': counts, 'reason': 'pdf_error:' + type(exc).__name__}))


def pdf_summary(raw):
    if len(raw) > BYTE_LIMIT:
        return {'pages': [], 'reason': 'byte_limit'}
    try:
        result = subprocess.run([sys.executable, os.path.abspath(__file__), '--pdf-worker'], input=raw,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=TIME_LIMIT, check=False)
        if result.returncode or len(result.stdout) > 32768:
            return {'pages': [], 'reason': 'worker_error'}
        result = json.loads(result.stdout.decode('utf-8'))
        if not isinstance(result.get('pages'), list) or len(result['pages']) > PAGE_LIMIT:
            raise ValueError('invalid worker output')
        return result
    except subprocess.TimeoutExpired:
        return {'pages': [], 'reason': 'time_limit'}
    except (OSError, ValueError, UnicodeError):
        return {'pages': [], 'reason': 'worker_error'}


class _NoDTD(ET.TreeBuilder):
    def doctype(self, name, pubid, system):
        raise ValueError('DTD is outside this bounded structure check')


def office_reason(raw, ext):
    expected = {'.docx': 'word/document.xml', '.xlsx': 'xl/workbook.xml', '.pptx': 'ppt/presentation.xml'}[ext]
    roots = {'.docx': '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document',
             '.xlsx': '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}workbook',
             '.pptx': '{http://schemas.openxmlformats.org/presentationml/2006/main}presentation'}
    types = {'.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml',
             '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml',
             '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entries = z.infolist()
            if len(entries) > ZIP_ENTRIES or sum(e.file_size for e in entries) > ZIP_EXPANDED:
                return 'zip_limit'
            names = [e.filename for e in entries]
            if (len(names) != len(set(names)) or '[Content_Types].xml' not in names or
                    expected not in names or '_rels/.rels' not in names):
                return 'wrong_office_structure'
            parsed = []
            for name in ('[Content_Types].xml', expected, '_rels/.rels'):
                info = z.getinfo(name)
                if info.file_size > XML_LIMIT:
                    return 'xml_limit'
                content = z.read(info)
                if b'<!DOCTYPE' in content.upper() or b'<!ENTITY' in content.upper():
                    return 'xml_dtd'
                parsed.append(ET.fromstring(content, parser=ET.XMLParser(target=_NoDTD())))
            ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
            if parsed[0].tag != '{%s}Types' % ns or parsed[1].tag != roots[ext] or not any(
                    e.tag == '{%s}Override' % ns and e.get('PartName') == '/' + expected and
                    e.get('ContentType') == types[ext] for e in parsed[0]):
                return 'wrong_office_structure'
            relns = 'http://schemas.openxmlformats.org/package/2006/relationships'
            reltype = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument'
            mainrels = [e for e in parsed[2] if e.tag == '{%s}Relationship' % relns and e.get('Type') == reltype]
            if (parsed[2].tag != '{%s}Relationships' % relns or len(mainrels) != 1 or
                    mainrels[0].get('TargetMode') == 'External' or
                    mainrels[0].get('Target') not in (expected, '/' + expected)):
                return 'wrong_office_structure'
        return ''
    except (ValueError, OSError, RuntimeError, zipfile.BadZipFile, ET.ParseError, NotImplementedError):
        return 'invalid_office'


def audit(root, rows, lib):
    warnings, cached, actual = [], {}, {}
    def warn(row, vi, en):
        warnings.append((row, lib.L(vi, en)))
    # Re-read and compare rows before using content binding from a single workbook snapshot.
    book = lib.read_book(root, require_columns=False)
    content = lib.content_find(root)
    binding_ok = (book.get('ok') and book['data'] == rows and content.get('ok') and
                  content.get('snapshot') == book.get('snapshot'))
    entries = content.get('entries', []) if binding_ok else []
    for rec in rows:
        n = rec['_row']
        ident = lib.fmt(rec.get('id'))
        sha = str(rec.get('law_sha') or '').strip().lower()
        if ident and lib.SHA256_RE.fullmatch(sha):
            prior = cached.setdefault(sha, {})
            for other, otherrow in prior.items():
                if other != ident:
                    warn(n, 'SHA đã ghi trùng ID %s (dòng %d); chưa chứng minh trùng nội dung hiện tại' % (other, otherrow),
                         'Cached SHA matches ID %s (row %d); current bytes not established' % (other, otherrow))
                    break
            prior[ident] = n
        path = lib.norm_path(rec.get('file'))
        if not path:
            continue
        full, why = lib.locate_source(root, path)
        if full is None:
            warn(n, 'chưa đọc nguồn trong phạm vi: %s' % why, 'source bytes not read within scope: %s' % why)
            if lib.fold(rec.get('verify')) == 'da doi chieu toan van':
                warn(n, 'chưa kiểm binding: không đọc được bytes nguồn', 'binding not checked: source bytes unavailable')
            continue
        try:
            before = os.stat(full)
            with open(full, 'rb') as stream:
                raw = stream.read(BYTE_LIMIT + 1)
            after = os.stat(full)
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise ValueError('source_changed_during_read')
            if len(raw) > BYTE_LIMIT:
                raise ValueError('byte_limit')
        except (OSError, ValueError) as exc:
            warn(n, 'chưa kiểm nguồn/lớp chữ: %s' % exc, 'source/text layer not checked: %s' % exc)
            if lib.fold(rec.get('verify')) == 'da doi chieu toan van':
                warn(n, 'chưa kiểm binding: không đọc được bytes nguồn', 'binding not checked: source bytes unavailable')
            continue
        digest = hashlib.sha256(raw).hexdigest()
        if not lib.SHA256_RE.fullmatch(sha):
            warn(n, 'thiếu SHA hợp lệ trong sổ; chưa có căn cứ đối chiếu bytes', 'valid cached SHA missing; bytes basis unavailable')
        elif sha != digest:
            warn(n, 'SHA file thực khác sổ; bytes chưa đồng bộ', 'actual SHA differs from index; bytes are unsynced')
        if ident:
            prior = actual.setdefault(digest, {})
            for other, otherrow in prior.items():
                if other != ident:
                    warn(n, 'SHA file thực trùng ID %s (dòng %d); cần xem xét, không tự gộp' % (other, otherrow),
                         'actual SHA matches ID %s (row %d); review, do not merge automatically' % (other, otherrow))
                    break
            prior[ident] = n
        if lib.fold(rec.get('verify')) == 'da doi chieu toan van':
            bound = [e for e in entries if e['source_id'] == ident and e['check_level'] == 'DECLARED_CHECK'
                     and not e['superseded_by'] and e['basis_state'] == 'CURRENT_CATALOG_BASIS'
                     and e['source_path'] == path and e['source_sha256'] == digest]
            if bound:
                warn(n, 'có lời khai kiểm gắn revision/SHA trong phạm vi %s; chưa chứng thực lời khai hoặc toàn văn' % bound[0]['check_scope'],
                     'declared check bound to revision/SHA within scope %s; declaration and full text not verified' % bound[0]['check_scope'])
            else:
                reason = 'no_matching_declaration' if binding_ok else 'content_sheet_unavailable_or_changed'
                warn(n, 'thiếu căn cứ gắn lời khai kiểm với revision/SHA (%s)' % reason,
                     'missing declared-check binding to revision/SHA (%s)' % reason)
        ext = os.path.splitext(path)[1].lower()
        if ext == '.pdf':
            if not raw.startswith(b'%PDF-'):
                warn(n, 'chưa kiểm lớp chữ: không có chữ ký PDF', 'text layer not checked: PDF signature missing')
                continue
            result = pdf_summary(raw)
            for i, count in enumerate(result['pages'], 1):
                if count < 300:
                    warn(n, 'PDF trang %d: %d ký tự; mật độ thấp là dấu hiệu cần kiểm, không kết luận bản quét' % (i, count),
                         'PDF page %d: %d characters; low density is an indicator, not a scan determination' % (i, count))
            if result['reason']:
                warn(n, 'chưa kiểm lớp chữ đầy đủ (%d trang có kết quả ghi nhận): %s' % (len(result['pages']), result['reason']),
                     'text layer not fully checked (%d pages with recorded results): %s' % (len(result['pages']), result['reason']))
            else:
                warn(n, 'đã khảo sát lớp chữ %d trang; không xác minh toàn văn' % len(result['pages']),
                     'text layer surveyed on %d pages; full text not verified' % len(result['pages']))
        elif ext in ('.docx', '.xlsx', '.pptx'):
            reason = office_reason(raw, ext)
            if reason:
                warn(n, 'cấu trúc Office sai hoặc chưa kiểm: %s' % reason, 'Office structure invalid or not checked: %s' % reason)
    return warnings


if __name__ == '__main__' and sys.argv[1:] == ['--pdf-worker']:
    pdf_worker()
