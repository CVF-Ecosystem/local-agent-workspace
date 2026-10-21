# Bằng chứng mô phỏng kịch bản nghiệm thu — 2026-10-17

Thư mục này là bằng chứng cho mục 3 và mục 4 của [BAO_CAO_KIEM_THU_VA_DANH_GIA_2026-10-17.md](../../BAO_CAO_KIEM_THU_VA_DANH_GIA_2026-10-17.md). Agent sau đọc các file kết quả và log ở đây để kiểm lại đánh giá, không cần chạy lại hay viết lại gì.

Bản mô phỏng dùng dữ liệu giả và Chromium headless. Đây không phải nghiệm thu người thật.

## Tệp

| Tệp | Nội dung |
|---|---|
| `journey.py` | Chạy ba nhiệm vụ của kịch bản qua bảng điều khiển thật (`tools/app.py`), theo `roadmap/KICH_BAN_NGHIEM_THU_NGUOI_DUNG.md` mục 2.2–2.4 và 3. Khôi phục ngày 2026-10-17 từ nội dung đã chạy lần đầu; xem mục "Cảnh báo". |
| `errors2.py` | Hai ca lỗi qua giao diện (nâng cấp từ thư mục không tồn tại; kiểm file không tồn tại). Bản `errors.py` chạy lần đầu lỗi import nên không dùng. |
| `measure.py` | Đo hộp kết quả và nút đóng ở 1280 px và 390 px. Import `errors2` từ thư mục scratch (xem "Cảnh báo"). |
| `lan-1-ban-dau/` | Kết quả chạy lần đầu: `result.json`, `errors.json`, bảy ảnh chụp; `full_suite.log` (129 ca test); `build_rc1.log` và `local-agent-workspace-v1.8.0-rc1.zip.gate.json` (cổng rc1). |
| `lan-2-chay-lai-tu-journey-da-khoi-phuc/` | Chạy lại bằng `journey.py` đã khôi phục, rồi `errors2.py` và `measure.py`: `journey.log`, `result.json`, `errors.json`, `errors2.log`, `measure.log`, ảnh chụp. |

Kiểm tra chéo: `steps` của `result.json` và `errors.json` ở lần 1 và lần 2 giống nhau từng bước (13 và 2 bước). Cả hai lần đều có 0 lỗi console, không tính 404 của favicon.

## Đầu vào (nằm trong thư mục scratch của phiên, đường dẫn cố định trong script)

Thư mục gốc: `C:\Users\DELL\AppData\Local\Temp\claude\d--UNG-DUNG-AI-TOOL-AI-2026-Controlled-Vibe-Framework-CVF\c10e50f7-d8b3-4ff6-9cec-4f49b976eb5e\scratchpad` (gọi là `S`).

- `S\ktnd\zip\local-agent-workspace-v1.8.0-rc1.zip`: tạo bằng `python tools/build_release.py --rc 1 --out <thư mục>`. Công cụ này cho ZIP tái lập được; SHA-256 `fcfed6d222ce7a092a07f2fd2ba81162057d06f51183505ae3de161035213800`.
- `S\ktnd\goi-moi\local-agent-workspace-v1.8.0`: giải nén ZIP vào đây, thêm dòng `Dòng mới từ gói phát hành (dữ liệu giả).` vào cuối `.agent/README.md`, rồi chạy `python tools/check_package.py --write-manifest`.
- `S\ktnd\du-lieu-gia\bien-ban-thu.txt`: ba dòng theo KICH_BAN mục 2.2.

Lệnh: `python -B journey.py`, sau đó `python -B errors2.py`, rồi `python -B measure.py`. Cần Python 3.8+ với `playwright` và Chromium (`python -m playwright install chromium`).

## Cảnh báo

- `journey.py` và `errors2.py` xóa rồi tạo lại `S\ui`. Đừng đặt script trong thư mục đó; lần đầu đã mất `journey.py` vì lỗi này.
- `measure.py` import `errors2` từ `S`, không từ thư mục này. Nếu `S` đã đổi, chép `errors2.py` vào `S` trước.
- Đường dẫn trong script là đường dẫn scratch của phiên 2026-10-17. Muốn chạy ở phiên khác, sửa hằng `S` và tạo lại các đầu vào ở trên.
- Script không đổi file nào trong kho. Đầu ra nằm trong `S\ui`.
