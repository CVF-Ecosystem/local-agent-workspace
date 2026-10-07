/*
 * xlsx-mini-reader.js — đọc .xlsx KHÔNG cần thư viện ngoài, chạy trong trình duyệt hiện đại và Node 18+.
 * Reads .xlsx with NO external library, in modern browsers and Node 18+.
 *
 * Dùng / Usage:
 *   const sheets = await readXlsx(arrayBuffer);   // [{name, rows, formulas, nocache}]
 *   // rows: mảng các dòng, mỗi dòng là mảng ô (null = ô trống). Chỉ số dòng/cột bắt đầu từ 0; rows[i] ứng với dòng Excel i+1.
 *   // Ngày trong Excel là số serial (số ngày từ 1899-12-30): tự đổi ở phía người dùng. Ô công thức không có giá trị đã tính -> null
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
    const files = {};
    for (let k = 0; k < n; k++) {
      if (u32(b, p) !== 0x02014b50) throw new Error('ZIP hỏng (danh mục trung tâm).');
      const method = u16(b, p + 10), csize = u32(b, p + 20), nlen = u16(b, p + 28), elen = u16(b, p + 30), clen = u16(b, p + 32), off = u32(b, p + 42);
      const name = new TextDecoder().decode(b.subarray(p + 46, p + 46 + nlen));
      files[name] = { method, csize, off };
      p += 46 + nlen + elen + clen;
    }
    return files;
  }
  async function zipRead(b, files, name) {
    const f = files[name];
    if (!f) return null;
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
    const o = {}; const re = /([\w:.-]+)\s*=\s*"([^"]*)"/g; let m;
    while ((m = re.exec(s))) o[m[1]] = unesc(m[2]);
    return o;
  }
  function textOf(xml) { // nối mọi <t>, bỏ phần phiên âm <rPh>
    xml = xml.replace(/<rPh[\s\S]*?<\/rPh>/g, '');
    let out = ''; const re = /<t(?:\s[^>]*)?>([\s\S]*?)<\/t>/g; let m;
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
    const wbXml = await zipRead(b, files, 'xl/workbook.xml');
    if (!wbXml) throw new Error('Không thấy xl/workbook.xml: đây không phải sổ Excel .xlsx.');
    const relsXml = (await zipRead(b, files, 'xl/_rels/workbook.xml.rels')) || '';
    const rels = {};
    (relsXml.match(/<Relationship\b[^>]*>/g) || []).forEach(t => { const a = attrs(t); rels[a.Id] = a.Target; });
    const ssXml = await zipRead(b, files, 'xl/sharedStrings.xml');
    const shared = ssXml ? (ssXml.match(/<si\b[\s\S]*?<\/si>/g) || []).map(textOf) : [];

    const sheets = [];
    const list = wbXml.match(/<sheet\b[^>]*>/g) || [];
    for (let i = 0; i < list.length; i++) {
      const a = attrs(list[i]);
      let target = rels[a['r:id']] || ('worksheets/sheet' + (i + 1) + '.xml');
      target = target.replace(/^\/?(xl\/)?/, 'xl/');
      const xml = await zipRead(b, files, target);
      const sh = { name: a.name, rows: [], formulas: 0, nocache: 0, state: a.state || 'visible' };
      if (!xml) { sheets.push(sh); continue; }
      const cellRe = /<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g; let m;
      let rowCursor = -1;
      const rowRe = /<row\b([^>]*?)(?:\/>|>([\s\S]*?)<\/row>)/g; let rm;
      while ((rm = rowRe.exec(xml))) {
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
          const vm = /<v>([\s\S]*?)<\/v>/.exec(inner);
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
