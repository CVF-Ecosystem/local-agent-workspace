"""V2-F: dựng lab dữ liệu giả với gói giao E, kiểm offline và chạy MỘT lượt Claude CLI (hai native invocation tuần tự). Script hỗ trợ bài đo, không phải công cụ sản phẩm.
Driver này chỉ gồm setup/anchor/selftest/prepare/run. Assess và collect sau lượt nằm ở v2f_post.py (entry riêng), để bytes driver đã chạy không đổi.

Dùng (đường Windows có drive tuyệt đối): / Usage:
  python -B v2f.py setup --base <thu-muc-moi>          dựng lab + hai fixture + manifest + setup.json (offline, không gọi AI)
  python -B v2f.py anchor                              chốt EXPECTED_SETUP_SHA256/EXPECTED_LAB vào bridge (sau setup, trước pin bridge)
  python -B v2f.py selftest                            kiểm delta F trên fixture tách khỏi slot live (offline)
  python -B v2f.py prepare --evidence <dir>            preflight, lưu bytes/hash runtime, ghi request.json BEFORE_CALL; chưa gọi model
  python -B v2f.py run --evidence <dir>                kiểm lại bytes, gọi đúng MỘT lần claude; cổng init; không retry
"""
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
META = os.path.join(HERE, '..', 'meta')
SETUP_PATH = os.path.normpath(os.path.join(META, 'setup.json'))
MANIFEST_PATH = os.path.normpath(os.path.join(META, 'bridge_manifest.json'))
BRIDGE = os.path.join(HERE, 'main_bridge.py')
POST = os.path.join(HERE, 'v2f_post.py')
CLAUDE_BASELINE = {'size': 242411680, 'sha256': '6d34836bf4d62f4bd5221fb69899ed5b2edc380d35fb0f23218c62fae94e28b9', 'version': '2.1.81 (Claude Code)'}
CLAUDE = r'C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe\claude.EXE'
MODEL = 'claude-sonnet-5-5'
TIMEOUT = 300
BUDGET = '0.75'
ENV_ADDED = {'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
TOOLS = 'Agent,Read,Grep,Glob,Write,Bash'
PROMPT_FILE = os.path.join(HERE, 'prompt-v2f.txt')
BRIDGE_FWD = BRIDGE.replace('\\', '/')
CMD_OBSERVE = 'python -I -B "%s" observe' % BRIDGE_FWD
CMD_CHECKPOINT = 'python -I -B "%s" checkpoint' % BRIDGE_FWD
ALLOWED = 'Agent,Read,Grep,Glob,Write,Bash(%s),Bash(%s)' % (CMD_OBSERVE, CMD_CHECKPOINT)
SCHEMA_REL = '.cvf/contracts/v3/control.schema.json'
SCHEMA_POINTER = '#/$defs/result'
BASELINE = {'roles/README.md': '2f42490f39ed16a4ad30310da28f1bf1764ee3bed48a501f62cc54b842e73ef5',
            'tools/office.py': 'f7e6ae546d97f4f1dda7817b4189ed0bf3f78b1aa8471ce6dfc2f100e1308caf',
            'roles/office/MAIN.md': '929d5319ed8b1b66fd5c4a793321a302892e4307175272cc6a5a95a3ab880183',
            SCHEMA_REL: '21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642',
            'tools/artifacts.py': 'be315aff047b0d73d0a9d15693ac72049edfbb15e9499bb0163687906f782c1a',
            'tools/native_agents.py': 'e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e'}
WORK, TASK_ID, AID = 'v2f', 'report', 'a1'
TASK_REL = 'working/v2f/report/TASK.json'
SLOT = 'working/v2f/report/assignments/a1'
CAND_REL = SLOT + '/candidate/draft.txt'
RESULT_REL = SLOT + '/RESULT.json'
SOURCE_REL = 'references/source-documents/LAB-V2F-ghi-chu.txt'
REQUEST_REL = 'working/v2f/request/user-request.txt'
DISPATCH_REL = 'working/v2f/setup/dispatch-package.json'
BRIEF_REL = 'working/v2f/setup/worker-brief.md'
CONTRACT_REL = 'roles/office/executive-secretary.md'
CATALOG_REL = 'roles/office/catalog.json'
WORKER = {'actor_id': 'worker-v2f', 'role': 'worker'}
MAIN = {'actor_id': 'main', 'role': 'main'}
PERIOD = 'báo cáo ngày 20/10/2026'
READER = 'trưởng nhóm giả LAB-V2F'
PURPOSE = 'thử nghiệm nội bộ của bài đo V2-F, không phát hành'
DRIVE_ABS = re.compile(r'^[A-Za-z]:\\')
REPARSE = 0x400
SOURCE_TEXT = ('DỮ LIỆU GIẢ — KHÔNG PHÁT HÀNH\n'
               'Ghi chú V2F (nhóm giả LAB-V2F, chỉ dùng cho bài đo kỹ thuật)\n\n'
               '[N1] Ngày 20/10/2026: kiểm kê kho giả Z-07 đã kiểm 8 trên 10 lô theo kế hoạch.\n'
               '[N2] Số lô lệch sau kiểm kê: chưa có giá trị cụ thể (chờ bảng tổng hợp).\n')
USER_REQUEST = ('Từ ghi chú LAB-V2F (references/source-documents/LAB-V2F-ghi-chu.txt), soạn giúp một đoạn %s gửi %s (mục đích: %s) '
                'về kiểm kê kho giả Z-07, nêu rõ điều còn thiếu.\n' % (PERIOD, READER, PURPOSE))
FRAGMENT_RE = re.compile(r'```json\n(.*?)\n```', re.S)


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


def inside(base, p):
    nb, np_ = os.path.normcase(os.path.realpath(base)), os.path.normcase(os.path.realpath(p))
    return np_ == nb or np_.startswith(nb + os.sep)


def form_problem(p):
    if not isinstance(p, str) or not p:
        return 'EMPTY'
    if '/' in p:
        return 'FORWARD_SLASH_OR_POSIX_STYLE'
    if not DRIVE_ABS.match(p):
        return 'NOT_DRIVE_ABSOLUTE'
    if any(ord(c) < 32 for c in p) or p.rstrip() != p or p.endswith('.'):
        return 'CONTROL_OR_TRAILING'
    if any(x in ('..', '.') for x in p.split('\\')[1:]) or ':' in p[2:] or '?' in p or '*' in p:
        return 'DOT_SEGMENT_OR_RESERVED'
    return None


def reparse_chain(p):
    bad, cur = [], os.path.splitdrive(p)[0] + '\\'
    for part in [x for x in p[len(cur):].split('\\') if x]:
        cur = os.path.join(cur, part)
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            break
        if os.path.islink(cur) or getattr(st, 'st_file_attributes', 0) & REPARSE:
            bad.append(cur)
    return bad


def import_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bridge_module():
    b = import_path('v2f_main_bridge', BRIDGE)
    b.EXEMPT.add(Path(os.path.abspath(__file__)).resolve())  # driver này không phải mã owner; chỉ dùng cho self-test/discover / this driver is not owner code
    return b


def pyrun(args, cwd, check=True):
    env = dict(os.environ, **ENV_ADDED)
    r = subprocess.run([sys.executable, '-B'] + args, cwd=cwd, capture_output=True, env=env, stdin=subprocess.DEVNULL, timeout=300)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    if check and r.returncode != 0:
        sys.exit('command failed (%s): %s\n%s' % (r.returncode, args, out))
    return r.returncode, out


# ---------------------------------------------------------------- schema locators (setup, from the real lab file)
def schema_reads(lab):
    """Dòng bắt đầu/kết thúc của $defs.result và mọi $defs mà nó tham chiếu (bao đóng $ref cục bộ), tính từ chính file schema trong lab. / Line ranges of the result def and its local $ref closure."""
    text = open(labp(lab, SCHEMA_REL), encoding='utf-8').read()
    lines = text.split('\n')
    data = json.loads(text)
    defs = data['$defs']
    starts = {}
    inside_defs = False
    for n, line in enumerate(lines, 1):
        if line.startswith('  "$defs"'):
            inside_defs = True
            continue
        m = re.match(r'^    "([^"]+)": ', line)
        if inside_defs and m and m.group(1) in defs and m.group(1) not in starts:
            starts[m.group(1)] = n
    order = sorted(starts.items(), key=lambda kv: kv[1])
    end_of = {name: (order[i + 1][1] - 1 if i + 1 < len(order) else len(lines)) for i, (name, _) in enumerate(order)}
    seen, stack = set(), ['result']
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)

        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k == '$ref' and isinstance(v, str) and v.startswith('#/$defs/'):
                        stack.append(v[len('#/$defs/'):].split('/')[0])
                    else:
                        walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(defs[name])
    names = ['result'] + sorted(seen - {'result'}, key=lambda k: starts[k])  # $defs.result đứng đầu / result first
    return [{'pointer': '#/$defs/' + n, 'line_from': starts[n], 'line_to': end_of[n]} for n in names], len(lines)


