"""Deterministic interleaving of the reviewer's lock race, against (1) the previous protocol rebuilt from its code and (2) the current writer_lock."""
import contextlib
import os
import sys
import tempfile
import threading

LAW = r'D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\local-agent-workspace'
sys.path.insert(0, os.path.join(LAW, 'tools'))
import library_sync  # noqa: E402


class Busy(Exception):
    pass


@contextlib.contextmanager
def previous_protocol(folder, after_stale_check):
    """Exists -> read the id -> 'dead' -> unlink -> create again with O_EXCL; release = unlink. (Rebuilt from the previous library_sync.)"""
    lock = os.path.join(folder, 'index.lock')
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        dead = open(lock).read().strip() == '999999'  # stale_lock(): readable id of a process that is gone
        after_stale_check()
        if not dead:
            raise Busy()
        try:
            os.unlink(lock)
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except OSError:
            raise Busy()
    try:
        os.write(fd, b'1')
        os.close(fd)
        yield
    finally:
        os.unlink(lock)


def run(make_lock):
    folder = tempfile.mkdtemp(prefix='a06-lockrace-')
    open(os.path.join(folder, 'index.lock'), 'w').write('999999')
    b_in, a_resume, log = threading.Event(), threading.Event(), []

    def writer_a():
        try:
            with make_lock(folder, lambda: (b_in.wait(5), None)[1]):
                log.append('A entered while B holds: %s' % b_in.is_set())
                a_resume.set()
        except Busy:
            log.append('A busy')
        except Exception as e:  # noqa: BLE001
            log.append('A error ' + repr(e))

    def writer_b():
        try:
            with make_lock(folder, lambda: None):
                log.append('B entered')
                b_in.set()
                a_resume.wait(5)
                log.append('B lock file still there when B leaves: %s' % os.path.exists(os.path.join(folder, 'index.lock')))
        except Busy:
            log.append('B busy')
            b_in.set()
        except Exception as e:  # noqa: BLE001
            log.append('B cleanup/other error ' + repr(e))
            b_in.set()
    ta, tb = threading.Thread(target=writer_a), threading.Thread(target=writer_b)
    ta.start()
    tb.start()
    ta.join(10)
    tb.join(10)
    return log


print('previous protocol:')
for line in run(previous_protocol):
    print('  ', line)


@contextlib.contextmanager
def current_protocol(folder, _pause):
    root = os.path.dirname(folder)
    # writer_lock works on a project root; build one around this folder
    yield from _current(root)


def _current(_root):
    raise NotImplementedError


# current writer_lock: same interleaving, there is no "stale check" to pause between, so run A and B against the real thing
project = tempfile.mkdtemp(prefix='a06-lockrace-proj-')
lock_dir = os.path.join(project, '.agent', 'runtime', 'library')
os.makedirs(lock_dir)
open(os.path.join(lock_dir, 'index.lock'), 'w').write('999999')
log, barrier, a_done = [], threading.Barrier(2), threading.Event()


def worker(name, hold):
    barrier.wait()
    try:
        with library_sync.writer_lock(project):
            log.append('%s entered' % name)
            hold.wait(5)
    except library_sync.SyncError:
        log.append('%s busy' % name)
    except Exception as e:  # noqa: BLE001
        log.append('%s error %r' % (name, e))


release = threading.Event()
t1, t2 = threading.Thread(target=worker, args=('A', release)), threading.Thread(target=worker, args=('B', release))
t1.start()
t2.start()
threading.Timer(0.5, release.set).start()
t1.join(10)
t2.join(10)
print('current protocol:')
for line in log:
    print('  ', line)
print('   lock file present afterwards (never deleted):', os.path.exists(os.path.join(lock_dir, 'index.lock')))
