#!/usr/bin/env python3
"""Công cụ tính hẹp cho vai văn phòng (V4), CHỈ ĐỌC. / Narrow compute tool for the office roles, READ ONLY.

Dùng (mã chạy từ cây LAW cố định, dữ liệu ở project) / Usage (code from the fixed LAW tree, data in the project):
  python -X utf8 -B tools/office_compute.py run --project ROOT --request FILE|-    một phép tính định sẵn trên CSV / one preset calculation on CSV
  python -X utf8 -B tools/office_compute.py canary [--client C --client-version V --observed-by WHO]   canary vô hại, không đọc file / harmless canary, reads no file

Mã thoát / exit codes: 0 đạt; 1 bị từ chối (JSON `outcome=REFUSED` ở stdout); 2 lỗi dùng.

Phép tính chỉ gồm `aggregate` (lọc, nhóm, đếm, tổng, tổng tích, trung bình gia quyền) và `compare_prices` (so giá cùng kỳ/loại giá/tiền tệ,
đổi đơn vị theo hệ số được nêu) trên Decimal. Không eval/exec, không shell, không mạng, không import mã từ dữ liệu, không ghi file.
Chỉ đọc đúng các file CSV mà TASK hiện hành liệt kê trong `inputs` (khớp path và digest), sau khi qua TASK, marker phương pháp,
quyền của lab (scope) và thao tác. Kết quả và vết chỉ ra stdout; không có tác động ngoài đọc.
`actor` do người gọi khai, không được xác thực; digest chỉ kiểm bytes; đây không phải sandbox, grant hay bằng chứng host đã cấp công cụ cho vai.
Only the preset operations above run, on Decimal. No eval/exec, shell, network, code import from data, or writes. It reads only the CSV files the
current TASK lists in `inputs` (path and digest match), after the TASK, method marker, lab scope permission and operation checks. Results go to stdout.
`actor` is caller-declared and unauthenticated; digests check bytes only; this is not a sandbox, a grant or proof the host gave the role a tool.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import platform
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, localcontext

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import office  # noqa: E402  (read_rel, parse_json, guard_task, SOURCE_ZONES)
import publish_new  # noqa: E402  (path_form_problem)

SCHEMA_REQUEST = 'law.office-compute/1'
SCHEMA_RESULT = 'law.office-compute-result/1'
SCHEMA_PROBE = 'law.office-compute-probe/1'
SCHEMA_SCOPE = 'law.office-compute-scope/1'
SCHEMA_ROUTE = 'law.office-compute-route/1'
OPERATIONS = ('aggregate', 'compare_prices')
REQUEST_KEYS = ('schema', 'actor', 'task', 'scope', 'operation', 'inputs', 'params')
TASK_KEYS = ('path', 'task_id', 'task_revision', 'digest')
MAX_REQUEST = 64 * 1024
MAX_SCOPE = 16 * 1024
MAX_TASK = 256 * 1024
MAX_CSV = 2 * 1024 * 1024
MAX_ROWS = 50000
MAX_INPUTS = 4

NAME_RE = re.compile(r'^[a-z][a-z0-9_]{0,30}$')
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
CELL_INT = re.compile(r'^-?\d{1,18}$')
CELL_DEC = re.compile(r'^-?\d{1,18}\.(\d{1,2}|\d{4,9})$')
CELL_GROUPED = re.compile(r'^-?\d{1,3}([.,]\d{3})+$')
CELL_TRIPLE = re.compile(r'^-?\d{1,18}[.,]\d{3}$')
CELL_COMMA = re.compile(r'^-?\d{1,18},\d{1,9}$')
CONTROL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
MARKER_ID_RE = re.compile(r'^OFFICE-METHOD:([a-z][a-z0-9-]{1,62}):v[1-9][0-9]{0,5}$')
PRICE_COLUMNS = ('id', 'period', 'unit', 'price_type', 'currency', 'price')

MESSAGES = {
    'REQUEST_INVALID': ('Yêu cầu tính không hợp lệ.', 'The compute request is invalid.'),
    'TASK_REFUSED': ('TASK không hợp lệ hoặc không khớp yêu cầu.', 'The TASK is invalid or does not match the request.'),
    'SCOPE_REFUSED': ('Phạm vi hoặc quyền của lab không cho phép phép tính này.', 'The lab scope or permission does not allow this calculation.'),
    'INPUT_REFUSED': ('Nguồn không nằm trong inputs của TASK hoặc không đọc được.', 'The source is not a TASK input or cannot be read.'),
    'PARAMS_INVALID': ('Tham số của phép tính không hợp lệ.', 'The operation parameters are invalid.'),
    'DATA_REFUSED': ('Dữ liệu CSV không đọc được theo cấu trúc đã nêu.', 'The CSV data cannot be read as described.'),
}


def sha_of(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def canon(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')


def msg(stage):
    pair = MESSAGES.get(stage)
    return '%s / %s' % pair if pair else stage


class Refused(Exception):
    def __init__(self, stage, code):
        super().__init__('%s: %s' % (stage, code))
        self.stage, self.code = stage, code


_TRACE = []


def _read(root, rel, limit):
    """Cổng đọc file duy nhất của công cụ (test đặt spy tại đây); ghi đường dẫn đã mở vào vết. (bytes, None) hoặc (None, lý do).
    The one file-read gate; it records every path opened. (bytes, None) or (None, reason)."""
    _TRACE.append(rel)
    return office.read_rel(root, rel, limit)


# ------------------------------------------------------------------ giá trị ô / cell values
def classify(raw):
    """(lớp, [(nhãn, Decimal)]) của một ô chuỗi. Lớp: MISSING, NOT_APPLICABLE, ZERO, NUMBER, AMBIGUOUS, INVALID.
    Không bỏ khoảng trắng, không đoán dấu phân cách; chuỗi mơ hồ giữ nguyên chữ và nêu các cách đọc (`thousands`, `decimal`).
    Class and labelled readings of one string cell: no trimming and no separator guessing; an ambiguous string keeps its text and lists its readings."""
    if raw == '':
        return 'MISSING', []
    if raw == 'NA':
        return 'NOT_APPLICABLE', []
    if CELL_INT.match(raw) or CELL_DEC.match(raw):
        value = Decimal(raw)
        return ('ZERO' if value == 0 else 'NUMBER'), [('plain', value)]
    if CELL_GROUPED.match(raw) or CELL_TRIPLE.match(raw) or CELL_COMMA.match(raw):
        sign = '-' if raw.startswith('-') else ''
        body = raw.lstrip('-')
        readings = []
        if CELL_GROUPED.match(raw) or CELL_TRIPLE.match(raw):
            readings.append(('thousands', Decimal(sign + re.sub(r'[.,]', '', body))))
        if len(re.findall(r'[.,]', body)) == 1:
            readings.append(('decimal', Decimal(sign + body.replace(',', '.'))))
        return 'AMBIGUOUS', readings
    return 'INVALID', []


def fmt(value):
    """Chuỗi thập phân không số mũ. / Plain decimal string."""
    if value == value.to_integral_value():
        return str(int(value))
    # normalize() rounds to the active Decimal context (usually 28 digits).
    # Formatting the exact coefficient preserves all source-supported digits.
    plain = format(value, 'f')
    return plain.rstrip('0').rstrip('.') if '.' in plain else plain


def quantize(value, places):
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


# ------------------------------------------------------------------ yêu cầu / request
def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _text(v, limit):
    return isinstance(v, str) and 0 < len(v) <= limit and not CONTROL_RE.search(v)


def check_request(req):
    """[mã] của yêu cầu tính: trường lạ, kiểu, độ dài. / Problems of the request form."""
    if not isinstance(req, dict):
        return ['REQUEST_INVALID:NOT_OBJECT']
    problems = ['REQUEST_INVALID:UNKNOWN_FIELD=' + k for k in sorted(set(req) - set(REQUEST_KEYS))]
    problems += ['REQUEST_INVALID:%s.MISSING' % k for k in REQUEST_KEYS if k not in req]
    if problems:
        return problems
    if req['schema'] != SCHEMA_REQUEST:
        problems.append('REQUEST_INVALID:schema')
    if not _text(req['actor'], 120):
        problems.append('REQUEST_INVALID:actor')
    if req['operation'] not in OPERATIONS:
        problems.append('REQUEST_INVALID:operation')
    task = req['task']
    if not (isinstance(task, dict) and set(task) == set(TASK_KEYS) and _text(task['path'], 300) and _text(task['task_id'], 120)
            and _is_int(task['task_revision']) and task['task_revision'] >= 1 and isinstance(task['digest'], str) and DIGEST_RE.match(task['digest'])):
        problems.append('REQUEST_INVALID:task')
    if not _text(req['scope'], 300):
        problems.append('REQUEST_INVALID:scope')
    ins = req['inputs']
    if not (isinstance(ins, list) and 1 <= len(ins) <= MAX_INPUTS and all(
            isinstance(i, dict) and set(i) == {'path', 'digest'} and _text(i['path'], 300) and isinstance(i['digest'], str) and DIGEST_RE.match(i['digest'])
            for i in ins)):
        problems.append('REQUEST_INVALID:inputs')
    elif len({i['path'] for i in ins}) != len(ins):
        problems.append('REQUEST_INVALID:inputs.DUPLICATE')
    if not isinstance(req['params'], dict):
        problems.append('REQUEST_INVALID:params')
    return problems


def _rel_problem(rel, zones):
    if publish_new.path_form_problem(rel):
        return 'PATH_UNSUPPORTED_FORM'
    parts = rel.split('/')
    if len(parts) < 2 or parts[0] not in zones:
        return 'ZONE_NOT_ALLOWED'
    return None


def load_scope(root, rel):
    """(scope, None) hoặc (None, mã). Quyền của lab: ALLOWED khi và chỉ khi permission.status == 'ALLOWED'; thiếu hoặc lạ là UNKNOWN.
    The lab permission file; anything but an explicit ALLOWED is refused."""
    why = _rel_problem(rel, ('working',))
    if why:
        return None, 'SCOPE_PATH:' + why
    data, why = _read(root, rel, MAX_SCOPE)
    if data is None:
        return None, 'SCOPE_MISSING:' + str(why)
    doc, why = office.parse_json(data)
    if why:
        return None, 'SCOPE_INVALID:' + why
    ok = (isinstance(doc, dict) and doc.get('schema') == SCHEMA_SCOPE and _text(doc.get('scope_id'), 120)
          and isinstance(doc.get('permission'), dict) and isinstance(doc.get('operations'), list) and isinstance(doc.get('methods'), list)
          and all(isinstance(x, str) for x in doc['operations'] + doc['methods']))
    if not ok:
        return None, 'SCOPE_INVALID:SHAPE'
    status = doc['permission'].get('status')
    if status != 'ALLOWED':
        return None, 'PERMISSION_%s' % (status if status == 'NOT_ALLOWED' else 'UNKNOWN')
    doc['_digest'] = sha_of(data)
    return doc, None


def load_task(root, task, inputs):
    """Kiểm TASK hiện hành so với yêu cầu: bytes, ID, revision, marker phương pháp, và mọi input yêu cầu phải nằm trong inputs của TASK.
    (thông tin hoặc None, mã). Chỉ kiểm cấu trúc tối thiểu; không thay checkpoint. / Minimal TASK checks; not the checkpoint."""
    why = _rel_problem(task['path'], ('working',))
    if why:
        return None, 'TASK_PATH:' + why
    data, why = _read(root, task['path'], MAX_TASK)
    if data is None:
        return None, 'TASK_UNREADABLE:' + str(why)
    if sha_of(data) != task['digest']:
        return None, 'TASK_CHANGED'
    doc, why = office.parse_json(data)
    if why or not isinstance(doc, dict) or doc.get('record_type') != 'task':
        return None, 'TASK_INVALID'
    if doc.get('task_id') != task['task_id'] or doc.get('task_revision') != task['task_revision']:
        return None, 'TASK_ID_OR_REVISION_MISMATCH'
    problems = office.guard_task(doc, lambda rel: _read(root, rel, office.MAX_RESOURCE))
    if problems:
        return None, 'TASK_GUARD:' + problems[0]
    marker = [r for r in doc.get('acceptance', {}).get('requirements', []) if str(r.get('req_id', '')).startswith('OFFICE-METHOD:')]
    found = MARKER_ID_RE.match(marker[0].get('req_id', '')) if len(marker) == 1 else None
    if not found:
        return None, 'TASK_NOT_OFFICE_METHOD'
    declared = {}
    for item in doc.get('inputs', []):
        if isinstance(item, dict) and isinstance(item.get('path'), str):
            declared[item['path']] = item.get('digest')
    for item in inputs:
        if item['path'] not in declared:
            return None, 'INPUT_NOT_IN_TASK:' + item['path']
        if declared[item['path']] != item['digest']:
            return None, 'INPUT_DIGEST_NOT_TASK:' + item['path']
    return {'method': found.group(1)}, None


# ------------------------------------------------------------------ CSV
def read_csv(root, item):
    """Bảng đọc từ một input đã bind. Đọc một lần, so digest, UTF-8 chặt, không BOM, đúng số cột; lỗi ⇒ Refused. / One read, digest check, strict UTF-8."""
    why = _rel_problem(item['path'], office.SOURCE_ZONES)
    if why:
        raise Refused('INPUT_REFUSED', 'INPUT_' + why)
    data, why = _read(root, item['path'], MAX_CSV)
    if data is None:
        raise Refused('INPUT_REFUSED', 'INPUT_UNREADABLE:%s' % why)
    if sha_of(data) != item['digest']:
        raise Refused('INPUT_REFUSED', 'INPUT_CHANGED:' + item['path'])
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        raise Refused('DATA_REFUSED', 'CSV_NOT_UTF8')
    if text.startswith('﻿'):
        raise Refused('DATA_REFUSED', 'CSV_BOM')
    rows = []
    try:
        reader = csv.reader(io.StringIO(text, newline=''), strict=True)
        header = next(reader, None)
        if not header or len(set(header)) != len(header) or any(not h for h in header):
            raise Refused('DATA_REFUSED', 'CSV_HEADER')
        for rec in reader:
            if not rec:
                continue
            if len(rec) != len(header):
                raise Refused('DATA_REFUSED', 'CSV_ROW_SHAPE:line=%d' % reader.line_num)
            if len(rows) >= MAX_ROWS:
                raise Refused('DATA_REFUSED', 'CSV_TOO_MANY_ROWS')
            rows.append({'line': reader.line_num, 'cells': dict(zip(header, rec))})
    except csv.Error:
        raise Refused('DATA_REFUSED', 'CSV_PARSE')
    return {'path': item['path'], 'digest': item['digest'], 'bytes': len(data), 'columns': header, 'rows': rows}


def _need_columns(table, names):
    missing = [n for n in names if n not in table['columns']]
    if missing:
        raise Refused('DATA_REFUSED', 'COLUMN_NOT_FOUND:' + missing[0])


# ------------------------------------------------------------------ aggregate
def _names(v, limit=3):
    return isinstance(v, list) and len(v) <= limit and all(isinstance(x, str) and 0 < len(x) <= 60 for x in v) and len(set(v)) == len(v)


def check_aggregate(p):
    """Tham số của aggregate → mã lỗi hoặc None. / Validate aggregate parameters."""
    if set(p) - {'filters', 'group_by', 'key', 'measures'} or 'measures' not in p:
        return 'PARAMS_INVALID:FIELDS'
    flt = p.get('filters', [])
    if not (isinstance(flt, list) and len(flt) <= 6):
        return 'PARAMS_INVALID:filters'
    for f in flt:
        if not (isinstance(f, dict) and isinstance(f.get('column'), str) and f.get('op') in ('eq', 'ne', 'in')):
            return 'PARAMS_INVALID:filters'
        if f['op'] == 'in':
            if set(f) != {'column', 'op', 'values'} or not (isinstance(f['values'], list) and f['values'] and all(isinstance(x, str) for x in f['values'])):
                return 'PARAMS_INVALID:filters'
        elif set(f) != {'column', 'op', 'value'} or not isinstance(f['value'], str):
            return 'PARAMS_INVALID:filters'
    if not _names(p.get('group_by', [])) or not _names(p.get('key', [])):
        return 'PARAMS_INVALID:group_by_or_key'
    ms = p['measures']
    if not (isinstance(ms, list) and 1 <= len(ms) <= 8):
        return 'PARAMS_INVALID:measures'
    seen = set()
    for m in ms:
        if not (isinstance(m, dict) and isinstance(m.get('name'), str) and NAME_RE.match(m['name']) and m['name'] not in seen):
            return 'PARAMS_INVALID:measure.name'
        seen.add(m['name'])
        kind = m.get('kind')
        allowed = {'name', 'kind'}
        if kind == 'sum':
            allowed |= {'column'}
            if not isinstance(m.get('column'), str):
                return 'PARAMS_INVALID:measure.column'
        elif kind in ('sum_product', 'weighted_mean'):
            allowed |= {'columns'} | ({'round_places'} if kind == 'weighted_mean' else set())
            cols = m.get('columns')
            if not (isinstance(cols, list) and len(cols) == 2 and all(isinstance(c, str) for c in cols)):
                return 'PARAMS_INVALID:measure.columns'
            if kind == 'weighted_mean' and not (_is_int(m.get('round_places')) and 0 <= m['round_places'] <= 6):
                return 'PARAMS_INVALID:measure.round_places'
        elif kind != 'count_rows':
            return 'PARAMS_INVALID:measure.kind'
        if set(m) - allowed:
            return 'PARAMS_INVALID:measure.fields'
    return None


def _row_key(row, key):
    return {k: row['cells'][k] for k in key} if key else {'line': row['line']}


def _measure(m, rows, key):
    """Kết quả một measure trên nhóm dòng: giá trị, dòng bị loại theo lớp, cách đọc mơ hồ. / One measure over a row group."""
    out = {'name': m['name'], 'kind': m['kind']}
    if m['kind'] == 'count_rows':
        out.update(value=str(len(rows)), formula='COUNT(rows)')
        return out
    cols = [m['column']] if m['kind'] == 'sum' else m['columns']
    counted, excluded, zero_rows, ambiguous = [], [], 0, []
    for row in rows:
        classes = [classify(row['cells'][c]) for c in cols]
        if all(k in ('NUMBER', 'ZERO') for k, _ in classes):
            counted.append([rd[0][1] for _, rd in classes])
            zero_rows += any(k == 'ZERO' for k, _ in classes)
            continue
        entry = {'line': row['line'], 'key': _row_key(row, key), 'cells': {c: row['cells'][c] for c in cols},
                 'reasons': {c: k for c, (k, _) in zip(cols, classes) if k not in ('NUMBER', 'ZERO')}}
        excluded.append(entry)
        if all(k in ('NUMBER', 'ZERO', 'AMBIGUOUS') for k, _ in classes) and any(k == 'AMBIGUOUS' for k, _ in classes):
            ambiguous.append((entry, classes))

    def total(vectors):
        with localcontext() as ctx:
            ctx.prec = 60
            if m['kind'] == 'sum':
                return sum((v[0] for v in vectors), Decimal(0))
            return sum((v[0] * v[1] for v in vectors), Decimal(0))

    def finish(vectors):
        if m['kind'] != 'weighted_mean':
            return fmt(total(vectors))
        with localcontext() as ctx:
            ctx.prec = 60
            weight = sum((v[1] for v in vectors), Decimal(0))
            return None if weight == 0 else fmt(quantize(total(vectors) / weight, m['round_places']))

    if m['kind'] == 'sum':
        formula = 'SUM(%s)' % cols[0]
    elif m['kind'] == 'sum_product':
        formula = 'SUM(%s*%s)' % (cols[0], cols[1])
    else:
        formula = 'SUM(%s*%s)/SUM(%s), ROUND_HALF_UP %d places' % (cols[0], cols[1], cols[1], m['round_places'])
    out.update(value=finish(counted), formula=formula + ' over rows where every column is NUMBER or ZERO', rows_counted=len(counted), rows_zero=zero_rows,
               rows_excluded=len(excluded), excluded=excluded)
    if m['kind'] == 'weighted_mean' and out['value'] is None:
        out['value_note'] = 'WEIGHT_SUM_ZERO'
    if ambiguous:
        alts = {}
        for label in ('thousands', 'decimal'):
            vectors = [list(v) for v in counted]
            for _, classes in ambiguous:
                row_vec = []
                for k, rd in classes:
                    pick = [v for lab, v in rd if lab == label] if k == 'AMBIGUOUS' else [rd[0][1]]
                    row_vec.append(pick[0] if pick else None)
                if None in row_vec:
                    vectors = None
                    break
                vectors.append(row_vec)
            if vectors is not None:
                alts[label] = finish(vectors)
        out['ambiguous_rows'] = [{'line': e['line'], 'key': e['key'], 'raw': e['cells'],
                                  'readings': {c: {lab: fmt(v) for lab, v in rd} for c, (k, rd) in zip(cols, classes) if k == 'AMBIGUOUS'}}
                                 for e, classes in ambiguous]
        out['alternatives'] = {'note': 'Kết quả nếu mọi dòng mơ hồ được đọc theo cùng một cách; thiếu khóa nghĩa là có dòng không có cách đọc đó. Công cụ không chọn hộ',
                               'totals_if': alts}
    return out


def run_aggregate(table, p):
    key = p.get('key', [])
    group_by = p.get('group_by', [])
    refs = [f['column'] for f in p.get('filters', [])] + key + group_by
    for m in p['measures']:
        refs += [m['column']] if m['kind'] == 'sum' else (m['columns'] if m['kind'] != 'count_rows' else [])
    _need_columns(table, refs)
    rows = table['rows']
    steps = [{'step': 'load', 'path': table['path'], 'rows': len(rows)}]
    for f in p.get('filters', []):
        before = len(rows)
        if f['op'] == 'eq':
            rows = [r for r in rows if r['cells'][f['column']] == f['value']]
        elif f['op'] == 'ne':
            rows = [r for r in rows if r['cells'][f['column']] != f['value']]
        else:
            rows = [r for r in rows if r['cells'][f['column']] in f['values']]
        steps.append({'step': 'filter', 'column': f['column'], 'op': f['op'], 'value': f.get('value', f.get('values')),
                      'rows_before': before, 'rows_after': len(rows)})
    issues = []
    if key:
        seen = {}
        for r in rows:
            seen.setdefault(tuple(r['cells'][k] for k in key), []).append(r)
        for k, group in seen.items():
            if len(group) > 1:
                same = len({tuple(sorted(g['cells'].items())) for g in group}) == 1
                issues.append({'code': 'DUPLICATE_KEY', 'key': dict(zip(key, k)), 'conflicting': not same,
                               'rows': [{'line': g['line'], 'cells': g['cells']} for g in group]})
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r['cells'][g] for g in group_by), []).append(r)
    if not group_by:
        groups = {(): rows}
    out_groups = [{'group': dict(zip(group_by, gk)), 'rows': len(gr), 'measures': [_measure(m, gr, key) for m in p['measures']]}
                  for gk, gr in sorted(groups.items())]
    for g in out_groups:
        for m in g['measures']:
            if m.get('ambiguous_rows'):
                issues.append({'code': 'AMBIGUOUS_NUMBER', 'measure': m['name'], 'group': g['group'], 'rows': m['ambiguous_rows']})
    return {'steps': steps, 'rows_in_scope': len(rows), 'groups': out_groups, 'issues': issues,
            'totals_status': 'NOT_CLEAN' if issues else 'CLEAN_AS_DEFINED',
            'rules': ['Ô trống = MISSING, "NA" = NOT_APPLICABLE, 0 = ZERO (tính vào tổng); chuỗi mơ hồ (ví dụ 1.234) giữ nguyên chữ, không vào tổng, nêu cách đọc',
                      'Không bỏ trùng khóa, không điền chỗ thiếu, không đổi kỳ; tổng chính xác bằng Decimal, làm tròn chỉ ở weighted_mean (ROUND_HALF_UP)']}


# ------------------------------------------------------------------ compare_prices
def check_compare(p):
    if set(p) != {'columns', 'frame', 'conversions', 'round_places'}:
        return 'PARAMS_INVALID:FIELDS'
    cols, frame = p['columns'], p['frame']
    if not (isinstance(cols, dict) and set(cols) == set(PRICE_COLUMNS) and all(isinstance(v, str) for v in cols.values())):
        return 'PARAMS_INVALID:columns'
    if not (isinstance(frame, dict) and set(frame) == {'period', 'price_type', 'currency', 'unit'} and all(isinstance(v, str) and v for v in frame.values())):
        return 'PARAMS_INVALID:frame'
    conv = p['conversions']
    if not (isinstance(conv, list) and len(conv) <= 6):
        return 'PARAMS_INVALID:conversions'
    for c in conv:
        if not (isinstance(c, dict) and set(c) == {'from_unit', 'to_unit', 'multiply'} and all(isinstance(v, str) and v for v in c.values())):
            return 'PARAMS_INVALID:conversions'
        if classify(c['multiply'])[0] != 'NUMBER' or Decimal(c['multiply']) <= 0:
            return 'PARAMS_INVALID:conversions.multiply'
    if len({c['from_unit'] for c in conv}) != len(conv):
        return 'PARAMS_INVALID:conversions.DUPLICATE'
    if not (_is_int(p['round_places']) and 0 <= p['round_places'] <= 6):
        return 'PARAMS_INVALID:round_places'
    return None


def run_compare(table, p):
    cols, frame = p['columns'], p['frame']
    _need_columns(table, list(cols.values()))
    conv = {c['from_unit']: c for c in p['conversions'] if c['to_unit'] == frame['unit']}
    issues, ids = [], {}
    for r in table['rows']:
        ids.setdefault(r['cells'][cols['id']], []).append(r)
    for rid, group in ids.items():
        if len(group) > 1:
            prices = {g['cells'][cols['price']] for g in group}
            issues.append({'code': 'DUPLICATE_ID', 'id': rid, 'conflicting': len(prices) > 1,
                           'rows': [{'line': g['line'], 'cells': g['cells']} for g in group]})
    rows_out = []
    for r in table['rows']:
        c = r['cells']
        reasons = ['OUT_OF_FRAME:%s=%s' % (f, c[cols[f]]) for f in ('period', 'price_type', 'currency') if c[cols[f]] != frame[f]]
        kind, readings = classify(c[cols['price']])
        converted, formula = None, None
        if kind not in ('NUMBER', 'ZERO'):
            reasons.append('PRICE_%s' % kind)
        elif c[cols['unit']] == frame['unit']:
            converted, formula = readings[0][1], '%s (đơn vị %s, không đổi)' % (c[cols['price']], frame['unit'])
        elif c[cols['unit']] in conv:
            step = conv[c[cols['unit']]]
            with localcontext() as ctx:
                ctx.prec = 60
                converted = readings[0][1] * Decimal(step['multiply'])
            formula = '%s x %s (%s -> %s)' % (c[cols['price']], step['multiply'], c[cols['unit']], frame['unit'])
        else:
            reasons.append('UNIT_NO_CONVERSION:%s' % c[cols['unit']])
        in_frame = not reasons
        rows_out.append({'id': c[cols['id']], 'line': r['line'], 'cells': c, 'in_frame': in_frame, 'reasons': reasons,
                         'converted_price': fmt(converted) if in_frame else None, 'formula': formula if in_frame else None})
    kept = [(Decimal(x['converted_price']), x) for x in rows_out if x['in_frame']]
    stats = None
    if kept:
        values = [v for v, _ in kept]
        with localcontext() as ctx:
            ctx.prec = 60
            mean = quantize(sum(values, Decimal(0)) / len(values), p['round_places'])
            spread = max(values) - min(values)
        stats = {'count': len(values), 'min': fmt(min(values)), 'max': fmt(max(values)), 'spread': fmt(spread), 'mean': fmt(mean),
                 'min_ids': [x['id'] for v, x in kept if v == min(values)], 'max_ids': [x['id'] for v, x in kept if v == max(values)]}
    by_reason = {}
    for x in rows_out:
        for why in x['reasons']:
            by_reason[why] = by_reason.get(why, 0) + 1
    return {'frame': frame, 'conversions': p['conversions'],
            'steps': [{'step': 'load', 'path': table['path'], 'rows': len(table['rows'])},
                      {'step': 'frame', 'rows_in_frame': len(kept), 'rows_excluded': len(rows_out) - len(kept)}],
            'rows': rows_out, 'excluded_by_reason': by_reason, 'stats': stats, 'issues': issues,
            'stats_status': 'NOT_CLEAN' if issues else 'CLEAN_AS_DEFINED',
            'rules': ['Chỉ so các dòng cùng kỳ, loại giá, tiền tệ với khung; đổi đơn vị chỉ theo hệ số được nêu; không đổi tiền tệ hay thuế',
                      'Trung bình đơn giản trên các dòng trong khung, ROUND_HALF_UP %d chữ số; không phải giá đã mua, thị phần hay dự báo' % p['round_places']]}


# ------------------------------------------------------------------ chạy / run
def run(request, root):
    """Chạy một phép tính. Trả dict kết quả (outcome COMPUTED hoặc REFUSED); không ghi gì. / Run one calculation; writes nothing."""
    root = os.path.abspath(root)
    del _TRACE[:]
    base = {'schema': SCHEMA_RESULT, 'tool': 'tools/office_compute.py',
            'claims': {'actor_authenticated': False, 'host_tool_grant_proven': False, 'sandbox': False}}

    def refuse(stage, code):
        return dict(base, outcome='REFUSED', stage=stage, code=code, message=msg(stage), reads=list(_TRACE), writes=[])

    problems = check_request(request)
    if problems:
        return refuse('REQUEST_INVALID', problems[0])
    task_info, why = load_task(root, request['task'], request['inputs'])
    if why:
        return refuse('TASK_REFUSED', why)
    scope, why = load_scope(root, request['scope'])
    if why:
        return refuse('SCOPE_REFUSED', why)
    if request['operation'] not in scope['operations'] or task_info['method'] not in scope['methods']:
        return refuse('SCOPE_REFUSED', 'OPERATION_OR_METHOD_NOT_ALLOWED')
    params = request['params']
    why = check_aggregate(params) if request['operation'] == 'aggregate' else check_compare(params)
    if why:
        return refuse('PARAMS_INVALID', why)
    if len(request['inputs']) != 1:
        return refuse('PARAMS_INVALID', 'PARAMS_INVALID:ONE_INPUT_PER_OPERATION')
    try:
        table = read_csv(root, request['inputs'][0])
        body = run_aggregate(table, params) if request['operation'] == 'aggregate' else run_compare(table, params)
    except Refused as exc:
        return refuse(exc.stage, exc.code)
    task = request['task']
    result = dict(base, outcome='COMPUTED', operation=request['operation'], actor_declared=request['actor'],
                  task={'path': task['path'], 'task_id': task['task_id'], 'task_revision': task['task_revision'], 'digest': task['digest'],
                        'method': task_info['method']},
                  scope={'path': request['scope'], 'digest': scope['_digest'], 'scope_id': scope['scope_id']},
                  request_digest=sha_of(canon(request)),
                  inputs=[{'path': table['path'], 'digest': table['digest'], 'bytes': table['bytes'], 'rows': len(table['rows']), 'columns': table['columns']}],
                  params=params, result=body, reads=list(_TRACE), writes=[],
                  limits=['Chỉ đọc đúng input của TASK; không tác động ngoài đọc',
                          'actor do người gọi khai, không xác thực; không chứng minh host cấp công cụ cho vai',
                          'Kiểm chéo một kết quả trọng yếu bằng đường tính khác là việc của người dùng kết quả (test, review hoặc chuyên viên), không phải của công cụ'])
    result['result_digest'] = sha_of(canon(result))
    return result


# ------------------------------------------------------------------ canary, probe, route
CANARY_ROWS = (('C1', '2026-10', '4'), ('C2', '2026-10', '0'), ('C3', '2026-10', ''), ('C4', '2026-09', '9'))


def canary_result():
    """Phép tính vô hại trên dữ liệu nhúng sẵn (không đọc file). / A harmless calculation on embedded rows; reads no file."""
    rows = [{'line': i + 2, 'cells': {'id': a, 'period': b, 'qty': c}} for i, (a, b, c) in enumerate(CANARY_ROWS)]
    table = {'path': '(canary)', 'digest': None, 'columns': ['id', 'period', 'qty'], 'rows': rows}
    p = {'filters': [{'column': 'period', 'op': 'eq', 'value': '2026-10'}], 'key': ['id'],
         'measures': [{'name': 'rows', 'kind': 'count_rows'}, {'name': 'qty_sum', 'kind': 'sum', 'column': 'qty'}]}
    return run_aggregate(table, p)


def owner_digest():
    with open(os.path.abspath(__file__), 'rb') as fh:
        return sha_of(fh.read())


def canary(client='UNKNOWN', client_version='UNKNOWN', observed_by='UNKNOWN'):
    """Biên nhận canary do người gọi lưu làm probe. Chỉ chứng minh lệnh chạy được ở tiến trình gọi, không chứng minh chuyên viên có công cụ.
    Probe receipt the caller saves; it shows only that the command ran in the calling process."""
    return {'schema': SCHEMA_PROBE, 'owner': 'tools/office_compute.py', 'owner_digest': owner_digest(), 'canary_digest': sha_of(canon(canary_result())),
            'observed': {'client': client[:120], 'client_version': client_version[:60], 'observed_by': observed_by[:60],
                         'at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'python': platform.python_version(),
                         'platform': platform.platform()},
            'layer': 'CALLING_PROCESS_ONLY', 'specialist_tool_observed': False,
            'limits': ['Biên nhận tự lưu, không xác thực actor hay host', 'Chỉ chứng minh Main chạy được lệnh; chưa chứng minh vai chuyên viên có công cụ']}


def prepare_route(route, root, method=None, operation=None):
    """Chuẩn bị tuyến compute host-session: đối chiếu probe và quyền của lab, trả trạng thái từng chiều. Chỉ đọc; KHÔNG là quyền chạy và không là lời gọi đã quan sát.
    State: ROUTE_READY_UNVERIFIED hoặc ROUTE_REFUSED. / Prepare the host-session route; read only, not permission to run, not an observed call."""
    root = os.path.abspath(root)
    problems = []
    probe_state = {'status': 'NOT_READ', 'layer': None}
    why = _rel_problem(route['probe'], ('working',))
    data, rd = (None, 'PATH:' + why) if why else _read(root, route['probe'], MAX_SCOPE)
    if data is None:
        problems.append('PROBE_MISSING:' + str(rd))
    else:
        doc, why = office.parse_json(data)
        if why or not (isinstance(doc, dict) and doc.get('schema') == SCHEMA_PROBE):
            problems.append('PROBE_INVALID')
        elif doc.get('owner_digest') != owner_digest():
            problems.append('PROBE_OWNER_CHANGED')
        elif doc.get('canary_digest') != sha_of(canon(canary_result())):
            problems.append('PROBE_CANARY_MISMATCH')
        elif doc.get('layer') != 'CALLING_PROCESS_ONLY' or doc.get('specialist_tool_observed') is not False:
            problems.append('PROBE_CLAIMS_MORE_THAN_MAIN')
        else:
            probe_state = {'status': 'MATCHES_OWNER', 'layer': doc['layer'], 'digest': sha_of(data), 'observed': doc.get('observed')}
    if problems:
        probe_state = {'status': 'INVALID', 'layer': None}
    scope, why = load_scope(root, route['scope'])
    if why:
        problems.append(why)
    elif ((method is not None and method not in scope['methods']) or
          (operation is not None and operation not in scope['operations'])):
        problems.append('OPERATION_OR_METHOD_NOT_ALLOWED')
    perm = {'status': 'ALLOWED' if scope else (why.split(':')[0] if why.startswith('PERMISSION_') else 'NOT_VERIFIED'), 'scope': route['scope']}
    ready = not problems
    return {'schema': SCHEMA_ROUTE, 'state': 'ROUTE_READY_UNVERIFIED' if ready else 'ROUTE_REFUSED', 'problems': problems,
            'dimensions': {'requested': 'compute', 'exporter': 'ABSENT', 'host_probe': probe_state, 'permission': perm, 'specialist_call': 'NOT_OBSERVED'},
            'methods_allowed': scope['methods'] if scope else [], 'operations_allowed': scope['operations'] if scope else [],
            'command': ['python', '-X', 'utf8', '-B', '<LAW>/tools/office_compute.py', 'run', '--project', '<PROJECT>', '--request', '-'] if ready else [],
            'limits': ['ROUTE_READY_UNVERIFIED không phải được phép chạy và không phải đã chạy',
                       'Probe chỉ ở phía Main; chuyên viên phải gọi thật trong lượt của mình và được quan sát',
                       'Không đổi exporter native, không gỡ held mặc định; đây là tuyến host-session dưới quyền bảo trì, không phải sandbox']}


# ------------------------------------------------------------------ CLI
def _out(obj):
    sys.stdout.flush()
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    sys.stdout.flush()


def _refused(code):
    _out({'schema': SCHEMA_RESULT, 'outcome': 'REFUSED', 'stage': 'REQUEST_INVALID', 'code': code, 'reads': [], 'writes': []})
    return 1


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(prog='office_compute.py', description='Công cụ tính hẹp cho vai văn phòng, chỉ đọc. / Narrow office compute tool, read only.')
    sub = ap.add_subparsers(dest='cmd')
    p = sub.add_parser('run')
    p.add_argument('--project', required=True)
    p.add_argument('--request', required=True)
    p = sub.add_parser('canary')
    p.add_argument('--client', default='UNKNOWN')
    p.add_argument('--client-version', default='UNKNOWN')
    p.add_argument('--observed-by', default='UNKNOWN')
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_usage(sys.stderr)
        return 2
    if args.cmd == 'canary':
        _out(canary(args.client, args.client_version, args.observed_by))
        return 0
    if not os.path.isdir(args.project):
        return _refused('PROJECT_NOT_A_DIRECTORY')
    if args.request == '-':
        data = sys.stdin.buffer.read(MAX_REQUEST + 1)
    else:
        try:
            with open(args.request, 'rb') as fh:
                data = fh.read(MAX_REQUEST + 1)
        except OSError:
            data = None
    if data is None or len(data) > MAX_REQUEST:
        return _refused('REQUEST_UNREADABLE_OR_TOO_LARGE')
    req, why = office.parse_json(data)
    if why:
        return _refused('REQUEST_INVALID:' + why)
    res = run(req, args.project)
    _out(res)
    return 0 if res['outcome'] == 'COMPUTED' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
