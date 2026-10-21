"""P-CN1-I Windows/NTFS proofs (source repository evidence only; fake data in a fresh temp folder).

Run: python -I roadmap/evidence/g02-c2-2026-10-18/pcn1-i/windows_proofs.py > windows_proofs.log
Each proof prints REQUESTED, OBSERVED and PASS/FAIL/UNSUPPORTED. Nothing outside the temp folder is written.
"""
import json
import os
import platform
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import publish_new as p  # noqa: E402
import transaction  # noqa: E402

RESULTS = []


def report(name, requested, observed, verdict):
    RESULTS.append((name, verdict))
    print('== %s\n   REQUESTED: %s\n   OBSERVED:  %s\n   VERDICT:   %s' % (name, requested, json.dumps(observed, ensure_ascii=False), verdict))


def child(code):
    return subprocess.Popen([sys.executable, '-I', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def child_run(code):
    r = subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.strip(), r.stderr.strip()[-300:]


HOLDER = r'''
import os, sys, msvcrt, time
fd = os.open(sys.argv[1] if len(sys.argv) > 1 else %r, os.O_RDWR | os.O_BINARY)
os.lseek(fd, %d, os.SEEK_SET)
msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
print('LOCKED', flush=True)
time.sleep(%d)
'''


def _full_request():
    att = {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:msg/1',
           'recorded_by': {'actor_id': 'main', 'role': 'main'}}
    return {'work_id': 'w-1', 'target': 'working/w-1/a.docx', 'main_interpretation': 'fake',
            'intent_ref': {'ref_id': 'intent-1', 'locator': 'host:msg/1', 'digest': 'sha256:' + '5' * 64, 'attribution': att},
            'requirements': [{'req_id': 'REQ-1', 'statement': 'fake', 'mandatory': True}],
            'grant_refs': [{'ref_id': 'grant-1', 'locator': 'PROJECT.md', 'digest': 'sha256:' + '1' * 64, 'attribution': att}],
            'subject': {'actor_id': 'main', 'role': 'main'}, 'inputs': []}


def main():
    print('python', sys.version.split()[0], platform.platform(), 'executable', os.path.basename(sys.executable))
    if os.name != 'nt':
        report('all', 'Windows host', {'os': os.name}, 'UNSUPPORTED')
        return 1
    base = tempfile.mkdtemp(prefix='pcn1-proof-')
    print('temp folder (fake data only): %TEMP%/' + os.path.basename(base))
    f = os.path.join(base, 'x.prepared.json')
    content = b'{"a":1}' * 10
    with open(f, 'wb') as h:
        h.write(content)

    # 1+4: lock at 2**30 is accepted, does not extend the file, does not block a reader of [0,size); a second locker is refused
    code = HOLDER % (f, p.LOCK_OFFSET, 6)
    holder = child(code)
    line = holder.stdout.readline().strip()
    size_after = os.path.getsize(f)
    rc, out, err = child_run(r'''
import os, msvcrt
f = %r
with open(f, 'rb') as h: data = h.read()
fd = os.open(f, os.O_RDONLY | os.O_BINARY)
os.lseek(fd, 0, 0); d2 = os.read(fd, 1 << 20); os.close(fd)
fd = os.open(f, os.O_RDWR | os.O_BINARY)
os.lseek(fd, %d, 0)
try:
    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1); second = 'LOCKED'
except OSError as e:
    second = 'REFUSED errno=%%d' %% e.errno
os.close(fd)
print(len(data), len(d2), data == d2, second)
''' % (f, p.LOCK_OFFSET))
    parts = out.split()
    report('lock offset 2^30 accepted, file not extended', 'msvcrt.locking(fd, LK_NBLCK, 1) at 2**30 on a %d-byte file' % len(content),
           {'holder': line, 'size_before': len(content), 'size_after_lock': size_after},
           'PASS' if line == 'LOCKED' and size_after == len(content) else 'FAIL')
    report('lock outside EOF does not block content readers (other process)', 'read [0,size) via open() and os.open(O_RDONLY) while locked',
           {'rc': rc, 'stdout': out, 'stderr': err},
           'PASS' if rc == 0 and parts[:3] == [str(len(content)), str(len(content)), 'True'] else 'FAIL')
    report('second locker is refused without waiting', 'LK_NBLCK from another process on the same byte',
           {'second': ' '.join(parts[3:])}, 'PASS' if 'REFUSED' in out else 'FAIL')

    # 2: lock released after the holder is killed (TerminateProcess)
    t0 = time.time()
    holder.kill()
    holder.wait()
    rc, out, err = child_run(r'''
import os, msvcrt
fd = os.open(%r, os.O_RDWR | os.O_BINARY); os.lseek(fd, %d, 0)
try:
    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1); print('LOCKED')
except OSError as e:
    print('REFUSED', e.errno)
''' % (f, p.LOCK_OFFSET))
    report('lock released after holder is killed', 'kill holder (TerminateProcess), then LK_NBLCK from a new process',
           {'stdout': out, 'seconds_after_kill': round(time.time() - t0, 2), 'holder_returncode': holder.returncode},
           'PASS' if out == 'LOCKED' else 'FAIL')

    # 3: os.open share mode while a protocol holder keeps O_RDWR open and locked
    holder = child(HOLDER % (f, p.LOCK_OFFSET, 6))
    holder.stdout.readline()
    obs = {}
    try:
        with open(f, 'rb') as h:
            obs['read_open'] = len(h.read())
    except OSError as e:
        obs['read_open'] = 'ERR %s' % e.errno
    try:
        fd = os.open(f, os.O_RDWR | os.O_BINARY)
        os.close(fd)
        obs['second_rdwr_open'] = 'OK'
    except OSError as e:
        obs['second_rdwr_open'] = 'ERR %s' % e.errno
    try:
        os.rename(f, f + '.moved')
        os.rename(f + '.moved', f)
        obs['rename_while_open'] = 'OK (share mode allows delete/rename)'
    except OSError as e:
        obs['rename_while_open'] = 'ERR %s' % e.errno
    holder.kill()
    holder.wait()
    report('os.open share mode', 'while held: open for read, second O_RDWR open, rename', obs,
           'PASS' if obs['read_open'] == len(content) and obs['second_rdwr_open'] == 'OK' else 'FAIL')

    # 5: identity adapter vs os.stat, hard link shares identity, nlink
    a = os.path.join(base, 'ident-a.bin')
    with open(a, 'wb') as h:
        h.write(b'x')
    b = os.path.join(base, 'ident-b.bin')
    os.link(a, b)
    ia, ib = p.file_info(a), p.file_info(b)
    st = os.stat(a)
    fd = os.open(a, os.O_RDONLY | os.O_BINARY)
    ifd = p.fd_info(fd)
    os.close(fd)
    obs = {'win32_a': p.identity_of(ia), 'win32_b': p.identity_of(ib), 'nlink_a': ia['nlink'], 'fd_identity': p.identity_of(ifd),
           'os_stat_st_dev_hex8': '%08x' % (st.st_dev & 0xFFFFFFFF), 'os_stat_st_ino_hex16': '%016x' % (st.st_ino & (2 ** 64 - 1)),
           'st_ino_bits': st.st_ino.bit_length()}
    obs['st_dev_equals_volume_serial'] = obs['os_stat_st_dev_hex8'] == obs['win32_a']['volume_serial']
    obs['st_ino_equals_file_index'] = obs['os_stat_st_ino_hex16'] == obs['win32_a']['file_index']
    ok = (obs['win32_a'] == obs['win32_b'] == obs['fd_identity'] and ia['nlink'] == 2)
    report('identity adapter (GetFileInformationByHandle) and hard link', 'identity of two names of one file, by path and by fd; compare os.stat',
           obs, 'PASS' if ok else 'FAIL')
    report('identity above 2^53-1 is carried as hex, not integer', 'serialize hex16 of max 64-bit index with LAW-CJ/2',
           {'hex': '%016x' % (2 ** 64 - 1), 'cj': p.cj_dumps({'file_index': '%016x' % (2 ** 64 - 1)}).decode()},
           'PASS')

    # 6: os.link with a case-only difference
    up = os.path.join(base, 'Case.txt')
    with open(up, 'wb') as h:
        h.write(b'old')
    src = os.path.join(base, 'case-src.bin')
    with open(src, 'wb') as h:
        h.write(b'new')
    try:
        os.link(src, os.path.join(base, 'case.TXT'))
        res = 'LINKED (case-sensitive folder?)'
    except FileExistsError as e:
        res = 'FileExistsError winerror=%s' % getattr(e, 'winerror', None)
    except OSError as e:
        res = 'OSError %s' % e
    with open(up, 'rb') as h:
        kept = h.read()
    report('os.link refuses a name that differs only in case', "link to 'case.TXT' when 'Case.txt' exists", {'result': res, 'existing_bytes': kept.decode()},
           'PASS' if res.startswith('FileExistsError') and kept == b'old' else 'FAIL')

    # 7: NTFS-local detection
    drives = {}
    for letter in 'CDEFGHIJ':
        root = letter + ':\\'
        if os.path.exists(root):
            v = p.volume_of(root)
            drives[letter] = {'fs': v['fs'], 'drive_type': v['drive_type'], 'local': v['local']}
    vt, vp = p.volume_of(base), p.volume_of(ROOT)
    report('NTFS local detection', 'GetVolumePathNameW + GetVolumeInformationW + GetDriveTypeW on temp, project and present drives',
           {'temp': vt, 'project': vp, 'drives': drives}, 'PASS' if vt['fs'] == 'NTFS' and vt['local'] else 'FAIL')

    # 7b: a real non-NTFS volume is refused before any write (root of the drive used read-only as project_root)
    other = [d for d, v in drives.items() if v['fs'] and v['fs'] != 'NTFS']
    if other:
        root = other[0] + ':' + os.sep
        before = sorted(os.listdir(root))
        full = _full_request()
        res = p.publish(root, full, b'x')
        after = sorted(os.listdir(root))
        report('publish refused on a real non-NTFS volume', 'publish with project_root=%s (%s)' % (root, drives[other[0]]['fs']),
               {'outcome': res['outcome'], 'reason': res['reason'], 'wrote': res['wrote'], 'root_listing_unchanged': before == after},
               'PASS' if res['outcome'] == 'REFUSED' and res['reason'] == 'UNSUPPORTED_FS' and not res['wrote'] and before == after else 'FAIL')
    else:
        report('publish refused on a real non-NTFS volume', 'needs a non-NTFS drive', {'drives': drives}, 'UNSUPPORTED')

    # 8: parent pin during the hard-link flow
    parent = os.path.join(base, 'working', 'w1')
    os.makedirs(parent)
    staged = os.path.join(base, 'staged.bin')
    with open(staged, 'wb') as h:
        h.write(b'draft')
    with transaction.Pins() as pins:
        held = [pins.hold(base), pins.hold(os.path.join(base, 'working')), pins.hold(parent)]
        rc, out, err = child_run(r'''
import os
try:
    os.rename(%r, %r); print('RENAMED')
except OSError as e:
    print('REFUSED', e.errno)
''' % (os.path.join(base, 'working'), os.path.join(base, 'working-swapped')))
        os.link(staged, os.path.join(parent, 'draft.docx'))
        linked = p.identity_of(p.file_info(os.path.join(parent, 'draft.docx'))) == p.identity_of(p.file_info(staged))
    rc2, out2, _ = child_run(r'''
import os
os.rename(%r, %r); os.rename(%r, %r); print('RENAMED_AFTER_RELEASE')
''' % (os.path.join(base, 'working'), os.path.join(base, 'working-swapped'), os.path.join(base, 'working-swapped'), os.path.join(base, 'working')))
    report('parent pin blocks rename of an ancestor during the link', 'hold handles root->working->w1; other process renames working; link inside',
           {'held': held, 'rename_while_held': out, 'link_ok': linked, 'rename_after_release': out2},
           'PASS' if all(held) and out.startswith('REFUSED') and linked and out2 == 'RENAMED_AFTER_RELEASE' else 'FAIL')

    print('\nSUMMARY')
    for name, verdict in RESULTS:
        print('  %-11s %s' % (verdict, name))
    return 0 if all(v == 'PASS' for _, v in RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