def pointer_resolves(schema_doc, pointer):
    cur = schema_doc
    for part in pointer.lstrip('#').strip('/').split('/'):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


# ---------------------------------------------------------------- setup (offline)
def setup(base):
    why = form_problem(base)
    if why:
        sys.exit('base refused: ' + why)
    if os.path.lexists(base) or reparse_chain(base) or os.path.normcase(os.path.realpath(base)) != os.path.normcase(os.path.abspath(base)):
        sys.exit('base exists, resolves elsewhere or has a reparse component: refusing')
    if inside(REPO, base) or inside(base, REPO):
        sys.exit('base overlaps the source tree: refusing')
    for rel, want in BASELINE.items():
        if file_sha(os.path.join(REPO, *rel.split('/'))) != want:
            sys.exit('source baseline differs from the work order: ' + rel)
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import check_package as cp
    os.makedirs(base)
    tmpl = os.path.join(base, 'template')
    cp.materialize(tmpl, branding=False)
    pyrun([os.path.join(tmpl, 'tools', 'new_project.py'), '--name', 'project', '--dest', base, '--apply', '--lang', 'vi'], tmpl)
    lab = os.path.join(base, 'project')
    if not os.path.isdir(lab) or form_problem(lab) or reparse_chain(lab) or os.path.normcase(os.path.realpath(lab)) != os.path.normcase(os.path.abspath(lab)):
        sys.exit('lab not created at a plain drive-absolute path: ' + lab)
    for rel in ('tools/office.py', 'roles/office/MAIN.md', SCHEMA_REL):  # lab phải mang E hiện tại và schema canonical (README của lab là bản project, recipe chạy từ cây LAW đã pin) / the lab must carry current E and the canonical schema
        if file_sha(labp(lab, rel)) != BASELINE[rel]:
            sys.exit('lab file differs from the E/canonical baseline: ' + rel)
    write_bytes(labp(lab, SOURCE_REL), SOURCE_TEXT.encode('utf-8'))
    write_bytes(labp(lab, REQUEST_REL), USER_REQUEST.encode('utf-8'))
    pyrun([os.path.join('tools', 'library.py'), 'init'], lab)
    pyrun([os.path.join('tools', 'library.py'), 'sync', '--apply'], lab)
    # profile + native (owner tools); full model ID, grants=[]
    choices = {'host': 'claude-code',
               'roles': {'scout': {'model': None, 'tier': None, 'effort': None}, 'worker': {'model': MODEL, 'tier': None, 'effort': None},
                         'reviewer': {'model': None, 'tier': None, 'effort': None}},
               'fallback': {'model': None, 'tier': None, 'effort': None, 'allowed': False}, 'requested_limits': {'max_concurrency': None, 'max_depth': None}}
    cf = os.path.join(base, 'choices.json')
    save(cf, choices)
    _, prev = pyrun([os.path.join('tools', 'execution_profile.py'), 'preview-config', '--choices', cf], lab, check=False)
    plan = re.search(r'"plan_sha256"\s*:\s*"([0-9a-f]{64})"', prev)
    args = [os.path.join('tools', 'execution_profile.py'), 'apply-config', '--choices', cf]
    if plan:
        args += ['--expect-plan', plan.group(1)]
    _, applied = pyrun(args, lab)
    _, nprev = pyrun([os.path.join('tools', 'native_agents.py'), 'preview', '--role', 'worker'], lab, check=False)
    nplan = re.search(r'"plan_sha256"\s*:\s*"([0-9a-f]{64})"', nprev) or re.search(r'([0-9a-f]{64})', nprev)
    if not nplan:
        sys.exit('no native plan token:\n' + nprev)
    _, napplied = pyrun([os.path.join('tools', 'native_agents.py'), 'apply', '--role', 'worker', '--expect-plan', nplan.group(1)], lab)
    # TASK / dispatch package from the owners (setup, not Main)
    bridge = bridge_module()
    recipe = bridge.load_recipe(REPO)
    v3 = recipe['load_v3'](REPO)
    import office
    compose_request = {'method': 'executive-secretary', 'reason': 'Smoke kỹ thuật V2-F: phương pháp do setup chọn rõ, không phải routing tự nhiên.',
                      'request': USER_REQUEST.strip(), 'sources': [{'path': SOURCE_REL, 'note': 'ghi chú giả LAB-V2F'}], 'output_format': 'text', 'lang': 'vi'}
    comp = office.compose(compose_request, root=lab)
    if comp['outcome'] != 'COMPOSED' or comp['state'] != 'PREPARED':
        sys.exit('compose not PREPARED: %s' % json.dumps({k: comp[k] for k in ('outcome', 'state', 'problems', 'held', 'missing')}, ensure_ascii=False))
    brief = comp['brief']
    if len(FRAGMENT_RE.findall(brief)) != 1 or office.RESULT_SCHEMA_REF not in brief:
        sys.exit('E brief lacks the single illustrative fragment or the schema reference')
    book = v3['library'].read_book(lab)
    counts = v3['library'].id_counts(book['data'])
    recs = [v3['library'].record(r, counts) for r in book['data']]
    hit = [r for r in recs if r['file'] == SOURCE_REL]
    if len(hit) != 1 or hit[0]['identity'] != 'ok':
        sys.exit('source not registered once in the ledger: %s' % hit)
    frag = comp['task_fragment']
    inp = copy.deepcopy(frag['inputs'])
    if len(inp) != 1:
        sys.exit('expected one input')
    inp[0]['source_id'], inp[0]['revision'] = hit[0]['id'], str(hit[0]['revision'])
    task = {'schema_version': 'law.cvf.control/3', 'record_type': 'task', 'evaluation_basis': 'COOPERATIVE_WORKFLOW', 'work_id': WORK, 'task_id': TASK_ID, 'task_revision': 1,
            'proposed_by': dict(MAIN),
            'intent': {'refs': [{'ref_id': 'intent-1', 'kind': 'user_intent', 'locator': REQUEST_REL, 'digest': 'sha256:' + file_sha(labp(lab, REQUEST_REL)),
                                 'attribution': {'source_class': 'UNVERIFIED', 'channel': 'NONE', 'recorded_by': dict(MAIN),
                                                 'note': 'yêu cầu là fixture lab giả do setup viết, không phải xác nhận của người dùng thật'}}],
                       'main_interpretation': frag['main_interpretation'] + ' TASK này do setup chuẩn bị cho bài đo V2-F (không phải Main tự nhận yêu cầu); lab dữ liệu giả, không có grant sản phẩm.'},
            'authority': {'grant_refs': [], 'subject': dict(WORKER)},
            'inputs': inp,
            'effects': {'actions': [{'operation': 'create_new', 'tool': 'Write', 'targets': [CAND_REL, RESULT_REL], 'write_zone': 'working'}],
                        'expected_outputs': [CAND_REL], 'on_missing': 'RETURN_TO_MAIN'},
            'acceptance': {'requirements': [frag['acceptance_requirement']]},
            'context_refs': frag['context_refs'], 'envelope': {'role': 'worker'}}
    raw = json.dumps(task, ensure_ascii=False, indent=2).encode('utf-8')
    write_bytes(labp(lab, TASK_REL), raw)
    task_raw = 'sha256:' + sha(raw)
    parsed, raw_digest, why = recipe['read_record'](v3, lab, TASK_REL, 'task')
    if why or raw_digest != task_raw:
        sys.exit('loader rejected the TASK: %s' % why)
    guard = v3['office'].guard_task(parsed, lambda rel: recipe['read_file'](lab, rel))
    if guard:
        sys.exit('office guard: %s' % guard)
    stub = recipe['binding_stub'](v3, parsed)
    write_bytes(labp(lab, BRIEF_REL), brief.encode('utf-8'))
    if open(labp(lab, BRIEF_REL), 'rb').read() != office.compose(compose_request, root=lab)['brief'].encode('utf-8'):
        sys.exit('stored brief is not byte-identical to a fresh E compose')
    reads, schema_lines = schema_reads(lab)
    schema_doc = load(labp(lab, SCHEMA_REL))
    if not pointer_resolves(schema_doc, SCHEMA_POINTER) or reads[0]['pointer'] != SCHEMA_POINTER:
        sys.exit('schema pointer does not resolve in the lab schema')
    absd = {'lab_root': lab, 'dispatch_package': labp(lab, DISPATCH_REL), 'task': labp(lab, TASK_REL), 'brief': labp(lab, BRIEF_REL), 'source': labp(lab, SOURCE_REL),
            'contract': labp(lab, CONTRACT_REL), 'catalog': labp(lab, CATALOG_REL), 'candidate': labp(lab, CAND_REL), 'result': labp(lab, RESULT_REL), 'schema_file': labp(lab, SCHEMA_REL)}
    for k, v in absd.items():
        if k not in ('dispatch_package', 'candidate', 'result') and not os.path.exists(v):
            sys.exit('absolute path does not exist: %s %s' % (k, v))
    dispatch = {'note': 'Gói giao do SETUP chuẩn bị cho bài đo V2-F (không phải Main tự lập). Binding tính bằng recipe binding_stub từ TASK này, trước dispatch.',
                'lab_root': lab,
                'paths_absolute': {k: v for k, v in absd.items() if k != 'lab_root'},
                'paths_relative_canonical': {'task': TASK_REL, 'brief': BRIEF_REL, 'source': SOURCE_REL, 'contract': CONTRACT_REL, 'catalog': CATALOG_REL, 'candidate': CAND_REL, 'result': RESULT_REL, 'schema_file': SCHEMA_REL},
                'task_path': TASK_REL, 'task_id': TASK_ID, 'task_revision': 1, 'task_raw_digest': task_raw, 'binding': stub,
                'candidate_path': CAND_REL, 'result_path': RESULT_REL, 'brief_path': BRIEF_REL, 'worker_logical_actor': dict(WORKER),
                'result_id': 'r-v2f-report-a1', 'method_contract': CONTRACT_REL, 'source_path': SOURCE_REL,
                'report_period': PERIOD, 'report_reader': READER, 'report_purpose': PURPOSE,
                'period_reader_note': 'Kỳ, người đọc và mục đích do SETUP khai (dữ liệu giả); Worker không tự suy. Thiếu hoặc mâu thuẫn thì trả Main.',
                'schema_file': absd['schema_file'], 'schema_pointer': SCHEMA_POINTER,
                'schema_note': 'schema_file là đường file thật để Read, không chứa dấu #. schema_pointer là chỉ mục JSON-pointer trong file đó, tách riêng; không ghép thành đường Read. Dùng Read với offset/limit theo schema_read_ranges (số dòng của chính file này, 1-based) để lấy $defs.result và các $defs nó tham chiếu.',
                'schema_read_ranges': reads, 'schema_total_lines': schema_lines,
                'observation_interface': {'who': 'Main chạy lệnh observe (Bash), Worker không có Bash', 'stdout': 'JSON; Main chuyển cho Worker2 NGUYÊN VĂN object "observation" (không tóm tắt, không sửa); ok=true và problems=[] mới được chuyển',
                                          'worker_use': 'candidate path/digest và định danh TASK trong observation là căn cứ outputs/artifacts/evidence của RESULT'},
                'invocation_plan': {'phase1': 'Worker invocation 1: chỉ Write candidate, chưa RESULT', 'phase2': 'Worker invocation 2 (mới, không resume): Read lại hồ sơ, Write RESULT; agentId thực chỉ điền từ trace vào assessment, không sửa TASK sau dispatch', 'logical_actor_both': dict(WORKER)}}
    save(labp(lab, DISPATCH_REL), dispatch)
    os.makedirs(labp(lab, SLOT + '/candidate'))
    # fixture lab (tách khỏi slot live) + manifest discovery in a fresh interpreter
    fx_lab = os.path.join(base, 'fixture', 'project')
    fx_lab2 = os.path.join(base, 'fixture2', 'project')  # lab KHÁC, tồn tại, cùng TASK bytes: dùng cho ca anchor sai lab / another existing lab with the same TASK bytes
    shutil.copytree(lab, fx_lab)
    shutil.copytree(lab, fx_lab2)
    setup_doc = {'lab': lab, 'work_id': WORK, 'task_id': TASK_ID, 'assignment_id': AID, 'task_rel': TASK_REL, 'candidate_rel': CAND_REL, 'result_rel': RESULT_REL,
                 'task_raw_digest': task_raw, 'binding_stub': stub, 'manifest_sha256': None, 'created_at': now(), 'paths_absolute': dispatch['paths_absolute'],
                 'compose_request': compose_request,
                 'note': 'Setup metadata tin cậy, ngoài lab. task_raw_digest và binding_stub tính trước dispatch từ TASK setup; không đổi giữa hai pha.'}
    fx_setup = dict(setup_doc, lab=fx_lab)
    write_bytes(labp(fx_lab, CAND_REL), 'Ứng viên fixture\n'.encode('utf-8'))
    fx_setup_path = os.path.join(base, 'fixture', 'setup.json')
    save(fx_setup_path, fx_setup)
    code, out = pyrun(['-I', os.path.join(HERE, 'v2f.py'), 'discover-inner', fx_setup_path], base)
    loaded = json.loads(out.strip().splitlines()[-1])
    files = {rel: file_sha(os.path.join(REPO, *rel.split('/'))) for rel in sorted(set(loaded) | {'.cvf/checks/control_check_v3.py'} | set(bridge.DATA_PINS))}
    manifest = {'schema': 'law.v2f.bridge-manifest/1', 'created_at': now(), 'law_root': REPO, 'readme_sha256': file_sha(os.path.join(REPO, 'roles', 'README.md')),
                'baseline_six': {k: file_sha(os.path.join(REPO, *k.split('/'))) for k in BASELINE}, 'files': files}
    save(MANIFEST_PATH, manifest)
    setup_doc['manifest_sha256'] = file_sha(MANIFEST_PATH)
    save(SETUP_PATH, setup_doc)
    print(json.dumps({'lab': lab, 'fixture_lab': fx_lab, 'fixture2_lab': fx_lab2, 'task_raw_digest': task_raw, 'pinned_files': len(files), 'manifest_sha256': setup_doc['manifest_sha256'],
                      'brief_sha256': file_sha(labp(lab, BRIEF_REL)), 'schema_read_ranges': reads, 'profile_apply_tail': applied.strip()[-300:], 'native_apply_tail': napplied.strip()[-300:]}, ensure_ascii=False, indent=2))


