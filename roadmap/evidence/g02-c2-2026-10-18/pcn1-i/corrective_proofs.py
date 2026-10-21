"""P-CN1-I corrective: re-measure only the primitives the corrective changed. Fake data in a fresh temp folder.

Run: python -I roadmap/evidence/g02-c2-2026-10-18/pcn1-i/corrective_proofs.py
  1. delete through the verified handle: removes only that name of a hard-linked file; a second opener cannot
     remove/rename the object while the handle is open; a different file under the same name is reported CHANGED.
  2. folder pin + identity: a pinned folder cannot be removed/renamed (so cannot be replaced by a junction); a path that is
     already a junction is told apart from the folder the handle follows (file_info vs handle identity).
  3. root junction is seen as a reparse point by file_info (not by link_free).
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import publish_new as p  # noqa: E402
import transaction  # noqa: E402

RESULTS = []


def report(name, requested, observed, verdict):
    RESULTS.append((name, verdict))
    print('== %s\n   REQUESTED: %s\n   OBSERVED:  %s\n   VERDICT:   %s\n' % (name, requested, observed, verdict))


def junction(link, target):
    r = subprocess.run(['cmd', '/c', 'mklink', '/J', link, target], capture_output=True, text=True)
    return r.returncode == 0


def main():
    base = tempfile.mkdtemp(prefix='law-pcn1-corr-')
    try:
        # 1. delete through the verified handle
        staged, target = os.path.join(base, 'x.staged'), os.path.join(base, 'target.docx')
        with open(staged, 'wb') as h:
            h.write(b'draft bytes')
        os.link(staged, target)
        ident = p.identity_of(p.file_info(staged))
        other = os.path.join(base, 'other.bin')
        with open(other, 'wb') as h:
            h.write(b'other')
        changed = p._delete_exact(other, ident)
        blocked = {}
        real = p._fail_point

        def probe(point):
            if point == 'cleanup':
                for name, fn in (('remove', lambda: os.remove(staged)), ('rename', lambda: os.rename(staged, staged + '2'))):
                    try:
                        fn()
                        blocked[name] = 'NOT_BLOCKED'
                    except OSError as e:
                        blocked[name] = 'winerror %s' % e.winerror
            real(point)
        p._fail_point = probe
        try:
            done = p._delete_exact(staged, ident)
        finally:
            p._fail_point = real
        obs = {'different_file_same_name_check': changed, 'while_handle_open': blocked, 'delete': done,
               'staged_exists': os.path.exists(staged), 'hard_link_kept': os.path.exists(target) and open(target, 'rb').read() == b'draft bytes',
               'other_file_kept': os.path.exists(other)}
        report('delete through the verified handle', 'delete staged by handle; probe remove/rename while open; wrong identity',
               obs, 'PASS' if changed == 'CHANGED' and done == 'DELETED' and set(blocked.values()) == {'winerror 32'}
               and not obs['staged_exists'] and obs['hard_link_kept'] and obs['other_file_kept'] else 'FAIL')

        # 2. folder pin + identity
        work = os.path.join(base, 'working')
        os.mkdir(work)
        outside = os.path.join(base, 'outside')
        os.mkdir(outside)
        with transaction.Pins() as pins:
            held = p._PinSet(pins)
            state = held.pin(work)
            res = {}
            for name, fn in (('rmdir', lambda: os.rmdir(work)), ('rename', lambda: os.rename(work, work + '-moved'))):
                try:
                    fn()
                    res[name] = 'NOT_BLOCKED'
                except OSError as e:
                    res[name] = 'winerror %s' % e.winerror
        link = os.path.join(base, 'link')
        made = junction(link, outside)
        with transaction.Pins() as pins:
            state_link = p._PinSet(pins).pin(link) if made else 'NO_JUNCTION'
        info = p.file_info(link) if made else None
        report('folder pin proves the path is the held folder', 'pin a folder, try rmdir/rename; pin a junction path',
               {'pin': state, 'while_pinned': res, 'junction_pin': state_link,
                'junction_is_reparse': bool(info and info['attributes'] & 0x400)},
               'PASS' if state == 'OK' and set(res.values()) == {'winerror 32'} and state_link == 'UNSAFE'
               and info and info['attributes'] & 0x400 else 'FAIL')

        # 3. root junction
        rootlink = os.path.join(base, 'rootlink')
        made = junction(rootlink, work)
        report('root junction is detected', 'junction as project root', {'root_problem_plain': p._root_problem(work),
                                                                     'root_problem_junction': p._root_problem(rootlink),
                                                                     'link_free_sees_it': transaction.link_free(rootlink, rootlink)},
               'PASS' if made and p._root_problem(work) is None and p._root_problem(rootlink) == 'ROOT_LINKED' else 'FAIL')
    finally:
        for name in ('link', 'rootlink'):
            try:
                os.rmdir(os.path.join(base, name))
            except OSError:
                pass
        shutil.rmtree(base, ignore_errors=True)
    print('SUMMARY')
    for name, verdict in RESULTS:
        print('  %-5s %s' % (verdict, name))
    return 0 if all(v == 'PASS' for _, v in RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
