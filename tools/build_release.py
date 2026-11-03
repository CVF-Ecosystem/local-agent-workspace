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
Profile `.agent/EXECUTION_PROFILE.json` luôn giao ở dạng mẫu sạch (owner PROFILE, không lựa chọn, không grant), kể cả khi kho nguồn có profile riêng,
và không nằm trong MANIFEST; schema và helper là file package thường.
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
BEHAVIOUR_TEST_TIMEOUT_S = 1800
GATE_LABEL = {'passed': 'đạt', 'failed': 'lỗi', 'skipped': 'bỏ qua', 'nested': 'lồng nhau'}

def copy_release_tree(stage, branding=True):
    """Ghi bản giao vào cây tạm bằng projection chung của check_package (cùng file, cùng bytes với new/adopt): mẫu sạch PROJECT/STATE/HANDOFF,
    `.cvf` chỉ closure v3, phép thay tham chiếu. Trả về (file, file nhận diện). MANIFEST do bước `--write-manifest` trong cây tạm tính trên bytes thực giao.
    Writes the shipped bytes via the shared projection; the MANIFEST is computed afterwards from the bytes that actually ship."""
    brand = set(cp.branding_files()) | {'assets/branding.js'}
    files = cp.materialize(stage, branding=branding, manifest=False)
    return files, (sorted(set(files) & brand) if branding else [])

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

def run_behaviour_child(events_path):
    """Observe the ordinary unittest discovery/run without replacing its oracle.

    These hooks are process-local. Unknown phases remain explicit if a custom TestCase
    bypasses the standard hooks. Raw stdout/stderr are owned by the parent launcher.
    """
    import unittest
    trace = open(events_path, 'a', encoding='utf-8', buffering=1)
    clock, dumps, getpid = time.monotonic, json.dumps, os.getpid
    now, utc = datetime.datetime.now, datetime.timezone.utc
    utcnow = lambda: now(utc).isoformat()
    started = clock()

    def event(kind, **fields):
        fields.update(event=kind, pid=getpid(), elapsed_s=round(clock() - started, 6),
                      utc=utcnow())
        trace.write(dumps(fields, ensure_ascii=True) + '\n')
        trace.flush()

    class Result(unittest.TextTestResult):
        def startTest(self, test):
            self._gate_started = clock()
            self._gate_outcome = 'UNKNOWN'
            event('test_start', test=test.id())
            super().startTest(test)

        def stopTest(self, test):
            super().stopTest(test)
            event('test_end', test=test.id(), outcome=self._gate_outcome,
                  duration_s=round(clock() - self._gate_started, 6))

    def outcome_hook(name, outcome):
        original = getattr(unittest.TextTestResult, name)
        def observed(self, test, *args, **kwargs):
            # Fixture errors have no startTest/stopTest; preserve them as distinct events.
            event('outcome', test=test.id(), outcome=outcome)
            self._gate_outcome = outcome
            return original(self, test, *args, **kwargs)
        setattr(Result, name, observed)

    for name, outcome in [('addSuccess', 'success'), ('addFailure', 'failure'),
                          ('addError', 'error'), ('addSkip', 'skip'),
                          ('addExpectedFailure', 'expected_failure'),
                          ('addUnexpectedSuccess', 'unexpected_success')]:
        outcome_hook(name, outcome)
    original_subtest = unittest.TextTestResult.addSubTest
    def subtest(self, test, subtest, err):
        if err is not None:
            self._gate_outcome = 'failure' if issubclass(err[0], test.failureException) else 'error'
            event('outcome', test=test.id(), outcome=self._gate_outcome, subtest=True)
        return original_subtest(self, test, subtest, err)
    Result.addSubTest = subtest

    def phase_hook(owner, name, phase):
        original = getattr(owner, name)
        def observed(self, *args, **kwargs):
            identity = self.id() if isinstance(self, unittest.TestCase) else None
            event('phase_start', phase=phase, test=identity)
            begin = clock()
            try:
                return original(self, *args, **kwargs)
            finally:
                event('phase_end', phase=phase, test=identity,
                      duration_s=round(clock() - begin, 6))
        setattr(owner, name, observed)

    for name, phase in [('_callSetUp', 'test_setup'), ('_callTestMethod', 'test_body'),
                        ('_callTearDown', 'test_teardown'), ('doCleanups', 'test_cleanup')]:
        phase_hook(unittest.TestCase, name, phase)
    for name, phase in [('_handleModuleFixture', 'module_fixture'),
                        ('_handleClassSetUp', 'class_setup'),
                        ('_tearDownPreviousClass', 'class_teardown'),
                        ('_handleModuleTearDown', 'module_teardown')]:
        phase_hook(unittest.TestSuite, name, phase)
    phase_hook(unittest.TestLoader, 'discover', 'discovery')
    event('suite_start', phase='discovery')
    try:
        unittest.main(module=None, argv=['python -m unittest', 'discover', '-s', 'tests', '-v'],
                      testRunner=unittest.TextTestRunner(verbosity=2, resultclass=Result))
    finally:
        event('suite_exit')
        trace.close()


