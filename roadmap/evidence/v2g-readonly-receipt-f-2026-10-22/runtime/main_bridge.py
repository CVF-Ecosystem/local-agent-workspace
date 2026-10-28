"""V2-G: cầu nối bảo trì cho Main, CHỈ ĐỌC, CHỈ MỘT lệnh `checkpoint` trên artifact native F đã có. Script hỗ trợ bài đo, không phải công cụ sản phẩm. / Read-only maintenance bridge: one `checkpoint` over the existing F artifact.

Chạy (lệnh duy nhất Main được phép): / The only command Main may run:
  python -I -B "<đường dẫn>/main_bridge.py" checkpoint

Bridge nằm trong kho nguồn tin cậy, NGOÀI dữ liệu lab. Lab chỉ là data root: không import, không exec mã từ lab hay từ dữ liệu của caller.
- Không nhận đối số nào ngoài `checkpoint`. Đường lab, ba định danh (TASK/RESULT/candidate), digest TASK thô, stub binding và snapshot cả cây lab lấy từ `working/v2g/meta/config.json`.
- ANCHOR: hằng EXPECTED_CONFIG_SHA256 và EXPECTED_LAB nằm trong chính file này, chốt SAU khi config/manifest hoàn tất và TRƯỚC khi driver pin hash bridge. Bridge băm bytes thô của config
  và so với hằng trước khi dùng bất kỳ trường nào bên trong, rồi so `lab` với hằng; không nhận override qua argv/env. Đây là anchor mã bảo trì do operator kiểm soát, không phải sandbox của host.
- Nạp đúng khối `law-recipe: task-result-checkpoint` của roles/README.md kho nguồn khi raw hash khớp V2-B, rồi gọi `load_v3` từ cây LAW cố định.
- SỬA FINDING F: policy thực dùng là `.cvf/rules/v3/ROUTING_POLICY.json` (loader.POLICY_REL). Bridge pin đúng file đó (hằng POLICY_SHA256 + manifest), đối chiếu đường loader thực đọc và bytes owner đã nạp; pin v1 cùng tên không được chấp nhận.
- Trước mọi operation: hash manifest và README, hash mọi file LAW được pin; ba file của lab đúng đường/size/SHA; cả cây lab đúng snapshot; sau khi nạp owner, mọi module đã nạp phải nằm trong cây LAW (đã pin) hoặc thư viện chuẩn/site-packages.
- Chỉ stdout và mã thoát: không ghi gì, không RESULT, sidecar, cache, sổ hay bytecode. `checkpoint` không publish, không tự gán MET/PASS.
Self-integrity của chính file này do driver kiểm bằng hash trước lượt (không tự chứng minh bằng cách tự hash). / This file's own bytes are pinned by the driver before the run.
"""
import sys

sys.dont_write_bytecode = True

import hashlib
import importlib
import json
import os
import re
import sysconfig
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAW = HERE.parents[2]  # working/v2g/scripts -> kho nguồn / source tree
EXEMPT = {Path(__file__).resolve()}  # chính bridge (driver kiểm hash trước lượt) / this file; the driver pins its bytes before the run
META = HERE.parent / 'meta'
CONFIG_PATH = META / 'config.json'
MANIFEST_PATH = META / 'bridge_manifest.json'
EXPECTED_CONFIG_SHA256 = 'aa8f30a31defe3fc8f15da7e96ed2c826e486e1d47fe98103f8fb9599350615d'  # được điền SAU config/manifest, TRƯỚC khi driver pin bridge / filled after config+manifest, before the driver pins this file
EXPECTED_LAB = 'C:\\Users\\DELL\\AppData\\Local\\Temp\\claude\\d--UNG-DUNG-AI-TOOL-AI-2026-CVF-Workspace-local-agent-workspace\\c9b7c50b-e251-4e37-bfc9-2edaa0c24add\\scratchpad\\law-v2f-run1\\project'  # đường lab drive-absolute đã chốt / the resolved lab path fixed after setup
README_REL = 'roles/README.md'
README_SHA256 = '2f42490f39ed16a4ad30310da28f1bf1764ee3bed48a501f62cc54b842e73ef5'  # recipe V2-B đã nhận
SCHEMA_REL = '.cvf/contracts/v3/control.schema.json'
SCHEMA_SHA256 = '21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642'
POLICY_REL = '.cvf/rules/v3/ROUTING_POLICY.json'  # policy v3 THỰC DÙNG (loader.POLICY_REL) / the policy the loader actually reads
POLICY_SHA256 = 'af141b37c242119c07fe0b6268a498a66ea89efd8caacb9a95cbfb06e7235084'
RECIPE_RE = re.compile(r'```python\n# law-recipe: task-result-checkpoint\n(.*?)```', re.S)
REPARSE = 0x400
LIMITS = ['BYTES_DIGEST_ONLY', 'NOT_PASS_NOT_GRANT_NOT_CONTENT_CHECK', 'NOT_ATOMIC_SNAPSHOT']
ARTIFACT_KEYS = ('task', 'result', 'candidate')


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    with open(path, 'rb') as fh:
        return sha_bytes(fh.read())


