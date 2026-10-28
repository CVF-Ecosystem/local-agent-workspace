#!/usr/bin/env python3
"""Read-only office work view from explicit STATE references (V5).

python -B tools/work_status.py --project DIR
The law-work/1 STATE marker navigates only; it grants nothing. No discovery,
AI, writer, process control, import from the data project or Markdown execution.
Matching is a point-in-time observation, not review/acceptance or host enforcement.
"""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import office
import task_checkpoint as tc
import execution_profile
import transaction

MARKER = 'law-work/1'
TASK_RE = re.compile(r'^working/([A-Za-z0-9][A-Za-z0-9._-]{0,127})/([A-Za-z0-9][A-Za-z0-9._-]{0,127})/TASK\.json$')
MAX_TASKS, MAX_RESULTS = 12, 16
LIMITS = ['READ_ONLY_POINT_IN_TIME', 'BINDING_MATCH_IS_NOT_ACCEPTANCE',
          'PERMISSION_AND_HOST_NOT_AUTHENTICATED', 'TOCTOU_NOT_ELIMINATED']


def sections(text):
    result, current = {}, None
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    for line in text.splitlines():
        if line.startswith('## '):
            current = line[3:].strip()
            result[current] = []
        elif current and line.strip() and len(result[current]) < 12:
            result[current].append(line.strip()[:2000])
    return result


