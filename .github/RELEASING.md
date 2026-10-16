# Phát hành Local Agent Workspace / Releasing Local Agent Workspace

Tài liệu cho người bảo trì kho nguồn. Thư mục `.github/` không vào gói phát hành.
Maintainer guide for the source repository. The `.github/` folder is never packaged.

---

# Tiếng Việt

## 1. Ma trận hỗ trợ chính thức

Ô nào chưa có bằng chứng chạy thì ghi là chưa xác nhận; cấu hình CI không được tính là đã kiểm thử.

| Hệ điều hành | Python | Trạng thái |
|---|---|---|
| Windows 11 | 3.11.9 | Đã chạy cục bộ ngày 2026-10-13: kiểm package, bộ kiểm thử hành vi, dựng RC và bản chính thức. Không nằm trong ma trận CI. |
| Windows (latest) | 3.8, 3.12 | Chỉ có trong CI (`.github/workflows/ci.yml`). Chưa chạy. |
| Ubuntu (latest) | 3.8, 3.12 | Chỉ có trong CI. Chưa chạy. |
| macOS (latest, Apple silicon) | 3.12 | Chỉ có trong CI. Chưa chạy. |
| Mọi tổ hợp khác (ví dụ Python 3.9, 3.10, 3.13) | — | Chưa kiểm thử, không phải hỗ trợ chính thức. |

Chỉ coi một ô là hỗ trợ chính thức khi job CI tương ứng đã chạy xanh trên commit sắp phát hành.

## 2. Chính sách phiên bản

Số phiên bản nằm trong `VERSION` (MAJOR.MINOR.PATCH). Đó là nguồn duy nhất.

- **MAJOR**: thay đổi không tương thích ngược: đổi cấu trúc `.agent/` hoặc thư mục project, đổi định dạng `MANIFEST.sha256`, đổi schema envelope `local-agent-workspace/result-v1`, bỏ lệnh hoặc cờ đã có.
- **MINOR**: thêm tương thích ngược: công cụ, skill, cờ, cổng kiểm, hoặc mục nội dung mới.
- **PATCH**: sửa lỗi, sửa tài liệu, cập nhật mẫu mà không đổi định dạng dữ liệu của project.
- Mỗi bản phát hành phải có mục trong `CHANGELOG.md` với tiêu đề khớp `VERSION` (`check_package` kiểm).
- Release candidate (`--rc N`) là bản thử để nghiệm thu: không đổi `VERSION`, tên ZIP có hậu tố `-rcN`.

## 3. Checklist phát hành (RC -> nghiệm thu -> chính thức)

1. **Nguồn**: nâng `VERSION`, thêm `CHANGELOG.md`, sửa các chuỗi phiên bản còn lại (`check_package` báo chỗ lệch). Chạy `python tools/build_guides_html.py`.
2. **Kiểm nguồn**: `python tools/check_package.py --release` và `python -B -m unittest discover -s tests -v` đều phải đạt.
3. **Release candidate**: `python tools/build_release.py --rc 1`. Kết quả nằm trong `dist/`: `local-agent-workspace-v<VERSION>-rc1.zip` và `.gate.json` cạnh nó. Mở báo cáo, kiểm mọi cổng là `passed` và `git.dirty` là `false`.
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
- ZIP không chứa timestamp: hai lần dựng từ cùng nguồn phải cho cùng SHA-256.

## 5. Quay lại khi nâng cấp (cho người dùng)

Trước khi nâng cấp, giữ một bản sao của project (mục 1 trong `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`). Để quay lại, dùng bản sao đó để khôi phục phần không phù hợp (mục 8 của cùng hướng dẫn). Công cụ nâng cấp mặc định chỉ báo cáo và không xóa file. Nếu nâng cấp bị gián đoạn giữa chừng, dùng `python tools/transaction.py resume|rollback <mã>` hoặc trang "Tình trạng ứng dụng" (mục 9). Bản tiếng Anh: `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`, mục 1, 8 và 9.

## 6. Giới hạn còn lại

