/*
 * xlsx-mini-reader.js — đọc .xlsx KHÔNG cần thư viện ngoài, chạy trong trình duyệt hiện đại và Node 18+.
 * Reads .xlsx with NO external library, in modern browsers and Node 18+.
 *
 * Dùng / Usage:
 *   const sheets = await readXlsx(arrayBuffer);   // [{name, rows, formulas, nocache}]
 *   // rows: mảng các dòng, mỗi dòng là mảng ô (null = ô trống). Chỉ số dòng/cột bắt đầu từ 0; rows[i] ứng với dòng Excel i+1.
 *   // Ngày theo hệ 1900 là số serial; đổi theo cột ở phía người dùng. Hệ 1904 bị từ chối. Ô công thức không có cache -> null
 *   //   và được đếm vào `nocache` (file tạo bằng openpyxl chưa mở/lưu trong Excel thì như vậy).
 *
 * Giới hạn / Limits: chỉ đọc giá trị; không đọc định dạng, ngày (đổi serial -> ngày), ô gộp, công thức, file mã hóa/.xls/.xlsb.
 * Cần DecompressionStream('deflate-raw') (Chrome/Edge 80+, Firefox 113+, Safari 16.4+, Node 18+). Thiếu thì báo lỗi rõ, không đoán.
 * Nhúng nguyên file này vào <script> của công cụ HTML (không CDN). Luôn thử với file .xlsx THẬT của người dùng trước khi giao.
 */