def anchor():
    """Chốt hằng anchor vào bridge SAU setup, TRƯỚC khi driver pin hash bridge. Chỉ ghi hai hằng; hash setup lấy từ bytes thô setup.json. / Fix the two anchor constants in the bridge."""
    setup_doc = load(SETUP_PATH)
    lab = setup_doc['lab']
    want_sha = file_sha(SETUP_PATH)
    with open(BRIDGE, 'rb') as fh:
        text = fh.read().decode('utf-8')
    a1, a2 = 'EXPECTED_SETUP_SHA256 = None  #', 'EXPECTED_LAB = None  #'
    if text.count(a1) != 1 or text.count(a2) != 1:
        sys.exit('anchor already set or bridge shape changed: refusing')
    text = text.replace(a1, 'EXPECTED_SETUP_SHA256 = %r  #' % want_sha).replace(a2, 'EXPECTED_LAB = %r  #' % lab)
    write_bytes(BRIDGE, text.encode('utf-8'))
    b = import_path('v2f_main_bridge_check', BRIDGE)
    if b.EXPECTED_SETUP_SHA256 != want_sha or b.EXPECTED_LAB != lab:
        sys.exit('anchor not read back')
    print(json.dumps({'expected_setup_sha256': want_sha, 'expected_lab': lab, 'bridge_sha256': file_sha(BRIDGE)}, ensure_ascii=False, indent=2))


