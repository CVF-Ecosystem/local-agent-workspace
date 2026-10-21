import hashlib
import os
import subprocess
import sys

ROOT = sys.argv[1]
WF = '.cvf/checks/v3/workflow.py'
W = 'tools/publish_new.py'

MUTATIONS = [
    ('M1 snapshot guard always MET', WF, "        state, rebuilt = observer.rebuild_task(self.task, self.rid)\n",
     "        return ('MET', set())\n        state, rebuilt = observer.rebuild_task(self.task, self.rid)\n",
     ['tests.test_control_v3_workflow.StableSnapshot']),
    ('M2 checker ignores runtime parents', WF, "        if obs.get('runtime_parents_ready') is False:\n",
     "        if False:\n", ['tests.test_control_v3_workflow.StableSnapshot']),
    ('M3 writer creates missing parents again', W, "required=len(RUNTIME_PARENTS))", "required=0)", ['tests.test_publish_new']),
    ('M5 no rid collision check before prepared open', W, "    if _rid_files(project, rid):  # a file of this rid appeared",
     "    if False:  # a file of this rid appeared", ['tests.test_publish_new']),
    ('M6 invalid rid accepted', W, "elif type(request_id) is str and RID_RE.fullmatch(request_id):", "elif isinstance(request_id, str):", ['tests.test_publish_new']),
    ('M7 staged orphan ignored under the lock', W, "os.path.lexists(_evidence_path(project, rid, 'staged'))\n                    or identity_of(mine)",
     "False\n                    or identity_of(mine)", ['tests.test_publish_new']),
]

for label, rel, old, new, mods in MUTATIONS:
    path = os.path.join(ROOT, rel)
    with open(path, 'rb') as f:
        original = f.read()
    text = original.decode('utf-8')
    old, new = old.replace(chr(10), chr(13) + chr(10)), new.replace(chr(10), chr(13) + chr(10))
    assert text.count(old) == 1, (label, text.count(old))
    try:
        with open(path, 'wb') as f:
            f.write(text.replace(old, new).encode('utf-8'))
        proc = subprocess.run([sys.executable, '-B', '-m', 'unittest'] + mods, cwd=ROOT, capture_output=True, text=True, timeout=300)
        tail = [l for l in proc.stderr.strip().splitlines() if l.startswith(('FAILED', 'OK', 'Ran'))]
        print('%-52s -> %s' % (label, ' | '.join(tail)))
    finally:
        with open(path, 'wb') as f:
            f.write(original)
    assert hashlib.sha256(open(path, 'rb').read()).hexdigest() == hashlib.sha256(original).hexdigest()
