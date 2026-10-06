#!/usr/bin/env python3
"""Đóng gói ZIP phát hành từ nguồn package. Chỉ cần Python 3.8+.

Dùng (từ thư mục gốc của package nguồn):
  python tools/build_release.py [--out dist] [--skip-check]

Các bước: kiểm `check_package.py --release` -> ghi MANIFEST.sha256 -> đóng ZIP (LF, thứ tự cố định,
không file project) -> giải nén thử vào thư mục tạm và chạy `--verify`.
"""
import argparse, io, os, subprocess, sys, tempfile, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_package as cp  # noqa: E402

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='dist')
    ap.add_argument('--skip-check', action='store_true')
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
    cp.write_manifest()
    top = 'local-agent-workspace-v%s' % ver
    out_dir = os.path.join(ROOT, a.out)
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, top + '.zip')
    files = [f for f in cp.all_files() if f != '.agent/PACKAGE_INFO.json'
             and (cp.in_manifest(f) or f in cp.USER_FILES or f == 'MANIFEST.sha256')]
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(files):
            data = open(cp.P(rel), 'rb').read()
            if os.path.splitext(rel)[1] in cp.TEXT_EXT:
                data = data.replace(b'\r\n', b'\n')
            zi = zipfile.ZipInfo(top + '/' + rel, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (0o755 if rel.endswith(('.py', '.command')) else 0o644) << 16
            z.writestr(zi, data)
    # kiểm lại: giải nén vào thư mục tạm và --verify
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        r = subprocess.run([sys.executable, os.path.join(tmp, top, 'tools', 'check_package.py'), '--verify'],
                           capture_output=True, cwd=os.path.join(tmp, top))
        out = r.stdout.decode('utf-8', 'replace')
        if r.returncode != 0:
            print(out)
            sys.exit('ZIP không khớp MANIFEST sau khi giải nén.')
    digest = hashlib.sha256(open(zpath, 'rb').read()).hexdigest()
    print('Đã tạo %s (%d file, %.0f KB)\nSHA-256: %s' % (os.path.relpath(zpath, ROOT), len(files), os.path.getsize(zpath) / 1024, digest))

if __name__ == '__main__':
    main()