def marker(text):
    # A malformed or duplicate marker never falls back to a filesystem search.
    if text.count(MARKER) != 1:
        return None, 'NO_WORK' if MARKER not in text else 'AMBIGUOUS_WORK_MARKER'
    hits = re.findall(r'<!-- law-work/1 (.*?) -->', text, re.S)
    if len(hits) != 1:
        return None, 'INVALID_WORK_MARKER'
    doc, why = office.parse_json(hits[0].encode('utf-8'))
    if why or not isinstance(doc, dict) or set(doc) != {'work_id', 'tasks'}:
        return None, 'INVALID_WORK_MARKER'
    if not isinstance(doc['work_id'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', doc['work_id']):
        return None, 'INVALID_WORK_ID'
    if not isinstance(doc['tasks'], list) or not 1 <= len(doc['tasks']) <= MAX_TASKS:
        return None, 'INVALID_WORK_TASKS'
    seen = set()
    for item in doc['tasks']:
        if not isinstance(item, dict) or set(item) != {'task', 'results'}:
            return None, 'INVALID_TASK_REFERENCE'
        path = item['task']
        match = TASK_RE.fullmatch(path) if isinstance(path, str) else None
        if not match or match.group(1) != doc['work_id'] or path in seen:
            return None, 'INVALID_TASK_REFERENCE'
        seen.add(path)
        refs = item['results']
        if not isinstance(refs, list) or len(refs) > MAX_RESULTS or any(not isinstance(p, str) for p in refs) or len(set(refs)) != len(refs):
            return None, 'INVALID_RESULT_REFERENCES'
        prefix = path[:-len('TASK.json')] + 'assignments/'
        for ref in refs:
            if office.publish_new.path_form_problem(ref) or not ref.startswith(prefix):
                return None, 'INVALID_RESULT_REFERENCE'
            suffix = ref[len(prefix):].split('/')
            if len(suffix) != 2 or suffix[-1] != 'RESULT.json':
                return None, 'INVALID_RESULT_REFERENCE'
    return doc, None


def _safe_scope(task):
    # Explicit data/context refs only; never open arbitrary secrets from a TASK.
    for item in task['inputs'] + task.get('context_refs', []):
        path = item['path']
        if not path.startswith(('references/', 'working/', 'output/', 'archive/', 'roles/', 'skills/')):
            return False
    return True


def _permission(root):
    # Snapshot the two explicit owner files. The owner status helper also enumerates
    # transaction journals, which a Work view must not do.
    for rel in ['PROJECT.md', '.agent/EXECUTION_PROFILE.json']:
        full = os.path.join(root, *rel.split('/'))
        if os.path.lexists(full) and (not transaction.link_free(full, root) or not os.path.isfile(full)):
            return {'state': 'UNAVAILABLE', 'roles': {}, 'problem': 'PERMISSION_PATH_UNSAFE'}
    try:
        project, _ = execution_profile.read_plain(os.path.join(root, 'PROJECT.md'))
        profile, _ = execution_profile.read_plain(os.path.join(root, '.agent', 'EXECUTION_PROFILE.json'))
        if project is None or profile is None:
            return {'state': 'NOT_INSPECTED', 'roles': {}, 'problem': 'PERMISSION_SOURCE_UNAVAILABLE'}
        doc = execution_profile.parse_json_bytes(profile)
        valid, _, _ = execution_profile.evaluate_doc(doc)
        line = execution_profile.project_line(project.decode('utf-8'))[0]
        if valid != 'OK' or doc['authority_owner'] != 'PROFILE' or line != 'POINTER':
            return {'state': 'NOT_INSPECTED', 'roles': {}, 'problem': 'PERMISSION_OWNER_UNVERIFIED'}
        roles = {}
        for role in ('scout', 'worker', 'reviewer'):
            claimed = any(execution_profile._grant_claims_role(g, role) for g in doc.get('grants') or [])
            roles[role] = {'permission': 'GRANT_CLAIMED' if claimed else 'NO_GRANT',
                           'applied': 'NOT_INSPECTED', 'registration': 'NOT_INSPECTED'}
        return {'state': 'CLAIMS_UNVERIFIED', 'roles': roles,
                'profile_digest': tc.sha(profile), 'grant_claim_count': len(doc.get('grants') or []),
                'problem': 'TRANSACTIONS_AND_HOST_NOT_INSPECTED'}
    except Exception:
        return {'state': 'UNAVAILABLE', 'roles': {}, 'problem': 'PERMISSION_UNREADABLE'}


def status(project_root):
    root = os.path.abspath(project_root)
    out = {'schema': 'law.work-status/1', 'result': 'ERROR', 'work_id': None,
           'tasks': [], 'decisions': [], 'waiting': [], 'permission': {},
           'host_stop': 'UNCONFIRMED', 'writes': [], 'scan': False, 'ai_calls': False,
           'reopen_prompt': '', 'stop_prompt': '', 'limits': list(LIMITS), 'problems': []}
    data, why = office.read_rel(root, '.agent/STATE.md', limit=65536)
    if why:
        out['problems'] = ['STATE_' + why]
        return out
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        out['problems'] = ['STATE_NOT_UTF8']
        return out
    out['state_digest'] = tc.sha(data)
    parts = sections(text)
    out['decisions'] = parts.get('Decisions', [])
    out['waiting'] = parts.get('Waiting on user', []) + parts.get('Open items', [])
    doc, why = marker(text)
    if why:
        out['result'] = 'NO_WORK' if why == 'NO_WORK' else 'HELD'
        out['problems'] = [] if why == 'NO_WORK' else [why]
        return out
    out['work_id'] = doc['work_id']
    out['permission'] = _permission(root)
    try:
        v3 = tc.load_v3()
    except Exception:
        out['problems'] = ['CHECKPOINT_OWNER_UNAVAILABLE']
        out['result'] = 'HELD'
        return out
    cache, digest_cache, total_bytes = {}, {}, [0]

    def named_read(project, rel):
        if rel not in cache:
            blob, problem = tc.read_file(project, rel)
            if blob is not None:
                total_bytes[0] += len(blob)
                if total_bytes[0] > 16 * 1024 * 1024:
                    blob, problem = None, 'VIEW_READ_BUDGET_EXCEEDED'
                elif rel in digest_cache and tc.sha(blob) != digest_cache[rel][0]:
                    blob, problem = None, 'CHANGED_DURING_VIEW'
            cache[rel] = blob, problem
        return cache[rel]

    def named_digest(project, rel):
        if rel in cache:
            blob, problem = cache[rel]
            return (tc.sha(blob), len(blob), None) if blob is not None else (None, 0, problem)
        if rel not in digest_cache:
            digest, size, problem = tc.file_digest(project, rel, limit=max(0, 16 * 1024 * 1024 - total_bytes[0]))
            total_bytes[0] += size
            if problem == 'TOO_LARGE':
                problem = 'VIEW_READ_BUDGET_EXCEEDED'
            digest_cache[rel] = digest, size, problem
        return digest_cache[rel]

    for ref in doc['tasks']:
        task, raw, why = tc.read_record(v3, root, ref['task'], 'task', reader=named_read)
        row = {'task_path': ref['task'], 'task_id': None, 'task_revision': None,
               'actor': None, 'method': None, 'intent': '', 'requirements': [],
               'assignments': [], 'problems': []}
        out['tasks'].append(row)
        if why:
            row['problems'].append(why)
            continue
        match = TASK_RE.fullmatch(ref['task'])
        if task['work_id'] != doc['work_id'] or task['task_id'] != match.group(2):
            row['problems'].append('TASK_IDENTITY_MISMATCH')
            continue
        row.update(task_id=task['task_id'], task_revision=task['task_revision'],
                   task_digest=raw, actor=task['authority']['subject'],
                   intent=task['intent']['main_interpretation'][:4000],
                   requirements=[{'req_id': x['req_id'], 'mandatory': x['mandatory'], 'statement': x['statement'][:1500]}
                                 for x in task['acceptance']['requirements'][:20]])
        markers = [x['req_id'] for x in row['requirements'] if x['req_id'].startswith('OFFICE-METHOD:')]
        row['method'] = markers[0] if len(markers) == 1 else None
        if not _safe_scope(task):
            row['problems'].append('INPUT_SCOPE_UNSUPPORTED')
            continue
        row['problems'] += office.guard_task(task, lambda rel: named_read(root, rel))
        allowed = {ref['task']} | set(ref['results'])
        allowed.update(x['path'] for x in task['inputs'] + task.get('context_refs', []))
        if any('source_id' in x for x in task['inputs'] + task.get('context_refs', [])):
            allowed.add('references/_INDEX.xlsx')
        allowed.update(x for a in task['effects']['actions'] for x in a['targets'])
        # Only known result paths: no walk/listdir, no newest-file heuristic.
        if not ref['results']:
            row['assignments'].append({'result_path': None, 'state': 'MISSING', 'problems': ['NO_RESULT_REFERENCE'],
                                       'candidate': None, 'declared_states': [], 'gaps': []})
        for result_rel in ref['results']:
            result, _, _ = tc.read_record(v3, root, result_rel, 'result', reader=named_read)
            slot = result_rel.rsplit('/', 1)[0] + '/'
            if result:
                allowed.update(a['path'] for a in result['artifacts'] if a['path'].startswith(slot + 'candidate/'))

            def scoped_reader(project, rel):
                if rel not in allowed or not rel.startswith(('references/', 'working/', 'output/', 'archive/', 'roles/', 'skills/')):
                    return None, 'READ_SCOPE_UNSUPPORTED'
                return named_read(project, rel)

            def scoped_digest(project, rel):
                if rel not in allowed or not rel.startswith(('references/', 'working/', 'output/', 'archive/', 'roles/', 'skills/')):
                    return None, 0, 'READ_SCOPE_UNSUPPORTED'
                return named_digest(project, rel)

            cp = tc.checkpoint(v3, root, ref['task'], result_rel, reader=scoped_reader, digest_reader=scoped_digest)
            if cp.get('raw', {}).get('task') != raw:
                cp['problems'].append('TASK_CHANGED_DURING_VIEW')
            result = cp.get('result')
            problems = cp['problems']
            state = 'MATCHED' if not problems else ('MISSING' if any(p.startswith('RECORD_RESULT ') and 'MISSING_OR_NOT_REGULAR' in p for p in problems) else 'STALE')
            art = result['artifacts'][0] if result and len(result['artifacts']) == 1 else None
            row['assignments'].append({'result_path': result_rel, 'state': state, 'problems': problems[:40],
                                       'candidate': {'path': art['path'], 'digest': art['digest']} if art else None,
                                       'declared_states': result.get('acceptance_states', []) if result else [],
                                       'gaps': [x[:1000] for x in result.get('gaps', [])[:12]] if result else []})
    out['result'] = 'HELD' if any(
        t['problems'] or any(a['state'] != 'MATCHED' for a in t['assignments'])
        for t in out['tasks']
    ) else 'READY'
    refs = '\n'.join('%s (TASK %s)' % (row['task_path'], row.get('task_digest', 'UNKNOWN')) for row in out['tasks'])
    out['reopen_prompt'] = ('Tiếp việc từ .agent/STATE.md, .agent/HANDOFF.md và TASK hiện hành trên đĩa:\n' + refs +
                            '\nĐọc đúng RESULT/candidate đã tham chiếu, kiểm lại binding/nguồn/quyền hiện hành; giữ phần không khớp ở trạng thái chờ. '
                            'Không tạo lại kết quả hay gọi AI chỉ để mở/xem; tiếp trong quyền đã có, hỏi phần thật sự thiếu.')
    out['stop_prompt'] = ('Đề nghị Main dừng phần việc ' + doc['work_id'] +
                         ' sau khi đối chiếu TASK hiện hành. Không tiếp nhận kết quả về muộn hoặc thay Nháp hiện tại. '
                         'Yêu cầu dừng chưa chứng minh host đã dừng; cần ghi quan sát xác nhận trước khi nói đã dừng.')
    return out


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = ap.parse_args()
    print(json.dumps(status(args.project), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
