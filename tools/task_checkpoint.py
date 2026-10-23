#!/usr/bin/env python3
"""Shared read-only TASK/RESULT checkpoint, promoted from the accepted A-11 recipe.

Uses the fixed checker/owners beside this file, never executes project Markdown.
Matching bytes/binding is not a grant, semantic review, host state or user acceptance.
Reads named local files only. Cooperative point-in-time checks retain TOCTOU limits.
"""
import hashlib
import importlib
import importlib.util
import json
import os
import posixpath
import sys
from pathlib import Path

def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def read_file(project, rel):
    """(bytes, None) hoặc (None, lý do). Đọc một lần; thiếu, đi qua liên kết hay lỗi đọc không bao giờ được coi là 'không đổi'."""
    import office
    return office.read_rel(project, rel, limit=2 * 1024 * 1024)


def load_v3(law=None):
    """Nạp package v3 từ cây LAW cố định `law` (có .cvf và tools). Không import gì từ data root hay tests."""
    trusted = Path(__file__).resolve().parents[1]
    law = trusted if law is None else Path(law).resolve()
    if law != trusted:
        raise RuntimeError("checker code must come from the fixed LAW tree")
    spec = importlib.util.spec_from_file_location('law_cvf_entry_v3', str(law / '.cvf' / 'checks' / 'control_check_v3.py'))
    entry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entry)
    entry._load_package()
    name = entry.PACKAGE_NAME
    mod = lambda leaf: importlib.import_module(name + '.' + leaf)
    tools_dir = str(law / 'tools')
    sys.path[:] = [tools_dir] + [p for p in sys.path if p != tools_dir]
    library = importlib.import_module('library')
    office = importlib.import_module('office')
    for owner in (library, importlib.import_module('transaction'), importlib.import_module('publish_new'), office):
        if Path(owner.__file__).resolve().parent != law / 'tools':
            raise RuntimeError('owner không nạp từ cây LAW cố định')
    owners = mod('loader').load_owners()
    return {'pkg': importlib.import_module(name), 'loader': mod('loader'), 'refs': mod('refs'), 'binding': mod('binding'),
            'canon': mod('canon'), 'owners': owners, 'library': library, 'office': office,
            'policy_ctx': mod('binding').make_policy_context(owners.policy_bytes)}


def binding_stub(v3, task):
    """Main tính khi giao việc; vai nhận chép nguyên văn vào RESULT.binding rồi thêm `outputs`."""
    d = v3['canon'].binding_digests(task, v3['owners'].policy)
    pkg = v3['pkg']
    return {'bind_version': pkg.BIND_VERSION, 'evaluation_basis': pkg.EVALUATION_BASIS, 'task_id': task['task_id'],
            'task_revision': task['task_revision'], 'intent_digest': d['intent_digest'],
            'accepted_task_digest': d['accepted_task_digest'], 'context_digest': d['context_digest'],
            'policy_version': pkg.POLICY_VERSION, 'policy_digest': d['policy_digest'],
            'inputs': json.loads(json.dumps(task['inputs']))}


def read_record(v3, project, rel, want, reader=None):
    """(record, digest bytes thô, None) hoặc (None, None, lý do): strict parse, literal, schema và miền canonical của owner."""
    data, why = (reader or read_file)(project, rel)
    if data is None:
        return None, None, 'RECORD_%s %s' % (want.upper(), why)
    bundle, out = v3['loader'].inspect_structure(data, v3['owners'])
    if bundle is None or bundle.get('record_type') != want:
        return None, None, 'RECORD_REJECTED %s %s' % (want, ','.join(sorted(out.reasons)) or 'WRONG_TYPE')
    return bundle, sha(data), None


