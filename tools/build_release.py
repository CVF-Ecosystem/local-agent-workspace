#!/usr/bin/env python3
"""Cổng chất lượng rồi dựng ZIP phát hành trong thư mục tạm, không sửa working tree. Chỉ cần Python 3.8+.

Dùng (từ thư mục gốc của package nguồn):
  python tools/build_release.py                      bản chính thức: chạy đủ cổng rồi đóng ZIP
  python tools/build_release.py --rc N               release candidate N: local-agent-workspace-v<VERSION>-rcN.zip
  python tools/build_release.py --rc N --skip-check  RC không chạy cổng (báo cáo ghi `skipped`); bản chính thức không được dùng cờ này

Cổng bắt buộc, chạy trước khi đóng gói. Không có ZIP nào được tạo khi một cổng ở trạng thái `failed`:
  package_check    check_package --release: cấu trúc, mẫu phát hành, song ngữ, phiên bản, và HTML khớp Markdown
  python38_compat  kiểm gần đúng tương thích Python 3.8 (heuristic, xem check_package.py)
  behaviour_tests  python -B -m unittest discover -s tests; chỉ áp dụng khi có thư mục tests/ (kho nguồn)
  release_tree     check_package --release trên cây phát hành tạm; luôn chạy, kể cả với --skip-check

Build lồng nhau: khi cổng behaviour_tests chạy bộ kiểm thử, nó đặt LOCAL_AGENT_WORKSPACE_GATE_NESTED=1.
Build được gọi bên trong bộ kiểm thử với biến này chỉ bỏ qua đúng cổng behaviour_tests và ghi `nested`
(tránh đệ quy); các cổng khác vẫn chạy. `nested` không phải `passed`: tiến trình cha đã chạy bộ kiểm thử.

Báo cáo cổng: <ZIP>.gate.json (schema local-agent-workspace/release-gate-v1), chỉ ghi khi ZIP được tạo.
Các bước sau cổng: dựng cây tạm -> chép PROJECT/STATE/HANDOFF sạch từ `release_templates/` -> tạo manifest
trong cây tạm -> kèm nhận diện đơn vị trong assets/ (logo, branding.json, font; bỏ bằng --no-branding) -> đóng ZIP (không có timestamp, byte-reproducible) -> giải nén và chạy `--verify`.
Mã thoát: 0 thành công; 1 cổng không đạt hoặc lỗi đóng gói; 2 lỗi dùng (ví dụ --skip-check không kèm --rc).
"""
import argparse, datetime, hashlib, io, json, os, platform, shutil, subprocess, sys, tempfile, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_package as cp  # noqa: E402
from result_schema import emit, make  # noqa: E402

GATE_ENV = 'LOCAL_AGENT_WORKSPACE_GATE_NESTED'
GATE_SCHEMA = 'local-agent-workspace/release-gate-v1'
GATE_LABEL = {'passed': 'đạt', 'failed': 'lỗi', 'skipped': 'bỏ qua', 'nested': 'lồng nhau'}

TEMPLATE_OVERLAYS = {
    'PROJECT.md': 'release_templates/PROJECT.md',
    '.agent/STATE.md': 'release_templates/.agent/STATE.md',
    '.agent/HANDOFF.md': 'release_templates/.agent/HANDOFF.md',
    'en/PROJECT.md': 'release_templates/en/PROJECT.md',
    'en/.agent/STATE.md': 'release_templates/en/.agent/STATE.md',
    'en/.agent/HANDOFF.md': 'release_templates/en/.agent/HANDOFF.md',
}

