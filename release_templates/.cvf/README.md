# Kiểm soát điều phối (candidate v3) / Orchestration controls (candidate v3)

**Trạng thái / Status: CANDIDATE_NOT_ACTIVE.** Bản này mang một runtime duy nhất, v3, ở dạng ứng viên. Nó **không** tự kích hoạt,
không cấp quyền (grant) và không chặn thao tác nào của máy; mức bảo đảm là hợp tác/ADVISORY.
This package carries exactly one runtime, v3, as a candidate. It does **not** activate itself, grants nothing and blocks nothing on the machine; the assurance level is cooperative/ADVISORY.

## Tiếng Việt

**Có gì trong thư mục này**

- `rules/v3/CONTROL_RULES.md`: quy tắc sản phẩm cho việc giao vai và tác động; `rules/v3/ROUTING_POLICY.json`: bảng routing.
- `contracts/v3/CONTROL_CONTRACT.md` và `contracts/v3/control.schema.json`: hợp đồng task/review/result và JSON Schema.
- `checks/control_check_v3.py` cùng thư mục `checks/v3/`: checker chỉ đọc cho luồng một file mới (P-CN1). Checker không cấp quyền; kết quả PASS chỉ là kết quả hợp tác (ADVISORY).
- Không có trong bản này: runtime hay phiên bản khác, ví dụ/vectors kiểm thử, bằng chứng đánh giá, dữ liệu vận hành (`.agent/runtime`), grant hay verdict review của người bảo trì.

**Luồng đã được nhận (có giới hạn)**: tạo một file nháp mới trong `working/` hoặc `output/` bằng `tools/publish_new.py`, ghi chú vận hành STATE/HANDOFF bằng `tools/context_update.py`,
chọn và mở "Nháp hiện tại" bằng `tools/current_draft.py` hoặc bảng điều khiển. Việc chọn/mở bản không phải nghiệm thu.

**Điều kiện chạy** (kiểm bằng đúng Python đang chạy bảng điều khiển; bảng "Tình trạng ứng dụng" hiện kết quả):

- Windows, ổ NTFS cục bộ (không phải ổ mạng, đồng bộ đám mây hay ổ rời). Nơi khác, thẻ Nháp hiện tại báo không dùng được và không làm gì.
- Python có thư viện `jsonschema` từ 4.18 trở lên (Draft 2020-12). Thiếu hoặc quá cũ thì tính năng này báo không dùng được; các phần khác của workspace vẫn chạy.
  Công cụ **không tự cài** gì. Nếu cần, tự cài vào đúng Python hoặc venv của dự án rồi mở lại bảng điều khiển, ví dụ `python -m pip install "jsonschema>=4.18"`.
- Hai owner `tools/publish_new.py` và `tools/context_update.py` phải đúng từng byte với pin trong `rules/v3/ROUTING_POLICY.json`. File đã sửa tay hoặc đổi dòng kết thúc sẽ bị từ chối.

**Quyền**: file ở đây không phải nguồn cấp quyền. Quyền do người dùng cấp trong phiên; STATE/HANDOFF/PROJECT không tự cấp. Agent không tự mở rộng quyền hay hạ yêu cầu review.

**Nâng cấp**: nâng cấp chỉ được thêm candidate này khi dự án chưa có `.cvf`, hoặc cập nhật khi `.cvf` đã là đúng closure v3 này (cùng byte máy đọc). Dự án có `.cvf` khác (phiên bản cũ, thiếu file, đã sửa) được giữ nguyên toàn bộ và bị chặn kèm giải thích; không có tự động chuyển đổi.

## English

**What is in this folder**

- `rules/v3/CONTROL_RULES.md`: product rules for delegating to roles and for effects; `rules/v3/ROUTING_POLICY.json`: the routing table.
- `contracts/v3/CONTROL_CONTRACT.md` and `contracts/v3/control.schema.json`: the task/review/result contract and its JSON Schema.
- `checks/control_check_v3.py` with the `checks/v3/` folder: a read-only checker for the one-new-file flow (P-CN1). It grants nothing; a PASS is a cooperative (ADVISORY) result only.
- Not in this package: any other runtime or version, test examples/vectors, evaluation evidence, operational data (`.agent/runtime`), maintainers' grants or review verdicts.

**Accepted flow (with limits)**: create one new draft file under `working/` or `output/` with `tools/publish_new.py`, write STATE/HANDOFF notes with `tools/context_update.py`,
choose and open the "Current draft" with `tools/current_draft.py` or the control panel. Selecting or opening a draft is not acceptance.

**Requirements** (checked with the exact Python that runs the control panel; the "App status" page shows the result):

- Windows with a local NTFS drive (not a network drive, cloud-synced folder or removable drive). Elsewhere the Current draft card reports unavailable and does nothing.
- A Python with the `jsonschema` library 4.18 or newer (Draft 2020-12). If it is missing or too old this feature reports unavailable; the rest of the workspace keeps working.
  Nothing is installed for you. If you need it, install it yourself into the Python or venv this project uses, then reopen the panel, for example `python -m pip install "jsonschema>=4.18"`.
- `tools/publish_new.py` and `tools/context_update.py` must match the pins in `rules/v3/ROUTING_POLICY.json` byte for byte. A hand-edited file, or one with changed line endings, is refused.

**Authority**: nothing here grants authority. The user grants it in the session; STATE, HANDOFF and PROJECT never do. An agent does not widen a grant or lower a review requirement.

**Upgrade**: an upgrade adds this candidate only when the project has no `.cvf`, or updates it when `.cvf` already is exactly this v3 closure (same machine-read bytes). A project whose `.cvf` is different (an older version, missing files, edited) is left untouched and blocked with an explanation; there is no automatic migration.