def fixture_result(fx, obs, brief_text, mutate=None):
    """RESULT fixture (KHÔNG phải Worker native): header/binding từ gói giao + quan sát, hai mảng con lấy từ fragment của brief E đã render; chỉ ghi đè GIÁ TRỊ của khóa đã có. / Test-driver RESULT built from the rendered brief fragment."""
    cand = obs['candidate']
    outputs = [{'path': cand['path'], 'digest': cand['digest'], 'role': 'ACTUAL_BYTES'}]
    task = load(labp(fx['lab'], fx['task_rel']))
    frag = json.loads(FRAGMENT_RE.findall(brief_text)[0])
    reqs, evid = [], []
    for i, q in enumerate(task['acceptance']['requirements']):
        r = copy.deepcopy(frag['requirements'][min(i, len(frag['requirements']) - 1)])
        r['req_id'], r['mandatory'] = q['req_id'], q['mandatory']
        reqs.append(r)
    e = copy.deepcopy(frag['evidence'][0])
    e['evidence_id'], e['req_id'], e['locator'], e['scope'] = 'ev-1', reqs[0]['req_id'], 'main-observation:artifacts.observe_file', 'fixture only'
    evid.append(e)
    res = {'schema_version': 'law.cvf.control/3', 'record_type': 'result', 'evaluation_basis': 'COOPERATIVE_WORKFLOW', 'result_id': 'r-fixture',
           'binding': dict(fx['binding_stub'], outputs=outputs), 'produced_by': dict(WORKER), 'artifacts': outputs, 'evidence': evid, 'requirements': reqs, 'gaps': ['fixture'],
           'acceptance_states': ['CANDIDATE'], 'state_set_by': dict(WORKER)}
    if mutate:
        mutate(res)
    return res


def compose_inner(setup_path):
    """Chạy trong interpreter mới: soạn lại brief bằng helper E từ cùng yêu cầu và in hash. / Fresh interpreter: recompose the brief with the E helper and print its hash."""
    sd = load(setup_path)
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import office
    out = office.compose(sd['compose_request'], root=sd['lab'])
    print(json.dumps({'brief_sha256': sha(out['brief'].encode('utf-8')), 'schema_ref': office.RESULT_SCHEMA_REF, 'outcome': out['outcome'], 'state': out['state']}))


def discover_inner(setup_path):
    """Chạy trong interpreter mới (-I): nạp owner như bridge và in tập file LAW đã nạp. / Fresh interpreter: load the way the bridge does and print the loaded LAW files."""
    b = bridge_module()
    fx = load(setup_path)
    r = b.run('observe', setup=fx, manifest={}, discover=True)
    if not r.get('ok'):
        sys.exit('discover observe refused: %s' % r.get('problems'))
    brief = open(labp(fx['lab'], BRIEF_REL), encoding='utf-8').read()
    write_bytes(labp(fx['lab'], fx['result_rel']), json.dumps(fixture_result(fx, r['observation'], brief), ensure_ascii=False, indent=2).encode('utf-8'))
    c = b.run('checkpoint', setup=fx, manifest={}, discover=True)
    if not c.get('ok'):
        sys.exit('discover checkpoint problems: %s' % c.get('problems'))
    print(json.dumps(sorted(b.law_loaded_files(REPO))))


