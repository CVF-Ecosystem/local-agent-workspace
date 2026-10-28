"""V2-F: assess và collect SAU lượt, entry riêng tách khỏi driver đã chạy (v2f.py giữ nguyên bytes). Chỉ đọc trace/lab, ghi vào thư mục evidence; không sửa lab, RESULT hay driver.

  python -B v2f_post.py assess  --evidence <dir>   dựng assessment từ stream.jsonl, ghi assessment.json (không sửa request.json)
  python -B v2f_post.py collect --evidence <dir>   sao chép các file output/giao sau lượt và ghi baseline-after.json
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
META = os.path.join(HERE, '..', 'meta')
SETUP_PATH = os.path.normpath(os.path.join(META, 'setup.json'))
MANIFEST_PATH = os.path.normpath(os.path.join(META, 'bridge_manifest.json'))
TASK_REL = 'working/v2f/report/TASK.json'
SLOT = 'working/v2f/report/assignments/a1'
CAND_REL = SLOT + '/candidate/draft.txt'
RESULT_REL = SLOT + '/RESULT.json'
SOURCE_REL = 'references/source-documents/LAB-V2F-ghi-chu.txt'
DISPATCH_REL = 'working/v2f/setup/dispatch-package.json'
BRIEF_REL = 'working/v2f/setup/worker-brief.md'
REQUEST_REL = 'working/v2f/request/user-request.txt'
CONTRACT_REL = 'roles/office/executive-secretary.md'
CATALOG_REL = 'roles/office/catalog.json'
SCHEMA_REL = '.cvf/contracts/v3/control.schema.json'
BASELINE = {'roles/README.md': '2f42490f39ed16a4ad30310da28f1bf1764ee3bed48a501f62cc54b842e73ef5',
            'tools/office.py': 'f7e6ae546d97f4f1dda7817b4189ed0bf3f78b1aa8471ce6dfc2f100e1308caf',
            'roles/office/MAIN.md': '929d5319ed8b1b66fd5c4a793321a302892e4307175272cc6a5a95a3ab880183',
            SCHEMA_REL: '21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642',
            'tools/artifacts.py': 'be315aff047b0d73d0a9d15693ac72049edfbb15e9499bb0163687906f782c1a',
            'tools/native_agents.py': 'e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e'}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with open(path, 'rb') as fh:
        return sha(fh.read())


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def save(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def labp(lab, rel):
    return os.path.join(lab, *rel.split('/'))


def _norm(p):
    return os.path.normcase(os.path.normpath(p)) if isinstance(p, str) else None


def tree(root):
    files, dirs = {}, []
    for d, subdirs, names in os.walk(root):
        dirs.extend(os.path.relpath(os.path.join(d, n), root).replace('\\', '/') for n in subdirs)
        for n in names:
            p = os.path.join(d, n)
            files[os.path.relpath(p, root).replace('\\', '/')] = file_sha(p)
    return {'files': files, 'dirs': sorted(dirs)}


def assess_stream(events, lab=None, cmd_observe=None, cmd_checkpoint=None):
    """Đọc trace stream-json và dựng mapping hai invocation <-> pha. Chỉ dùng điều quan sát được; thiếu mắt xích thì complete=False. / Build the two-invocation mapping from the trace only."""
    lab = lab or ''

    def rel(p):
        if lab and isinstance(p, str) and os.path.isabs(p):
            try:
                r = os.path.relpath(p, lab).replace('\\', '/')
            except ValueError:
                return p
            return p if r.startswith('..') else r
        return p
    uses, results = [], {}
    init = None
    final = None
    for i, ev in enumerate(events):
        t = ev.get('type')
        if t == 'system' and ev.get('subtype') == 'init' and init is None:
            init = {'tools': ev.get('tools'), 'agents': ev.get('agents'), 'model': ev.get('model'), 'claude_code_version': ev.get('claude_code_version'),
                    'permissionMode': ev.get('permissionMode'), 'mcp_servers': ev.get('mcp_servers')}
        if t == 'result':
            final = {k: ev.get(k) for k in ('subtype', 'is_error', 'total_cost_usd', 'num_turns', 'duration_ms', 'duration_api_ms', 'stop_reason', 'modelUsage', 'permission_denials', 'errors')}
        content = (ev.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for it in content:
            if not isinstance(it, dict):
                continue
            if t == 'assistant' and it.get('type') == 'tool_use':
                inp = it.get('input') or {}
                row = {'event': i, 'id': it.get('id'), 'parent': ev.get('parent_tool_use_id'), 'name': it.get('name')}
                if it.get('name') in ('Read', 'Write', 'Grep', 'Glob'):
                    row['raw_path'] = inp.get('file_path') or inp.get('path')
                    row['path'] = rel(row['raw_path'])
                if it.get('name') == 'Read':
                    row['offset'], row['limit'] = inp.get('offset'), inp.get('limit')
                if it.get('name') == 'Write':
                    c = inp.get('content')
                    row['content_sha256'] = sha(c.encode('utf-8')) if isinstance(c, str) else None
                    row['content_chars'] = len(c) if isinstance(c, str) else None
                if it.get('name') == 'Bash':
                    row['command'] = inp.get('command')
                if it.get('name') in ('Agent', 'Task'):
                    row['subagent_type'] = inp.get('subagent_type')
                    row['model_override'] = inp.get('model')
                    row['run_in_background'] = inp.get('run_in_background')
                    row['other_keys'] = sorted(k for k in inp if k not in ('description', 'subagent_type', 'prompt', 'model', 'run_in_background'))
                    row['prompt_sha256'] = sha(inp.get('prompt', '').encode('utf-8')) if isinstance(inp.get('prompt'), str) else None
                    row['prompt_chars'] = len(inp.get('prompt') or '')
                if it.get('name') == 'SendMessage':
                    row['to'] = inp.get('to')
                uses.append(row)
            if t == 'user' and it.get('type') == 'tool_result':
                cont = it.get('content')
                text = cont if isinstance(cont, str) else ' '.join(x.get('text', '') for x in cont if isinstance(x, dict)) if isinstance(cont, list) else ''
                results[it.get('tool_use_id')] = {'event': i, 'is_error': it.get('is_error'), 'text_head': text[:1500], 'text_full': text, 'text_sha256': sha(text.encode('utf-8')), 'text_chars': len(text),
                                                  'agent_id': (re.search(r'agentId:\s*([0-9A-Za-z_-]+)', text) or [None, None])[1]}
    top = [u for u in uses if not u['parent']]
    agents = [u for u in top if u['name'] in ('Agent', 'Task')]
    bash = [u for u in top if u['name'] == 'Bash']
    problems, notes = [], []
    if init is None:
        problems.append('NO_INIT_EVENT')
    if len(agents) != 2:
        problems.append('AGENT_CALLS=%d (expected 2)' % len(agents))
    ids = [results.get(a['id'], {}).get('agent_id') for a in agents]
    if len(agents) == 2 and (not all(ids) or ids[0] == ids[1]):
        problems.append('AGENT_IDS_MISSING_OR_EQUAL %s' % ids)
    for a in agents:
        if a.get('subagent_type') != 'law-worker' or a.get('model_override') or a.get('run_in_background') or a.get('other_keys'):
            problems.append('AGENT_CALL_NOT_PLAIN_FOREGROUND_LAW_WORKER event=%s' % a['event'])
    banned = sorted({u['name'] for u in uses if u['name'] not in ('Agent', 'Task', 'Read', 'Grep', 'Glob', 'Write', 'Bash')})
    if banned:
        problems.append('UNEXPECTED_TOOLS %s' % banned)
    if [u for u in top if u['name'] == 'Write']:
        problems.append('MAIN_WROTE')
    cmds = [(b['command'] or '').strip() for b in bash]
    if len(bash) != 2 or (cmd_observe is not None and (cmds[0] != cmd_observe or cmds[1] != cmd_checkpoint)):
        problems.append('MAIN_BASH_NOT_OBSERVE_THEN_CHECKPOINT %s' % cmds)
    outcomes = []
    for bsh in bash:
        txt = (results.get(bsh['id']) or {}).get('text_full') or ''
        try:
            doc = json.loads(txt[txt.index('{'):]) if '{' in txt else {}
        except ValueError:
            doc = {}
        outcomes.append({'event': bsh['event'], 'command': bsh['command'], 'is_error': (results.get(bsh['id']) or {}).get('is_error'), 'ok': doc.get('ok'), 'verdict': doc.get('verdict'),
                         'problems': doc.get('problems'), 'refused_before_operation': doc.get('refused_before_operation'), 'identity': doc.get('identity'),
                         'observation_candidate': (doc.get('observation') or {}).get('candidate')})
    if len(outcomes) == 2:
        if outcomes[0]['ok'] is not True or outcomes[0]['problems'] != []:
            problems.append('OBSERVE_NOT_OK %s' % outcomes[0]['problems'])
        c = outcomes[1]
        if c['ok'] is not True or c['problems'] != [] or c['verdict'] != 'CHECKED_NOT_PASS':
            problems.append('CHECKPOINT_NOT_OK verdict=%s problems=%s' % (c['verdict'], c['problems']))
        ident = c.get('identity') or {}
        if ident.get('task_equals_dispatch_digest') is not True or ident.get('result_binding_equals_dispatch_stub_before_outputs') is not True:
            problems.append('CHECKPOINT_IDENTITY_NOT_TRUE %s' % {k: ident.get(k) for k in ('task_equals_dispatch_digest', 'result_binding_equals_dispatch_stub_before_outputs')})
        oc, cc = outcomes[0].get('observation_candidate') or {}, ident.get('candidate') or {}
        if not oc or oc.get('digest') != cc.get('digest') or oc.get('path') != cc.get('path'):
            problems.append('OBSERVE_AND_CHECKPOINT_CANDIDATE_DIFFER')
    by_parent = {}
    for u in uses:
        if u['parent']:
            by_parent.setdefault(u['parent'], []).append(u)
    phases = []
    failed_reads, schema_reads = [], []
    for n, a in enumerate(agents[:2]):
        kids = by_parent.get(a['id'], [])
        writes = [k['path'] for k in kids if k['name'] == 'Write']
        reads = [k['path'] for k in kids if k['name'] == 'Read']
        other = sorted({k['name'] for k in kids if k['name'] not in ('Read', 'Grep', 'Glob', 'Write')})
        read_rows = []
        for k in kids:
            if k['name'] != 'Read':
                continue
            res = results.get(k['id']) or {}
            row = {'event': k['event'], 'path': k['path'], 'raw_path': k.get('raw_path'), 'offset': k.get('offset'), 'limit': k.get('limit'), 'is_error': res.get('is_error'),
                   'result_chars': res.get('text_chars'), 'result_sha256': res.get('text_sha256')}
            read_rows.append(row)
            if res.get('is_error') or res.get('text_chars') is None or (isinstance(k['path'], str) and '.json#' in k['path']):
                failed_reads.append(dict(row, phase=n + 1, head=(res.get('text_head') or '')[:300]))
        phases.append({'phase': n + 1, 'agent_tool_use_id': a['id'], 'agent_tool_name': a['name'], 'agent_id': ids[n] if n < len(ids) else None, 'writes': writes, 'reads': reads, 'read_rows': read_rows,
                       'other_tools': other, 'terminal_result': {k: v for k, v in (results.get(a['id']) or {}).items() if k in ('event', 'is_error', 'text_sha256', 'text_chars')}})
    main_failed = [dict(event=u['event'], path=u.get('path'), head=(results.get(u['id']) or {}).get('text_head', '')[:200]) for u in top if u['name'] == 'Read' and (results.get(u['id']) or {}).get('is_error')]
    if len(phases) == 2:
        p1, p2 = phases
        if p1['writes'] != [CAND_REL]:
            problems.append('PHASE1_WRITES %s' % p1['writes'])
        if p2['writes'] != [RESULT_REL]:
            problems.append('PHASE2_WRITES %s' % p2['writes'])
        for need in (BRIEF_REL, TASK_REL, SOURCE_REL):
            if not any(_norm(r) == _norm(need) for r in p1['reads']):
                problems.append('PHASE1_NO_READ ' + need)
        for need in (BRIEF_REL, TASK_REL, CAND_REL, SOURCE_REL, CONTRACT_REL):
            if not any(_norm(r) == _norm(need) for r in p2['reads']):
                problems.append('PHASE2_NO_READ ' + need)
        # schema: Worker 2 phải có một Read thành công đúng file schema thật mà kết quả mang nội dung result/refs, không chỉ Read thất bại hoặc đường `...json#...`
        good = []
        for k in by_parent.get(agents[1]['id'], []):
            if k['name'] == 'Read' and _norm(k.get('path')) == _norm(SCHEMA_REL):
                res = results.get(k['id']) or {}
                txt = res.get('text_full') or ''
                if not res.get('is_error') and 'evidence_id' in txt and 'mandatory' in txt:
                    good.append({'event': k['event'], 'offset': k.get('offset'), 'limit': k.get('limit'), 'result_chars': res.get('text_chars'), 'has_result_def': '"result"' in txt})
        schema_reads = good
        if not good:
            problems.append('PHASE2_NO_SUCCESSFUL_SCHEMA_READ_WITH_RESULT_CONTENT')
        if p1['other_tools'] or p2['other_tools']:
            problems.append('CHILD_OTHER_TOOLS %s %s' % (p1['other_tools'], p2['other_tools']))
        order = [agents[0]['event'], bash[0]['event'] if bash else None, agents[1]['event'], bash[1]['event'] if len(bash) > 1 else None]
        if None in order or order != sorted(order):
            problems.append('ORDER_NOT_AGENT1_OBSERVE_AGENT2_CHECKPOINT %s' % order)
        t1 = results.get(agents[0]['id'], {}).get('event')
        if t1 is None or (bash and bash[0]['event'] < t1):
            problems.append('OBSERVE_BEFORE_PHASE1_TERMINAL_RESULT')
        t2 = results.get(agents[1]['id'], {}).get('event')
        if t2 is None or (len(bash) > 1 and bash[1]['event'] < t2):
            problems.append('CHECKPOINT_BEFORE_PHASE2_TERMINAL_RESULT')
    if failed_reads:
        notes.append('CHILD_FAILED_OR_FRAGMENT_READS=%d (xem failed_reads; không tự là lỗi nếu có Read thành công sau đó)' % len(failed_reads))
    if main_failed:
        notes.append('MAIN_FAILED_READS=%d' % len(main_failed))
    if final and final.get('permission_denials'):
        notes.append('PERMISSION_DENIALS=%d' % len(final['permission_denials']))
    complete = not problems and final is not None
    status = 'IMPLEMENTED_PENDING_REVIEW' if complete else ('LIVE_NOT_RUN' if not uses else 'PARTIAL')
    return {'complete': complete, 'status': status, 'problems': problems, 'notes': notes, 'init': init, 'result_event': final, 'phases': phases, 'failed_child_reads': failed_reads,
            'failed_main_reads': main_failed, 'phase2_schema_reads': schema_reads, 'main_bash': outcomes, 'tool_use_count': len(uses),
            'tool_use_names': sorted({u['name'] for u in uses}), 'agent_calls': [{k: v for k, v in a.items() if k != 'parent'} for a in agents],
            'note': 'Mapping hai actual agentId <-> pha là khai báo cooperative suy từ trace; không xác thực danh tính/quyền của host. Terminal result không là bằng chứng remote stop.'}


def reconcile(evidence, lab, a):
    """Đối chiếu bytes lab sau lượt với request.json trước lượt và với content Write trong trace. / Compare the lab after with the recorded before and with the Write content."""
    req = load(os.path.join(evidence, 'request.json'))
    before = req['before_tree']
    after = tree(lab)
    added = sorted(set(after['files']) - set(before['files']))
    removed = sorted(set(before['files']) - set(after['files']))
    changed = sorted(k for k in before['files'] if k in after['files'] and before['files'][k] != after['files'][k])
    out = {'added': added, 'removed': removed, 'changed': changed, 'dirs_added': sorted(set(after['dirs']) - set(before['dirs'])), 'dirs_removed': sorted(set(before['dirs']) - set(after['dirs']))}
    out['added_equal_candidate_and_result_only'] = sorted(added) == sorted([CAND_REL, RESULT_REL])
    out['nothing_removed_or_changed'] = not removed and not changed
    return out


def assess(evidence):
    req = load(os.path.join(evidence, 'request.json'))
    events = []
    with open(os.path.join(evidence, 'stream.jsonl'), 'rb') as fh:
        for raw in fh:
            try:
                events.append(json.loads(raw.decode('utf-8', 'replace')))
            except ValueError:
                pass
    cmds = req['allowed_tools_rules'][-2:]
    obs_cmd, chk_cmd = [c[len('Bash('):-1] for c in cmds]
    a = assess_stream(events, req.get('lab'), obs_cmd, chk_cmd)
    # nội dung Write trong trace == bytes file trên đĩa
    lab = req['lab']
    rec = reconcile(evidence, lab, a)
    writes = []
    for e in events:
        for it in ((e.get('message') or {}).get('content') or []):
            if isinstance(it, dict) and it.get('type') == 'tool_use' and it.get('name') == 'Write':
                inp = it.get('input') or {}
                p = inp.get('file_path')
                c = inp.get('content')
                if isinstance(p, str) and isinstance(c, str):
                    r = os.path.relpath(p, lab).replace('\\', '/') if os.path.isabs(p) else p
                    disk = labp(lab, r) if not r.startswith('..') else None
                    on_disk = file_sha(disk) if disk and os.path.isfile(disk) else None
                    writes.append({'path': r, 'trace_content_sha256': sha(c.encode('utf-8')), 'trace_content_chars': len(c), 'disk_sha256': on_disk,
                                   'disk_equals_trace_content_utf8': on_disk == sha(c.encode('utf-8')),
                                   'disk_equals_trace_content_crlf_variant': on_disk == sha(c.replace('\n', '\r\n').encode('utf-8'))})
    rec['writes_vs_disk'] = writes
    doc = {'assessed_at': now(), 'assessment_machine': a, 'lab_reconcile': rec, 'driver_sha256_now': file_sha(os.path.join(HERE, 'v2f.py')),
           'driver_sha256_before_call': req['runtime_pins']['v2f.py']['sha256']}
    doc['driver_bytes_unchanged_since_prepare'] = doc['driver_sha256_now'] == doc['driver_sha256_before_call']
    save(os.path.join(evidence, 'assessment.json'), doc)
    print(json.dumps({k: a[k] for k in ('complete', 'status', 'problems', 'notes')}, ensure_ascii=False, indent=2))
    for ph in a['phases']:
        print(json.dumps({k: ph[k] for k in ('phase', 'agent_id', 'writes', 'reads')}, ensure_ascii=False))
    print(json.dumps(a['result_event'], ensure_ascii=False))
    print(json.dumps({k: rec[k] for k in ('added', 'removed', 'changed', 'added_equal_candidate_and_result_only', 'nothing_removed_or_changed')}, ensure_ascii=False))
    print(json.dumps(rec['writes_vs_disk'], ensure_ascii=False))


def collect(evidence):
    setup_doc = load(SETUP_PATH)
    lab = setup_doc['lab']
    ev_lab = os.path.join(evidence, 'lab-after')
    items = {'TASK.json': TASK_REL, 'dispatch-package.json': DISPATCH_REL, 'worker-brief.md': BRIEF_REL, 'user-request.txt': REQUEST_REL, 'LAB-V2F-ghi-chu.txt': SOURCE_REL,
             'candidate-draft.txt': CAND_REL, 'RESULT.json': RESULT_REL, 'native-worker.md': '.claude/agents/law-worker.md',
             'receipt-worker.json': '.agent/runtime/native-agents/claude-code/law-worker.json', 'profile.json': '.agent/EXECUTION_PROFILE.json',
             'catalog.json': CATALOG_REL, 'executive-secretary.md': CONTRACT_REL, 'control.schema.json': SCHEMA_REL}
    copied = {}
    for name, rel in items.items():
        src = labp(lab, rel)
        if os.path.isfile(src):
            with open(src, 'rb') as fh:
                data = fh.read()
            write_bytes(os.path.join(ev_lab, name), data)
            copied[name] = {'lab_path': rel, 'sha256': sha(data), 'size': len(data)}
        else:
            copied[name] = {'lab_path': rel, 'present': False}
    after = {'collected_at': now(), 'copies': copied, 'baseline_six_after': {rel: {'sha256': file_sha(os.path.join(REPO, *rel.split('/'))), 'baseline': want,
                                                                                 'equal': file_sha(os.path.join(REPO, *rel.split('/'))) == want} for rel, want in BASELINE.items()},
             'runtime_sources_after': {n: file_sha(os.path.join(HERE, n)) for n in ('v2f.py', 'main_bridge.py', 'prompt-v2f.txt', 'v2f_post.py')},
             'setup_sha256_after': file_sha(SETUP_PATH), 'manifest_sha256_after': file_sha(MANIFEST_PATH),
             'pycache_files_in_source_tree': len([1 for d, _, ns in os.walk(REPO) for n in ns if d.endswith('__pycache__')])}
    save(os.path.join(evidence, 'baseline-after.json'), after)
    print(json.dumps(after, ensure_ascii=False, indent=2)[:3500])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('assess', 'collect'))
    ap.add_argument('--evidence', required=True)
    a = ap.parse_args()
    if a.cmd == 'assess':
        assess(a.evidence)
    else:
        collect(a.evidence)


if __name__ == '__main__':
    main()