def inside(base, path):
    b, p = os.path.normcase(os.path.realpath(str(base))), os.path.normcase(os.path.realpath(str(path)))
    return p == b or p.startswith(b + os.sep)


def trusted_prefixes():
    """Thư viện chuẩn và site-packages của Python gốc. / Stdlib and site-packages of the base interpreter."""
    paths = sysconfig.get_paths()
    out = {sys.base_prefix, sys.prefix, paths.get('stdlib'), paths.get('platstdlib'), paths.get('purelib'), paths.get('platlib')}
    return [p for p in out if p]


def reparse_chain(p):
    """Thành phần đường dẫn là symlink/junction/reparse point. / Path components that are links or reparse points."""
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


def tree(root):
    files, dirs = {}, []
    for d, subdirs, names in os.walk(root):
        dirs.extend(os.path.relpath(os.path.join(d, n), root).replace('\\', '/') for n in subdirs)
        for n in names:
            p = os.path.join(d, n)
            files[os.path.relpath(p, root).replace('\\', '/')] = sha_file(p)
    return {'files': files, 'dirs': sorted(dirs)}


def tree_digest(t):
    return sha_bytes(json.dumps(t, sort_keys=True).encode('utf-8'))


# ---------------------------------------------------------------- pin / provenance
def pin_problems(law, manifest, readme_expected=README_SHA256):
    """Hash README và mọi file LAW được pin; manifest phải mang đúng policy v3 thực dùng và schema. / README, every pinned LAW file, and the actual v3 policy + schema pins."""
    problems = []
    law = Path(law)
    readme = law / README_REL
    if not readme.is_file() or sha_file(readme) != readme_expected:
        problems.append('RECIPE_README_HASH_DRIFT')
    if manifest.get('readme_sha256') != readme_expected:
        problems.append('MANIFEST_README_PIN_DRIFT')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        return problems + ['MANIFEST_FILES_MISSING']
    if files.get(POLICY_REL) != POLICY_SHA256:
        problems.append('MANIFEST_POLICY_V3_PIN_MISSING_OR_WRONG')
    if files.get(SCHEMA_REL) != SCHEMA_SHA256:
        problems.append('MANIFEST_SCHEMA_PIN_MISSING_OR_WRONG')
    for rel, want in sorted(files.items()):
        p = law.joinpath(*rel.split('/'))
        if not inside(law, p) or not p.is_file():
            problems.append('PIN_MISSING ' + rel)
        elif sha_file(p) != want:
            problems.append('PIN_DRIFT ' + rel)
    return problems


def loaded_module_problems(law, lab, manifest):
    """Mọi module đã nạp phải nằm trong cây LAW và được pin, hoặc trong thư viện chuẩn/site-packages; module từ lab hay nơi khác bị từ chối. / Reject any module resolved outside the fixed trees."""
    problems, law, trusted = [], Path(law), trusted_prefixes()
    files = manifest.get('files', {})
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, '__file__', None)
        if not f:
            continue
        p = Path(f).resolve()
        if p in EXEMPT:
            continue
        if inside(law, p):
            rel = p.relative_to(Path(os.path.realpath(str(law)))).as_posix() if p.is_absolute() else str(p)
            if rel not in files:
                problems.append('UNPINNED_LAW_MODULE %s=%s' % (name, rel))
        elif lab is not None and inside(lab, p):
            problems.append('MODULE_FROM_LAB %s' % name)
        elif not any(inside(t, p) for t in trusted):
            problems.append('MODULE_OUTSIDE_TRUSTED_TREE %s' % name)
    return problems


