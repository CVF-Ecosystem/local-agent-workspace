# Bao cao G-03/2a

trace: `replay_trace.jsonl` (41 dong); origin: ['OFFLINE_REPLAY']

| Ca | Trang thai | Chi tiet |
|---|---|---|
| T0 SessionStart fire | UNKNOWN | khong co ban ghi start |
| T0 InstructionsLoaded memory_type | UNKNOWN | khong co ban ghi |
| T0 effective source/plugin-mod (/hooks, /status) | UNKNOWN | can operator dan ket qua /hooks va /status (lenh cuc bo); khong thay trong trace; xem t0_inventory.json cho ban kiem ke file |
| T1 Main Write allowed/ (allow + bytes) | OFFLINE_ONLY | decision=allow fs=None |
| T1 Main Write denied/ (deny + file vang) | OFFLINE_ONLY | decision=deny fs=None |
| T1 child tool call co agent_id/agent_type | OFFLINE_ONLY | agent_ids=['child-1'] agent_types=['general-purpose'] subagent_events=[] |
| T1 child Write allowed/ & denied/ | OFFLINE_ONLY | allow=[] deny=['deny'] fs_allow=None fs_deny=None |
| T1 Agent labels (khong la proof reviewer) | OFFLINE_ONLY | pre: subagent_type/requested_model=[('general-purpose', None), ('general-purpose', None), ('general-purpose', None)] ; post keys=[] resolvedModel=[] |
| T2-exception onFailure:block | OFFLINE_ONLY | hook_started=True hook_decided=False file_exists=None -> can doi chieu file |
| T2-malformed onFailure:block | OFFLINE_ONLY | hook_started=True hook_decided=True file_exists=None -> can doi chieu file |
| T2-timeout onFailure:block | OFFLINE_ONLY | hook_started=True hook_decided=False file_exists=None -> can doi chieu file |
| T2 missing executable (Glob) | UNKNOWN | observe=0 post=0 (post vang suy ra tool khong chay; can bao cao cua model/GUI de xac nhan thong diep) |
| T2 missing script qua python (Grep; exit 2 cua python) | UNKNOWN | observe=0 post=0 (post vang suy ra tool khong chay; can bao cao cua model/GUI de xac nhan thong diep) |
| T3-silent exit0 khong quyet dinh tren denied/ | OFFLINE_ONLY | decision=['SILENT_EXIT0'] file=None (file ton tai = exit0 im lang KHONG tu fail-closed) |
| T3-plain exit0 khong quyet dinh tren denied/ | OFFLINE_ONLY | decision=['PLAINTEXT_EXIT0'] file=None (file ton tai = exit0 im lang KHONG tu fail-closed) |
| T4 Bash literal denied/ (hook deny vs allow Bash(*)/PowerShell(*) toan cuc) | OFFLINE_ONLY | decision=['deny'] permission_mode=['REPLAY'] file=None |
| T4 PowerShell literal denied/ (hook deny vs allow Bash(*)/PowerShell(*) toan cuc) | OFFLINE_ONLY | decision=['deny'] permission_mode=['REPLAY'] file=None |
| T4 gian tiep (chuoi ghep): hook khong thay -> bypass | OFFLINE_ONLY | decision=['NO_DECISION'] file=None (file ton tai = duong shell cung named effect KHONG bi chan) |
| T4 canary denied/ nguyen ven | UNKNOWN | canary=None (so voi lab_manifest.json) |
| T5 ask trong phien lab | OFFLINE_ONLY | decision=['ask'] permission_mode=['REPLAY'] permission_events=[] file=None ; GUI: operator phai ghi co hien prompt hay khong, da chon gi (khong tick remember) |
| T6 Pre/Post bytes = detection hai thoi diem | OFFLINE_ONLY | pre={'sha256': 'b5f10fd86b164329', 'size': 21} post={'sha256': 'eddd19ecc79adc8a', 'size': 60} (khong khoa byte, khong atomic commit, khong preservation) |
| Ngan sach Agent | INFO | cho phep=1 (toi da 1), bi gate deny=2 |