def _behaviour_trace_event(path, kind, **fields):
    fields.update(event=kind, pid=os.getpid(), utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with open(path, 'a', encoding='utf-8') as trace:
        trace.write(json.dumps(fields, ensure_ascii=True) + '\n')
        trace.flush()


def gate_behaviour_tests():
    if not os.path.isdir(cp.P('tests')):
        return gate_result('skipped', 'không có thư mục tests/ (không phải kho nguồn)')
    if os.environ.get(GATE_ENV) == '1':
        return gate_result('nested', 'build lồng trong bộ kiểm thử; tiến trình cha đã chạy bộ kiểm thử')
    env = dict(os.environ, PYTHONUTF8='1', PYTHONUNBUFFERED='1', **{GATE_ENV: '1'})
    # Unique persistent diagnostics: no cleanup-on-exit and no caller-controlled log names.
    diagnostic = tempfile.mkdtemp(prefix='local-agent-behaviour-')
    events = os.path.join(diagnostic, 'events.jsonl')
    outpath, errpath = (os.path.join(diagnostic, name) for name in ('stdout.log', 'stderr.log'))
    bootstrap = ('import sys; sys.path.insert(0, %r); import build_release; '
                 'build_release.run_behaviour_child(%r)') % (HERE, events)
    command = [sys.executable, '-B', '-c', bootstrap]
    begin, timed_out = time.monotonic(), False
    _behaviour_trace_event(events, 'parent_start', timeout_s=BEHAVIOUR_TEST_TIMEOUT_S)
    with open(outpath, 'xb') as stdout, open(errpath, 'xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
        _behaviour_trace_event(events, 'spawn', child_pid=child.pid)
        try:
            code = child.wait(timeout=BEHAVIOUR_TEST_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            timed_out = True
            child.kill()
            code = child.wait()
    # The exact child has exited. Descendant state is not inferred from its exit.
    active, current = [], None
    with open(events, encoding='utf-8') as trace:
        for line in trace:
            try:
                record = json.loads(line)
            except ValueError:
                continue  # abrupt termination may leave a final partial record
            kind = record.get('event')
            if kind == 'test_start':
                current = record.get('test')
            elif kind == 'test_end':
                current = None
            elif kind == 'phase_start':
                active.append(record.get('phase'))
            elif kind == 'phase_end' and active:
                active.pop()
    _behaviour_trace_event(events, 'parent_end', child_pid=child.pid, returncode=code,
                          timed_out=timed_out, elapsed_s=round(time.monotonic() - begin, 6),
                          current_unfinished=current, phase=active[-1] if active else 'UNKNOWN',
                          descendants='UNKNOWN')
    # Stream the durable raw files; keep only the existing bounded error tail in memory.
    from collections import deque
    tail, ran, last, skips, test_label = deque(maxlen=40), '', '', [], ''
    for path in (outpath, errpath):
        with open(path, encoding='utf-8', errors='replace') as raw:
            for line in raw:
                line = line.rstrip('\r\n')
                if not line.strip():
                    continue
                tail.append(line)
                last = line
                if line.startswith('Ran '):
                    ran = line
                if line.startswith('test') and ' (' in line:
                    test_label = line.split(' ... ', 1)[0]
                if '... skipped ' in line:
                    skips.append(line if line.startswith('test') else test_label + ' | ' + line)
    reference = '; diagnostics (internal raw stdout/stderr/events): ' + diagnostic
    if timed_out:
        errors = ['Partial output — unfinished test run; not a complete summary:'] + list(tail)
        return gate_result('failed', 'quá %d giây' % BEHAVIOUR_TEST_TIMEOUT_S + reference, errors)
    detail = ('%s; %s' % (ran, last)).strip('; ')
    if skips:
        detail += '; skipped tests:\n' + '\n'.join(skips)
    if code == 0:
        return gate_result('passed', detail + reference)
    return gate_result('failed', 'mã thoát %d; %s' % (code, detail) + reference, list(tail))

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
        try:
            files, brand = copy_release_tree(stage, branding=not a.no_branding)
        except cp.ProjectionError as e:
            fail(a, 1, 'Không đóng gói: nguồn hoặc projection giao đi bất thường (%s). Không tạo ZIP.' % e, status='error',
                 findings=[{'severity': 'error', 'message': 'projection: %s' % e}], unchecked=unchecked_items(records))
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
        try:
            projected = cp.delivery_manifest(files, branding=not a.no_branding)
        except cp.ProjectionError as e:
            fail(a, 1, 'Không đóng gói: không dựng được MANIFEST theo projection (%s).' % e, status='error')
        with open(os.path.join(stage, 'MANIFEST.sha256'), 'rb') as mf:
            if mf.read() != projected:  # hai đường tính MANIFEST phải ra cùng bytes / both ways of computing the MANIFEST must agree
                fail(a, 1, 'Không đóng gói: MANIFEST trong cây tạm lệch MANIFEST tính từ projection.', status='error',
                     findings=[{'severity': 'error', 'message': 'manifest: cây tạm lệch projection'}])
        files.append('MANIFEST.sha256')
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            for rel in sorted(files):
                path = os.path.join(stage, *rel.split('/'))
                data = open(path, 'rb').read()
                if os.path.splitext(rel)[1] in cp.TEXT_EXT and rel not in cp.BYTE_EXACT + cp.CVF_MACHINE + cp.CVF_DEPENDENCIES:  # critical runtime bytes ship verbatim
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