(function (root) {
  'use strict';

  function u16(b, o) { return b[o] | (b[o + 1] << 8); }
  function u32(b, o) { return (b[o] | (b[o + 1] << 8) | (b[o + 2] << 16) | (b[o + 3] << 24)) >>> 0; }

  async function inflateRaw(bytes) {
    if (typeof DecompressionStream === 'undefined') throw new Error('Trình duyệt chưa hỗ trợ DecompressionStream; dùng bản mới hơn hoặc nhúng thư viện đọc Excel.');
    const ds = new DecompressionStream('deflate-raw');
    const out = new Response(new Blob([bytes]).stream().pipeThrough(ds));
    return new Uint8Array(await out.arrayBuffer());
  }

  // ---- ZIP: đọc danh mục trung tâm rồi giải nén từng mục khi cần
  function zipIndex(b) {
    let eocd = -1;
    for (let i = b.length - 22; i >= Math.max(0, b.length - 65557); i--) {
      if (u32(b, i) === 0x06054b50) { eocd = i; break; }
    }
    if (eocd < 0) throw new Error('Không phải file .xlsx (thiếu cấu trúc ZIP).');
    const n = u16(b, eocd + 10);
    let p = u32(b, eocd + 16);
    const files = Object.create(null);
    for (let k = 0; k < n; k++) {
      if (u32(b, p) !== 0x02014b50) throw new Error('ZIP hỏng (danh mục trung tâm).');
      const method = u16(b, p + 10), csize = u32(b, p + 20), nlen = u16(b, p + 28), elen = u16(b, p + 30), clen = u16(b, p + 32), off = u32(b, p + 42);
      const name = new TextDecoder().decode(b.subarray(p + 46, p + 46 + nlen));
      if (Object.prototype.hasOwnProperty.call(files, name)) files[name] = null;
      else files[name] = { method, csize, off };
      p += 46 + nlen + elen + clen;
    }
    return files;
  }
  async function zipRead(b, files, name) {
    const f = files[name];
    if (!Object.prototype.hasOwnProperty.call(files, name)) return null;
    if (!f) throw new Error('ZIP có mục trùng: ' + name);
    if (u32(b, f.off) !== 0x04034b50) throw new Error('ZIP hỏng (đầu mục ' + name + ').');
    const start = f.off + 30 + u16(b, f.off + 26) + u16(b, f.off + 28);
    const raw = b.subarray(start, start + f.csize);
    if (f.method === 0) return new TextDecoder().decode(raw);
    if (f.method === 8) return new TextDecoder().decode(await inflateRaw(raw));
    throw new Error('Kiểu nén ZIP chưa hỗ trợ: ' + f.method);
  }

  // ---- XML nhẹ bằng regex (đủ cho cấu trúc cố định của .xlsx)
  function unesc(s) {
    return s.replace(/\r\n?/g, '\n').replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCodePoint(parseInt(h, 16)))
      .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(+d))
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&');
  }
  function attrs(s) {
    const o = Object.create(null); const re = /([\w:.-]+)\s*=\s*(["'])([\s\S]*?)\2/g; let m, pos = 0;
    while ((m = re.exec(s))) {
      if (s.slice(pos, m.index).trim() || Object.prototype.hasOwnProperty.call(o, m[1])) throw new Error('Thuộc tính XML không hợp lệ hoặc bị trùng.');
      o[m[1]] = unesc(m[3]); pos = re.lastIndex;
    }
    if (s.slice(pos).replace(/\/\s*$/, '').trim()) throw new Error('Thuộc tính XML không được hỗ trợ.');
    return o;
  }
  function criticalXml(xml, rootName) {
    if (!xml) throw new Error('Thiếu XML ' + rootName + '.');
    // Comments are not markup; prefixed elements are rejected rather than silently ignored.
    xml = xml.replace(/<!--[\s\S]*?-->/g, '');
    if (/<!--|-->|<!DOCTYPE|<!ENTITY|<\/?[\w.-]+:/.test(xml)) throw new Error('Cú pháp XML chưa hỗ trợ: ' + rootName);
    const clean = xml.replace(/^\s*<\?xml[\s\S]*?\?>/, '').trim();
    const root = new RegExp('^<' + rootName + '(?:\\s[^>]*)?>[\\s\\S]*<\\/' + rootName + '\\s*>$');
    if (!root.test(clean)) throw new Error('XML không hợp lệ hoặc không phải ' + rootName + '.');
    // Basic structural checks only; unsupported XML syntax fails closed, not a full XML engine.
    const tags = /<([^>]*)>/g, stack = []; let token, pos = 0;
    while ((token = tags.exec(clean))) {
      if (/[<>]/.test(clean.slice(pos, token.index))) throw new Error('XML không hợp lệ: ' + rootName);
      const t = token[1], close = /^\/([\w.-]+)\s*$/.exec(t);
      if (close) {
        if (stack.pop() !== close[1]) throw new Error('XML đóng thẻ không khớp: ' + rootName);
      } else {
        const open = /^([\w.-]+)([\s\S]*)$/.exec(t);
        if (!open) throw new Error('Cú pháp XML chưa hỗ trợ: ' + rootName);
        attrs(open[2]);
        if (!/\/\s*$/.test(open[2])) stack.push(open[1]);
      }
      pos = tags.lastIndex;
    }
    if (stack.length || /[<>]/.test(clean.slice(pos))) throw new Error('XML chưa hoàn chỉnh: ' + rootName);
    return clean;
  }
  function internalTarget(target) {
    if (!target || /[\\\\?#%]/.test(target) || /^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith('//')) throw new Error('Đích relationship không được hỗ trợ.');
    const parts = target.startsWith('/') ? [] : ['xl'];
    for (const part of target.split('/')) {
      if (!part || part === '.') continue;
      if (part === '..') { if (!parts.length) throw new Error('Đích relationship vượt ZIP.'); parts.pop(); }
      else parts.push(part);
    }
    if (!parts.length) throw new Error('Đích relationship rỗng.');
    return parts.join('/');
  }
  function textOf(xml) { // nối mọi <t>, bỏ phần phiên âm <rPh>
    xml = xml.replace(/<rPh[\s\S]*?<\/rPh\s*>/g, '');
    let out = ''; const re = /<t(?:\s[^>]*)?>([\s\S]*?)<\/t\s*>/g; let m;
    while ((m = re.exec(xml))) out += m[1];
    return unesc(out);
  }
  function colIndex(ref) {
    const m = /^([A-Z]+)/.exec(ref); let n = 0;
    for (const ch of m[1]) n = n * 26 + (ch.charCodeAt(0) - 64);
    return n - 1;
  }

  async function readXlsx(arrayBuffer) {
    const b = new Uint8Array(arrayBuffer);
    const files = zipIndex(b);
    const wbXml = criticalXml(await zipRead(b, files, 'xl/workbook.xml'), 'workbook');
    const props = wbXml.match(/<workbookPr\b[^>]*>/g) || [];
    if (props.length > 1) throw new Error('workbookPr bị trùng.');
    if (props.length) {
      const a = attrs(props[0].replace(/^<workbookPr\b/, '').replace(/>$/, ''));
      if (Object.keys(a).some(k => /(^|:)date1904$/.test(k) && k !== 'date1904')) throw new Error('date1904 chưa hỗ trợ namespace.');
      if (a.date1904 !== undefined && !['0', '1', 'false', 'true'].includes(a.date1904)) throw new Error('date1904 không hợp lệ.');
      if (a.date1904 === '1' || a.date1904 === 'true') throw new Error('Hệ ngày Excel 1904 chưa được hỗ trợ.');
    }
    const relsXml = criticalXml(await zipRead(b, files, 'xl/_rels/workbook.xml.rels'), 'Relationships');
    const rels = Object.create(null);
    (relsXml.match(/<Relationship\b[^>]*>/g) || []).forEach(t => {
      const a = attrs(t.replace(/^<Relationship\b/, '').replace(/>$/, ''));
      if (!a.Id || Object.prototype.hasOwnProperty.call(rels, a.Id)) throw new Error('Relationship thiếu hoặc trùng Id.');
      rels[a.Id] = a;
    });
    const ssXml = await zipRead(b, files, 'xl/sharedStrings.xml');
    const shared = ssXml ? (ssXml.match(/<si\b[\s\S]*?<\/si\s*>/g) || []).map(textOf) : [];
    const sheets = [];
    const list = wbXml.match(/<sheet\b[^>]*>/g) || [];
    if (!list.length) throw new Error('Không thấy sheet được khai báo.');
    const usedTargets = new Set(), usedIds = new Set();
    for (let i = 0; i < list.length; i++) {
      const a = attrs(list[i].replace(/^<sheet\b/, '').replace(/>$/, ''));
      const id = a['r:id'];
      if (!a.name || !id || usedIds.has(id) || !rels[id]) throw new Error('Sheet thiếu hoặc trùng relationship.');
      usedIds.add(id);
      const rel = rels[id];
      if (rel.TargetMode && rel.TargetMode !== 'Internal') throw new Error('Relationship ngoài không được hỗ trợ.');
      if (!/^http:\/\/(schemas\.openxmlformats\.org\/officeDocument\/2006|purl\.oclc\.org\/ooxml\/officeDocument)\/relationships\/worksheet$/.test(rel.Type || '')) throw new Error('Relationship không phải worksheet được hỗ trợ.');
      const target = internalTarget(rel.Target);
      if (usedTargets.has(target)) throw new Error('Nhiều sheet dùng cùng một part.');
      usedTargets.add(target);
      const xml = criticalXml(await zipRead(b, files, target), 'worksheet');
      const dataTags = xml.match(/<sheetData\b[^>]*\/>|<sheetData\b[^>]*>[\s\S]*?<\/sheetData\s*>/g) || [];
      if (dataTags.length !== 1 || (xml.match(/<sheetData\b/g) || []).length !== 1) throw new Error('sheetData thiếu hoặc không hợp lệ.');
      const dataBody = dataTags[0].replace(/^<sheetData\b[^>]*>/, '').replace(/<\/sheetData\s*>$/, '');
      if (!/^<sheetData\b[^>]*\/>$/.test(dataTags[0]) && dataBody.replace(/<row\b[^>]*\/>|<row\b[^>]*>[\s\S]*?<\/row\s*>/g, '').trim()) throw new Error('Nội dung sheetData chưa hỗ trợ.');
      const sh = { name: a.name, rows: [], formulas: 0, nocache: 0, state: a.state || 'visible' };
      const cellRe = /<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c\s*>)/g; let m;
      let rowCursor = -1;
      const rowRe = /<row\b([^>]*?)(?:\/>|>([\s\S]*?)<\/row\s*>)/g; let rm;
      while ((rm = rowRe.exec(dataTags[0]))) {
        const ra = attrs(rm[1]);
        const ri = ra.r ? (+ra.r - 1) : (rowCursor + 1);
        rowCursor = ri;
        const body = rm[2] || '';
        const row = [];
        cellRe.lastIndex = 0;
        let ci = -1;
        while ((m = cellRe.exec(body))) {
          const ca = attrs(m[1]); const inner = m[2] || '';
          ci = ca.r ? colIndex(ca.r) : ci + 1;
          const hasF = /<f\b/.test(inner);
          if (hasF) sh.formulas++;
          const vm = /<v\s*>([\s\S]*?)<\/v\s*>/.exec(inner);
          let val = null;
          if (ca.t === 'inlineStr') val = textOf(inner);
          else if (vm) {
            const raw = unesc(vm[1]);
            if (ca.t === 's') val = shared[+raw] != null ? shared[+raw] : null;
            else if (ca.t === 'b') val = raw === '1';
            else if (ca.t === 'str' || ca.t === 'e') val = raw;
            else { const num = Number(raw); val = raw !== '' && !isNaN(num) ? num : raw; }
          }
          if (hasF && (!vm || vm[1] === '')) sh.nocache++;
          if (val !== null && val !== '') { while (row.length < ci) row.push(null); row[ci] = val; }
        }
        while (sh.rows.length < ri) sh.rows.push([]);
        sh.rows[ri] = row;
      }
      sheets.push(sh);
    }
    return sheets;
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { readXlsx };
  root.readXlsx = readXlsx;
})(typeof window !== 'undefined' ? window : globalThis);
