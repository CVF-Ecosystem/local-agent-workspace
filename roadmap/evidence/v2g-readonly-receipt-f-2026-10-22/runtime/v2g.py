"""V2-G: dựng config/manifest độc lập, kiểm offline và chạy MỘT lượt Claude CLI Main-only readonly trên artifact native F đã có. Script hỗ trợ bài đo, không phải công cụ sản phẩm.
Driver này chỉ gồm setup/anchor/selftest/prepare/run. Assess và collect sau lượt nằm ở v2g_post.py (entry riêng), để bytes driver đã chạy không đổi.
Không dựng lab, không ghi vào lab F, không gọi bridge/driver F.

Dùng: / Usage:
  python -B v2g.py setup                       dựng config.json + bridge_manifest.json (offline, chỉ ghi working/v2g/meta/, không gọi AI)
  python -B v2g.py anchor                      chốt EXPECTED_CONFIG_SHA256/EXPECTED_LAB vào bridge (sau setup, trước pin bridge)
  python -B v2g.py selftest                    kiểm helper trên lab F hiện có (chỉ đọc) và fixture/config tách trong tempfile (offline)
  python -B v2g.py prepare --evidence <dir>    preflight, lưu bytes/hash runtime, ghi request.json BEFORE_CALL; chưa gọi model
  python -B v2g.py run --evidence <dir>        kiểm lại bytes, gọi đúng MỘT lần claude; cổng init; không retry
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
META = os.path.join(HERE, '..', 'meta')
CONFIG_PATH = os.path.normpath(os.path.join(META, 'config.json'))
MANIFEST_PATH = os.path.normpath(os.path.join(META, 'bridge_manifest.json'))
BRIDGE = os.path.join(HERE, 'main_bridge.py')
POST = os.path.join(HERE, 'v2g_post.py')
PROMPT_FILE = os.path.join(HERE, 'prompt-v2g.txt')
F_EVIDENCE = os.path.join(REPO, 'roadmap', 'evidence', 'v2f-native-valid-result-2026-10-22')
F_SCRIPTS = os.path.join(REPO, 'working', 'v2f')
CLAUDE_BASELINE = {'size': 242411680, 'sha256': '6d34836bf4d62f4bd5221fb69899ed5b2edc380d35fb0f23218c62fae94e28b9', 'version': '2.1.81 (Claude Code)'}
CLAUDE = r'C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe\claude.EXE'
MODEL = 'claude-sonnet-5-5'
TIMEOUT = 120
BUDGET = '0.25'
ENV_ADDED = {'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
TOOLS = 'Read,Bash'
BRIDGE_FWD = BRIDGE.replace('\\', '/')
CMD_CHECKPOINT = 'python -I -B "%s" checkpoint' % BRIDGE_FWD
ALLOWED = 'Read,Bash(%s)' % CMD_CHECKPOINT
LAB = ('C:\\Users\\DELL\\AppData\\Local\\Temp\\claude\\d--UNG-DUNG-AI-TOOL-AI-2026-CVF-Workspace-local-agent-workspace\\c9b7c50b-e251-4e37-bfc9-2edaa0c24add\\scratchpad\\law-v2f-run1\\project')
TASK_REL = 'working/v2f/report/TASK.json'
CAND_REL = 'working/v2f/report/assignments/a1/candidate/draft.txt'
RESULT_REL = 'working/v2f/report/assignments/a1/RESULT.json'
ARTIFACTS = {  # bảng của phiếu V2-G, mục 3 / the work order table
    'task': {'rel': TASK_REL, 'size': 3009, 'sha256': '8dc05b3da636d1da1c2c5f18341667ff04e704dd8a4167201b65c397b6114280'},
    'result': {'rel': RESULT_REL, 'size': 3863, 'sha256': 'f3aa7e670cf5e5f9ef763b8bc127256bd20fc73617b14d16f59c0e3f6e54704e'},
    'candidate': {'rel': CAND_REL, 'size': 1158, 'sha256': '3c4d57666c3f426f843e1dbb898299532d913f536a357d203fafcdcba0d61cc1'}}
BASELINE = {'roles/README.md': '2f42490f39ed16a4ad30310da28f1bf1764ee3bed48a501f62cc54b842e73ef5',
            'tools/office.py': 'f7e6ae546d97f4f1dda7817b4189ed0bf3f78b1aa8471ce6dfc2f100e1308caf',
            'roles/office/MAIN.md': '929d5319ed8b1b66fd5c4a793321a302892e4307175272cc6a5a95a3ab880183',
            '.cvf/contracts/v3/control.schema.json': '21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642',
            '.cvf/rules/v3/ROUTING_POLICY.json': 'af141b37c242119c07fe0b6268a498a66ea89efd8caacb9a95cbfb06e7235084'}
DRIVE_ABS = re.compile(r'^[A-Za-z]:\\')
REPARSE = 0x400


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


def import_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bridge_module():
    b = import_path('v2g_main_bridge', BRIDGE)
    b.EXEMPT.add(Path(os.path.abspath(__file__)).resolve())  # driver này không phải mã owner; chỉ dùng cho self-test/discover / this driver is not owner code
    return b


def f_history_pins():
    """Bytes hiện tại của evidence F và script/meta F (lịch sử, không phải pin authority của G): so trước/sau để chứng minh không sửa. / F evidence + scripts as history."""
    return {'f_evidence': tree_digest(tree(F_EVIDENCE)), 'f_scripts_meta': tree_digest(tree(F_SCRIPTS))}


def lab_problems(lab):
    """Lab F đúng drive-absolute, không alias, không chồng cây LAW. / The F lab: plain, drive-absolute, outside the source tree."""
    problems = []
    if not DRIVE_ABS.match(lab) or not os.path.isdir(lab):
        problems.append('LAB_NOT_DRIVE_ABSOLUTE_DIR')
    elif os.path.normcase(os.path.realpath(lab)) != os.path.normcase(os.path.abspath(lab)):
        problems.append('LAB_RESOLVES_ELSEWHERE')
    if inside(REPO, lab) or inside(lab, REPO):
        problems.append('LAB_OVERLAPS_SOURCE_TREE')
    return problems


# ---------------------------------------------------------------- setup (offline, writes only working/v2g/meta/)
def discover_inner(tmp_cfg):
    """Chạy trong interpreter mới (-I): nạp owner như bridge và in tập file LAW đã nạp hoặc đã mở (có audit hook). / Fresh interpreter: load the way the bridge does and report loaded and opened LAW files."""
    law = os.path.realpath(REPO)
    opened = set()

    def hook(event, args):
        if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                opened.add(os.path.realpath(os.fsdecode(args[0])))
            except (OSError, ValueError):
                pass
    sys.addaudithook(hook)
    b = bridge_module()
    cfg = load(tmp_cfg)
    recipe = b.load_recipe(REPO)
    v3 = recipe['load_v3'](REPO)
    import importlib
    for name in ('artifacts', 'library_sync'):
        importlib.import_module(name)
    cp = recipe['checkpoint'](v3, cfg['lab'], cfg['task_rel'], cfg['result_rel'])
    stub = recipe['binding_stub'](v3, cp['task']) if cp.get('task') else None
    skip = ('working/v2g/', 'working/v2f/')
    rels = sorted(r for r in (os.path.relpath(p, law).replace('\\', '/') for p in opened if inside(law, p) and os.path.isfile(p))
                  if '__pycache__' not in r and not r.endswith('.pyc') and not r.startswith(skip))
    print(json.dumps({'problems': cp['problems'], 'loaded': sorted(b.law_loaded_files(REPO)), 'opened': rels, 'stub': stub}))


def setup():
    problems = lab_problems(LAB)
    if problems:
        sys.exit('lab refused: %s' % problems)
    for key, a in ARTIFACTS.items():
        p = labp(LAB, a['rel'])
        data = open(p, 'rb').read()
        if len(data) != a['size'] or sha(data) != a['sha256']:
            sys.exit('artifact differs from the work order table: %s' % key)
    for rel, want in BASELINE.items():
        if file_sha(os.path.join(REPO, *rel.split('/'))) != want:
            sys.exit('source baseline differs from the work order: ' + rel)
    f_setup, f_req = load(os.path.join(F_SCRIPTS, 'meta', 'setup.json')), load(os.path.join(F_EVIDENCE, 'request.json'))
    if f_setup['lab'] != LAB or f_req['lab'] != LAB:
        sys.exit('lab differs from the F request/setup')
    lab_tree = tree(LAB)
    if tree_digest(lab_tree) != tree_digest(f_req['after_tree']):
        sys.exit('lab tree differs from the F stored after_tree: stop, do not rebuild')
    with tempfile.TemporaryDirectory(prefix='law-v2g-setup-') as td:
        tmp_cfg = os.path.join(td, 'discover.json')
        save(tmp_cfg, {'lab': LAB, 'task_rel': TASK_REL, 'result_rel': RESULT_REL})
        r = subprocess.run([sys.executable, '-I', '-B', os.path.abspath(__file__), 'discover-inner', tmp_cfg], cwd=td, capture_output=True, stdin=subprocess.DEVNULL, timeout=300,
                           env=dict(os.environ, **ENV_ADDED))
    out = r.stdout.decode('utf-8', 'replace').strip().splitlines()
    if r.returncode != 0 or not out:
        sys.exit('discover failed (%s): %s' % (r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')))
    found = json.loads(out[-1])
    if found['problems'] or not found['stub']:
        sys.exit('discover checkpoint problems: %s' % found['problems'])
    if found['stub'] != f_setup['binding_stub']:
        sys.exit('the stub recomputed from the live TASK differs from the F setup stub: stop')
    files = {rel: file_sha(os.path.join(REPO, *rel.split('/')))
             for rel in sorted(set(found['loaded']) | set(found['opened']) | {'.cvf/checks/control_check_v3.py', '.cvf/rules/v3/ROUTING_POLICY.json', '.cvf/contracts/v3/control.schema.json'})}
    manifest = {'schema': 'law.v2g.bridge-manifest/1', 'created_at': now(), 'law_root': REPO, 'readme_sha256': BASELINE['roles/README.md'],
                'baseline': {k: file_sha(os.path.join(REPO, *k.split('/'))) for k in BASELINE}, 'files': files,
                'note': 'Pin policy THỰC DÙNG là .cvf/rules/v3/ROUTING_POLICY.json (loader.POLICY_REL); không pin v1 .cvf/rules/ROUTING_POLICY.json.'}
    save(MANIFEST_PATH, manifest)
    config = {'schema': 'law.v2g.config/1', 'lab': LAB, 'work_id': 'v2f', 'task_id': 'report', 'assignment_id': 'a1', 'task_rel': TASK_REL, 'candidate_rel': CAND_REL, 'result_rel': RESULT_REL,
              'artifacts': ARTIFACTS, 'task_raw_digest': 'sha256:' + ARTIFACTS['task']['sha256'], 'binding_stub': found['stub'],
              'lab_snapshot': {'files': len(lab_tree['files']), 'dirs': len(lab_tree['dirs']), 'tree_digest': tree_digest(lab_tree)},
              'manifest_sha256': file_sha(MANIFEST_PATH), 'created_at': now(),
              'f_history': {'note': 'Chỉ để đối chiếu lịch sử, không là pin authority của G.', 'f_setup_json_sha256': file_sha(os.path.join(F_SCRIPTS, 'meta', 'setup.json')),
                            'f_manifest_sha256': file_sha(os.path.join(F_SCRIPTS, 'meta', 'bridge_manifest.json')), 'f_after_tree_digest': tree_digest(f_req['after_tree']),
                            'f_bridge_policy_pin': 'v1 .cvf/rules/ROUTING_POLICY.json (finding F, không sửa hồi tố)'},
              'note': 'Config tin cậy, ngoài lab. Giá trị lấy từ phiếu V2-G và lab F hiện có; không tạo lại lab/file.'}
    save(CONFIG_PATH, config)
    print(json.dumps({'config_sha256': file_sha(CONFIG_PATH), 'manifest_sha256': config['manifest_sha256'], 'pinned_files': len(files), 'lab_snapshot': config['lab_snapshot'],
                      'opened_data_not_py': [r for r in found['opened'] if not r.endswith('.py')], 'v3_policy_pinned': files['.cvf/rules/v3/ROUTING_POLICY.json'],
                      'v1_policy_pinned': '.cvf/rules/ROUTING_POLICY.json' in files}, ensure_ascii=False, indent=2))


def anchor():
    """Chốt hằng anchor vào bridge SAU setup, TRƯỚC khi driver pin hash bridge. / Fix the two anchor constants in the bridge."""
    config = load(CONFIG_PATH)
    want_sha = file_sha(CONFIG_PATH)
    with open(BRIDGE, 'rb') as fh:
        text = fh.read().decode('utf-8')
    a1, a2 = 'EXPECTED_CONFIG_SHA256 = None  #', 'EXPECTED_LAB = None  #'
    if text.count(a1) != 1 or text.count(a2) != 1:
        sys.exit('anchor already set or bridge shape changed: refusing')
    text = text.replace(a1, 'EXPECTED_CONFIG_SHA256 = %r  #' % want_sha).replace(a2, 'EXPECTED_LAB = %r  #' % config['lab'])
    write_bytes(BRIDGE, text.encode('utf-8'))
    b = import_path('v2g_main_bridge_check', BRIDGE)
    if b.EXPECTED_CONFIG_SHA256 != want_sha or b.EXPECTED_LAB != config['lab']:
        sys.exit('anchor not read back')
    print(json.dumps({'expected_config_sha256': want_sha, 'expected_lab': config['lab'], 'bridge_sha256': file_sha(BRIDGE)}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- selftest (offline, readonly on the live lab; negatives on tempfile copies/configs)
def selftest():
    import copy
    b = bridge_module()
    config, manifest = load(CONFIG_PATH), load(MANIFEST_PATH)
    live = config['lab']
    live_before = tree(live)
    f_before = f_history_pins()
    results = []
    anchor_const = (b.EXPECTED_CONFIG_SHA256, b.EXPECTED_LAB)
    pyc_before = sorted(os.path.join(d, n) for d, _, ns in os.walk(REPO) for n in ns if d.endswith('__pycache__'))

    def case(name, ok, detail=None):
        results.append({'case': name, 'ok': bool(ok), 'detail': detail})

    def refused(r, token):
        return (not r['ok']) and r.get('refused_before_operation') is True and any(p.startswith(token) for p in r['problems'])

    case('anchor constants in the bridge equal the config raw SHA256 and the lab', b.EXPECTED_CONFIG_SHA256 == file_sha(CONFIG_PATH) and b.EXPECTED_LAB == live)
    case('config manifest_sha256 equals the manifest bytes; the manifest pins actual v3 policy and not v1',
         config['manifest_sha256'] == file_sha(MANIFEST_PATH) and manifest['files'].get('.cvf/rules/v3/ROUTING_POLICY.json') == b.POLICY_SHA256 == BASELINE['.cvf/rules/v3/ROUTING_POLICY.json']
         and '.cvf/rules/ROUTING_POLICY.json' not in manifest['files'])
    case('lab is a plain drive-absolute path and the live tree equals the config snapshot', not lab_problems(live) and tree_digest(live_before) == config['lab_snapshot']['tree_digest'])
    # --- dương: lab F hiện có, chỉ đọc
    r = b.run('checkpoint', config=config, manifest=manifest)
    ident = r.get('identity') or {}
    case('positive on the existing F lab (injected config, read-only): ok, problems=[], CHECKED_NOT_PASS, identity true, tree unchanged',
         r['ok'] and r['problems'] == [] and r['verdict'] == 'CHECKED_NOT_PASS' and ident.get('task_equals_dispatch_digest') is True and ident.get('result_binding_equals_dispatch_stub_before_outputs') is True
         and ident.get('raw_digests_equal_config') is True and r['lab_snapshot']['equal'] is True and tree(live) == live_before, r['problems'])
    case('identity: raw TASK/RESULT/candidate digests and candidate size equal the work-order table',
         ident.get('task_raw_digest') == 'sha256:' + ARTIFACTS['task']['sha256'] and ident.get('result_raw_digest') == 'sha256:' + ARTIFACTS['result']['sha256']
         and (ident.get('candidate') or {}).get('digest') == 'sha256:' + ARTIFACTS['candidate']['sha256'] and (ident.get('candidate') or {}).get('size') == ARTIFACTS['candidate']['size'])
    pol = r.get('policy') or {}
    case('policy: loader path, disk bytes and owner bytes are the pinned v3 file',
         pol.get('loader_policy_rel') == 'rules/v3/ROUTING_POLICY.json' and pol.get('disk_sha256') == pol.get('owner_bytes_sha256') == pol.get('owner_policy_sha256') == b.POLICY_SHA256
         and pol.get('resolved_path', '').lower().endswith('.cvf\\rules\\v3\\routing_policy.json'), pol)
    # --- âm: manifest/config lệch, trên lab F hiện có (không sửa file live)
    m = copy.deepcopy(manifest)
    del m['files']['.cvf/rules/v3/ROUTING_POLICY.json']
    case('manifest without the v3 policy pin is refused before the operation', refused(b.run('checkpoint', config=config, manifest=m), 'MANIFEST_POLICY_V3_PIN_MISSING_OR_WRONG'))
    m = copy.deepcopy(manifest)
    m['files']['.cvf/rules/v3/ROUTING_POLICY.json'] = '0' * 64
    r = b.run('checkpoint', config=config, manifest=m)
    case('manifest with a wrong v3 policy hash is refused (pin wrong and drift)', refused(r, 'MANIFEST_POLICY_V3_PIN_MISSING_OR_WRONG') and any(p.startswith('PIN_DRIFT .cvf/rules/v3/ROUTING_POLICY.json') for p in r['problems']), r['problems'])
    f_manifest = load(os.path.join(F_SCRIPTS, 'meta', 'bridge_manifest.json'))
    case('the F manifest (pins v1 policy only) is refused: the same file name under rules/ is not the v3 owner', refused(b.run('checkpoint', config=config, manifest=f_manifest), 'MANIFEST_POLICY_V3_PIN_MISSING_OR_WRONG'))
    m = copy.deepcopy(manifest)
    m['files']['.cvf/contracts/v3/control.schema.json'] = '1' * 64
    case('manifest with a wrong schema pin is refused', refused(b.run('checkpoint', config=config, manifest=m), 'MANIFEST_SCHEMA_PIN_MISSING_OR_WRONG'))
    m = copy.deepcopy(manifest)
    m['files']['tools/artifacts.py'] = '2' * 64
    case('owner drift (pin mismatch) is refused before the operation', refused(b.run('checkpoint', config=config, manifest=m), 'PIN_DRIFT tools/artifacts.py'))

    class FakeLoader:
        POLICY_REL = ('rules', 'ROUTING_POLICY.json')

        @staticmethod
        def default_cvf_dir():
            return Path(REPO) / '.cvf'
    probs, _ = b.policy_problems(REPO, {'loader': FakeLoader, 'owners': type('O', (), {'policy_bytes': b'x', 'policy_sha256': '3' * 64, 'schema_sha256': b.SCHEMA_SHA256})()})
    case('policy check refuses a loader whose POLICY_REL is the v1 path', any(p.startswith('LOADER_POLICY_REL_NOT_V3') for p in probs), probs)
    recipe = b.load_recipe(REPO)
    v3 = recipe['load_v3'](REPO)
    fake_owner = type('O', (), {'policy_bytes': b'tampered', 'policy_sha256': '4' * 64, 'schema_sha256': b.SCHEMA_SHA256})()
    probs, _ = b.policy_problems(REPO, dict(v3, owners=fake_owner))
    case('policy check refuses owner bytes that are not the pinned v3 policy', 'POLICY_V3_OWNER_BYTES_NOT_PINNED' in probs, probs)
    for key in ('task', 'result', 'candidate'):
        c = copy.deepcopy(config)
        c['artifacts'][key]['sha256'] = '5' * 64
        case('config with a wrong %s raw hash is refused before the operation' % key, refused(b.run('checkpoint', config=c, manifest=manifest), 'ARTIFACT_HASH_DIFFERS %s' % key))
    c = copy.deepcopy(config)
    c['artifacts']['candidate']['size'] = 1159
    case('config with a wrong candidate size is refused before the operation', refused(b.run('checkpoint', config=c, manifest=manifest), 'ARTIFACT_SIZE_DIFFERS candidate'))
    c = copy.deepcopy(config)
    c['lab_snapshot']['tree_digest'] = '6' * 64
    case('config with a different whole-lab snapshot is refused before the operation', refused(b.run('checkpoint', config=c, manifest=manifest), 'LAB_TREE_DIFFERS_FROM_SNAPSHOT'))
    c = copy.deepcopy(config)
    c['task_raw_digest'] = 'sha256:' + '7' * 64
    r = b.run('checkpoint', config=c, manifest=manifest)
    case('config with a TASK digest different from the dispatched one is HOLD', (not r['ok']) and r['verdict'] == 'HOLD' and 'TASK_CHANGED_SINCE_DISPATCH' in r['problems'], r['problems'])
    c = copy.deepcopy(config)
    c['binding_stub']['intent_digest'] = 'sha256:' + '8' * 64
    r = b.run('checkpoint', config=c, manifest=manifest)
    case('config with a binding stub different from the RESULT binding is HOLD', (not r['ok']) and r['verdict'] == 'HOLD' and 'BINDING_DIFFERS_FROM_DISPATCH_STUB' in r['problems'], r['problems'])
    case('the live lab is unchanged by the negative cases', tree(live) == live_before)
    # --- anchor + fixture tách: bản sao lab trong tempfile (cùng TASK bytes), không ghi vào lab live
    base = tempfile.mkdtemp(prefix='law-v2g-selftest-')
    try:
        fx = os.path.join(base, 'lab-copy')
        shutil.copytree(live, fx)
        fx_cfg_path, fx_man_path = os.path.join(base, 'config.json'), os.path.join(base, 'manifest.json')
        shutil.copyfile(MANIFEST_PATH, fx_man_path)

        def with_config(lab_for_config, lab_for_anchor, mutate=None):
            c = copy.deepcopy(config)
            c['lab'] = lab_for_config
            c['manifest_sha256'] = file_sha(fx_man_path)
            if mutate:
                mutate(c)
            save(fx_cfg_path, c)
            b.EXPECTED_CONFIG_SHA256, b.EXPECTED_LAB = file_sha(fx_cfg_path), lab_for_anchor
            return b.run('checkpoint', config_path=fx_cfg_path, manifest_path=fx_man_path)
        try:
            tc = tree(fx)
            r = with_config(fx, fx)
            case('anchored positive on a tempfile copy of the lab (same TASK bytes): ok, CHECKED_NOT_PASS, copy unchanged', r['ok'] and r['verdict'] == 'CHECKED_NOT_PASS' and tree(fx) == tc, r['problems'])
            r = with_config(fx, live)
            case('anchor: a coherent config for ANOTHER existing lab with the same TASK bytes is refused before the operation (lab mismatch)', r['problems'] == ['ANCHOR_LAB_MISMATCH'] and r['refused_before_operation'], r['problems'])
            b.EXPECTED_CONFIG_SHA256, b.EXPECTED_LAB = '9' * 64, fx
            r = b.run('checkpoint', config_path=fx_cfg_path, manifest_path=fx_man_path)
            case('anchor: a config file whose raw SHA is not the anchored one is refused before the operation', r['problems'] == ['ANCHOR_CONFIG_SHA_MISMATCH'] and r['refused_before_operation'], r['problems'])
            for key, rel in (('candidate', CAND_REL), ('result', RESULT_REL), ('task', TASK_REL)):
                p = labp(fx, rel)
                original = open(p, 'rb').read()
                write_bytes(p, original + b'x')
                r = with_config(fx, fx)
                case('tempfile copy with changed %s bytes is refused before the operation' % key, refused(r, 'ARTIFACT_HASH_DIFFERS %s' % key) or refused(r, 'ARTIFACT_SIZE_DIFFERS %s' % key), r['problems'])
                write_bytes(p, original)
            write_bytes(labp(fx, 'working/v2f/extra.txt'), b'x')
            r = with_config(fx, fx)
            case('tempfile copy with one added file is refused (whole-lab snapshot)', refused(r, 'LAB_TREE_DIFFERS_FROM_SNAPSHOT'), r['problems'])
            os.remove(labp(fx, 'working/v2f/extra.txt'))
            os.makedirs(labp(fx, 'working/v2f/emptydir'))
            r = with_config(fx, fx)
            case('tempfile copy with one added empty directory is refused (whole-lab snapshot)', refused(r, 'LAB_TREE_DIFFERS_FROM_SNAPSHOT'), r['problems'])
        finally:
            b.EXPECTED_CONFIG_SHA256, b.EXPECTED_LAB = anchor_const
    finally:
        shutil.rmtree(base, ignore_errors=True)
    # --- đúng lệnh Main sẽ chạy, từ cwd lab, trên lab F thật, qua anchor thật
    pre = tree(live)
    p = subprocess.run([sys.executable, '-I', '-B', BRIDGE, 'checkpoint'], cwd=live, capture_output=True, stdin=subprocess.DEVNULL, timeout=120)
    out = json.loads(p.stdout.decode('utf-8')) if p.stdout.strip() else {}
    case('the exact command from the lab cwd (sys.executable subprocess; NOT a Bash allow-rule proof; maintainer offline, not the Main proof): exit 0, ok, CHECKED_NOT_PASS, tree unchanged',
         p.returncode == 0 and out.get('ok') is True and out.get('problems') == [] and out.get('verdict') == 'CHECKED_NOT_PASS' and tree(live) == pre == live_before, {'exit': p.returncode, 'problems': out.get('problems')})
    p = subprocess.run([sys.executable, '-I', '-B', BRIDGE, 'observe'], cwd=live, capture_output=True, stdin=subprocess.DEVNULL, timeout=120)
    case('any other operation (observe) is refused by usage', p.returncode == 2, p.returncode)
    prompt_text = render_prompt().decode('utf-8')
    needed = [CMD_CHECKPOINT, live] + [labp(live, a['rel']) for a in ARTIFACTS.values()] + [a['sha256'] for a in ARTIFACTS.values()]
    missing = [x for x in needed if x not in prompt_text]
    case('rendered prompt carries the lab root, three absolute Read paths, expected hashes and the single command; no placeholder left', not missing and not re.search(r'\{[A-Z_]+\}', prompt_text), missing)
    case('argv has Read,Bash only, one Bash allow rule, no add-dir/bypass/teams', ' '.join(argv()).count('--add-dir') == 0 and '--dangerously-skip-permissions' not in argv() and argv()[argv().index('--tools') + 1] == 'Read,Bash'
         and argv()[argv().index('--allowedTools') + 1] == ALLOWED)
    pyc_after = sorted(os.path.join(d, n) for d, _, ns in os.walk(REPO) for n in ns if d.endswith('__pycache__'))
    case('no bytecode was added to the source tree', pyc_before == pyc_after, {'before': len(pyc_before), 'after': len(pyc_after)})
    case('F evidence and F scripts/meta are unchanged by the self-test', f_history_pins() == f_before)
    case('the live lab is unchanged by the whole self-test', tree(live) == live_before, tree_digest(live_before))
    print(json.dumps({'passed': sum(x['ok'] for x in results), 'failed': [x for x in results if not x['ok']], 'cases': results}, ensure_ascii=False, indent=2))
    return 0 if all(x['ok'] for x in results) else 1


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
    config = load(CONFIG_PATH)
    a = config['artifacts']
    sub = {'{CHECKPOINT}': CMD_CHECKPOINT, '{LAB}': config['lab'], '{P_TASK}': labp(config['lab'], a['task']['rel']), '{P_RESULT}': labp(config['lab'], a['result']['rel']),
           '{P_CAND}': labp(config['lab'], a['candidate']['rel']), '{R_TASK}': a['task']['rel'], '{R_RESULT}': a['result']['rel'], '{R_CAND}': a['candidate']['rel'],
           '{S_TASK}': str(a['task']['size']), '{S_RESULT}': str(a['result']['size']), '{S_CAND}': str(a['candidate']['size']),
           '{H_TASK}': a['task']['sha256'], '{H_RESULT}': a['result']['sha256'], '{H_CAND}': a['candidate']['sha256']}
    with open(PROMPT_FILE, encoding='utf-8', newline='') as fh:
        text = fh.read()
    for k, v in sub.items():
        text = text.replace(k, v)
    return text.encode('utf-8')


def baseline_view():
    return {rel: {'sha256': file_sha(os.path.join(REPO, *rel.split('/'))), 'baseline': want, 'equal': file_sha(os.path.join(REPO, *rel.split('/'))) == want} for rel, want in BASELINE.items()}


def runtime_files():
    """Bytes runtime mà lượt sẽ dùng: driver, bridge, prompt, post, config, manifest. / Runtime source bytes pinned before the call."""
    return {'v2g.py': os.path.abspath(__file__), 'main_bridge.py': BRIDGE, 'prompt-v2g.txt': PROMPT_FILE, 'v2g_post.py': POST, 'config.json': CONFIG_PATH, 'bridge_manifest.json': MANIFEST_PATH}


def prepare(evidence):
    config, manifest = load(CONFIG_PATH), load(MANIFEST_PATH)
    lab = config['lab']
    problems = lab_problems(lab)
    if os.path.lexists(evidence) and os.listdir(evidence):
        problems.append('EVIDENCE_DIR_NOT_EMPTY')
    if not inside(REPO, evidence):
        problems.append('EVIDENCE_DIR_OUTSIDE_REPO')
    b = bridge_module()
    pins = b.pin_problems(REPO, manifest)
    if b.EXPECTED_CONFIG_SHA256 != file_sha(CONFIG_PATH) or b.EXPECTED_LAB != lab:
        problems.append('BRIDGE_ANCHOR_NOT_FIXED_TO_CONFIG_AND_LAB')
    exe_size, exe_sha = os.path.getsize(CLAUDE), file_sha(CLAUDE)
    if exe_size != CLAUDE_BASELINE['size'] or exe_sha != CLAUDE_BASELINE['sha256']:
        problems.append('CLI_BINARY_DIFFERS_FROM_BASELINE size=%s sha256=%s' % (exe_size, exe_sha))
    if file_sha(MANIFEST_PATH) != config['manifest_sha256']:
        problems.append('MANIFEST_HASH_DIFFERS_FROM_CONFIG')
    lab_probs, before = b.lab_problems(lab, config)
    problems += lab_probs
    if any(not v['equal'] for v in baseline_view().values()):
        problems.append('SOURCE_BASELINE_DRIFT')
    if problems or pins:
        sys.exit('prepare refused: %s %s' % (problems, pins))
    ver = subprocess.run([CLAUDE, '--version'], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace').strip()
    if ver != CLAUDE_BASELINE['version']:
        sys.exit('prepare refused: CLI version %r differs from baseline %r (no update, no other host)' % (ver, CLAUDE_BASELINE['version']))
    prompt = render_prompt()
    os.makedirs(evidence, exist_ok=True)
    write_bytes(os.path.join(evidence, 'prompt.txt'), prompt)
    pins_rt = {}
    for name, src in runtime_files().items():
        with open(src, 'rb') as fh:
            data = fh.read()
        write_bytes(os.path.join(evidence, 'runtime', name), data)  # bản bytes lưu TRƯỚC Popen / byte copy saved before Popen
        pins_rt[name] = {'origin': os.path.relpath(src, REPO).replace('\\', '/'), 'sha256': sha(data), 'size': len(data)}
    owner_pins = {rel: {'sha256': want} for rel, want in sorted(manifest['files'].items())}
    req = {
        'phase': 'BEFORE_CALL', 'recorded_at': now(), 'envelope': 'V2-G (roadmap/WORKORDER_V2G_2026-10-22.md)', 'host_version': ver, 'executable': CLAUDE,
        'executable_size_bytes': exe_size, 'executable_sha256': exe_sha, 'executable_baseline': CLAUDE_BASELINE, 'lab': lab,
        'authorization': 'PROJECT maintainer lab exception 18/10 + work order V2-G 22/10 handed to Claude by the operator; not product authority, no product grant in the lab (grants=[])',
        'models_requested': {'main': MODEL}, 'effort_requested': {'main': None},
        'model_basis': 'Operator named no model/effort in the handover message (task, one attempt, timeout 120s, budget 0.25 USD only). Lab choice: the model id of the Claude session handed this work order (claude-sonnet-5-5, as stated by that session); no --effort flag passed, so effort is requested UNKNOWN/observed UNKNOWN; not a product preset, to be confirmed by the operator in review',
        'operator_selection_before_call': {'budget_usd_cli_requested': float(BUDGET), 'timeout_seconds': TIMEOUT, 'parent_attempts': 1, 'workers': 0, 'on_missing_evidence': 'PARTIAL, no retry, no compensating action',
                                          'handover': 'wait for Codex review', 'model': 'not stated', 'effort': 'not stated'},
        'limits': {'ai_attempts': 1, 'sessions': 1, 'parent_attempt_number_overall': 6, 'native_invocations': 0, 'child': None, 'send_message_calls': 0, 'main_bash_commands': 1,
                   'main_reads': 3, 'max_budget_usd_cli_requested': float(BUDGET), 'timeout_seconds': TIMEOUT, 'paid_retry': False},
        'cumulative_before': {'attempts': 5, 'telemetry_usd_known': 3.0068661, 'c_telemetry': 'UNKNOWN',
                              'note': 'V1-B 0.7669449 + B2 0.75837945 + D 0.6987528 + F 0.78278895 = 3.0068661; V2-C telemetry NOT_OBSERVED; G is attempt 6, recorded separately; the full total stays UNKNOWN; budget is a requested parameter, not an invoice or a hard cap'},
        'scope': {'read': [TASK_REL, RESULT_REL, CAND_REL], 'main_writes': 'none (Write tool is not in the tool list)', 'main_shell': [CMD_CHECKPOINT], 'cooperative': 'tool list and allow rule are requested configuration; the trace is observation; not a sandbox'},
        'argv_without_prompt': argv(), 'allowed_tools_rules': ['Read', 'Bash(%s)' % CMD_CHECKPOINT], 'tools_flag': TOOLS, 'prompt_via': 'stdin (UTF-8), saved as prompt.txt', 'prompt_sha256': sha(prompt),
        'runtime_pins': pins_rt, 'owner_pins_count': len(owner_pins), 'owner_pins': owner_pins,
        'env_added': ENV_ADDED, 'env_note': 'Environment otherwise inherited, not copied into the record',
        'init_gate': {'rule': 'terminate the process unless the init event lists exactly Read and Bash and no other tool', 'enforcement': 'driver reads stdout line by line and kills the process tree on the init event; stdout buffering may let the model act before the kill, which is recorded if it happens'},
        'preflight': {'lab_path_problems': problems, 'baseline': baseline_view(), 'bridge_sha256': file_sha(BRIDGE), 'manifest_sha256': file_sha(MANIFEST_PATH), 'config_sha256': file_sha(CONFIG_PATH),
                      'pin_problems': pins, 'pinned_files': len(manifest['files']), 'artifacts': config['artifacts'], 'lab_snapshot': config['lab_snapshot'], 'f_history_pins': f_history_pins(),
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
    config = load(CONFIG_PATH)
    lab = config['lab']
    with open(os.path.join(evidence, 'prompt.txt'), 'rb') as fh:
        prompt = fh.read()
    pf = req['preflight']
    drift = []
    if sha(prompt) != req['prompt_sha256'] or render_prompt() != prompt:
        drift.append('prompt')
    for name, src in runtime_files().items():
        if file_sha(src) != req['runtime_pins'][name]['sha256'] or file_sha(os.path.join(evidence, 'runtime', name)) != req['runtime_pins'][name]['sha256']:
            drift.append('runtime:' + name)
    if tree(lab) != req['before_tree'] or lab != req['lab']:
        drift.append('lab tree')
    if file_sha(BRIDGE) != pf['bridge_sha256'] or file_sha(MANIFEST_PATH) != pf['manifest_sha256'] or file_sha(CONFIG_PATH) != pf['config_sha256']:
        drift.append('bridge/manifest/config')
    if any(not v['equal'] for v in baseline_view().values()):
        drift.append('source baseline')
    if os.path.getsize(CLAUDE) != CLAUDE_BASELINE['size'] or file_sha(CLAUDE) != CLAUDE_BASELINE['sha256']:
        drift.append('CLI binary')
    for rel, want in req['owner_pins'].items():
        if file_sha(os.path.join(REPO, *rel.split('/'))) != want['sha256']:
            drift.append('owner:' + rel)
    if f_history_pins() != pf['f_history_pins']:
        drift.append('F evidence/scripts')
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
                gate.update(seen_init=True, tools=tools, agents=ev.get('agents') or [], mcp_servers=ev.get('mcp_servers'), model=ev.get('model'), session_id=ev.get('session_id'),
                            permission_mode=ev.get('permissionMode'), at_event=len(events) - 1)
                if sorted(tools) != ['Bash', 'Read']:
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
    print('exit', outcome, 'gate', {k: gate.get(k) for k in ('decision', 'tools', 'tool_use_events_before_exit')})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('setup', 'anchor', 'selftest', 'discover-inner', 'prepare', 'run'))
    ap.add_argument('arg', nargs='?')
    ap.add_argument('--evidence')
    a = ap.parse_args()
    if a.cmd == 'setup':
        setup()
    elif a.cmd == 'anchor':
        anchor()
    elif a.cmd == 'discover-inner':
        discover_inner(a.arg)
    elif a.cmd == 'selftest':
        sys.exit(selftest())
    elif a.cmd == 'prepare':
        prepare(a.evidence)
    else:
        run(a.evidence)


if __name__ == '__main__':
    main()
