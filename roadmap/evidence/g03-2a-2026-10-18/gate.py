"""G-03/2a lab hook. Chi dung trong thu muc lab LAW-G03-2a-*; khong phai gate san pham.

Goi: python -I -B gate.py <mode>   (stdin = JSON payload cua host)
mode: pre | post | observe | start | subagent | permission | instructions

Thiet ke:
- Chi ghi trace (whitelist field) vao <lab>/trace/trace.jsonl; khong dump env/token/noi dung.
- Quyet dinh ro rang cho Write/Edit/NotebookEdit (allowed/ -> allow, con lai -> deny),
  Bash/PowerShell (lenh chua "denied" -> deny, con lai KHONG quyet dinh), Agent (toi da 1 lan,
  khong de quy). Chuoi trong lenh chi la mot heuristic de thu hook co chay hay khong; khong phai
  phan tich tac dong that.
- Token trong ten file kich hoat cac che do hong de do onFailure/exit code (chi cho Write/Edit):
  T2-exception, T2-malformed, T2-timeout, T3-silent, T3-plain, T5-ask.
- origin = OFFLINE_REPLAY neu env LAW_G03_ORIGIN=OFFLINE_REPLAY (replay.py dat), nguoc lai HOST_HOOK.
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACE = os.path.join(LAB, "trace", "trace.jsonl")
ORIGIN = os.environ.get("LAW_G03_ORIGIN") or "HOST_HOOK"
HOME = os.path.expanduser("~")


def norm(p):
    return os.path.normcase(os.path.realpath(p))


def inside(path, sub):
    base = norm(os.path.join(LAB, sub))
    try:
        return os.path.commonpath([norm(path), base]) == base
    except ValueError:
        return False


def rel(path):
    try:
        r = os.path.relpath(norm(path), norm(LAB))
    except ValueError:
        return "<other-drive>"
    return "<outside-lab>" if r.startswith("..") else r.replace("\\", "/")


def redact(s):
    return s.replace(HOME, "~") if isinstance(s, str) else s


def sha(path):
    # Never read outside the lab, including injected-failure filenames.
    if not inside(path, ""):
        return {"sha256": None, "error": "OUTSIDE_LAB_NOT_READ"}
    try:
        with open(path, "rb") as f:
            data = f.read()
        return {"sha256": hashlib.sha256(data).hexdigest()[:16], "size": len(data)}
    except FileNotFoundError:
        return {"sha256": None, "size": None, "exists": False}
    except OSError as e:
        return {"sha256": None, "error": type(e).__name__}


def log(rec):
    rec["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    rec["origin"] = ORIGIN
    os.makedirs(os.path.dirname(TRACE), exist_ok=True)
    with open(TRACE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def base_rec(mode, p):
    sid = p.get("session_id") or ""
    return {
        "hook_mode": mode,
        "event": p.get("hook_event_name"),
        "session": hashlib.sha256(sid.encode()).hexdigest()[:8] if sid else None,
        "agent_id": p.get("agent_id"),
        "agent_type": p.get("agent_type"),
        "permission_mode": p.get("permission_mode"),
        "cwd_rel": rel(p["cwd"]) if p.get("cwd") else None,
        "tool_name": p.get("tool_name"),
        "tool_use_id": p.get("tool_use_id"),
    }


def target_path(p):
    ti = p.get("tool_input") or {}
    t = ti.get("file_path") or ti.get("notebook_path")
    if not t:
        return None
    return t if os.path.isabs(t) else os.path.join(p.get("cwd") or LAB, t)


def emit(decision, reason):
    out = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                  "permissionDecision": decision,
                                  "permissionDecisionReason": reason}}
    sys.stdout.write(json.dumps(out))


def count_agent_calls():
    n = 0
    try:
        with open(TRACE, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if (r.get("hook_mode") == "pre" and r.get("tool_name") == "Agent"
                        and r.get("phase") == "decided" and r.get("origin") == ORIGIN):
                    n += 1
    except FileNotFoundError:
        pass
    return n


def do_pre(p):
    rec = base_rec("pre", p)
    tool = p.get("tool_name")
    ti = p.get("tool_input") or {}
    tp = target_path(p)
    if tp and not inside(tp, ""):
        rec.update(path_rel="<outside-lab>", phase="decided",
                   decision="deny", basis="outside-lab")
        emit("deny", "G03-2a lab: target outside lab, not read")
        log(rec)
        return 0
    if tp:
        rec["path_rel"] = rel(tp)
        rec["pre_bytes"] = sha(tp)
    if tool in ("Bash", "PowerShell"):
        rec["cmd_head"] = redact(str(ti.get("command", ""))[:200])
    if tool == "Agent":
        rec["subagent_type"] = ti.get("subagent_type")
        rec["requested_model"] = ti.get("model")
    name = os.path.basename(tp).casefold() if tp else ""
    rec["phase"] = "started"
    log(dict(rec))
    rec["phase"] = "decided"

    if tool in ("Write", "Edit", "NotebookEdit") and tp:
        if "t2-exception" in name:
            raise RuntimeError("T2 injected exception")
        if "t2-malformed" in name:
            sys.stdout.write("{not json")
            rec.update(decision="MALFORMED_JSON_EXIT0")
            log(rec)
            return 0
        if "t2-timeout" in name:
            time.sleep(10)
        if "t3-silent" in name:
            rec.update(decision="SILENT_EXIT0")
            log(rec)
            return 0
        if "t3-plain" in name:
            sys.stdout.write("LAW-G03-2A plain text, no decision\n")
            rec.update(decision="PLAINTEXT_EXIT0")
            log(rec)
            return 0
        if "t5-ask" in name:
            emit("ask", "G03-2a T5: hook asks the user")
            rec.update(decision="ask")
            log(rec)
            return 0
        if inside(tp, "allowed"):
            emit("allow", "G03-2a lab: allowed/")
            rec.update(decision="allow")
        else:
            emit("deny", "G03-2a lab: write outside allowed/")
            rec.update(decision="deny")
        log(rec)
        return 0

    if tool in ("Bash", "PowerShell"):
        if "denied" in str(ti.get("command", "")).casefold():
            emit("deny", "G03-2a lab: command text mentions denied/")
            rec.update(decision="deny", basis="substring")
        else:
            rec.update(decision="NO_DECISION", basis="substring-miss")
        log(rec)
        return 0

    if tool == "Agent":
        if p.get("agent_id"):
            emit("deny", "G03-2a lab: no recursive delegation")
            rec.update(decision="deny", basis="recursive")
        elif count_agent_calls() >= 1:
            emit("deny", "G03-2a lab: native Agent budget (1) used")
            rec.update(decision="deny", basis="budget")
        else:
            rec.update(decision="NO_DECISION", basis="first-agent-call")
        log(rec)
        return 0

    rec.update(decision="NO_DECISION", basis="tool-not-gated")
    log(rec)
    return 0


def do_post(p):
    rec = base_rec("post", p)
    tp = target_path(p)
    if tp:
        rec["path_rel"] = rel(tp)
        rec["post_bytes"] = sha(tp)
    tr = p.get("tool_response")
    if isinstance(tr, dict):
        rec["tool_response_keys"] = sorted(tr.keys())[:20]
        for k in ("resolvedModel", "success", "is_error"):
            if k in tr and isinstance(tr[k], (str, bool, int)):
                rec[k] = tr[k]
    elif tr is not None:
        rec["tool_response_type"] = type(tr).__name__
    log(rec)
    return 0


def do_observe(p):
    rec = base_rec("observe", p)
    tp = target_path(p)
    if tp:
        rec["path_rel"] = rel(tp)
    log(rec)
    return 0


def do_start(p):
    rec = base_rec("start", p)
    rec["payload_keys"] = sorted(p.keys())
    for k in ("source", "model"):
        if k in p and isinstance(p[k], str):
            rec[k] = p[k]
    rec["env_flags"] = {k: (os.environ.get(k) if k in ("CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_VERSION") else "present")
                        for k in ("CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_VERSION", "CLAUDECODE",
                                  "CLAUDE_PROJECT_DIR", "CLAUDE_CONFIG_DIR", "CLAUDE_CODE_GIT_BASH_PATH")
                        if k in os.environ}
    log(rec)
    return 0


def do_subagent(p):
    rec = base_rec("subagent", p)
    rec["payload_keys"] = sorted(p.keys())
    atp = p.get("agent_transcript_path")
    if atp:
        rec["agent_transcript_basename"] = os.path.basename(atp)
    log(rec)
    return 0


def do_permission(p):
    rec = base_rec("permission", p)
    tp = target_path(p)
    if tp:
        rec["path_rel"] = rel(tp)
    rec["payload_keys"] = sorted(p.keys())
    log(rec)
    return 0


def do_instructions(p):
    rec = base_rec("instructions", p)
    rec["memory_type"] = p.get("memory_type")
    rec["load_reason"] = p.get("load_reason")
    fp = p.get("file_path")
    rec["file"] = redact(fp) if fp else None
    log(rec)
    return 0


MODES = {"pre": do_pre, "post": do_post, "observe": do_observe, "start": do_start,
         "subagent": do_subagent, "permission": do_permission, "instructions": do_instructions}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in MODES:
        sys.stderr.write("unknown mode\n")
        return 1
    raw = sys.stdin.buffer.read()
    p = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    return MODES[mode](p)


if __name__ == "__main__":
    sys.exit(main())