def copy_release_tree(stage, branding=True):
    """Chép file package (và nhận diện đơn vị trong assets/ khi branding=True) vào cây tạm. Trả về (file, file nhận diện)."""
    brand = cp.branding_files() if branding else []
    files = [f for f in cp.all_files() if f not in ('.agent/PACKAGE_INFO.json', '.agent/MERGE_STATUS.json', 'MANIFEST.sha256')
             and (cp.in_manifest(f) or f in cp.USER_FILES or f in brand)]
    for rel in files:
        dst = os.path.join(stage, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(cp.P(rel), dst)
    for rel, src in TEMPLATE_OVERLAYS.items():
        dst = os.path.join(stage, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(cp.P(src), dst)
    if brand:  # branding.js dựng lại từ branding.json để trang hướng dẫn trong ZIP đúng ngay / rebuilt so the guides are right on unzip
        js = cp.branding_js()
        js_path = os.path.join(stage, 'assets', 'branding.js')
        if js:
            os.makedirs(os.path.dirname(js_path), exist_ok=True)
            with io.open(js_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(js)
            if 'assets/branding.js' not in files:
                files.append('assets/branding.js')
                brand.append('assets/branding.js')
    return files, sorted(brand)

def run_stage(stage, *args):
    return subprocess.run([sys.executable, os.path.join(stage, 'tools', 'check_package.py')] + list(args),
                          capture_output=True, cwd=stage, env=dict(os.environ, PYTHONUTF8='1'))

# ---------------------------------------------------------------- cổng chất lượng
def gate_result(status, detail, errors=(), warnings=()):
    return {'status': status, 'detail': detail, 'errors': list(errors), 'warnings': list(warnings)}

def gate_package_check():
    errs, warns = cp.check_all(release=True)
    detail = '%d lỗi, %d cảnh báo (gồm đồng bộ HTML với Markdown)' % (len(errs), len(warns))
    return gate_result('failed' if errs else 'passed', detail, errs, warns)

def gate_python38():
    errs = cp.check_py38()
    return gate_result('failed' if errs else 'passed', '%d vấn đề (heuristic, xem check_package.py)' % len(errs), errs)

def gate_behaviour_tests():
    if not os.path.isdir(cp.P('tests')):
        return gate_result('skipped', 'không có thư mục tests/ (không phải kho nguồn)')
    if os.environ.get(GATE_ENV) == '1':
        return gate_result('nested', 'build lồng trong bộ kiểm thử; tiến trình cha đã chạy bộ kiểm thử')
    env = dict(os.environ, PYTHONUTF8='1', **{GATE_ENV: '1'})
    try:
        r = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests'],
                           cwd=ROOT, env=env, capture_output=True, timeout=900)
    except subprocess.TimeoutExpired:
        return gate_result('failed', 'quá 900 giây')
    lines = [l for l in (r.stdout + r.stderr).decode('utf-8', 'replace').splitlines() if l.strip()]
    ran = next((l for l in lines if l.startswith('Ran ')), '')
    detail = ('%s; %s' % (ran, lines[-1] if lines else '')).strip('; ')
    if r.returncode == 0:
        return gate_result('passed', detail)
    return gate_result('failed', 'mã thoát %d; %s' % (r.returncode, detail), lines[-40:])

def run_gates(skip):
    """Chạy các cổng theo thứ tự. Trả về (bản ghi cho báo cáo, chi tiết lỗi theo tên cổng)."""
    specs = (('package_check', gate_package_check), ('python38_compat', gate_python38),
             ('behaviour_tests', gate_behaviour_tests))
    records, details = [], {}
    for name, fn in specs:
        t0 = time.perf_counter()
        res = gate_result('skipped', '--skip-check (chỉ dùng với --rc)') if skip else fn()
        records.append(gate_record(name, res, t0))
        details[name] = res
    return records, details

def gate_record(name, res, t0):
    return {'name': name, 'status': res['status'], 'duration_s': round(time.perf_counter() - t0, 2), 'detail': res['detail']}

# ---------------------------------------------------------------- báo cáo cổng
def git_state():
    """Commit và cờ dirty; None nếu không có git hoặc không phải kho git. Không bao giờ làm lỗi build."""
    try:
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, timeout=30)
        if head.returncode != 0:
            return None
        st = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    dirty = bool(st.stdout.strip()) if st.returncode == 0 else None
    return {'commit': head.stdout.decode('ascii', 'replace').strip(), 'dirty': dirty}

def write_gate_report(path, report):
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

# ---------------------------------------------------------------- đầu ra
def fail(a, code, message, status='blocked', findings=None, unchecked=None):
    """In thông báo; với --result-json, envelope có code trùng mã thoát rồi thoát với mã đó."""
    print(message)
    if a.result_json:
        emit(make(status, code=code, message=message, changes=False,
                  findings=findings or [], unchecked=unchecked or []))
    sys.exit(code)

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='dist')
    ap.add_argument('--rc', type=int, default=None, metavar='N',
                    help='dựng release candidate N: tên ZIP có -rcN (build release candidate N)')
    ap.add_argument('--skip-check', action='store_true',
                    help='bỏ qua các cổng, ghi skipped trong báo cáo; chỉ dùng với --rc (skip gates, --rc only)')
    ap.add_argument('--no-branding', action='store_true',
                    help='không kèm logo, tên đơn vị, font trong assets/ (leave organization branding out)')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.rc is not None and a.rc < 0:
        fail(a, 2, 'Không đóng gói: --rc phải là số không âm.', status='error',
             findings=[{'severity': 'error', 'message': '--rc phải là số không âm'}])
    if a.skip_check and a.rc is None:
        fail(a, 2, 'Không đóng gói: --skip-check chỉ được dùng với --rc N. Bản chính thức luôn chạy đủ cổng.',
             findings=[{'severity': 'error', 'message': '--skip-check bị từ chối khi không có --rc'}])
    ver = cp.rd('VERSION').strip()
    kind = 'official' if a.rc is None else 'rc'
    archive = 'local-agent-workspace-v%s%s.zip' % (ver, '' if a.rc is None else '-rc%d' % a.rc)
    top = 'local-agent-workspace-v%s' % ver
    out_dir = os.path.join(ROOT, a.out)
    zpath = os.path.join(out_dir, archive)
    rpath = zpath + '.gate.json'

    records, details = run_gates(a.skip_check)
    print('Cổng chất lượng / quality gates (%s):' % kind)
    for rec in records:
        print('  - %s: %s (%s)' % (rec['name'], GATE_LABEL[rec['status']], rec['detail']))
    for name in ('package_check', 'python38_compat'):
        for w in details[name]['warnings']: print('Cảnh báo: ' + w)
        for e in details[name]['errors']: print('LỖI: ' + e)
    for line in details['behaviour_tests']['errors']: print(line)
    failed = [r for r in records if r['status'] == 'failed']
    if failed:
        for old in (zpath, rpath):  # không để lại ZIP/báo cáo cũ cùng tên có thể bị phát hành nhầm / no stale archive
            if os.path.isfile(old):
                os.remove(old)
        names = ', '.join(r['name'] for r in failed)
        findings = [{'severity': 'error', 'message': '%s: %s' % (r['name'], r['detail'])} for r in failed]
        fail(a, 1, 'Không đóng gói: cổng bắt buộc chưa đạt (%s). Không tạo ZIP.' % names,
             findings=findings, unchecked=unchecked_items(records))

    os.makedirs(out_dir, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='local-agent-release-') as stage:
        files, brand = copy_release_tree(stage, branding=not a.no_branding)
        t0 = time.perf_counter()
        checked = run_stage(stage, '--release')
        stage_rec = {'name': 'release_tree', 'status': 'failed' if checked.returncode else 'passed',
                     'duration_s': round(time.perf_counter() - t0, 2),
                     'detail': 'check_package --release trên cây phát hành tạm'}
        records.append(stage_rec)
        if checked.returncode:
            sys.stdout.write((checked.stdout + checked.stderr).decode('utf-8', 'replace'))
            fail(a, 1, 'Không đóng gói: cây phát hành tạm chưa đạt kiểm tra (release_tree). Không tạo ZIP.',
                 findings=[{'severity': 'error', 'message': 'release_tree: check_package --release trên cây tạm chưa đạt'}],
                 unchecked=unchecked_items(records))
        written = run_stage(stage, '--write-manifest')
        if written.returncode:
            sys.stdout.write((written.stdout + written.stderr).decode('utf-8', 'replace'))
            fail(a, 1, 'Không tạo được manifest trong cây phát hành tạm.', status='error')
        files.append('MANIFEST.sha256')
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            for rel in sorted(files):
                path = os.path.join(stage, *rel.split('/'))
                data = open(path, 'rb').read()
                if os.path.splitext(rel)[1] in cp.TEXT_EXT:
                    data = data.replace(b'\r\n', b'\n')
                zi = zipfile.ZipInfo(top + '/' + rel, date_time=(1980, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = (0o755 if rel.endswith(('.py', '.command')) else 0o644) << 16
                z.writestr(zi, data)
    with tempfile.TemporaryDirectory(prefix='local-agent-verify-') as tmp:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        r = subprocess.run([sys.executable, os.path.join(tmp, top, 'tools', 'check_package.py'), '--verify'],
                           capture_output=True, cwd=os.path.join(tmp, top))
        out = r.stdout.decode('utf-8', 'replace')
        if r.returncode != 0:
            print(out)
            os.remove(zpath)  # ZIP lỗi không được để lại
            fail(a, 1, 'ZIP không khớp MANIFEST sau khi giải nén. Đã xóa ZIP.', status='error',
                 findings=[{'severity': 'error', 'message': 'verify: ZIP không khớp MANIFEST'}])
    digest = hashlib.sha256(open(zpath, 'rb').read()).hexdigest()
    report = {
        'schema': GATE_SCHEMA,
        'version': ver,
        'kind': kind,
        'rc': a.rc,
        'skip_check': a.skip_check,
        'archive': archive,
        'archive_sha256': digest,
        'branding': brand,
        'gates': [{k: r[k] for k in ('name', 'status', 'duration_s', 'detail')} for r in records],
        'platform': {'system': platform.system(), 'release': platform.release()},
        'python': platform.python_version(),
        'git': git_state(),
        'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    write_gate_report(rpath, report)
    try:
        shown_path = os.path.relpath(zpath, ROOT)
    except ValueError:  # Windows: output can be on a different drive.
        shown_path = os.path.abspath(zpath)
    print('Đã tạo %s (%d file, %.0f KB)\nSHA-256: %s' % (shown_path, len(files), os.path.getsize(zpath) / 1024, digest))
    print('Báo cáo cổng / gate report: %s' % os.path.basename(rpath))
    if brand:
        print('Kèm nhận diện đơn vị / organization branding included: %s (bỏ bằng --no-branding)' % ', '.join(brand))
    if a.result_json:
        emit(make('success', message='Release archive created (%s)' % kind, changes=True,
                  files=[{'path': os.path.abspath(zpath), 'action': 'created'},
                         {'path': os.path.abspath(rpath), 'action': 'created'}],
                  archive=os.path.abspath(zpath), sha256=digest, file_count=len(files),
                  kind=kind, gate_report=os.path.abspath(rpath), unchecked=unchecked_items(records)))

def unchecked_items(records):
    return [{'tool': 'build_release.py', 'gate': r['name'], 'reason': '%s: %s' % (GATE_LABEL[r['status']], r['detail'])}
            for r in records if r['status'] in ('skipped', 'nested')]

if __name__ == '__main__':
    main()
