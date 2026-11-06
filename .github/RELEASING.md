# Phát hành Local Agent Workspace / Releasing Local Agent Workspace

Tài liệu cho người bảo trì kho nguồn. Thư mục `.github/` không vào gói phát hành.
Maintainer guide for the source repository. The `.github/` folder is never packaged.

---

# Tiếng Việt

## 1. Ma trận hỗ trợ chính thức

Ô nào chưa có bằng chứng chạy thì ghi là chưa xác nhận; cấu hình CI không được tính là đã kiểm thử. Bảng dưới ghi **bằng chứng lịch sử RC4**, nguồn `2552d7d`, không xác nhận HEAD hiện tại hay bản final. CI [39985758160](https://github.com/CVF-Ecosystem/local-agent-workspace/actions/runs/39985758160) toàn run thất bại: 3/5 job đạt, 2 job thất bại.

| Hệ điều hành | Python | Bằng chứng RC4 và giới hạn |
|---|---|---|
| Windows/NTFS local | 3.11.9 | 4/4 gate đạt; 1.622 test, 6 skip (5 file-symlink, 1 non-Windows refusal). Chưa là final. |
| Windows Server 2025 CI | 3.12.10 | Job đạt; bộ test và gate build mỗi lượt 1.622 test, 48 skip. Năm ca file-symlink bị skip local đã đạt tại đây; không chứng minh mọi môi trường hay loại bỏ giới hạn TOCTOU. |
| Windows CI | 3.8 | Job thất bại: 1 failure, 48 skip; chưa xác nhận hỗ trợ. |
| Ubuntu CI | 3.8 và 3.12 | Cả hai job đạt, mỗi bộ test có 447 skip, gồm ca cần Windows và browser; không chứng minh đầy đủ nghiệp vụ văn phòng Linux. |
| macOS CI | 3.12 | Job thất bại: 1 error, 447 skip; chưa xác nhận hỗ trợ. |
| Mọi tổ hợp khác (ví dụ Python 3.9, 3.10, 3.13) | — | Chưa kiểm trong bằng chứng RC4 này; không suy hỗ trợ. |

Chỉ coi một ô là hỗ trợ chính thức khi job CI tương ứng đã chạy xanh trên commit sắp phát hành; các skip và phạm vi sử dụng vẫn phải được xem xét.

### Prototype văn phòng nội bộ và RC4

Ma trận Prototype trong README VI/EN gắn với đúng source/artifact được kiểm. RC4 là Prototype Windows/DATAMOCK đã công bố, không chứng minh usability người thật, các host khác hoặc hỗ trợ chính thức trên HEAD hiện tại. Năm ca file-symlink local bị skip được quan sát đạt trên CI Windows/Python 3.12 của đúng nguồn RC4; không suy mọi loại liên kết hay môi trường đều đạt. Giữ các skip và giới hạn hợp tác trong báo cáo.

Trước khi giao phần V7, đối chiếu toàn bộ điều kiện mốc và khoảng trống theo AGENTS quy tắc10/mục8.3 roadmap. Hướng dẫn hoặc matrix đổi sau candidate thì gate cũ chỉ có giá trị cho snapshot cũ; bản giao mới phải có gate đúng bytes và review boundary liên quan. Dùng evidence còn hiệu lực khi review, không chạy lại nghiệp vụ chỉ để lặp proof.

Candidate từ worktree dirty chỉ phục vụ kiểm nội bộ, không là nguồn sạch để công bố. Công bố vẫn phải theo quyền operator, source sạch, gate và ma trận đã xác nhận bên dưới. Giữ candidate cũ; không thay tag/asset đã công bố hoặc coi bản nội bộ là public RC mới. Feedback thật vẫn sau Prototype/MVP theo operator.

## 2. Chính sách phiên bản

Số phiên bản nằm trong `VERSION` (MAJOR.MINOR.PATCH). Đó là nguồn duy nhất.

- **MAJOR**: thay đổi không tương thích ngược: đổi cấu trúc `.agent/` hoặc thư mục project, đổi định dạng `MANIFEST.sha256`, đổi schema envelope `local-agent-workspace/result-v1`, bỏ lệnh hoặc cờ đã có.
- **MINOR**: thêm tương thích ngược: công cụ, skill, cờ, cổng kiểm, hoặc mục nội dung mới.
- **PATCH**: sửa lỗi, sửa tài liệu, cập nhật mẫu mà không đổi định dạng dữ liệu của project.
- Mỗi bản phát hành phải có mục trong `CHANGELOG.md` với tiêu đề khớp `VERSION` (`check_package` kiểm).
- Release candidate (`--rc N`) là bản thử để nghiệm thu: không đổi `VERSION`, tên ZIP có hậu tố `-rcN`.
- Bản preview đã công bố: [v1.9.0-rc4](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc4) (prerelease, chưa final), nguồn `2552d7d`; không coi đó là candidate cho delta hiện tại. Giữ các tag/asset đã công bố. RC tiếp theo dùng số `N` chưa được công bố sau khi kiểm tra; chưa chọn số hoặc cấp quyền build/phát hành tại đây.

## 3. Checklist phát hành (RC -> nghiệm thu -> chính thức)

1. **Nguồn**: nâng `VERSION`, thêm `CHANGELOG.md`, sửa các chuỗi phiên bản còn lại (`check_package` báo chỗ lệch). Chạy `python tools/build_guides_html.py`.
2. **Kiểm nguồn**: `python tools/check_package.py --release` và `python -B -m unittest discover -s tests -v` đều phải đạt.
3. **Release candidate**: trong phạm vi quyền đã cấp và sau khi kiểm tra số `N` chưa công bố, dùng `python tools/build_release.py --rc N` với `N` thay bằng số đã chọn. Kết quả nằm trong `dist/`: `local-agent-workspace-v<VERSION>-rcN.zip` và `.gate.json` cạnh nó. Không dùng lại tag/asset đã công bố. Mở báo cáo, kiểm mọi cổng là `passed` và `git.dirty` là `false`.
4. **Nghiệm thu RC**: giải nén RC vào thư mục mới; chạy `python tools/check_package.py --verify` (phải thoát 0); thử nâng cấp một bản sao project theo hướng dẫn ở mục 5; mở bảng điều khiển trên hệ điều hành đã chọn trong ma trận. Sửa lỗi trong nguồn rồi quay lại bước 1 với RC mới.
5. **Chính thức**: `python tools/build_release.py` (không có `--rc`). Lưu cặp ZIP và `.gate.json`, ghi SHA-256 trong ghi chú phát hành.

## 4. Cổng chất lượng và báo cáo cổng

`build_release.py` chạy các cổng trước khi đóng gói. Không có ZIP nào được tạo khi một cổng `failed`: công cụ thoát mã 1, envelope có `status: blocked` và `findings` liệt kê cổng lỗi; không có báo cáo cổng.

| Cổng | Kiểm gì |
|---|---|
| `package_check` | `check_package --release`: cấu trúc, mẫu phát hành sạch, song ngữ, phiên bản, và HTML khớp Markdown |
| `python38_compat` | Heuristic tương thích Python 3.8 (xem mục 6) |
| `behaviour_tests` | `python -B -m unittest discover -s tests`; chỉ có ở kho nguồn (khi có thư mục `tests/`) |
| `release_tree` | `check_package --release` trên cây phát hành tạm; luôn chạy, kể cả với `--skip-check` |

Trạng thái cổng: `passed` (đạt), `failed` (lỗi), `skipped` (bỏ qua vì `--skip-check` hoặc không có `tests/`), `nested` (xem dưới).

- `--skip-check` chỉ dùng với `--rc N`. Bản chính thức bị từ chối (thoát mã 2). Với RC, báo cáo ghi các cổng là `skipped`.
- **Build lồng nhau**: khi cổng `behaviour_tests` chạy bộ kiểm thử, nó đặt `LOCAL_AGENT_WORKSPACE_GATE_NESTED=1`. Một build được gọi từ bộ kiểm thử với biến này chỉ ghi `behaviour_tests` là `nested` và bỏ qua việc chạy lại bộ kiểm thử, tránh đệ quy. Các cổng khác vẫn chạy. `nested` không phải `passed`.
- **Báo cáo** `<ZIP>.gate.json`, schema `local-agent-workspace/release-gate-v1`: `version`, `kind` (`official` hoặc `rc`), `rc`, `skip_check`, `archive`, `archive_sha256`, `gates` (tên, trạng thái, `duration_s`, `detail`), `platform` (`system`, `release`), `python`, `git` (`commit`, `dirty`; `null` nếu không có git), `branding`, `generated_utc`.
- **Nhận diện đơn vị**: logo, `assets/branding.json` và font trong `assets/fonts/` của thư mục nguồn được đóng kèm ZIP; `assets/branding.js` dựng lại từ `branding.json`. Danh sách ghi ở `branding` trong báo cáo. Các file này không vào MANIFEST nên nâng cấp không ghi đè. Bỏ bằng `--no-branding` (ví dụ bản công khai chung). File khác trong `assets/` vẫn làm cổng không đạt.
- Ngân sách gate hành vi là 1.800 giây. CI Windows/Python 3.12 đã chạy thành công bước hành vi trong 1.108 giây; build RC2 đầu tại `30b7abe` hết 900 giây và không tạo ZIP. Tăng ngân sách giữ nguyên mọi test và điều kiện đạt; hết thời gian vẫn `failed`, không tạo artifact.
- ZIP không chứa timestamp: hai lần dựng từ cùng nguồn phải cho cùng SHA-256.

## 5. Quay lại khi nâng cấp (cho người dùng)

Trước khi nâng cấp, giữ một bản sao của project (mục 1 trong `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`). Để quay lại, dùng bản sao đó để khôi phục phần không phù hợp (mục 8 của cùng hướng dẫn). Công cụ nâng cấp mặc định chỉ báo cáo và không xóa file. Nếu nâng cấp bị gián đoạn giữa chừng, dùng `python tools/transaction.py resume|rollback <mã>` hoặc trang "Tình trạng ứng dụng" (mục 9). Bản tiếng Anh: `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`, mục 1, 8 và 9.

## 6. Giới hạn còn lại

- RC2 [v1.9.0-rc2](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc2), nguồn5335f68, đã công bố sau 4 gate cục bộ đạt. CI [39560119618](https://github.com/CVF-Ecosystem/local-agent-workspace/actions/runs/39560119618) trên nguồn cũ901e1d1 hoàn tất với 1/5 job đạt (Ubuntu3.12); Windows3.12 hành vi đạt nhưng buildtimeout900,3.8/mac lỗi fixture. Nguồn RC2 sửa các fixture và budget1800. Các số liệu RC2/CI cũ ở đoạn này được giữ từ bản hướng dẫn trước, chưa đối chiếu lại nguồn sơ cấp trong lượt cập nhật này. Đây là lịch sử RC2; CI 39548822713 cũng có các job ma trận thất bại ở bước hành vi như bảng cũ ghi nhận. Kết quả CI RC4 ở mục 1 không xóa thất bại cũ. Không suy gate cục bộ thành hỗ trợ chính thức toàn ma trận.
- Quan sát GitHub ngày 04/11/2026: endpoint [`latest`](https://api.github.com/repos/CVF-Ecosystem/local-agent-workspace/releases/latest) trả tag `v1.8.0`, nhưng tiêu đề là `Local Agent Workspace v1.9.0` và asset có tên `local-agent-workspace-v1.9.0-rc2.zip`. Không suy phiên bản payload từ alias; người bảo trì đối chiếu đúng release, payload và SHA-256 của artifact trước khi dùng làm bằng chứng. Quan sát này không xác minh payload stable 1.8.0.
- macOS và Python 3.8 chưa được chạy trên máy phát triển này; không có Python 3.8 trên máy. CI không kiểm Python 3.8 trên macOS (image `macos-13` đã ngừng).
- Kiểm tương thích 3.8 là heuristic: `ast.parse(feature_version=(3, 8))` và một danh sách regex. Có thể bỏ sót (ví dụ `dict | dict`) hoặc báo nhầm. Kiểm chứng thật là CI chạy trên Python 3.8.
- Cổng hành vi có kiểm thử giao diện bảng điều khiển bằng trình duyệt khi Playwright và Chromium khả dụng; thiếu điều kiện thì các lớp browser test bị skip. Kết quả trên máy này không chứng minh đã chạy trên mọi host hoặc CI.
- ZIP không có chữ ký số và chưa được notarize. SHA-256 chỉ cho biết file có toàn vẹn, không xác thực người phát hành.
- `platform.release()` trên Windows 11 có thể trả về `10` (giới hạn của Python).
- Một số cổng không áp dụng cho gói đã phát hành (không có `tests/`). Công cụ không từ chối bản chính thức có cây làm việc bẩn; hãy xem `git.dirty` trong báo cáo.

---

# English

## 1. Official support matrix

Anything without evidence of a run is listed as unconfirmed. A CI configuration is not the same as a test run. The table records **historical RC4 evidence** for source `2552d7d`; it does not establish current HEAD or final support. CI [39985758160](https://github.com/CVF-Ecosystem/local-agent-workspace/actions/runs/39985758160) failed overall: 3/5 jobs passed and 2 failed.

| Operating system | Python | RC4 evidence and limits |
|---|---|---|
| Local Windows/NTFS | 3.11.9 | 4/4 gates passed; 1,622 tests, 6 skips (5 file symlinks, 1 non-Windows refusal). Not final. |
| Windows Server 2025 CI | 3.12.10 | Job passed; both test and gate build ran 1,622 tests with 48 skips each. The five file-symlink cases skipped locally passed here; this does not establish every environment or remove TOCTOU limits. |
| Windows CI | 3.8 | Job failed: 1 failure, 48 skips; support unconfirmed. |
| Ubuntu CI | 3.8 and 3.12 | Both jobs passed, with 447 skips per test run, including Windows-dependent and browser cases; this does not establish full Linux office-work support. |
| macOS CI | 3.12 | Job failed: 1 error, 447 skips; support unconfirmed. |
| Any other combination (for example Python 3.9, 3.10, 3.13) | — | Not tested in this RC4 evidence; do not infer support. |

A cell counts as officially supported only when its CI job has passed on the commit being released; skips and intended use still need review.

### Internal office Prototype and RC4

The Prototype matrix in the Vietnamese and English READMEs belongs to the exact source/artifact checked. RC4 is a published Windows DATAMOCK Prototype; it does not establish real-user usability, other hosts or official support on current HEAD. Five local file-symlink skips were observed passing on Windows/Python 3.12 CI at the exact RC4 source; do not infer all link types or environments pass. Preserve skips and cooperative limits in the report.

Before a V7 assignment, account for every milestone condition and gap under AGENTS rule10/roadmap section8.3. Guide or matrix changes after a candidate leave its gate valid only for the old snapshot; a new deliverable needs a gate for its own bytes and review of the relevant boundary. Reuse valid evidence in review without replaying office work just to reproduce proof.

A candidate from a dirty worktree is for internal checking, not a clean publication source. Publication still needs the operator's authority, a clean source, gates and the confirmed matrix below. Keep earlier candidates; do not replace published tags/assets or label an internal build a new public RC. Real-user feedback remains after Prototype/MVP as instructed.

## 2. Version policy

The version lives in `VERSION` (MAJOR.MINOR.PATCH), which is the single source.

- **MAJOR**: incompatible changes: layout of `.agent/` or the project folder, the `MANIFEST.sha256` format, the `local-agent-workspace/result-v1` envelope schema, or removing an existing command or flag.
- **MINOR**: backward-compatible additions: tools, skills, flags, gates, or new content sections.
- **PATCH**: fixes, documentation, or template updates that do not change project data formats.
- Each release needs a `CHANGELOG.md` entry whose heading matches `VERSION` (checked by `check_package`).
- A release candidate (`--rc N`) is a trial build: `VERSION` does not change and the ZIP name carries `-rcN`.
- Published preview: [v1.9.0-rc4](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc4) (prerelease, not final), source `2552d7d`; it is not the candidate for the current delta. Preserve published tags/assets. A future RC uses an unpublished number `N` after checking; no number or build/release authority is selected here.

## 3. Release checklist (RC, acceptance, official)

1. **Source**: bump `VERSION`, add the `CHANGELOG.md` entry, fix remaining version strings (`check_package` reports mismatches). Run `python tools/build_guides_html.py`.
2. **Source checks**: `python tools/check_package.py --release` and `python -B -m unittest discover -s tests -v` must both pass.
3. **Release candidate**: within the existing granted scope and after checking that `N` is unpublished, use `python tools/build_release.py --rc N` with `N` replaced by the selected number. Output in `dist/`: `local-agent-workspace-v<VERSION>-rcN.zip` plus `.gate.json` beside it. Do not reuse published tags/assets. Open the report; every gate should be `passed` and `git.dirty` should be `false`.
4. **Acceptance of the RC**: unzip the RC into a new folder; run `python tools/check_package.py --verify` (must exit 0); try upgrading a copy of a real project as in section 5; open the control panel on each platform you claim. Fix issues in the source and go back to step 1 with a new RC.
5. **Official**: `python tools/build_release.py` (no `--rc`). Keep the ZIP and its `.gate.json` together and record the SHA-256 in the release notes.

## 4. Quality gates and the gate report

`build_release.py` runs the gates before packaging. If any gate is `failed`, no ZIP is created: the tool exits with code 1, the envelope has `status: blocked` and `findings` lists the failed gates, and no gate report is written.

| Gate | What it checks |
|---|---|
| `package_check` | `check_package --release`: structure, clean release templates, bilingual pairs, version, and HTML matching Markdown |
| `python38_compat` | Heuristic Python 3.8 compatibility (see section 6) |
| `behaviour_tests` | `python -B -m unittest discover -s tests`; only in the source repository (when `tests/` exists) |
| `release_tree` | `check_package --release` on the temporary release tree; always runs, even with `--skip-check` |

Gate statuses: `passed`, `failed`, `skipped` (by `--skip-check`, or no `tests/` folder), `nested` (see below).

- `--skip-check` works only with `--rc N`. An official build refuses it (exit code 2). For an RC, the report marks the gates `skipped`.
- **Nested builds**: when `behaviour_tests` runs the test suite, it sets `LOCAL_AGENT_WORKSPACE_GATE_NESTED=1`. A build started from inside the test suite with this variable records `behaviour_tests` as `nested` and does not run the suite again, which prevents recursion. The other gates still run. `nested` is not `passed`.
- **Report** `<ZIP>.gate.json`, schema `local-agent-workspace/release-gate-v1`: `version`, `kind` (`official` or `rc`), `rc`, `skip_check`, `archive`, `archive_sha256`, `gates` (name, status, `duration_s`, `detail`), `platform` (`system`, `release`), `python`, `git` (`commit`, `dirty`; `null` when git is unavailable), `branding`, `generated_utc`.
- **Organization branding**: the logo, `assets/branding.json` and fonts in `assets/fonts/` of the source folder are packed into the ZIP; `assets/branding.js` is rebuilt from `branding.json`. The list is in `branding` in the report. These files are not in MANIFEST, so upgrades never overwrite them. Leave them out with `--no-branding` (for example a generic public build). Any other file in `assets/` still fails the gate.
- The behaviour gate budget is 1,800 seconds. The Windows/Python 3.12 CI behaviour step passed in 1,108 seconds; the first RC2 build at `30b7abe` exceeded 900 seconds and created no ZIP. The larger budget keeps every test and pass condition; timeout still means `failed` and no artifact.
- The ZIP contains no timestamps: two builds from the same source must produce the same SHA-256.

## 5. Rolling back an upgrade (for users)

Before upgrading, keep a copy of the project (section 1 of `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`). To roll back, use that copy to restore the parts that do not fit (section 8 of the same guide). The upgrade tool only reports by default and does not delete files. If an upgrade is interrupted, use `python tools/transaction.py resume|rollback <id>` or the "App status" page (section 9). Vietnamese version: `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`, sections 1, 8 and 9.

## 6. Remaining limits

- [v1.9.0-rc2](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc2), source5335f68, is published after 4 local gates passed. CI [39560119618](https://github.com/CVF-Ecosystem/local-agent-workspace/actions/runs/39560119618) on older source901e1d1 completed with 1/5 jobs passing (Ubuntu3.12); Windows3.12 behaviour passed but the build timed out at900s, while3.8/mac had fixture errors. RC2 fixes those fixtures and uses the1800s budget. The older RC2/CI figures in this paragraph are retained from the previous guide and were not rechecked against primary sources in this update. This is RC2 history; CI 39548822713 also had matrix jobs fail at the behaviour step as recorded in the earlier table. The RC4 CI results in section 1 do not erase the earlier failures. Local gates do not establish official support for the whole matrix.
- GitHub observation on 4 November 2026: the [`latest` endpoint](https://api.github.com/repos/CVF-Ecosystem/local-agent-workspace/releases/latest) returns tag `v1.8.0`, but the title is `Local Agent Workspace v1.9.0` and the asset is named `local-agent-workspace-v1.9.0-rc2.zip`. Do not infer the payload version from the alias; maintainers verify the exact release, payload and artifact SHA-256 before treating it as evidence. This observation does not verify a stable 1.8.0 payload.
- macOS and Python 3.8 have not been run on this development machine, which has no Python 3.8. CI does not test Python 3.8 on macOS (the `macos-13` image is retired).
- The Python 3.8 check is a heuristic: `ast.parse(feature_version=(3, 8))` plus a regex list. It can miss cases (for example `dict | dict`) or report false positives. Real verification is the Python 3.8 CI job.
- The behaviour gate includes browser tests for the control panel when Playwright and Chromium are available; browser test classes are skipped when those prerequisites are missing. Results on this machine do not establish runs on every host or in CI.
- The ZIP is not code-signed or notarized. The SHA-256 shows the file is intact, not who published it.
- `platform.release()` can return `10` on Windows 11 (a Python limitation).
- Some gates do not apply to a packaged copy (there is no `tests/` folder). The tool does not refuse an official build from a dirty working tree; check `git.dirty` in the report.