def law_loaded_files(law):
    """Các file .py của cây LAW đang nằm trong sys.modules (dùng để dựng manifest khi setup). / LAW .py files currently loaded."""
    law, out = Path(os.path.realpath(str(law))), set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, '__file__', None)
        if f:
            p = Path(f).resolve()
            if p not in EXEMPT and inside(law, p) and p.suffix == '.py':
                out.add(p.relative_to(law).as_posix())
    return out


def load_recipe(law):
    readme = Path(law) / README_REL
    blocks = RECIPE_RE.findall(readme.read_text(encoding='utf-8'))
    if len(blocks) != 1:
        raise RuntimeError('RECIPE_BLOCK_COUNT %d' % len(blocks))
    ns = {'__name__': 'law_recipe_v2g'}
    exec(compile(blocks[0], 'roles/README.md#law-recipe', 'exec'), ns)  # mã tin cậy của cây LAW đã pin hash / trusted pinned LAW code
    return ns


def refuse(op, problems):
    return {'op': op, 'ok': False, 'refused_before_operation': True, 'problems': problems}


def policy_problems(law, v3):
    """Policy thực dùng: đường loader đọc (theo default_cvf_dir + POLICY_REL), file trên đĩa và bytes owner đã nạp phải cùng là v3 đã pin. / The loader's own path, the file on disk and the owner's bytes must all be the pinned v3."""
    law = Path(law)
    loader = v3['loader']
    rel = tuple(getattr(loader, 'POLICY_REL', ()))
    if '/'.join(rel) != POLICY_REL.replace('.cvf/', '', 1):
        return ['LOADER_POLICY_REL_NOT_V3 %s' % '/'.join(rel)], None
    path = Path(loader.default_cvf_dir()).joinpath(*rel)
    want = law.joinpath(*POLICY_REL.split('/'))
    if not path.is_file() or os.path.normcase(os.path.realpath(str(path))) != os.path.normcase(os.path.realpath(str(want))) or not inside(law, path):
        return ['POLICY_V3_PATH_MISMATCH'], None
    problems, disk = [], sha_file(path)
    owners = v3['owners']
    owner_bytes = getattr(owners, 'policy_bytes', None)
    owner = sha_bytes(owner_bytes) if isinstance(owner_bytes, (bytes, bytearray)) else None
    if disk != POLICY_SHA256:
        problems.append('POLICY_V3_DISK_HASH_NOT_PINNED')
    if owner != POLICY_SHA256 or getattr(owners, 'policy_sha256', None) != POLICY_SHA256:
        problems.append('POLICY_V3_OWNER_BYTES_NOT_PINNED')
    if getattr(owners, 'schema_sha256', None) != SCHEMA_SHA256:
        problems.append('SCHEMA_OWNER_BYTES_NOT_PINNED')
    return problems, {'rel': POLICY_REL, 'resolved_path': str(path.resolve()), 'loader_policy_rel': '/'.join(rel), 'disk_sha256': disk, 'owner_bytes_sha256': owner,
                      'owner_policy_sha256': getattr(owners, 'policy_sha256', None), 'pinned_sha256': POLICY_SHA256}


# ---------------------------------------------------------------- lab identity
def lab_problems(lab, config):
    """Lab đúng drive-absolute, không alias; ba file đúng đường/size/SHA; cả cây lab đúng snapshot. Trả (problems, tree_before)."""
    problems = []
    if not isinstance(lab, str) or not re.match(r'^[A-Za-z]:\\', lab) or not os.path.isdir(lab):
        return ['LAB_PATH_NOT_DRIVE_ABSOLUTE_DIR'], None
    if reparse_chain(lab) or os.path.normcase(os.path.realpath(lab)) != os.path.normcase(os.path.abspath(lab)):
        return ['LAB_REPARSE_OR_RESOLVE_DIFFERS'], None
    arts = config.get('artifacts')
    if not isinstance(arts, dict) or set(arts) != set(ARTIFACT_KEYS):
        return ['CONFIG_ARTIFACTS_SHAPE'], None
    for key in ARTIFACT_KEYS:
        a = arts[key]
        p = os.path.join(lab, *a['rel'].split('/'))
        if reparse_chain(p) or not os.path.isfile(p):
            problems.append('ARTIFACT_MISSING_OR_ALIAS %s' % key)
            continue
        with open(p, 'rb') as fh:
            data = fh.read()
        if len(data) != a['size']:
            problems.append('ARTIFACT_SIZE_DIFFERS %s' % key)
        if sha_bytes(data) != a['sha256']:
            problems.append('ARTIFACT_HASH_DIFFERS %s' % key)
    if problems:
        return problems, None
    before = tree(lab)
    snap = config.get('lab_snapshot') or {}
    if tree_digest(before) != snap.get('tree_digest') or len(before['files']) != snap.get('files') or len(before['dirs']) != snap.get('dirs'):
        problems.append('LAB_TREE_DIFFERS_FROM_SNAPSHOT')
    return problems, before


