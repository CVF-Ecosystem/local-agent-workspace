"""Mutation probes on a scratch COPY of the checker (never the repo): each mutation must make at least one workflow test fail."""
import os
import shutil
import subprocess
import sys
import tempfile

REPO = sys.argv[1]
MUTATIONS = [
    ('current bytes always MET', '.cvf/checks/v3/workflow.py',
     "        if (target.get('exists') is not True or target.get('regular') is not True or target.get('sha256') != content['sha256']\n                or target.get('size') != content['size']):",
     "        if False:"),
    ('identity not compared', '.cvf/checks/v3/workflow.py',
     "        if target.get('identity') != published.get('identity'):", "        if False:"),
    ('target exists ignored', '.cvf/checks/v3/workflow.py',
     "        if obs['target'].get('exists') is not False:\n            return 'NOT_MET', {'TARGET_EXISTS_OBSERVED'}", "        if False:\n            return 'NOT_MET', {'TARGET_EXISTS_OBSERVED'}"),
    ('mandatory requirement coverage ignored', '.cvf/checks/v3/workflow.py',
     "        if mandatory - given:\n            incomplete = True", "        if False:\n            incomplete = True"),
    ('stale task digest ignored', '.cvf/checks/v3/workflow.py',
     " or ua.get('accepted_task_digest') != mine.accepted_task.digest):", "):"),
    ('grant status ignored', '.cvf/checks/v3/workflow.py',
     "        if grant.get('status') != 'ACTIVE' or grant.get('example_only'):", "        if False:"),
    ('string prefix instead of segments', '.cvf/checks/v3/workflow.py',
     "        return any(p is not None and segs[:len(p)] == p for p in paths)", "        return any(p is not None and '/'.join(segs).startswith('/'.join(p)) for p in paths)"),
    ('pin compare skipped at dispatch', '.cvf/checks/v3/workflow.py',
     "            elif current != pin:", "            elif False:"),
    ('envelope exceeded false', '.cvf/checks/v3/workflow.py',
     "        self.env_value = 'T' if exceeded else ('U' if unknown else 'F')", "        self.env_value = 'F'"),
    ('assumption closed without observation', '.cvf/checks/v3/workflow.py',
     "            self.target_absent = bool(self.obs['available'] and self.obs['parents_link_free'] is True and isinstance(target, dict)\n                                      and target.get('exists') is False and not files)",
     "            self.target_absent = True"),
    ('history snapshot not compared', '.cvf/checks/v3/workflow.py',
     "        if not same or published.get('target') != self.target or published.get('content') != prepared.get('content'):", "        if False:"),
    ('receipt digest not compared', '.cvf/checks/v3/workflow.py',
     "                    or receipt.get('digest') != self.evidence['raw_published_sha256']\n", "\n"),
    ('observation failure treated as absent', '.cvf/checks/v3/workflow.py',
     "        if not obs['available'] or obs['parents_link_free'] is not True or not isinstance(obs['target'], dict):", "        if False:"),
    ('claim ACCEPTED_FOR_INTEGRATION accepted', '.cvf/checks/v3/workflow.py',
     "        if 'ACCEPTED_FOR_INTEGRATION' in res.get('acceptance_states', []):", "        if False:"),
    ('input change ignored at effect', '.cvf/checks/v3/workflow.py',
     "                elif sha != item['digest']:", "                elif False:"),
    ('duplicate result ignored', '.cvf/checks/v3/workflow.py',
     "            elif len(found) > 1:\n                statuses.append('NOT_MET')\n                reasons.add(duplicate)", "            elif False:\n                pass"),
]


def run(tmp, label):
    proc = subprocess.run([sys.executable, '-B', '-W', 'error::ResourceWarning', '-m', 'unittest', 'tests.test_control_v3_workflow'],
                          cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
    tail = proc.stdout.decode('utf-8', 'replace').strip().splitlines()[-1]
    return proc.returncode, tail


base = tempfile.mkdtemp(prefix='law-mut-')
try:
    for label, rel, old, new in MUTATIONS:
        tmp = os.path.join(base, 'copy')
        if os.path.exists(tmp):
            shutil.rmtree(tmp)
        os.makedirs(os.path.join(tmp, 'tests'))
        shutil.copytree(os.path.join(REPO, '.cvf'), os.path.join(tmp, '.cvf'), ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(os.path.join(REPO, 'tools'), os.path.join(tmp, 'tools'), ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy(os.path.join(REPO, 'tests', 'test_control_v3_workflow.py'), os.path.join(tmp, 'tests'))
        open(os.path.join(tmp, 'tests', '__init__.py'), 'w').close()
        path = os.path.join(tmp, *rel.split('/'))
        text = open(path, encoding='utf-8').read()
        if text.count(old) != 1:
            print('SKIP (pattern count %d): %s' % (text.count(old), label))
            continue
        open(path, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
        code, tail = run(tmp, label)
        print('%-45s %s  [%s]' % (label, 'CAUGHT' if code != 0 else 'SURVIVED', tail))
finally:
    shutil.rmtree(base, ignore_errors=True)
