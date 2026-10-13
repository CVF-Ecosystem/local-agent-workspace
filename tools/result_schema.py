#!/usr/bin/env python3
"""Stable machine-readable result envelope shared by command-line tools and the panel."""
import json

SCHEMA = 'local-agent-workspace/result-v1'
MARKER = '@@RESULT_JSON@@'
STATUSES = {'success', 'preview', 'issues', 'not_checked', 'blocked', 'partial', 'error'}

def make(status, code=0, message='', changes=None, merge_required=False,
         files=None, findings=None, unchecked=None, next_actions=None, **extra):
    if status not in STATUSES:
        raise ValueError('Unknown result status: ' + str(status))
    out = {
        'schema': SCHEMA,
        'status': status,
        'code': int(code),
        'message': message or '',
        'changes': changes,
        'merge_required': bool(merge_required),
        'files': files or [],
        'findings': findings or [],
        'unchecked': unchecked or [],
        'next_actions': next_actions or [],
    }
    out.update(extra)
    return out

def emit(result):
    print(MARKER + json.dumps(result, ensure_ascii=False, separators=(',', ':')))

def split_output(text):
    """Return human text and the last valid result envelope."""
    lines, result = [], None
    for line in text.splitlines():
        if line.startswith(MARKER):
            try:
                value = json.loads(line[len(MARKER):])
                if value.get('schema') == SCHEMA and value.get('status') in STATUSES:
                    result = value
                    continue
            except (ValueError, AttributeError):
                pass
        lines.append(line)
    return '\n'.join(lines).strip(), result
