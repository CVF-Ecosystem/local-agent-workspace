"""T0: kiem ke CHI DOC, da che — nguon cau hinh co the anh huong hook trong phien lab. Khong sua gi.
Ghi ten/khoa/su ton tai, KHONG ghi gia tri allow-list, token, credential, duong dan nguoi dung ngoai ~.
"""
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
C = os.path.join(HOME, ".claude")
out = {"label": "T0 inventory (chi doc, tai may nay; KHONG phai effective policy cua phien lab)"}


def keys(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
        return {"exists": True, "top_keys": sorted(d.keys()),
                "has_hooks": bool(d.get("hooks")), "has_sandbox": "sandbox" in d,
                "permissions_keys": sorted((d.get("permissions") or {}).keys()),
                "defaultMode": (d.get("permissions") or {}).get("defaultMode"),
                "allow_count": len((d.get("permissions") or {}).get("allow") or []),
                "deny_count": len((d.get("permissions") or {}).get("deny") or []),
                "disableAllHooks": d.get("disableAllHooks"), "allowManagedHooksOnly": d.get("allowManagedHooksOnly")}
    except FileNotFoundError:
        return {"exists": False}
    except Exception as e:
        return {"exists": True, "parse_error": type(e).__name__}


out["user_settings"] = keys(os.path.join(C, "settings.json"))
out["user_settings_local"] = keys(os.path.join(C, "settings.local.json"))
out["managed_file_ProgramFiles"] = os.path.exists(r"C:\Program Files\ClaudeCode\managed-settings.json")
out["managed_dir_ProgramFiles"] = os.path.isdir(r"C:\Program Files\ClaudeCode")
out["legacy_ProgramData_dir"] = os.path.isdir(r"C:\ProgramData\ClaudeCode")
for hive in ("HKLM", "HKCU"):
    r = subprocess.run(["reg", "query", hive + r"\SOFTWARE\Policies\ClaudeCode"], capture_output=True)
    out["registry_" + hive + "_policy_key"] = r.returncode == 0
pl = os.path.join(C, "plugins")
inv = {"dir_exists": os.path.isdir(pl), "entries": sorted(os.listdir(pl)) if os.path.isdir(pl) else []}
hook_files = []
if os.path.isdir(pl):
    for dp, dn, fn in os.walk(pl):
        dn[:] = [d for d in dn if d not in (".git", "node_modules", ".trash")]
        for f in fn:
            if f in ("hooks.json",) or f == "plugin.json":
                hook_files.append(os.path.relpath(os.path.join(dp, f), pl).replace("\\", "/"))
inv["hooks_or_plugin_json_files_count"] = len(hook_files)
inv["hooks_json_files"] = [f for f in hook_files if f.endswith("hooks.json")][:20]
for name in ("installed_plugins.json", "known_marketplaces.json", "blocklist.json"):
    p = os.path.join(pl, name)
    inv[name] = os.path.exists(p)
ip = os.path.join(pl, "installed_plugins.json")
if os.path.exists(ip):
    try:
        d = json.load(open(ip, encoding="utf-8"))
        inv["installed_plugin_names"] = sorted((d.get("plugins") or d).keys())[:50]
    except Exception as e:
        inv["installed_plugins_parse_error"] = type(e).__name__
out["plugins"] = inv
out["claude_dir_entries"] = sorted(os.listdir(C))
ext = os.path.join(HOME, ".vscode", "extensions")
out["vscode_claude_extension_dirs"] = sorted(d for d in os.listdir(ext) if d.startswith("anthropic.claude-code")) if os.path.isdir(ext) else []
vs = os.path.join(os.environ.get("APPDATA", ""), "Code", "User", "settings.json")
try:
    txt = open(vs, encoding="utf-8").read()
    out["vscode_user_settings_claude_keys"] = sorted({w.strip('"') for w in __import__("re").findall(r'"(claude[A-Za-z.]*)"\s*:', txt)})
except FileNotFoundError:
    out["vscode_user_settings_claude_keys"] = None
out["mods_dir_candidates"] = {n: os.path.isdir(os.path.join(C, n)) for n in ("mods", "mod", "daemon", "ide", "jobs")}
out["limits"] = ["Khong doc project .claude cua workspace khac; khong doc server-managed/remote settings; plugin/mod hook thuc su trong phien lab chi thay qua /hooks (GUI) -> UNKNOWN cho den khi operator dan."]
print(json.dumps(out, ensure_ascii=False, indent=1))
