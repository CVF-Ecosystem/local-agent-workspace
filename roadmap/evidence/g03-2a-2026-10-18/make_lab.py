"""Tao thu muc lab G-03/2a moi (khong ghi de), chi fixture gia. Khong dung PATH/interpreter moi.

python make_lab.py [--root DIR] [--name NAME]
In ra duong dan lab da resolve. Hook dung python.exe tuyet doi = sys.executable luc chay script nay,
dang exec-form (args) de khong qua shell. Khong sua ~/.claude, registry, ACL, bien moi truong.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def h(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def hook(py, gate, mode, timeout, on_failure):
    return {"type": "command", "command": py, "args": ["-I", "-B", gate, mode],
            "timeout": timeout, "onFailure": on_failure}


def build_settings(py, gate, lab):
    missing_exe = os.path.join(lab, "hooks", "no_such_executable.exe")
    missing_script = os.path.join(lab, "hooks", "no_such_script.py")
    return {
        "hooks": {
            "SessionStart": [{"hooks": [hook(py, gate, "start", 5, "continue")]}],
            "InstructionsLoaded": [{"hooks": [hook(py, gate, "instructions", 5, "continue")]}],
            "PreToolUse": [
                {"matcher": "Write|Edit|NotebookEdit|Bash|PowerShell|Agent",
                 "hooks": [hook(py, gate, "pre", 3, "block")]},
                {"matcher": "*", "hooks": [hook(py, gate, "observe", 5, "continue")]},
                {"matcher": "Glob",
                 "hooks": [{"type": "command", "command": missing_exe, "args": ["x"],
                            "timeout": 3, "onFailure": "block"}]},
                {"matcher": "Grep",
                 "hooks": [{"type": "command", "command": py,
                            "args": ["-I", "-B", missing_script], "timeout": 3, "onFailure": "block"}]},
            ],
            "PostToolUse": [{"matcher": "*", "hooks": [hook(py, gate, "post", 5, "continue")]}],
            "SubagentStart": [{"hooks": [hook(py, gate, "subagent", 5, "continue")]}],
            "SubagentStop": [{"hooks": [hook(py, gate, "subagent", 5, "continue")]}],
            "PermissionRequest": [{"hooks": [hook(py, gate, "permission", 5, "continue")]}],
            "PermissionDenied": [{"hooks": [hook(py, gate, "permission", 5, "continue")]}],
        }
    }


def make(root, name):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    lab = os.path.realpath(os.path.join(root, name or "LAW-G03-2a-" + stamp))
    if os.path.lexists(lab):
        sys.exit("lab da ton tai, khong ghi de: " + lab)
    for d in ("hooks", "trace", "allowed", "denied", "fixture", ".claude"):
        os.makedirs(os.path.join(lab, d))
    gate = os.path.join(lab, "hooks", "gate.py")
    shutil.copyfile(os.path.join(HERE, "gate.py"), gate)
    files = {
        "fixture/input.txt": "LAW-G03-2A fixture line 1\nLAW-G03-2A fixture line 2\nLAW-G03-2A fixture line 3\n",
        "allowed/T6-edit.txt": "LAW-G03-2A-T6 before\n",
        "denied/canary.txt": "LAW-G03-2A canary, must stay unchanged\n",
    }
    for rp, content in files.items():
        with open(os.path.join(lab, rp), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    py = os.path.realpath(sys.executable)
    settings = build_settings(py, gate, lab)
    with open(os.path.join(lab, ".claude", "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    manifest = {"lab": lab, "python": py, "created": datetime.now().isoformat(timespec="seconds"),
                "sha256": {rp: h(os.path.join(lab, rp)) for rp in list(files) + ["hooks/gate.py", ".claude/settings.json"]}}
    with open(os.path.join(lab, "lab_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return lab


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=tempfile.gettempdir())
    ap.add_argument("--name")
    a = ap.parse_args()
    print(make(a.root, a.name))