def checkpoint(v3, project, task_rel, result_rel, staged=None, reader=None):
    """Danh sách `problems` rỗng nghĩa là các quan hệ ĐÃ KIỂM khớp; không phải PASS, quyền hay nghiệm thu của người dùng."""
    reader = reader or read_file
    problems, cp = [], {'problems': [], 'candidate': None, 'ledger_snapshot': None}
    cp['problems'] = problems
    task, task_raw, why_t = read_record(v3, project, task_rel, 'task', reader)
    result, result_raw, why_r = read_record(v3, project, result_rel, 'result', reader)
    problems.extend(w for w in (why_t, why_r) if w)
    if problems:
        return cp
    cp.update(task=task, result=result, raw={'task': task_raw, 'result': result_raw})
    # 0. marker OFFICE-METHOD: hoặc context roles/office/: kiểm cả hai phía (TASK không có cả hai là legacy, không kiểm gì thêm)
    problems.extend(v3['office'].guard_task(task, lambda rel: reader(project, rel)))
    # 1. binding RESULT <-> TASK hiện hành
    index = v3['refs'].build_index([task, result])
    report = v3['binding'].compare_binding(index, 1, v3['policy_ctx'])
    states = {r.name: r.state for r in report.relations}
    if not report.applicable:
        problems.append('BINDING_NOT_APPLICABLE')
    problems.extend('BINDING %s=%s' % (n, s) for n, s in states.items() if s not in ('MATCH', 'NOT_BOUND', 'NOT_APPLICABLE'))
    if states.get('B-OUT-RESULT') != 'MATCH':
        problems.append('BINDING B-OUT-RESULT=%s' % states.get('B-OUT-RESULT'))
    # 2. bytes hiện tại của input và context_refs đúng digest đã bound
    for obj in task['inputs'] + task.get('context_refs', []):
        data, why = reader(project, obj['path'])
        if data is None:
            problems.append('INPUT %s %s' % (obj['path'], why))
        elif sha(data) != obj['digest']:
            problems.append('INPUT_CHANGED %s' % obj['path'])
    # 3. metadata sổ cho input có source_id
    library, wanted = v3['library'], [o for o in task['inputs'] + task.get('context_refs', []) if 'source_id' in o]
    if wanted:
        import transaction
        ledger_path = os.path.join(project, 'references', '_INDEX.xlsx')
        if not transaction.link_free(ledger_path, project) or os.path.islink(ledger_path):
            book = {'ok': False, 'kind': 'unsafe_path'}
        else:
            ledger, why = reader(project, 'references/_INDEX.xlsx')
            book = library.parse_book(ledger) if ledger is not None else {'ok': False, 'kind': why}
        if not book['ok']:
            problems.append('LEDGER_UNREADABLE %s' % book['kind'])
        else:
            cp['ledger_snapshot'] = book['snapshot']
            counts = library.id_counts(book['data'])
            records = [library.record(r, counts) for r in book['data']]
            for obj in wanted:
                hits = [x for x in records if x['id'] == obj['source_id']]
                if len(hits) != 1:
                    problems.append('LEDGER_ID_COUNT %s=%d' % (obj['source_id'], len(hits)))
                elif hits[0]['identity'] != 'ok' or str(hits[0]['revision']) != obj.get('revision') or hits[0]['file'] != obj['path']:
                    problems.append('LEDGER_METADATA_CHANGED %s' % obj['source_id'])
    # 4. candidate: đọc một lần, so SHA đầy đủ với RESULT.artifacts; staged phải là chính bytes đó
    slot, arts = posixpath.dirname(result_rel), result['artifacts']
    targets = [t for a in task['effects']['actions'] for t in a['targets']] + [a['path'] for a in arts]
    import publish_new  # owner cú pháp đường dẫn đã có, không tự chuẩn hóa alias
    if any(publish_new.path_form_problem(t) for t in targets):
        problems.append('TARGET_UNSUPPORTED_FORM')
    if any(not t.startswith(slot + '/') for t in targets):
        problems.append('TARGET_OUTSIDE_SLOT')
    if len(arts) != 1:
        problems.append('ARTIFACTS_COUNT')  # ví dụ này nhận đúng một candidate; nhiều candidate thì lặp theo từng artifact
    else:
        data, why = reader(project, arts[0]['path'])
        if data is None:
            problems.append('CANDIDATE %s' % why)
        elif sha(data) != arts[0]['digest']:
            problems.append('CANDIDATE_CHANGED')
        else:
            cp['candidate'] = data
        if staged is not None and (cp['candidate'] is None or sha(bytes(staged)) != arts[0]['digest']):
            problems.append('STAGED_NOT_CANDIDATE')
    return cp