- CI chưa chạy lần nào. Các ô chưa được xác nhận cho đến khi job xanh.
- macOS và Python 3.8 chưa được chạy trên máy phát triển này; không có Python 3.8 trên máy. CI không kiểm Python 3.8 trên macOS (image `macos-13` đã ngừng).
- Kiểm tương thích 3.8 là heuristic: `ast.parse(feature_version=(3, 8))` và một danh sách regex. Có thể bỏ sót (ví dụ `dict | dict`) hoặc báo nhầm. Kiểm chứng thật là CI chạy trên Python 3.8.
- Không có kiểm thử giao diện tự động (E2E) cho bảng điều khiển trong cổng này.
- ZIP không có chữ ký số và chưa được notarize. SHA-256 chỉ cho biết file có toàn vẹn, không xác thực người phát hành.
- `platform.release()` trên Windows 11 có thể trả về `10` (giới hạn của Python).
- Một số cổng không áp dụng cho gói đã phát hành (không có `tests/`). Công cụ không từ chối bản chính thức có cây làm việc bẩn; hãy xem `git.dirty` trong báo cáo.

---

# English

## 1. Official support matrix

Anything without evidence of a run is listed as unconfirmed. A CI configuration is not the same as a test run.

| Operating system | Python | Status |
|---|---|---|
| Windows 11 | 3.11.9 | Run locally on 2026-10-13: package check, behaviour test suite, RC and official builds. Not part of the CI matrix. |
| Windows (latest) | 3.8, 3.12 | CI configuration only (`.github/workflows/ci.yml`). Not run yet. |
| Ubuntu (latest) | 3.8, 3.12 | CI configuration only. Not run yet. |
| macOS (latest, Apple silicon) | 3.12 | CI configuration only. Not run yet. |
| Any other combination (for example Python 3.9, 3.10, 3.13) | — | Untested; not officially supported. |

A cell counts as officially supported only when its CI job has passed on the commit being released.

## 2. Version policy

The version lives in `VERSION` (MAJOR.MINOR.PATCH), which is the single source.

- **MAJOR**: incompatible changes: layout of `.agent/` or the project folder, the `MANIFEST.sha256` format, the `local-agent-workspace/result-v1` envelope schema, or removing an existing command or flag.
- **MINOR**: backward-compatible additions: tools, skills, flags, gates, or new content sections.
- **PATCH**: fixes, documentation, or template updates that do not change project data formats.
- Each release needs a `CHANGELOG.md` entry whose heading matches `VERSION` (checked by `check_package`).
- A release candidate (`--rc N`) is a trial build: `VERSION` does not change and the ZIP name carries `-rcN`.

## 3. Release checklist (RC, acceptance, official)

1. **Source**: bump `VERSION`, add the `CHANGELOG.md` entry, fix remaining version strings (`check_package` reports mismatches). Run `python tools/build_guides_html.py`.
2. **Source checks**: `python tools/check_package.py --release` and `python -B -m unittest discover -s tests -v` must both pass.
3. **Release candidate**: `python tools/build_release.py --rc 1`. Output in `dist/`: `local-agent-workspace-v<VERSION>-rc1.zip` plus `.gate.json` beside it. Open the report; every gate should be `passed` and `git.dirty` should be `false`.
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
- The ZIP contains no timestamps: two builds from the same source must produce the same SHA-256.

## 5. Rolling back an upgrade (for users)

Before upgrading, keep a copy of the project (section 1 of `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`). To roll back, use that copy to restore the parts that do not fit (section 8 of the same guide). The upgrade tool only reports by default and does not delete files. If an upgrade is interrupted, use `python tools/transaction.py resume|rollback <id>` or the "App status" page (section 9). Vietnamese version: `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`, sections 1, 8 and 9.

## 6. Remaining limits

- CI has not run yet. Every cell stays unconfirmed until its job passes.
- macOS and Python 3.8 have not been run on this development machine, which has no Python 3.8. CI does not test Python 3.8 on macOS (the `macos-13` image is retired).
- The Python 3.8 check is a heuristic: `ast.parse(feature_version=(3, 8))` plus a regex list. It can miss cases (for example `dict | dict`) or report false positives. Real verification is the Python 3.8 CI job.
- No automated UI (end-to-end) tests for the control panel are part of these gates.
- The ZIP is not code-signed or notarized. The SHA-256 shows the file is intact, not who published it.
- `platform.release()` can return `10` on Windows 11 (a Python limitation).
- Some gates do not apply to a packaged copy (there is no `tests/` folder). The tool does not refuse an official build from a dirty working tree; check `git.dirty` in the report.