# ---------------------------------------------------------------- selftest (offline, fixture only)
def selftest():
    """Kiểm delta F (gói giao, brief E, schema, fragment lồng, anchor/stub drift) trên fixture tách khỏi slot live; offline, không gọi AI. / Delta F checks on fixtures only."""
    b = bridge_module()
    post = import_path('v2f_post_check', POST)
    setup_doc, manifest = load(SETUP_PATH), load(MANIFEST_PATH)
    live = setup_doc['lab']
    base = os.path.dirname(live)
    fx_lab = os.path.join(base, 'fixture', 'project')
    fx_lab2 = os.path.join(base, 'fixture2', 'project')
    live_before = tree(live)
    results = []
    anchor_const = (b.EXPECTED_SETUP_SHA256, b.EXPECTED_LAB)

    def case(name, ok, detail=None):
        results.append({'case': name, 'ok': bool(ok), 'detail': detail})

    def fx_setup(**over):
        d = dict(setup_doc, lab=fx_lab)
        d.update(over)
        return d

    def reset(lab):
        for rel in (CAND_REL, RESULT_REL):
            p = labp(lab, rel)
            if os.path.lexists(p):
                os.remove(p)

    reset(fx_lab)
    reset(fx_lab2)
    pyc_before = sorted(os.path.join(d, n) for d, _, ns in os.walk(REPO) for n in ns if d.endswith('__pycache__'))
    # --- gói giao thật trong lab live (đọc, không ghi)
    disp = load(labp(live, DISPATCH_REL))
    sf = disp['schema_file']
    case('anchor constants in the bridge equal the live setup raw SHA256 and lab', b.EXPECTED_SETUP_SHA256 == file_sha(SETUP_PATH) and b.EXPECTED_LAB == live)
    case('lab root is a resolved plain drive-absolute path', form_problem(live) is None and not reparse_chain(live) and os.path.normcase(os.path.realpath(live)) == os.path.normcase(os.path.abspath(live)) and not inside(REPO, live) and not inside(live, REPO), live)
    case('schema_file is a real absolute file with no fragment, inside the lab, with the canonical bytes',
         form_problem(sf) is None and '#' not in sf and os.path.isfile(sf) and inside(live, sf) and file_sha(sf) == BASELINE[SCHEMA_REL] == file_sha(os.path.join(REPO, *SCHEMA_REL.split('/'))), {'schema_file': sf})
    case('schema_pointer is separate (#/$defs/result), resolves in the schema, and is not part of any Read path',
         disp['schema_pointer'] == SCHEMA_POINTER and pointer_resolves(load(sf), SCHEMA_POINTER) and not any('#' in v for v in disp['paths_absolute'].values()))
    ranges = disp['schema_read_ranges']
    rng_ok = bool(ranges) and ranges[0]['pointer'] == SCHEMA_POINTER and all(1 <= r['line_from'] <= r['line_to'] <= disp['schema_total_lines'] for r in ranges)
    case('schema_read_ranges cover $defs.result and its local $ref closure within the file', rng_ok, ranges)
    sch_lines = open(sf, encoding='utf-8').read().split('\n')
    first = ranges[0]
    seg = '\n'.join(sch_lines[first['line_from'] - 1:first['line_to']])
    case('the first range starts at the result definition and contains the nested field names', '"result": {' in sch_lines[first['line_from'] - 1] and 'evidence' in seg and 'requirements' in seg, first)
    abs_ok = all(form_problem(v) is None and inside(live, v) for v in disp['paths_absolute'].values())
    rel_ok = all(os.path.normcase(os.path.normpath(disp['paths_absolute'][k])) == os.path.normcase(os.path.normpath(labp(live, disp['paths_relative_canonical'][k])))
                 for k in disp['paths_absolute'] if k in disp['paths_relative_canonical'])
    exist_ok = all(os.path.exists(v) for k, v in disp['paths_absolute'].items() if k not in ('dispatch_package', 'candidate', 'result'))
    case('every absolute Read/Write path is real inside the lab and equals the canonical relative path of the TASK', abs_ok and rel_ok and exist_ok and not os.path.lexists(disp['paths_absolute']['candidate']) and not os.path.lexists(disp['paths_absolute']['result']))
    task = load(labp(live, TASK_REL))
    case('TASK targets equal the dispatched candidate/RESULT; expected_outputs is the candidate only; grants and grant_refs are empty',
         task['effects']['actions'][0]['targets'] == [CAND_REL, RESULT_REL] and task['effects']['expected_outputs'] == [CAND_REL] and task['authority']['grant_refs'] == []
         and load(labp(live, '.agent/EXECUTION_PROFILE.json')).get('grants') == [])
    case('TASK intent is UNVERIFIED/NONE and the TASK/binding in the package equal the setup', task['intent']['refs'][0]['attribution']['source_class'] == 'UNVERIFIED' and task['intent']['refs'][0]['attribution']['channel'] == 'NONE'
         and disp['binding'] == setup_doc['binding_stub'] and disp['task_raw_digest'] == setup_doc['task_raw_digest'] == 'sha256:' + file_sha(labp(live, TASK_REL)))
    srcb = open(labp(live, SOURCE_REL), encoding='utf-8').read()
    reqb = open(labp(live, REQUEST_REL), encoding='utf-8').read()
    case('period, reader and purpose are declared by setup in the package, the request and the source is consistent with the period',
         all(x in json.dumps(disp, ensure_ascii=False) for x in (PERIOD, READER, PURPOSE)) and PERIOD in reqb and READER in reqb and '20/10/2026' in srcb and 'DỮ LIỆU GIẢ' in srcb)
    brief = open(labp(live, BRIEF_REL), 'rb').read()
    _, fresh_out = pyrun(['-I', os.path.join(HERE, 'v2f.py'), 'compose-inner', SETUP_PATH], live)  # interpreter nhớ riêng: không nạp office vào tiến trình có bridge / fresh interpreter, keeps office out of the bridge process
    fresh = json.loads(fresh_out.strip().splitlines()[-1])
    case('the stored brief is byte-identical to a fresh compose by the E helper and keeps the illustrative fragment and schema reference',
         fresh['brief_sha256'] == sha(brief) and len(FRAGMENT_RE.findall(brief.decode('utf-8'))) == 1 and fresh['schema_ref'].encode() in brief and file_sha(os.path.join(REPO, 'tools', 'office.py')) == BASELINE['tools/office.py'],
         {'brief_sha256': sha(brief), 'fresh': fresh})
    # --- fragment lồng -> owner nghiêm ngặt -> checkpoint (fixture, không phải Worker native)
    body = 'Ứng viên fixture\r\ndòng hai ✓\n'.encode('utf-8')
    write_bytes(labp(fx_lab, CAND_REL), body)
    t1 = tree(fx_lab)
    r = b.run('observe', setup=fx_setup(), manifest=manifest)
    obs = r.get('observation')
    case('observe on the fixture: ok, digest equals an independent hash, read-only', r['ok'] and obs['candidate']['digest'] == 'sha256:' + sha(body) and tree(fx_lab) == t1, r['problems'])
    brief_text = brief.decode('utf-8')
    res_path = labp(fx_lab, RESULT_REL)
    res = fixture_result(fx_setup(), obs, brief_text)
    write_bytes(res_path, json.dumps(res, ensure_ascii=False, indent=2).encode('utf-8'))
    t2 = tree(fx_lab)
    r = b.run('checkpoint', setup=fx_setup(), manifest=manifest)
    case('checkpoint: a fixture RESULT (test driver, NOT a native Worker) built from the rendered brief fragment gives problems=[] and CHECKED_NOT_PASS',
         r['ok'] and r['problems'] == [] and r.get('verdict') == 'CHECKED_NOT_PASS' and r['identity']['task_equals_dispatch_digest'] is True
         and r['identity']['result_binding_equals_dispatch_stub_before_outputs'] is True and tree(fx_lab) == t2, r['problems'])

    def mut_evidence_id(x):
        del x['evidence'][0]['evidence_id']

    def mut_req_id(x):
        del x['evidence'][0]['req_id']

    def mut_mandatory(x):
        del x['requirements'][0]['mandatory']

    def mut_status(x):
        del x['requirements'][0]['status']

    def mut_state_note(x):
        x['requirements'][0]['state'] = 'UNKNOWN'
        x['requirements'][0]['note'] = 'x'
    for name, fn in (('evidence_id', mut_evidence_id), ('evidence req_id', mut_req_id), ('requirement mandatory', mut_mandatory), ('requirement status', mut_status), ('extra state/note', mut_state_note)):
        write_bytes(res_path, json.dumps(fixture_result(fx_setup(), obs, brief_text, fn), ensure_ascii=False, indent=2).encode('utf-8'))
        r = b.run('checkpoint', setup=fx_setup(), manifest=manifest)
        case('checkpoint: a nested-shape defect (%s) is refused by the strict owner, the fixture is not repaired' % name,
             (not r['ok']) and r.get('verdict') == 'HOLD' and any('RECORD_REJECTED' in p for p in r['problems']), r['problems'])
    write_bytes(res_path, json.dumps(res, ensure_ascii=False, indent=2).encode('utf-8'))
    # --- identity / stub / TASK drift (giữ từ D, chỉ ca đại diện)
    r = b.run('checkpoint', setup=fx_setup(task_raw_digest='sha256:' + '0' * 64), manifest=manifest)
    case('checkpoint: TASK differing from the dispatch digest is HOLD', (not r['ok']) and r.get('verdict') == 'HOLD' and 'TASK_CHANGED_SINCE_DISPATCH' in r['problems'], r['problems'])
    r = b.run('checkpoint', setup=fx_setup(binding_stub=dict(setup_doc['binding_stub'], intent_digest='sha256:' + '2' * 64)), manifest=manifest)
    case('checkpoint: stub delivered differs from the RESULT binding is HOLD', (not r['ok']) and r.get('verdict') == 'HOLD' and 'BINDING_DIFFERS_FROM_DISPATCH_STUB' in r['problems'], r['problems'])
    write_bytes(labp(fx_lab, CAND_REL), body + b'x')
    r = b.run('checkpoint', setup=fx_setup(), manifest=manifest)
    case('checkpoint: candidate changed after the RESULT is HOLD', (not r['ok']) and r.get('verdict') == 'HOLD' and 'CANDIDATE_CHANGED' in r['problems'], r['problems'])
    # --- anchor: setup khác / lab khác cùng TASK bytes
    fxdir = os.path.join(base, 'fixture')
    fx_setup_file, fx2_setup_file = os.path.join(fxdir, 'setup-anchor.json'), os.path.join(fxdir, 'setup-lab2.json')
    save(fx_setup_file, fx_setup())
    save(fx2_setup_file, fx_setup(lab=fx_lab2))
    case('the second lab exists and holds a TASK with the same bytes', file_sha(labp(fx_lab2, TASK_REL)) == file_sha(labp(fx_lab, TASK_REL)))
    reset(fx_lab)
    write_bytes(labp(fx_lab, CAND_REL), body)
    write_bytes(labp(fx_lab2, CAND_REL), body)
    t_a, t_b = tree(fx_lab), tree(fx_lab2)
    try:
        b.EXPECTED_SETUP_SHA256, b.EXPECTED_LAB = file_sha(fx_setup_file), fx_lab
        r = b.run('observe', setup_path=fx_setup_file)
        case('anchor: the anchored fixture setup file and lab give a positive read-only observe', r['ok'] and not r['refused_before_operation'] and tree(fx_lab) == t_a, r['problems'])
        r = b.run('observe', setup_path=fx2_setup_file)
        case('anchor: a coherent setup for ANOTHER existing lab with the same TASK bytes is refused before the operation (setup raw SHA)',
             (not r['ok']) and r['refused_before_operation'] and r['problems'] == ['ANCHOR_SETUP_SHA_MISMATCH'] and tree(fx_lab2) == t_b, r['problems'])
        b.EXPECTED_SETUP_SHA256, b.EXPECTED_LAB = file_sha(fx2_setup_file), fx_lab
        r = b.run('observe', setup_path=fx2_setup_file)
        case('anchor: even with the setup hash matching, a lab different from the fixed lab is refused before the operation',
             (not r['ok']) and r['refused_before_operation'] and r['problems'] == ['ANCHOR_LAB_MISMATCH'] and tree(fx_lab2) == t_b, r['problems'])
    finally:
        b.EXPECTED_SETUP_SHA256, b.EXPECTED_LAB = anchor_const
    reset(fx_lab)
    reset(fx_lab2)
    # --- bridge pin drift, one representative
    m1 = copy.deepcopy(manifest)
    m1['files']['tools/artifacts.py'] = '0' * 64
    r = b.run('observe', setup=fx_setup(), manifest=m1)
    case('owner drift (pin mismatch) refused before the operation', (not r['ok']) and r.get('refused_before_operation') and any(p.startswith('PIN_DRIFT') for p in r['problems']), r['problems'])
    case('the manifest pins the six baseline files, the schema among the pinned data files', set(manifest['baseline_six']) == set(BASELINE) and SCHEMA_REL in manifest['files'] and manifest['files']['tools/office.py'] == BASELINE['tools/office.py'])
    # --- the exact commands as subprocesses from the lab cwd against the LIVE setup: read-only refusals expected (no candidate yet)
    live_pre = tree(live)
    cmds = {}
    for name in ('observe', 'checkpoint'):
        p = subprocess.run([sys.executable, '-I', '-B', BRIDGE, name], cwd=live, capture_output=True, stdin=subprocess.DEVNULL, timeout=120)
        out = json.loads(p.stdout.decode('utf-8')) if p.stdout.strip() else {}
        cmds[name] = {'exit': p.returncode, 'ok': out.get('ok'), 'refused_before_operation': out.get('refused_before_operation'), 'problems': out.get('problems')}
    case('exact commands from the live cwd (sys.executable subprocess; NOT a Bash allow-rule proof): anchor passes, read-only refusals while the slot is empty',
         cmds['observe']['ok'] is False and cmds['checkpoint']['ok'] is False and cmds['observe']['refused_before_operation'] is False
         and cmds['checkpoint']['refused_before_operation'] is False and tree(live) == live_pre == live_before, cmds)
    # --- prompt thật
    prompt_text = render_prompt().decode('utf-8')
    needed = [CMD_OBSERVE, CMD_CHECKPOINT, 'agentId', 'KHÔNG gửi agentId', 'Worker 2', 'pha 1', 'pha 2', live, disp['paths_absolute']['brief'], disp['paths_absolute']['task'], disp['paths_absolute']['candidate'],
              disp['paths_absolute']['result'], sf, SCHEMA_POINTER, PERIOD, READER, 'BƯỚC']
    missing = [x for x in needed if x not in prompt_text]
    case('rendered prompt carries the lab root, absolute paths, schema file and pointer separately, period/reader, both commands and the no-resume rule; no placeholder left',
         not missing and not re.search(r'\{[A-Z_]+\}', prompt_text), missing)
    case('the prompt tells Main to hand the brief by path and not to summarise the RESULT shape', 'KHÔNG tóm tắt' in prompt_text and 'worker-brief' in prompt_text)
    syn = post.assess_stream([])
    case('assessment of an empty trace is NOT complete', syn['complete'] is False and syn['status'] != 'IMPLEMENTED_PENDING_REVIEW', syn['status'])
    pyc_after = sorted(os.path.join(d, n) for d, _, ns in os.walk(REPO) for n in ns if d.endswith('__pycache__'))
    case('no bytecode was added to the source tree', pyc_before == pyc_after, {'before': len(pyc_before), 'after': len(pyc_after)})
    case('the live lab is unchanged by the whole self-test', tree(live) == live_before, tree_digest(live_before))
    print(json.dumps({'passed': sum(r['ok'] for r in results), 'failed': [r for r in results if not r['ok']], 'cases': results}, ensure_ascii=False, indent=2))
    return 0 if all(r['ok'] for r in results) else 1


