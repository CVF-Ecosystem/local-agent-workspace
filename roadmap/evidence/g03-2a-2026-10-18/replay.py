"""OFFLINE REPLAY cua hook lab G-03/2a. KHONG phai ket qua host.

Chay gate.py that (cung python.exe, cung args exec-form lay tu settings.json cua lab tao boi make_lab.py)
voi payload gia, bang subprocess. Ap ngu nghia onFailure/exit code THEO TAI LIEU de du doan host se
lam gi — phan 'simulated_host' chi la du doan tu tai lieu, khong duoc coi la host da xu ly.
Tao lab tam rieng LAW-G03-2a-replay-*, chay, ghi replay_result.json canh script, roi don lab do
(chi khi xac nhan nam duoi thu muc tam, ten dung tien to, khong co link/junction).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_lab  # noqa: E402


def spawn(hook, payload, env):
    argv = [hook["command"]] + hook.get("args", [])
    t0 = time.time()
    try:
        r = subprocess.run(argv, input=json.dumps(payload).encode(), capture_output=True,
                           timeout=hook.get("timeout", 5), env=env)
        return {"kind": "exit", "code": r.returncode, "stdout": r.stdout.decode("utf-8", "replace"),
                "stderr_head": r.stderr.decode("utf-8", "replace")[-200:], "secs": round(time.time() - t0, 2)}
    except subprocess.TimeoutExpired:
        return {"kind": "timeout", "secs": round(time.time() - t0, 2)}
    except OSError as e:
        return {"kind": "cannot_start", "error": type(e).__name__, "secs": round(time.time() - t0, 2)}


def simulate_host(res, on_failure):
    """Du doan theo tai lieu hooks (code.claude.com/docs/en/hooks, 'Block the action when a hook fails')."""
    if res["kind"] in ("timeout", "cannot_start"):
        return "BLOCK" if on_failure == "block" else "CONTINUE_NORMAL_FLOW"
    code, out = res["code"], res["stdout"].strip()
    if code == 2:
        return "BLOCK (exit 2)"
    if code != 0:
        return "BLOCK (failure+onFailure=block)" if on_failure == "block" else "CONTINUE_NORMAL_FLOW"
    if not out:
        return "NO_DECISION -> normal permission flow"
    if out.startswith("{"):
        try:
            d = json.loads(out)["hookSpecificOutput"]["permissionDecision"]
            return "DECISION " + d
        except Exception:
            return "BLOCK (invalid output+onFailure=block)" if on_failure == "block" else "CONTINUE_NORMAL_FLOW"
    return "NO_DECISION (plain text only logged) -> normal permission flow"


def P(lab, event, tool, ti, **kw):
    d = {"session_id": "replay-session", "cwd": lab, "hook_event_name": event, "tool_name": tool,
         "tool_input": ti, "tool_use_id": "toolu_replay_" + hashlib.sha256(json.dumps(ti, sort_keys=True).encode()).hexdigest()[:8],
         "permission_mode": "REPLAY"}
    d.update(kw)
    return d


def safe_cleanup(lab):
    tmp = os.path.realpath(tempfile.gettempdir())
    real = os.path.realpath(lab)
    assert os.path.commonpath([real, tmp]) == tmp and os.path.basename(real).startswith("LAW-G03-2a-replay-")
    for dp, dns, fns in os.walk(real):
        for n in dns + fns:
            full = os.path.join(dp, n)
            assert not os.path.islink(full) and not (hasattr(os.path, "isjunction") and os.path.isjunction(full)), full
    shutil.rmtree(real)


def main():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    lab = make_lab.make(tempfile.gettempdir(), "LAW-G03-2a-replay-" + stamp)
    settings = json.load(open(os.path.join(lab, ".claude", "settings.json"), encoding="utf-8"))
    pre = settings["hooks"]["PreToolUse"]
    gate_hook = pre[0]["hooks"][0]
    glob_hook = pre[2]["hooks"][0]
    grep_hook = pre[3]["hooks"][0]
    post_hook = settings["hooks"]["PostToolUse"][0]["hooks"][0]
    env = dict(os.environ, LAW_G03_ORIGIN="OFFLINE_REPLAY")
    A = lambda *p: os.path.join(lab, "allowed", *p)
    D = lambda *p: os.path.join(lab, "denied", *p)
    results = []

    def run(case, hook, payload):
        res = spawn(hook, payload, env)
        res["case"] = case
        res["simulated_host"] = simulate_host(res, hook.get("onFailure"))
        res["label"] = "OFFLINE_REPLAY (simulated_host = du doan tu tai lieu, khong phai host)"
        results.append(res)
        return res

    W = lambda path: P(lab, "PreToolUse", "Write", {"file_path": path, "content": "x"})
    run("T1 Write allowed/", gate_hook, W(A("T1-main-allow.txt")))
    run("T1 Write denied/", gate_hook, W(D("T1-main-deny.txt")))
    run("T1 Write ngoai allowed (.claude/settings.json)", gate_hook, W(os.path.join(lab, ".claude", "settings.json")))
    run("T1 Write allowed/../denied traversal", gate_hook, W(os.path.join(lab, "allowed", "..", "denied", "t.txt")))
    run("T1 Write ALLOWED/ doi hoa-thuong", gate_hook, W(os.path.join(lab, "ALLOWED", "case.txt")))
    run("T1 Write denied/x:stream (ADS)", gate_hook, W(D("ads.txt:stream")))
    run("T1 Write 'denied./' dau cham cuoi", gate_hook, W(os.path.join(lab, "denied.", "dot.txt")))
    run("T4 Bash literal denied/", gate_hook, P(lab, "PreToolUse", "Bash", {"command": "echo x > denied/T4-bash.txt"}))
    run("T4 PowerShell literal denied/", gate_hook, P(lab, "PreToolUse", "PowerShell", {"command": "Set-Content denied/T4-ps.txt x"}))
    run("T4 PowerShell gian tiep 'den'+'ied'", gate_hook,
        P(lab, "PreToolUse", "PowerShell", {"command": "$d='den'+'ied'; Set-Content \"$d/T4-indirect.txt\" x"}))
    run("T1 Agent lan 1", gate_hook, P(lab, "PreToolUse", "Agent", {"subagent_type": "general-purpose", "prompt": "p", "description": "d"}))
    run("T1 Agent lan 2 (vuot ngan sach)", gate_hook, P(lab, "PreToolUse", "Agent", {"subagent_type": "general-purpose", "prompt": "p", "description": "d"}))
    run("T1 Agent de quy (co agent_id)", gate_hook,
        P(lab, "PreToolUse", "Agent", {"subagent_type": "general-purpose", "prompt": "p", "description": "d"}, agent_id="child-1", agent_type="general-purpose"))
    run("T1 child Write denied/ (agent_id)", gate_hook,
        dict(W(D("T1-child-deny.txt")), agent_id="child-1", agent_type="general-purpose"))
    run("T2 exception exit!=0,2", gate_hook, W(A("T2-exception.txt")))
    run("T2 malformed JSON exit0", gate_hook, W(A("T2-malformed.txt")))
    run("T2 timeout (>3s)", gate_hook, W(A("T2-timeout.txt")))
    run("T2 missing executable (Glob hook)", glob_hook, P(lab, "PreToolUse", "Glob", {"pattern": "*.txt"}))
    run("T2 missing script qua python -I (Grep hook)", grep_hook, P(lab, "PreToolUse", "Grep", {"pattern": "LAW"}))
    run("T3 exit0 im lang tren denied/", gate_hook, W(D("T3-silent.txt")))
    run("T3 plaintext exit0 tren denied/", gate_hook, W(D("T3-plain.txt")))
    run("T5 ask", gate_hook, W(A("T5-ask.txt")))

    # T6: Pre/Post chi la hai thoi diem
    t6 = A("T6-edit.txt")
    run("T6 Pre (Edit)", gate_hook, P(lab, "PreToolUse", "Edit", {"file_path": t6, "old_string": "before", "new_string": "after"}))
    open(t6, "w", encoding="utf-8").write("LAW-G03-2A-T6 mid-1\n")
    open(t6, "w", encoding="utf-8").write("LAW-G03-2A-T6 mid-2 (thay doi ngoai hook giua Pre va Post)\n")
    run("T6 Post (Edit) sau 2 lan ghi ngoai hook", post_hook,
        P(lab, "PostToolUse", "Edit", {"file_path": t6}, tool_response={"success": True}))

    trace = [json.loads(l) for l in open(os.path.join(lab, "trace", "trace.jsonl"), encoding="utf-8")]
    out = {"label": "OFFLINE_REPLAY", "python": sys.version.split()[0], "created": stamp,
           "cases": results, "trace_origin_values": sorted({t["origin"] for t in trace}),
           "trace_lines": len(trace)}
    with open(os.path.join(HERE, "replay_result.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "replay_trace.jsonl"), "w", encoding="utf-8") as f:
        for t in trace:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    safe_cleanup(lab)
    for r in results:
        print("%-52s %-12s %s" % (r["case"], r.get("code", r["kind"]), r["simulated_host"]))
    print("replay lab da don:", not os.path.exists(lab))


if __name__ == "__main__":
    main()
