"""V2-G: assess và collect SAU lượt, entry riêng tách khỏi driver đã chạy (v2g.py giữ nguyên bytes). Chỉ đọc trace/lab, ghi vào thư mục evidence; không sửa lab, config hay driver.

  python -B v2g_post.py assess  --evidence <dir>   dựng assessment từ stream.jsonl + request.json, ghi assessment.json (không sửa request.json)
  python -B v2g_post.py collect --evidence <dir>   sao chép ba artifact (origin: lab F, không phải Main Write), F provenance và ghi baseline-after.json
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
META = os.path.join(HERE, '..', 'meta')
CONFIG_PATH = os.path.normpath(os.path.join(META, 'config.json'))
MANIFEST_PATH = os.path.normpath(os.path.join(META, 'bridge_manifest.json'))
F_EVIDENCE = os.path.join(REPO, 'roadmap', 'evidence', 'v2f-native-valid-result-2026-10-22')
F_SCRIPTS = os.path.join(REPO, 'working', 'v2f')
POLICY_SHA256 = 'af141b37c242119c07fe0b6268a498a66ea89efd8caacb9a95cbfb06e7235084'
BASELINE = {'roles/README.md': '2f42490f39ed16a4ad30310da28f1bf1764ee3bed48a501f62cc54b842e73ef5',
            'tools/office.py': 'f7e6ae546d97f4f1dda7817b4189ed0bf3f78b1aa8471ce6dfc2f100e1308caf',
            'roles/office/MAIN.md': '929d5319ed8b1b66fd5c4a793321a302892e4307175272cc6a5a95a3ab880183',
            '.cvf/contracts/v3/control.schema.json': '21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642',
            '.cvf/rules/v3/ROUTING_POLICY.json': POLICY_SHA256}


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


def norm(p):
    return os.path.normcase(os.path.normpath(p)) if isinstance(p, str) else None


def tree(root):
    files, dirs = {}, []
    for d, subdirs, names in os.walk(root):
        dirs.extend(os.path.relpath(os.path.join(d, n), root).replace('\\', '/') for n in subdirs)
        for n in names:
            p = os.path.join(d, n)
            files[os.path.relpath(p, root).replace('\\', '/')] = file_sha(p)
    return {'files': files, 'dirs': sorted(dirs)}


def tree_digest(t):
    return sha(json.dumps(t, sort_keys=True).encode('utf-8'))


def assess_stream(events, config, cmd_checkpoint):
    """Đọc trace stream-json của lượt Main-only: ba Read thành công đúng đường tuyệt đối, đúng một Bash đúng lệnh, stdout checkpoint khớp bảng định danh. Thiếu mắt xích thì complete=False. / Build the Main-only mapping from the trace."""
    lab, arts = config['lab'], config['artifacts']
    want_paths = {k: labp(lab, a['rel']) for k, a in arts.items()}
    uses, results, init, final = [], {}, None, None
    for i, ev in enumerate(events):
        t = ev.get('type')
        if t == 'system' and ev.get('subtype') == 'init' and init is None:
            init = {k: ev.get(k) for k in ('tools', 'agents', 'model', 'claude_code_version', 'permissionMode', 'mcp_servers', 'slash_commands')}
        if t == 'result':
            final = {k: ev.get(k) for k in ('subtype', 'is_error', 'total_cost_usd', 'num_turns', 'duration_ms', 'duration_api_ms', 'stop_reason', 'modelUsage', 'permission_denials', 'errors', 'result')}
        content = (ev.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for it in content:
            if not isinstance(it, dict):
                continue
            if t == 'assistant' and it.get('type') == 'tool_use':
                inp = it.get('input') or {}
                row = {'event': i, 'id': it.get('id'), 'parent': ev.get('parent_tool_use_id'), 'name': it.get('name')}
                if it.get('name') == 'Read':
                    row.update(raw_path=inp.get('file_path'), offset=inp.get('offset'), limit=inp.get('limit'), other_keys=sorted(k for k in inp if k not in ('file_path', 'offset', 'limit')))
                if it.get('name') == 'Bash':
                    row['command'] = inp.get('command')
                    row['other_keys'] = sorted(k for k in inp if k not in ('command', 'description'))
                uses.append(row)
            if t == 'user' and it.get('type') == 'tool_result':
                cont = it.get('content')
                text = cont if isinstance(cont, str) else ' '.join(x.get('text', '') for x in cont if isinstance(x, dict)) if isinstance(cont, list) else ''
                results[it.get('tool_use_id')] = {'event': i, 'is_error': it.get('is_error'), 'text_full': text, 'text_sha256': sha(text.encode('utf-8')), 'text_chars': len(text)}
    problems, notes = [], []
    if init is None:
        problems.append('NO_INIT_EVENT')
    elif sorted(init.get('tools') or []) != ['Bash', 'Read']:
        problems.append('INIT_TOOLS_NOT_READ_BASH_ONLY %s' % init.get('tools'))
    names = [u['name'] for u in uses]
    if any(u['parent'] for u in uses):
        problems.append('CHILD_TOOL_USE_PRESENT')
    banned = sorted({n for n in names if n not in ('Read', 'Bash')})
    if banned:
        problems.append('UNEXPECTED_TOOLS %s' % banned)
    reads = [u for u in uses if u['name'] == 'Read']
    bash = [u for u in uses if u['name'] == 'Bash']
    read_rows = []
    for u in reads:
        res = results.get(u['id']) or {}
        read_rows.append({'event': u['event'], 'path': u['raw_path'], 'offset': u['offset'], 'limit': u['limit'], 'other_keys': u['other_keys'], 'is_error': res.get('is_error'),
                          'result_chars': res.get('text_chars'), 'result_sha256': res.get('text_sha256'), 'has_tool_result': u['id'] in results})
    matched = {}
    for k, want in want_paths.items():
        ok_rows = [r for r in read_rows if norm(r['path']) == norm(want) and r['has_tool_result'] and not r['is_error'] and r['offset'] in (None, 0, 1) and r['limit'] is None]
        matched[k] = len(ok_rows)
        if len(ok_rows) != 1:
            problems.append('READ_%s_SUCCESSFUL_COUNT=%d (expected 1)' % (k.upper(), len(ok_rows)))
    if len(reads) != 3 or any(norm(r['path']) not in {norm(w) for w in want_paths.values()} for r in read_rows):
        problems.append('READS_NOT_EXACTLY_THE_THREE_ABSOLUTE_PATHS %s' % [r['path'] for r in read_rows])
    cmd = [(b['command'] or '').strip() for b in bash]
    if len(bash) != 1 or cmd[0] != cmd_checkpoint or bash[0]['other_keys']:
        problems.append('BASH_NOT_EXACTLY_ONE_CHECKPOINT %s' % cmd)
    outcome = None
    if len(bash) == 1:
        res = results.get(bash[0]['id'])
        if res is None:
            problems.append('BASH_HAS_NO_TOOL_RESULT')
        else:
            txt = res['text_full']
            try:
                doc = json.loads(txt[txt.index('{'):]) if '{' in txt else {}
            except ValueError:
                doc = {}
            outcome = {'event': bash[0]['event'], 'is_error': res.get('is_error'), 'stdout_sha256': res['text_sha256'], 'stdout_chars': res['text_chars'], 'parsed': bool(doc),
                       'ok': doc.get('ok'), 'verdict': doc.get('verdict'), 'problems': doc.get('problems'), 'refused_before_operation': doc.get('refused_before_operation'),
                       'identity': doc.get('identity'), 'policy': doc.get('policy'), 'lab_snapshot': doc.get('lab_snapshot'), 'bridge': doc.get('bridge')}
            ident = doc.get('identity') or {}
            cand = ident.get('candidate') or {}
            if doc.get('ok') is not True or doc.get('problems') != [] or doc.get('verdict') != 'CHECKED_NOT_PASS':
                problems.append('CHECKPOINT_NOT_OK verdict=%s problems=%s' % (doc.get('verdict'), doc.get('problems')))
            if ident.get('task_raw_digest') != 'sha256:' + arts['task']['sha256'] or ident.get('result_raw_digest') != 'sha256:' + arts['result']['sha256']:
                problems.append('RAW_DIGEST_TASK_OR_RESULT_DIFFERS_FROM_TABLE')
            if cand.get('digest') != 'sha256:' + arts['candidate']['sha256'] or cand.get('size') != arts['candidate']['size'] or cand.get('path') != arts['candidate']['rel']:
                problems.append('CANDIDATE_IDENTITY_DIFFERS_FROM_TABLE')
            if ident.get('task_equals_dispatch_digest') is not True or ident.get('result_binding_equals_dispatch_stub_before_outputs') is not True or ident.get('raw_digests_equal_config') is not True:
                problems.append('IDENTITY_FLAGS_NOT_TRUE')
            pol = doc.get('policy') or {}
            if pol.get('loader_policy_rel') != 'rules/v3/ROUTING_POLICY.json' or not (pol.get('disk_sha256') == pol.get('owner_bytes_sha256') == pol.get('owner_policy_sha256') == POLICY_SHA256):
                problems.append('POLICY_NOT_PINNED_V3')
            if (doc.get('lab_snapshot') or {}).get('equal') is not True:
                problems.append('LAB_SNAPSHOT_NOT_EQUAL')
    if len(bash) == 1 and reads:
        last_read = max(r['event'] for r in read_rows)
        if bash[0]['event'] < last_read or any(not r['has_tool_result'] for r in read_rows):
            notes.append('BASH_ISSUED_BEFORE_ALL_READS_COMPLETED_OR_A_READ_HAS_NO_RESULT (order is a trace observation)')
    if final is None:
        problems.append('NO_RESULT_EVENT')
    elif final.get('is_error') or final.get('subtype') != 'success':
        problems.append('RESULT_EVENT_NOT_SUCCESS subtype=%s is_error=%s' % (final.get('subtype'), final.get('is_error')))
    if final and final.get('permission_denials'):
        notes.append('PERMISSION_DENIALS=%d' % len(final['permission_denials']))
    complete = not problems and final is not None
    status = 'IMPLEMENTED_PENDING_REVIEW' if complete else ('LIVE_NOT_RUN' if not uses and init is None else 'PARTIAL')
    return {'complete': complete, 'status': status, 'problems': problems, 'notes': notes, 'init': init, 'result_event': final, 'reads': read_rows, 'reads_matched': matched, 'bash': outcome,
            'bash_commands': cmd, 'tool_use_count': len(uses), 'tool_use_names': sorted(set(names)),
            'note': 'Danh sách công cụ/allow-rule là cấu hình đã yêu cầu; trace là quan sát; không claim sandbox hay khống chế mọi tác động từ xa. Terminal result không là bằng chứng remote stop.'}


def assess(evidence):
    req = load(os.path.join(evidence, 'request.json'))
    config = load(CONFIG_PATH)
    events = []
    with open(os.path.join(evidence, 'stream.jsonl'), 'rb') as fh:
        for raw in fh:
            try:
                events.append(json.loads(raw.decode('utf-8', 'replace')))
            except ValueError:
                pass
    cmd = req['allowed_tools_rules'][-1][len('Bash('):-1]
    a = assess_stream(events, config, cmd)
    lab = req['lab']
    before, after = req['before_tree'], req.get('after_tree') or tree(lab)
    snap = {'added': sorted(set(after['files']) - set(before['files'])), 'removed': sorted(set(before['files']) - set(after['files'])),
            'changed': sorted(k for k in before['files'] if k in after['files'] and before['files'][k] != after['files'][k]),
            'dirs_added': sorted(set(after['dirs']) - set(before['dirs'])), 'dirs_removed': sorted(set(before['dirs']) - set(after['dirs'])),
            'files_before': len(before['files']), 'files_after': len(after['files']), 'dirs_before': len(before['dirs']), 'dirs_after': len(after['dirs']),
            'tree_digest_before': tree_digest(before), 'tree_digest_after': tree_digest(after), 'config_snapshot_digest': config['lab_snapshot']['tree_digest']}
    snap['zero_change'] = not (snap['added'] or snap['removed'] or snap['changed'] or snap['dirs_added'] or snap['dirs_removed']) and snap['tree_digest_before'] == snap['tree_digest_after'] == snap['config_snapshot_digest']
    if not snap['zero_change']:
        a['problems'].append('LAB_NOT_ZERO_CHANGE')
        a['complete'], a['status'] = False, 'PARTIAL'
    cmp = {n: file_sha(os.path.join(HERE, n)) == req['runtime_pins'][n]['sha256'] for n in ('v2g.py', 'main_bridge.py', 'prompt-v2g.txt', 'v2g_post.py')}
    cmp.update({'config.json': file_sha(CONFIG_PATH) == req['runtime_pins']['config.json']['sha256'], 'bridge_manifest.json': file_sha(MANIFEST_PATH) == req['runtime_pins']['bridge_manifest.json']['sha256']})
    drivers = {k: v for k, v in cmp.items() if k != 'v2g_post.py'}
    if not all(drivers.values()):
        a['problems'].append('RUNTIME_SOURCE_CHANGED_SINCE_PREPARE %s' % [k for k, v in drivers.items() if not v])
        a['complete'], a['status'] = False, 'PARTIAL'
    doc = {'assessed_at': now(), 'assessment_machine': a, 'lab_snapshot_compare': snap, 'runtime_unchanged_since_prepare': cmp,
           'note': 'Assessment tách khỏi driver đã chạy; v2g_post.py chưa được pin lúc prepare nếu sửa sau (so sánh bên trên bỏ qua v2g_post.py).'}
    save(os.path.join(evidence, 'assessment.json'), doc)
    print(json.dumps({k: a[k] for k in ('complete', 'status', 'problems', 'notes')}, ensure_ascii=False, indent=2))
    print(json.dumps(a['result_event'], ensure_ascii=False)[:1500])
    print(json.dumps({k: v for k, v in snap.items() if k not in ('added', 'removed', 'changed')}, ensure_ascii=False), 'added', snap['added'], 'removed', snap['removed'], 'changed', snap['changed'])


def collect(evidence):
    config = load(CONFIG_PATH)
    lab = config['lab']
    ev_lab = os.path.join(evidence, 'artifact-copies')
    copied = {}
    for key, a in config['artifacts'].items():
        src = labp(lab, a['rel'])
        with open(src, 'rb') as fh:
            data = fh.read()
        name = {'task': 'TASK.json', 'result': 'RESULT.json', 'candidate': 'candidate-draft.txt'}[key]
        write_bytes(os.path.join(ev_lab, name), data)
        copied[name] = {'origin': 'lab F: ' + src, 'lab_path': a['rel'], 'sha256': sha(data), 'size': len(data), 'equals_table': sha(data) == a['sha256'] and len(data) == a['size'],
                        'authorship': 'copy made by the G collector for review; NOT a Main Write (Main has no Write tool); candidate and RESULT were written by the F native Worker invocations'}
    f_assess = load(os.path.join(F_EVIDENCE, 'assessment.json'))['assessment_machine']
    f_prov = {'f_evidence_dir': 'roadmap/evidence/v2f-native-valid-result-2026-10-22/', 'f_status': f_assess['status'], 'f_problems': f_assess['problems'],
              'f_native_invocations': [{'phase': p['phase'], 'agent_id': p['agent_id'], 'writes': p['writes']} for p in f_assess['phases']],
              'f_logical_worker': 'worker-v2f (role worker)', 'f_task': 'report revision 1, assignment a1', 'f_grants': [], 'f_intent': 'UNVERIFIED/NONE',
              'f_result_acceptance': 'CANDIDATE (requirement UNKNOWN)', 'f_checkpoint_in_original_trace': 'none (F lacked the same-session checkpoint; G does not backfill it)',
              'f_result_event': {k: (f_assess['result_event'] or {}).get(k) for k in ('subtype', 'total_cost_usd', 'num_turns')},
              'f_bridge_policy_pin': 'v1 .cvf/rules/ROUTING_POLICY.json (finding F, not corrected retroactively)'}
    after = {'collected_at': now(), 'copies': copied, 'f_provenance': f_prov,
             'baseline_after': {rel: {'sha256': file_sha(os.path.join(REPO, *rel.split('/'))), 'baseline': want, 'equal': file_sha(os.path.join(REPO, *rel.split('/'))) == want} for rel, want in BASELINE.items()},
             'runtime_sources_after': {n: file_sha(os.path.join(HERE, n)) for n in ('v2g.py', 'main_bridge.py', 'prompt-v2g.txt', 'v2g_post.py')},
             'config_sha256_after': file_sha(CONFIG_PATH), 'manifest_sha256_after': file_sha(MANIFEST_PATH),
             'f_history_pins_after': {'f_evidence': tree_digest(tree(F_EVIDENCE)), 'f_scripts_meta': tree_digest(tree(F_SCRIPTS))},
             'pycache_files_in_source_tree': len([1 for d, _, ns in os.walk(REPO) for n in ns if d.endswith('__pycache__')])}
    req = load(os.path.join(evidence, 'request.json'))
    after['f_history_unchanged'] = after['f_history_pins_after'] == req['preflight']['f_history_pins']
    save(os.path.join(evidence, 'baseline-after.json'), after)
    print(json.dumps({k: after[k] for k in ('copies', 'baseline_after', 'runtime_sources_after', 'f_history_unchanged', 'pycache_files_in_source_tree')}, ensure_ascii=False, indent=2)[:3500])


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