# ---------------------------------------------------------------- operation
def prepare(op, law, config, manifest):
    """Trả (recipe, v3, policy_view, tree_before, None) hoặc refusal. Không gọi operation khi còn vấn đề. / Pins, lab identity, recipe, owners, policy, loaded-module check."""
    law = Path(law)
    lab = config.get('lab')
    problems, tree_before = lab_problems(lab, config)
    if problems:
        return None, None, None, None, refuse(op, problems)
    if inside(law, lab) or inside(lab, law):
        return None, None, None, None, refuse(op, ['LAB_OVERLAPS_LAW_TREE'])
    problems = pin_problems(law, manifest)
    if problems:
        return None, None, None, None, refuse(op, problems)
    try:
        recipe = load_recipe(law)
        v3 = recipe['load_v3'](law)
        for name in ('artifacts', 'library_sync'):
            m = importlib.import_module(name)
            if Path(m.__file__).resolve().parent != Path(os.path.realpath(str(law))) / 'tools':
                return None, None, None, None, refuse(op, ['OWNER_NOT_FIXED_TREE ' + name])
    except Exception as exc:  # owner không nạp được: từ chối, không fallback / owner unavailable: refuse
        return None, None, None, None, refuse(op, ['OWNER_LOAD_FAILED %s' % type(exc).__name__])
    problems, view = policy_problems(law, v3)
    problems += loaded_module_problems(law, lab, manifest)
    if problems:
        return None, None, None, None, refuse(op, problems)
    return recipe, v3, view, tree_before, None


def anchored_config(op, config_path, manifest_path):
    """Đọc bytes thô config, kiểm anchor TRƯỚC khi dùng trường bên trong. Trả (config, manifest, None) hoặc (None, None, refusal). / Raw-hash the config before trusting any inner field."""
    if not (isinstance(EXPECTED_CONFIG_SHA256, str) and len(EXPECTED_CONFIG_SHA256) == 64 and isinstance(EXPECTED_LAB, str) and EXPECTED_LAB):
        return None, None, refuse(op, ['ANCHOR_NOT_SET'])
    try:
        raw_config = Path(config_path).read_bytes()
    except OSError:
        return None, None, refuse(op, ['CONFIG_UNREADABLE'])
    if sha_bytes(raw_config) != EXPECTED_CONFIG_SHA256:
        return None, None, refuse(op, ['ANCHOR_CONFIG_SHA_MISMATCH'])
    try:
        config = json.loads(raw_config.decode('utf-8'))
        raw_manifest = Path(manifest_path).read_bytes()
        manifest = json.loads(raw_manifest.decode('utf-8'))
    except (OSError, ValueError):
        return None, None, refuse(op, ['CONFIG_OR_MANIFEST_UNREADABLE'])
    lab = config.get('lab')
    if lab != EXPECTED_LAB or not isinstance(lab, str) or os.path.normcase(os.path.realpath(lab)) != os.path.normcase(os.path.abspath(EXPECTED_LAB)):
        return None, None, refuse(op, ['ANCHOR_LAB_MISMATCH'])
    if sha_bytes(raw_manifest) != config.get('manifest_sha256'):
        return None, None, refuse(op, ['MANIFEST_HASH_DRIFT'])
    return config, manifest, None


