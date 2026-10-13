#!/usr/bin/env python3
"""Lịch sử thao tác cục bộ của bảng điều khiển (JSON Lines) / Local operations history for the control panel.

Mỗi thao tác /api/run ghi một dòng: thời điểm UTC, tên thao tác, trạng thái, mã, số file tác động,
mã giao dịch (nếu có) và thời gian chạy. Chỉ giữ MAX_RECORDS dòng mới nhất.
Không bao giờ ghi nội dung tài liệu, đường dẫn, tên file, tên người, tên project, dữ liệu đã gõ hay khóa truy cập.
One line per /api/run action: UTC time, action name, status, code, files affected, transaction id (if any) and
duration. Only the newest MAX_RECORDS lines are kept. Never stores document content, paths, file names, names of
people, the project name, typed values or access tokens.

Tệp / File: <project>/.agent/runtime/operations.jsonl (không vào MANIFEST hay ZIP / never packaged).
"""
import datetime, io, json, os, re, threading

REL = ('.agent', 'runtime', 'operations.jsonl')
MAX_RECORDS = 500
STATUSES = ('success', 'preview', 'issues', 'not_checked', 'blocked', 'partial', 'error')
ACTION_RE = re.compile(r'[a-z_]{1,40}')
TXID_RE = re.compile(r'[0-9A-Za-z-]{1,80}')
_LOCK = threading.Lock()


def path(root):
    return os.path.join(root, *REL)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _clean(value):
    """Chỉ giữ các trường cho phép, đúng kiểu; None nếu dòng hỏng / Keep whitelisted fields with the right types only."""
    if not isinstance(value, dict) or value.get('status') not in STATUSES:
        return None
    act, tx = value.get('action'), value.get('transaction')
    return {'time': value.get('time') if isinstance(value.get('time'), str) else '',
            'action': act if isinstance(act, str) and ACTION_RE.fullmatch(act) else 'unknown',
            'status': value['status'],
            'code': value.get('code') if isinstance(value.get('code'), int) else -1,
            'files': _int(value.get('files')),
            'transaction': tx if isinstance(tx, str) and TXID_RE.fullmatch(tx) else None,
            'duration_ms': _int(value.get('duration_ms'))}


def _int(v):
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return 0


def _lines(p):
    try:
        with io.open(p, encoding='utf-8') as src:
            return [x.rstrip('\r\n') for x in src if x.strip()]
    except (OSError, UnicodeDecodeError):
        return []


def record(root, action, status, code=0, files=0, transaction=None, duration_ms=0):
    """Thêm một dòng, giữ tối đa MAX_RECORDS / Append one line and keep at most MAX_RECORDS."""
    rec = _clean({'time': _now(), 'action': action, 'status': status if status in STATUSES else 'error',
                  'code': code, 'files': files, 'transaction': transaction, 'duration_ms': duration_ms})
    line = json.dumps(rec, ensure_ascii=False, sort_keys=True)
    with _LOCK:
        p = path(root)
        lines = _lines(p) + [line]
        lines = lines[-MAX_RECORDS:]
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + '.tmp'
        with io.open(tmp, 'w', encoding='utf-8', newline='\n') as dst:
            dst.write('\n'.join(lines) + '\n')
        os.replace(tmp, p)
    return rec


def read(root):
    """Bản ghi hợp lệ, cũ trước; dòng hỏng bị bỏ qua / Valid records, oldest first; malformed lines are skipped."""
    with _LOCK:
        lines = _lines(path(root))
    out = []
    for line in lines:
        try:
            rec = _clean(json.loads(line))
        except ValueError:
            continue
        if rec is not None:
            out.append(rec)
    return out


def summary(records):
    """Lần gần nhất: thành công, lỗi, dang dở (None nếu chưa có) / Latest success, failure and unfinished records."""
    def last(statuses):
        for rec in reversed(records):
            if rec['status'] in statuses:
                return rec
        return None
    return {'last_success': last(('success', 'preview', 'issues')),
            'last_failure': last(('error', 'blocked', 'not_checked')),
            'last_unfinished': last(('partial',))}


def clear(root):
    """Xóa đúng file nhật ký và không làm gì khác / Remove only the log file. Returns True if it was removed."""
    with _LOCK:
        try:
            os.remove(path(root))
            return True
        except OSError:
            return False