# ---------------------------------------------------------------- driver: prepare / run
def claude_processes():
    cmd = ['powershell', '-NoProfile', '-Command',
           "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like '*Anthropic.ClaudeCode_Microsoft.Winget*' } | "
           "Select-Object ProcessId,ParentProcessId,CreationDate | ConvertTo-Json -Compress"]
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    return json.loads(r.stdout.decode('utf-8', 'replace').strip() or '[]')


def argv():
    return [CLAUDE, '-p', '--model', MODEL, '--tools', TOOLS, '--allowedTools', ALLOWED, '--setting-sources', 'project',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--permission-mode', 'default', '--disable-slash-commands',
            '--no-session-persistence', '--max-budget-usd', BUDGET, '--output-format', 'stream-json', '--verbose']


def render_prompt():
    setup_doc = load(SETUP_PATH)
    a = setup_doc['paths_absolute']
    sub = {'{OBSERVE}': CMD_OBSERVE, '{CHECKPOINT}': CMD_CHECKPOINT, '{LAB}': setup_doc['lab'], '{P_DISPATCH}': a['dispatch_package'], '{P_TASK}': a['task'], '{P_BRIEF}': a['brief'],
           '{P_SOURCE}': a['source'], '{P_CONTRACT}': a['contract'], '{P_CATALOG}': a['catalog'], '{P_CAND}': a['candidate'], '{P_RESULT}': a['result'], '{P_SCHEMA}': a['schema_file'],
           '{POINTER}': SCHEMA_POINTER, '{PERIOD}': PERIOD, '{READER}': READER, '{PURPOSE}': PURPOSE, '{R_TASK}': TASK_REL, '{R_CAND}': CAND_REL, '{R_RESULT}': RESULT_REL}
    with open(PROMPT_FILE, encoding='utf-8', newline='') as fh:
        text = fh.read()
    for k, v in sub.items():
        text = text.replace(k, v)
    return text.encode('utf-8')


def baseline_view():
    out = {}
    for rel, want in BASELINE.items():
        got = file_sha(os.path.join(REPO, *rel.split('/')))
        out[rel] = {'sha256': got, 'baseline': want, 'equal': got == want}
    return out


def runtime_files():
    """Bytes runtime que lượt sẽ dùng: driver, bridge, prompt, post, setup, manifest. / Runtime source bytes pinned before the call."""
    return {'v2f.py': os.path.abspath(__file__), 'main_bridge.py': BRIDGE, 'prompt-v2f.txt': PROMPT_FILE, 'v2f_post.py': POST, 'setup.json': SETUP_PATH, 'bridge_manifest.json': MANIFEST_PATH}


