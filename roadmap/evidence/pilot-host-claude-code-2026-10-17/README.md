# Pilot: model và effort theo vai trên Claude Code — 2026-10-17

Written for: người phản biện (Codex) và người duy trì LAW, để kiểm lại kết luận trong mục 4b của `roadmap/DANH_GIA_ROADMAP_LAW_R2_VA_DE_XUAT_2026-10-17.md`.

## Môi trường

- Claude Code CLI **2.1.81** (`claude --version`). Đây là bản cũ hơn các bản mà tài liệu chính thức nhắc tới; kết quả chỉ áp dụng cho bản này.
- Phiên chính: `--model claude-sonnet-5-5`.
- Vai thử: khai báo qua `--agents` (JSON) với tên `scout`, chạy bằng `-p` trong thư mục scratch. Không đổi cấu hình toàn cục hay file trong kho.
- Dữ liệu giả: `data.txt` 7 dòng. Chữ `r` trong "strawberry rhythm arrangement" là 6.
- Mỗi lần chạy có ngân sách `--max-budget-usd` 0.5 hoặc 0.2.

## Kết quả

| Test | Cấu hình vai | Kết quả quan sát | Kết luận |
|---|---|---|---|
| A | `"model":"haiku"` | Subagent chạy bằng `claude-haiku-4-5-20251001`. Trả lời 8 cho file 7 dòng. | Định tuyến theo model **có hiệu lực**. Alias `haiku` ánh xạ tới model 4.5, không phải 5.5. |
| E | `"model":"haiku"`, chạy bằng `npx @anthropic-ai/claude-code@2.1.302` (không cài đè bản toàn cục) | Subagent chạy `claude-haiku-5-5`. Trả lời 8. | Trên bản mới nhất, alias `haiku` ánh xạ tới Haiku 5.5 (Anthropic API). Alias vẫn đổi theo phiên bản và nhà cung cấp. |
| B | `"model":"claude-haiku-5-5"` | Subagent chạy đúng `claude-haiku-5-5` (trường `model` trong stream và `modelUsage`). Trả lời 8. | ID đầy đủ được tôn trọng. Nên ghim ID đầy đủ, không dùng alias. |
| C | `"effort":"low"` và `"effort":"max"`, cùng prompt | Cả hai trả lời đúng 6. Token đầu ra subagent: 149 và 151. | CLI nhận trường mà không báo lỗi. **Không quan sát được ảnh hưởng của effort** trên tác vụ nhỏ này. Một cặp mẫu, chưa đủ kết luận. |
| D | `"effort":"ultra-bogus"`, và trường lạ `bogusField` | Không báo lỗi. Ghi chú: phiên không gọi vai nên có thể việc kiểm tra chỉ diễn ra khi gọi. | Khâu nạp cấu hình **không kiểm tra** giá trị effort. |

## Quan sát phụ về chất lượng

- Ở Test A và B, subagent đếm 8 cho file 7 dòng. Nguyên nhân: công cụ Read hiển thị một dòng trống thứ 8 cho file kết thúc bằng xuống dòng. Đây là lỗi phương pháp đếm, không phải lỗi năng lực model.
- Phiên chính trả về "8" nguyên văn, không kiểm lại. Đây là ví dụ cụ thể cho lý do cần bước kiểm của điều phối hoặc writer.
- Ở Test A, subagent gọi Read với tham số sai (`path` thay vì `file_path`), bị từ chối, rồi tự sửa. Model nhỏ có thể dùng sai công cụ nhưng tự phục hồi được trong trường hợp này.

## Chi phí

Tổng chi phí ghi trong các file: khoảng **0,357 USD**, gồm cả hai lần chạy Test A. Số liệu lấy từ trường `total_cost_usd`.

## Những gì chưa kiểm

- Effort có tác động thật không: cần tác vụ suy luận dài hơn, và có cách đo token suy nghĩ nếu CLI cung cấp.
- Các phiên bản CLI mới hơn (tài liệu mô tả effort cho vai; bản 2.1.81 chưa chứng minh được).
- Claude Desktop có nạp `.claude/agents/` không.
- Codex và Antigravity: chưa pilot, chỉ có tài liệu chính thức.

## Tái lập

Chạy từ thư mục chứa `data.txt`:

```text
claude -p "Hãy giao việc cho subagent scout: đếm số dòng của file data.txt trong thư mục hiện tại. Trả lời đúng một con số." --agents '{"scout":{"description":"Đếm số dòng của một file văn bản được giao","prompt":"Bạn chỉ đếm số dòng của file được giao. Đếm bằng cách đọc file rồi trả về đúng một con số.","model":"claude-haiku-5-5"}}' --model claude-sonnet-5-5 --output-format stream-json --verbose --max-budget-usd 0.5
```

Phân tích sự kiện: `python parse.py <file.jsonl>` (chạy với `PYTHONUTF8=1` trên Windows).
