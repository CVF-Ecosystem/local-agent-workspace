#!/usr/bin/env python3
"""Dựng ZIP phát hành trong thư mục tạm, không sửa working tree. Chỉ cần Python 3.8+.

Dùng (từ thư mục gốc của package nguồn):
  python tools/build_release.py [--out dist] [--skip-check]

Các bước: kiểm nguồn và mẫu phát hành -> dựng cây tạm -> chép PROJECT/STATE/HANDOFF sạch từ
`release_templates/` -> tạo manifest trong cây tạm -> đóng ZIP -> giải nén và chạy `--verify`.
"""
import argparse, os, shutil, subprocess, sys, tempfile, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_package as cp  # noqa: E402
from result_schema import emit, make  # noqa: E402

TEMPLATE_OVERLAYS = {
    'PROJECT.md': 'release_templates/PROJECT.md',
    '.agent/STATE.md': 'release_templates/.agent/STATE.md',
    '.agent/HANDOFF.md': 'release_templates/.agent/HANDOFF.md',
    'en/PROJECT.md': 'release_templates/en/PROJECT.md',
    'en/.agent/STATE.md': 'release_templates/en/.agent/STATE.md',
    'en/.agent/HANDOFF.md': 'release_templates/en/.agent/HANDOFF.md',
}

def copy_release_tree(stage):
    files = [f for f in cp.all_files() if f not in ('.agent/PACKAGE_INFO.json', '.agent/MERGE_STATUS.json', 'MANIFEST.sha256')
             and (cp.in_manifest(f) or f in cp.USER_FILES)]
    for rel in files:
        dst = os.path.join(stage, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(cp.P(rel), dst)
    for rel, src in TEMPLATE_OVERLAYS.items():
        dst = os.path.join(stage, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(cp.P(src), dst)
    return files

def run_stage(stage, *args):
    return subprocess.run([sys.executable, os.path.join(stage, 'tools', 'check_package.py')] + list(args),
                          capture_output=True, cwd=stage, env=dict(os.environ, PYTHONUTF8='1'))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='dist')
    ap.add_argument('--skip-check', action='store_true')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ver = cp.rd('VERSION').strip()
    if not a.skip_check:
        errs, warns = cp.check_all(release=True)
        for w in warns: print('Cảnh báo: ' + w)
        if errs:
            for e in errs: print('LỖI: ' + e)
            sys.exit('Không đóng gói: package chưa đạt kiểm tra (%d lỗi).' % len(errs))
    top = 'local-agent-workspace-v%s' % ver
    out_dir = os.path.join(ROOT, a.out)
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, top + '.zip')
    with tempfile.TemporaryDirectory(prefix='local-agent-release-') as stage:
        files = copy_release_tree(stage)
        checked = run_stage(stage, '--release')
        if checked.returncode:
            sys.stdout.write((checked.stdout + checked.stderr).decode('utf-8', 'replace'))
            sys.exit('Không đóng gói: cây phát hành tạm chưa đạt kiểm tra.')
        written = run_stage(stage, '--write-manifest')
        if written.returncode:
            sys.stdout.write((written.stdout + written.stderr).decode('utf-8', 'replace'))
            sys.exit('Không tạo được manifest trong cây phát hành tạm.')
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
            sys.exit('ZIP không khớp MANIFEST sau khi giải nén.')
    digest = hashlib.sha256(open(zpath, 'rb').read()).hexdigest()
    try:
        shown_path = os.path.relpath(zpath, ROOT)
    except ValueError:  # Windows: output can be on a different drive.
        shown_path = os.path.abspath(zpath)
    print('Đã tạo %s (%d file, %.0f KB)\nSHA-256: %s' % (shown_path, len(files), os.path.getsize(zpath) / 1024, digest))
    if a.result_json:
        emit(make('success', message='Release archive created', changes=True,
                  files=[{'path': os.path.abspath(zpath), 'action': 'created'}],
                  archive=os.path.abspath(zpath), sha256=digest, file_count=len(files)))

if __name__ == '__main__':
    main()