def delivery_files(lab, setup_doc):
    a = setup_doc['paths_absolute']
    return {'dispatch-package.json': a['dispatch_package'], 'TASK.json': a['task'], 'worker-brief.md': a['brief'], 'source.txt': a['source'], 'executive-secretary.md': a['contract'],
            'catalog.json': a['catalog'], 'control.schema.json': a['schema_file'], 'user-request.txt': labp(lab, REQUEST_REL)}


def prepare(evidence):
    setup_doc, manifest = load(SETUP_PATH), load(MANIFEST_PATH)
    lab = setup_doc['lab']
    problems = []
    why = form_problem(lab)
    if why:
        problems.append('LAB_' + why)
    if not os.path.isdir(lab) or reparse_chain(lab) or os.path.normcase(os.path.realpath(lab)) != os.path.normcase(os.path.abspath(lab)):
        problems.append('LAB_MISSING_REPARSE_OR_RESOLVE_DIFFERS')
    if inside(REPO, lab) or inside(lab, REPO):
        problems.append('LAB_OVERLAPS_SOURCE_TREE')
    if os.path.lexists(evidence) and os.listdir(evidence):
        problems.append('EVIDENCE_DIR_NOT_EMPTY')
    if not inside(REPO, evidence) or reparse_chain(evidence):
        problems.append('EVIDENCE_DIR_OUTSIDE_REPO_OR_REPARSE')
    for rel in (CAND_REL, RESULT_REL):
        if os.path.lexists(labp(lab, rel)):
            problems.append('TARGET_EXISTS ' + rel)
    cdir = labp(lab, SLOT + '/candidate')
    if not os.path.isdir(cdir) or os.listdir(cdir):
        problems.append('SLOT_CANDIDATE_DIR_NOT_EMPTY_OR_MISSING')
    b = bridge_module()
    pins = b.pin_problems(REPO, manifest)
    if b.EXPECTED_SETUP_SHA256 != file_sha(SETUP_PATH) or b.EXPECTED_LAB != lab:
        problems.append('BRIDGE_ANCHOR_NOT_FIXED_TO_SETUP_AND_LAB')
    exe_size, exe_sha = os.path.getsize(CLAUDE), file_sha(CLAUDE)
    if exe_size != CLAUDE_BASELINE['size'] or exe_sha != CLAUDE_BASELINE['sha256']:
        problems.append('CLI_BINARY_DIFFERS_FROM_BASELINE size=%s sha256=%s' % (exe_size, exe_sha))
    task_raw = 'sha256:' + file_sha(labp(lab, TASK_REL))
    if task_raw != setup_doc['task_raw_digest']:
        problems.append('TASK_DIGEST_DIFFERS_FROM_SETUP')
    if file_sha(MANIFEST_PATH) != setup_doc['manifest_sha256']:
        problems.append('MANIFEST_HASH_DIFFERS_FROM_SETUP')
    base = baseline_view()
    if any(not v['equal'] for v in base.values()):
        problems.append('SOURCE_BASELINE_DRIFT')
    if file_sha(labp(lab, SCHEMA_REL)) != BASELINE[SCHEMA_REL]:
        problems.append('LAB_SCHEMA_DIFFERS_FROM_CANONICAL')
    if problems or pins:
        sys.exit('prepare refused: %s %s' % (problems, pins))
    ver = subprocess.run([CLAUDE, '--version'], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace').strip()
    if ver != CLAUDE_BASELINE['version']:
        sys.exit('prepare refused: CLI version %r differs from baseline %r (no update, no other host)' % (ver, CLAUDE_BASELINE['version']))
    prompt = render_prompt()
    before = tree(lab)
    os.makedirs(evidence, exist_ok=True)
    write_bytes(os.path.join(evidence, 'prompt.txt'), prompt)
    pins_rt = {}
    for name, src in runtime_files().items():
        with open(src, 'rb') as fh:
            data = fh.read()
        write_bytes(os.path.join(evidence, 'runtime', name), data)  # bản bytes lưu TRƯỚC Popen / byte copy saved before Popen
        pins_rt[name] = {'origin': os.path.relpath(src, REPO).replace('\\', '/'), 'sha256': sha(data), 'size': len(data)}
    deliv = {}
    for name, src in delivery_files(lab, setup_doc).items():
        with open(src, 'rb') as fh:
            data = fh.read()
        write_bytes(os.path.join(evidence, 'delivery-before', name), data)
        deliv[name] = {'lab_path': os.path.relpath(src, lab).replace('\\', '/'), 'sha256': sha(data), 'size': len(data)}
    owner_pins = {rel: {'sha256': want} for rel, want in sorted(manifest['files'].items())}
    profile = load(labp(lab, '.agent/EXECUTION_PROFILE.json'))
    req = {
        'phase': 'BEFORE_CALL', 'recorded_at': now(), 'envelope': 'V2-F (roadmap/WORKORDER_V2F_2026-10-22.md)', 'host_version': ver, 'executable': CLAUDE,
        'executable_size_bytes': exe_size, 'executable_sha256': exe_sha, 'executable_baseline': CLAUDE_BASELINE, 'lab': lab,
        'authorization': 'PROJECT maintainer lab exception 18/10 + work order V2-F 22/10 handed to Claude by the operator; not product authority, no product grant in the lab (grants=[])',
        'models_requested': {'main': MODEL, 'worker1': MODEL, 'worker2': MODEL},
        'model_basis': 'Operator named no model/effort in the handover message (sequence, timeout, budget only). Lab choice: the model id of the Claude session handed this work order (claude-sonnet-5-5, as stated by that session); the same id for Main and both Worker invocations; not a product preset, to be confirmed by the operator in review',
        'effort_requested': {'main': None, 'worker1': None, 'worker2': None},
        'operator_selection_before_call': {'budget_usd_cli_requested': float(BUDGET), 'timeout_seconds': TIMEOUT, 'parent_attempts': 1, 'workers': 2, 'sequence': 'sequential', 'on_missing_evidence': 'PARTIAL, no retry, no compensating RESULT edit', 'handover': 'wait for Codex review', 'model': 'not stated', 'effort': 'not stated'},
        'limits': {'ai_attempts': 1, 'sessions': 1, 'parent_attempt_number_overall': 5, 'native_invocations': 2, 'child': 'law-worker', 'send_message_calls': 0, 'main_bash_commands': 2,
                   'max_budget_usd_cli_requested': float(BUDGET), 'timeout_seconds': TIMEOUT, 'paid_retry': False},
        'cumulative_before': {'attempts': 4, 'telemetry_usd_known': 2.22407715, 'c_telemetry': 'UNKNOWN',
                              'note': 'V1-B 0.7669449 + B2 0.75837945 + D 0.6987528 = 2.22407715; V2-C telemetry NOT_OBSERVED; F is attempt 5, recorded separately; the full total stays UNKNOWN; budget is a requested parameter, not an invoice or a hard cap'},
        'scope': {
            'read': ['AGENTS.md', 'roles/**', 'working/v2f/setup/*', 'working/v2f/report/TASK.json', 'working/v2f/request/*', SOURCE_REL, '.cvf/** (the schema file is inside)'],
            'worker1_create_new': [CAND_REL], 'worker2_create_new': [RESULT_REL], 'main_writes': 'none (the Write tool is present only so the child can have it; not a grant)',
            'main_shell': [CMD_OBSERVE, CMD_CHECKPOINT], 'per_phase_write_scope': 'cooperative, not host-enforced'},
        'argv_without_prompt': argv(), 'allowed_tools_rules': ALLOWED.split(','), 'tools_flag': TOOLS, 'prompt_via': 'stdin (UTF-8), saved as prompt.txt', 'prompt_sha256': sha(prompt),
        'runtime_pins': pins_rt, 'delivery_pins': deliv, 'owner_pins_count': len(owner_pins), 'owner_pins': owner_pins,
        'env_added': ENV_ADDED, 'env_note': 'Environment otherwise inherited, not copied into the record',
        'init_gate': {'rule': 'terminate the process unless the init event lists Read, Write, Bash, a start tool (Agent or Task, raw name kept) and the native law-worker; SendMessage is NOT required; inventory is not an invocation proof',
                      'enforcement': 'driver reads stdout line by line and kills the process tree on the init event; stdout buffering may let the model act before the kill, which is recorded if it happens'},
        'preflight': {
            'lab_path_problems': problems, 'lab_reparse_chain': reparse_chain(lab), 'baseline_six': base, 'bridge_sha256': file_sha(BRIDGE), 'manifest_sha256': file_sha(MANIFEST_PATH),
            'setup_json_sha256': file_sha(SETUP_PATH), 'pin_problems': pins, 'pinned_files': len(manifest['files']), 'task_raw_digest': task_raw,
            'dispatch_package_sha256': file_sha(labp(lab, DISPATCH_REL)), 'brief_sha256': file_sha(labp(lab, BRIEF_REL)), 'schema_sha256': file_sha(labp(lab, SCHEMA_REL)),
            'profile': {'sha256': file_sha(labp(lab, '.agent/EXECUTION_PROFILE.json')), 'grants': profile.get('grants'), 'authority_owner': profile.get('authority_owner'),
                        'host': profile.get('host'), 'worker_model': profile['roles']['worker']['model']},
            'native_worker_sha256': file_sha(labp(lab, '.claude/agents/law-worker.md')),
            'native_receipt_sha256': file_sha(labp(lab, '.agent/runtime/native-agents/claude-code/law-worker.json')),
            'native_inventory_note': 'disk configuration only; whether the host loads and can invoke it is decided by the init event and the trace',
            'winget_claude_processes_before_call': claude_processes(),
            'D_c_dir': {'exists': os.path.isdir('D:\\c'), 'entries': len(os.listdir('D:\\c')) if os.path.isdir('D:\\c') else None, 'touched': False},
            'parent_child_local_state': 'NOT_OBSERVED (no-session-persistence; nothing saved by the CLI is read or relied on)'},
        'before_tree': before}
    save(os.path.join(evidence, 'request.json'), req)
    print('prepared', len(before['files']), 'files', len(before['dirs']), 'dirs; prompt', sha(prompt))


def kill_tree(proc):
    subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)