def run(op='checkpoint', law=LAW, config=None, manifest=None, config_path=None, manifest_path=None):
    """`config`/`manifest` dạng dict chỉ dùng cho fixture/discover trong Python (không qua argv); đường thật luôn qua anchor. / dict injection is for fixtures only; the real path always goes through the anchor."""
    if config is None or manifest is None:
        config, manifest, bad = anchored_config(op, config_path or CONFIG_PATH, manifest_path or MANIFEST_PATH)
        if bad:
            return bad
    recipe, v3, policy_view, tree_before, bad = prepare(op, law, config, manifest)
    if bad:
        return bad
    lab = config['lab']
    arts = config['artifacts']
    cp = recipe['checkpoint'](v3, lab, config['task_rel'], config['result_rel'])
    problems = list(cp['problems'])
    ident = {'task_raw_digest': None, 'task_equals_dispatch_digest': None, 'result_raw_digest': None, 'result_path': config['result_rel'],
             'candidate': None, 'result_binding_equals_dispatch_stub_before_outputs': None, 'raw_digests_equal_config': None}
    raw = cp.get('raw')
    if raw:
        ident['task_raw_digest'], ident['result_raw_digest'] = raw['task'], raw['result']
        ident['task_equals_dispatch_digest'] = raw['task'] == config['task_raw_digest']
        if not ident['task_equals_dispatch_digest']:
            problems.append('TASK_CHANGED_SINCE_DISPATCH')
        ident['raw_digests_equal_config'] = raw['task'] == 'sha256:' + arts['task']['sha256'] and raw['result'] == 'sha256:' + arts['result']['sha256']
        if not ident['raw_digests_equal_config']:
            problems.append('RAW_DIGEST_DIFFERS_FROM_CONFIG')
        binding = {k: v for k, v in cp['result']['binding'].items() if k != 'outputs'}
        ident['result_binding_equals_dispatch_stub_before_outputs'] = binding == config['binding_stub']
        if not ident['result_binding_equals_dispatch_stub_before_outputs']:
            problems.append('BINDING_DIFFERS_FROM_DISPATCH_STUB')
        art = cp['result']['artifacts']
        if cp['result']['binding'].get('outputs') != art:
            problems.append('BINDING_OUTPUTS_NOT_ARTIFACTS')
        if len(art) != 1 or art[0].get('path') != config['candidate_rel']:
            problems.append('ARTIFACT_NOT_DISPATCHED_CANDIDATE')
        if len(art) == 1:
            ident['candidate'] = {'path': art[0]['path'], 'digest': art[0]['digest'], 'role': art[0].get('role'),
                                  'size': len(cp['candidate']) if cp.get('candidate') is not None else None}
            if art[0]['digest'] != 'sha256:' + arts['candidate']['sha256'] or ident['candidate']['size'] != arts['candidate']['size']:
                problems.append('CANDIDATE_IDENTITY_DIFFERS_FROM_CONFIG')
    elif not problems:
        problems.append('CHECKPOINT_RETURNED_NO_RAW')
    tree_after = tree(lab)
    snapshot = {'digest_before': tree_digest(tree_before), 'digest_after': tree_digest(tree_after), 'files': len(tree_after['files']), 'dirs': len(tree_after['dirs']),
                'equal': tree_after == tree_before}
    if not snapshot['equal']:
        problems.append('LAB_TREE_CHANGED_DURING_CHECKPOINT')
    return {'op': op, 'refused_before_operation': False, 'limits': LIMITS, 'ok': not problems, 'verdict': 'HOLD' if problems else 'CHECKED_NOT_PASS', 'problems': problems,
            'identity': ident, 'ledger_snapshot': cp.get('ledger_snapshot'), 'policy': policy_view, 'lab_snapshot': snapshot,
            'bridge': {'config_sha256': EXPECTED_CONFIG_SHA256, 'manifest_sha256': config.get('manifest_sha256'),
                       'pinned_files': len(manifest.get('files', {}))},
            'note': 'problems rỗng = bytes/binding/ledger khớp theo recipe; không PASS, không quyền, không nghiệm thu nội dung, không publish'}


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(argv) != 2 or argv[1] != 'checkpoint':
        print(json.dumps(refuse('?', ['USAGE checkpoint']), ensure_ascii=True))
        return 2
    out = run('checkpoint')
    print(json.dumps(out, ensure_ascii=True, indent=2, sort_keys=False, default=str))
    return 0 if out.get('ok') else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