def run(evidence):
    path = os.path.join(evidence, 'request.json')
    req = load(path)
    if req.get('phase') != 'BEFORE_CALL':
        sys.exit('phase is not BEFORE_CALL: refusing a second attempt')
    setup_doc = load(SETUP_PATH)
    lab = setup_doc['lab']
    with open(os.path.join(evidence, 'prompt.txt'), 'rb') as fh:
        prompt = fh.read()
    pf = req['preflight']
    drift = []
    if sha(prompt) != req['prompt_sha256'] or render_prompt() != prompt:
        drift.append('prompt')
    for name, src in runtime_files().items():
        if file_sha(src) != req['runtime_pins'][name]['sha256'] or file_sha(os.path.join(evidence, 'runtime', name)) != req['runtime_pins'][name]['sha256']:
            drift.append('runtime:' + name)
    for name, src in delivery_files(lab, setup_doc).items():
        if file_sha(src) != req['delivery_pins'][name]['sha256']:
            drift.append('delivery:' + name)
    if tree(lab) != req['before_tree'] or lab != req['lab']:
        drift.append('lab tree')
    if file_sha(BRIDGE) != pf['bridge_sha256'] or file_sha(MANIFEST_PATH) != pf['manifest_sha256'] or file_sha(SETUP_PATH) != pf['setup_json_sha256']:
        drift.append('bridge/manifest/setup')
    if any(not v['equal'] for v in baseline_view().values()):
        drift.append('source baseline')
    if os.path.getsize(CLAUDE) != CLAUDE_BASELINE['size'] or file_sha(CLAUDE) != CLAUDE_BASELINE['sha256']:
        drift.append('CLI binary')
    for rel, want in req['owner_pins'].items():
        if file_sha(os.path.join(REPO, *rel.split('/'))) != want['sha256']:
            drift.append('owner:' + rel)
    for rel in (CAND_REL, RESULT_REL):
        if os.path.lexists(labp(lab, rel)):
            drift.append('target exists ' + rel)
    if drift:
        sys.exit('drift since prepare, not dispatching: %s' % drift)
    req['phase'] = 'STARTED'
    req['started_at'] = now()
    save(path, req)
    env = dict(os.environ)
    env.update(ENV_ADDED)
    outcome = {'timed_out': False, 'killed_by_init_gate': False}
    events, gate = [], {'seen_init': False}
    with open(os.path.join(evidence, 'stderr.log'), 'wb') as err, open(os.path.join(evidence, 'stream.jsonl'), 'wb') as out:
        proc = subprocess.Popen(argv(), cwd=lab, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, env=env)

        def on_timeout():
            outcome['timed_out'] = True
            kill_tree(proc)
        timer = threading.Timer(TIMEOUT, on_timeout)
        timer.start()
        try:
            proc.stdin.write(prompt)
            proc.stdin.close()
        except OSError:
            pass
        for raw in proc.stdout:
            out.write(raw)
            out.flush()
            try:
                ev = json.loads(raw.decode('utf-8', 'replace'))
            except ValueError:
                continue
            events.append(ev)
            if not gate['seen_init'] and ev.get('type') == 'system' and ev.get('subtype') == 'init':
                tools = ev.get('tools') or []
                agents_listed = ev.get('agents') or []
                gate.update(seen_init=True, tools=tools, agents=agents_listed, has_send_message='SendMessage' in tools, has_agent_tool='Agent' in tools, has_task_tool='Task' in tools,
                            has_law_worker=any('law-worker' in str(a) for a in agents_listed),
                            model=ev.get('model'), session_id=ev.get('session_id'), at_event=len(events) - 1)
                if not (all(t in tools for t in ('Read', 'Write', 'Bash')) and ('Agent' in tools or 'Task' in tools) and gate['has_law_worker']):
                    gate['decision'] = 'TERMINATE'
                    outcome['killed_by_init_gate'] = True
                    kill_tree(proc)
                else:
                    gate['decision'] = 'CONTINUE'
        try:
            proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            proc.wait(timeout=30)
        timer.cancel()
        outcome['exit_code'] = proc.returncode
    if not gate['seen_init']:
        gate['decision'] = 'NO_INIT_EVENT'
    uses = [c for e in events if e.get('type') == 'assistant' for c in (e.get('message', {}).get('content') or []) if isinstance(c, dict) and c.get('type') == 'tool_use']
    gate['tool_use_events_before_exit'] = len(uses)
    req = load(path)
    req['phase'] = 'FINISHED'
    req['finished_at'] = now()
    req['run_outcome'] = outcome
    req['init_gate_observed'] = gate
    req['winget_claude_processes_after_call'] = claude_processes()
    req['after_tree'] = tree(lab)
    save(path, req)
    print('exit', outcome, 'gate', {k: gate.get(k) for k in ('decision', 'has_send_message', 'has_agent_tool', 'has_task_tool', 'has_law_worker', 'tool_use_events_before_exit')})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('setup', 'anchor', 'selftest', 'discover-inner', 'compose-inner', 'prepare', 'run'))
    ap.add_argument('arg', nargs='?')
    ap.add_argument('--base')
    ap.add_argument('--evidence')
    a = ap.parse_args()
    if a.cmd == 'setup':
        setup(a.base)
    elif a.cmd == 'anchor':
        anchor()
    elif a.cmd == 'discover-inner':
        discover_inner(a.arg)
    elif a.cmd == 'compose-inner':
        compose_inner(a.arg)
    elif a.cmd == 'selftest':
        sys.exit(selftest())
    elif a.cmd == 'prepare':
        prepare(a.evidence)
    else:
        run(a.evidence)


if __name__ == '__main__':
    main()
