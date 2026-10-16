# Local Trợ lý AI Workspace v1.8

Workspace local cho công việc văn phòng với Claude, Codex, Gemini hoặc trợ lý AI khác.

**Mở `START_HERE.html` để đọc bộ hướng dẫn tiếng Việt (hoặc `START_HERE.en.html` cho bản tiếng Anh; mỗi trang có nút chuyển ngôn ngữ).** Trang này mở trực tiếp
trong trình duyệt, không cần cài đặt, máy chủ, font trực tuyến hay kết nối mạng.

## Cách bắt đầu

1. **Giữ một bộ mẫu:** tải ZIP từ [Releases](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/latest), giải nén một lần ra thư mục riêng. Thư mục này là bộ mẫu: giữ nguyên, không làm việc trong đó (và không làm việc bên trong ZIP).
2. **Tạo dự án cho từng công việc:** bấm đúp `APP.bat` (Windows) hoặc `APP.command` (macOS) trong bộ mẫu, nhập tên công việc ở trang "Tạo dự án mới", bấm "Xem trước khi tạo" rồi "Thực hiện". Bản sao được tạo cạnh bộ mẫu và khởi tạo sẵn; bộ mẫu không đổi.
3. **Đặt nguồn và giao việc:** chép tài liệu vào `references/` của dự án, mở thư mục dự án bằng ứng dụng AI (Claude, Codex, Gemini), gửi lời nhắc sao chép từ bảng điều khiển của dự án (điền phần trong ngoặc vuông trước khi gửi). Kết quả nằm trong `output/`.
4. **Tiếp tục phiên sau:** mở `APP` trong thư mục dự án; ô "Tiếp tục công việc" cho biết việc đang ở đâu; lời nhắc "Xem lại việc đang dở" giúp trợ lý AI tóm tắt lại trước khi làm tiếp.

Bảng điều khiển cần Python 3.8+. Không có Python: sao chép cả thư mục bộ mẫu (kể cả thư mục ẩn `.agent/`), đổi tên, mở bằng ứng dụng AI; xem `docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md`. Kiểm tra Excel và thư viện nguồn cần thêm `openpyxl` (`python -m pip install openpyxl`); công cụ không tự cài. Muốn thử trước bằng dữ liệu giả: `examples/demo-project/README.md`, làm trong một dự án thử.

## Dùng để làm gì?

Đây là thư mục mẫu để bắt đầu mỗi dự án công việc văn phòng với trợ lý AI theo cùng một chuẩn. Nó giúp AI nhớ bối cảnh
giữa các phiên (không phải giải thích lại), giữ file gọn và có luật làm việc rõ (không bịa số liệu, không ghi đè file gốc),
kèm mười bốn skill cho việc thường gặp; giải nén ở máy nào cũng cùng chuẩn. Phần giới thiệu đầy đủ có ở đầu `START_HERE.html`.

Đọc tài liệu, soạn quy trình, biểu mẫu, báo cáo; xử lý bảng tính khi cần; tiếp tục
công việc qua nhiều phiên; tạo báo cáo HTML gọn nhẹ. Workspace giữ tài liệu và ngữ
cảnh dự án, còn trợ lý AI lựa chọn cách làm phù hợp với yêu cầu.

Các hướng dẫn là gợi ý tác nghiệp, không phải quy trình bắt buộc cho mọi nhiệm vụ.
Việc nhỏ có thể làm trực tiếp; việc cần nguồn hoặc mẫu thì mở đúng phần hữu ích.
Đây không phải ứng dụng, framework trợ lý AI hay bộ công cụ phát triển phần mềm.

## Thiết lập tùy chọn và hướng dẫn tra cứu

Ngoài bảng điều khiển còn hai đường cho cùng kết quả. `SETUP.bat` / `SETUP.command` hỏi đáp trong cửa sổ lệnh; chạy ở bộ mẫu thì nó hỏi tạo bản sao (khuyên dùng) hay khởi tạo chính thư mục này. Hoặc dùng lệnh trong bộ mẫu (cần Python 3.8+, không cài thêm gì):

```text
python tools/new_project.py --name "Tên công việc" --apply
```

Thêm `--dest` để chọn nơi tạo, `--lang en` để dùng bản tiếng Anh của hướng dẫn trợ lý AI, skill và README; bỏ `--apply` để chỉ xem trước. Đã tự sao chép thư mục thì khởi tạo trong bản sao bằng `python tools/init_project.py --name "Tên project"`. Phiên bản của bộ công cụ nằm trong `VERSION`.

Bảng điều khiển (`APP`) ở bộ mẫu chỉ làm một việc chính: tạo dự án mới. Ở dự án, trang **Công việc** gồm: tiếp tục công việc (đọc từ `.agent/STATE.md`), giao việc cho trợ lý AI (lời nhắc để sao chép), tài liệu nguồn và kết quả. Quản lý kỹ năng và gói bổ sung theo lĩnh vực, chép skill vào ứng dụng, cập nhật bộ công cụ, chờ hợp nhất, bảo trì và tình trạng ứng dụng nằm trong nhóm "Quản lý và bảo trì". Bảng điều khiển chỉ là giao diện cho các công cụ trong `tools/`, chạy trên máy (không dùng mạng), tự tắt khi đóng trang. Nếu một lần ghi bị gián đoạn, trang **Tình trạng ứng dụng** cho phép tiếp tục hoặc phục hồi (xem `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`, mục 9).

- Dự án mới: `docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md` hoặc bản `.html` cùng tên.
- Dự án có sẵn và nâng cấp bộ công cụ: `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md` hoặc `.html`.
- Dùng hằng ngày: `docs/HUONG_DAN_SU_DUNG_VI.md` hoặc `.html`.
- Chọn và dùng skills: `docs/HUONG_DAN_SKILLS_VI.md` hoặc `.html`.

Các bản Markdown và HTML có cùng nội dung hướng dẫn. Trợ lý AI có thể đọc Markdown,
không cần đọc thêm bản HTML. HTML dành cho người dùng, không phải context mặc định.

## Tài nguyên trong bộ công cụ

| Tài nguyên | Hữu ích khi |
|---|---|
| `office-documents` | Soạn/chỉnh tài liệu nghiệp vụ; tham khảo mẫu SOP, biểu mẫu, cập nhật nội bộ. |
| `html-reports` | Tạo báo cáo định kỳ hoặc trang tổng quan chỉ số bằng một file HTML. |
| `vietnamese-editing` | Biên tập tiếng Việt khi thật sự cần chỉnh văn phong; không tự chạy sau mọi tài liệu. |
| `document-comparison` | Đối chiếu hai phiên bản quy định/quy trình/biểu mẫu thành bảng thay đổi. |
| `spreadsheet-check` | Kiểm tra nhanh Excel/CSV trước khi lấy số cho báo cáo; không sửa file gốc. |
| `meeting-minutes` | Biên bản họp: quyết định, việc cần làm, vấn đề chưa chốt. |
| `process-mapping` | Bảng bước, RACI và sơ đồ luồng cho quy trình. |
| `internal-comms` | Báo cáo tiến độ, thông báo, bản tin, FAQ, báo cáo sự cố. |
| `doc-coauthoring` | Đồng soạn tài liệu lớn từng bước; chỉ dùng khi bạn muốn trao đổi sâu. |
| `data-charts` | Vẽ biểu đồ từ bảng số liệu thành HTML offline (SVG), có mẫu và hướng dẫn chọn biểu đồ. |
| `vn-admin-documents` | Văn bản hành chính đúng thể thức: công văn, tờ trình, báo cáo, thông báo. |
| `excel-workbooks` | Dựng sổ theo dõi, form nhập liệu, báo cáo tự tổng hợp và phụ lục tính bằng Excel. |
| `excel-html-viewer` | Công cụ HTML một file, offline, đọc file Excel để xem số liệu trực quan. |
| `source-library` | Thư viện nguồn trong `references/` (pháp luật, quy chế, mẫu biểu) với chỉ mục Excel; tra trước khi trích dẫn. |

Mười bốn skill nằm trong `skills/local/shared/`, được ghi là `AVAILABLE` trong
`.agent/SKILL_INDEX.md`. Trợ lý AI dùng năng lực và native skill sẵn có; skill của bộ công cụ chỉ
bổ sung phần còn thiếu (mẫu, nguồn, quy tắc nghiệp vụ). Không dùng skill cũng là lựa chọn hợp lệ.
Thêm hay nhập skill, gói: theo chuẩn tiếp nhận ở `skills/README.md`.

Các mẫu HTML được viết riêng cho bộ công cụ, với dữ liệu minh họa có nhãn rõ ràng.
Không có template, script, font hoặc skill upstream nào được sao chép nguyên bộ.
Nguồn ý tưởng và phạm vi tham khảo được ghi trong `docs/NGUON_THAM_KHAO_VI.md`.

## Những file cần biết

```text
project/
├── START_HERE.html          Hướng dẫn cho người dùng (tiếng Việt)
├── START_HERE.en.html       Hướng dẫn cho người dùng (tiếng Anh)
├── SETUP.bat / SETUP.command  Bấm đúp để tạo hoặc thiết lập dự án (trình hướng dẫn hỏi đáp)
├── APP.bat / APP.command      Bảng điều khiển trong trình duyệt (tùy chọn)
├── README.md
├── AGENTS.md                Hướng dẫn chung cho agent
├── PROJECT.md               Ngữ cảnh ổn định của dự án
├── CLAUDE.md / GEMINI.md     Adapter mỏng, tùy môi trường
├── en/                      Cây tiếng Anh, chép đè lên thư mục gốc bởi init --lang en
├── tools/                   Khởi tạo, nâng cấp, gói lĩnh vực, kiểm tra đầu ra, kiểm tra package, đóng gói, dựng HTML
├── CHANGELOG.md
├── LICENSE                  Giấy phép MIT
├── VERSION                  Số phiên bản package (một nguồn duy nhất)
├── MANIFEST.sha256          Mã băm các file của package, để kiểm tra nguyên vẹn
├── docs/                    Hướng dẫn Markdown + HTML, bảng thuật ngữ Việt–Anh
├── examples/demo-project/   Bài thực hành (dữ liệu minh họa) để thử trong 10 phút
├── packs/                   Gói lĩnh vực (cài theo nhu cầu bằng tools/pack.py)
├── .agent/                  STATE, HANDOFF, INDEX, SKILL_INDEX, PENDING_LESSONS
├── skills/
│   ├── local/shared/        Mười bốn skill và các mẫu đi kèm
│   ├── local/project/       Hướng dẫn riêng của dự án, nếu cần
│   ├── external/            Skill bên ngoài do người dùng thêm
│   └── inbox/               Chỗ tạm, không bắt buộc
├── references/              Nguồn và mẫu nghiệp vụ của bạn
├── working/                 Bản đang làm
├── output/                  Bản giao hiện hành
└── archive/                 Bản cũ cần giữ
```

## Phiên bản tiếng Anh và công cụ bảo trì

Thư mục `en/` chứa bản tiếng Anh của toàn bộ nội dung chỉ có tiếng Việt: file hướng dẫn trợ lý AI
(`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `PROJECT.md`), ghi chú `.agent/`, mười bốn skill kèm tài liệu,
mẫu và script, README các thư mục, và bản README tiếng Anh này. Tên file và thư mục giống hệt bản
tiếng Việt, chỉ khác ngôn ngữ nội dung, nên `python tools/init_project.py --lang en` chép đè `en/` lên
thư mục gốc (trừ `en/PROJECT_INSTRUCTIONS_SNIPPET.md`, dùng để dán vào hướng dẫn Project). Giữ nguyên
thư mục `en/`: các file tiếng Anh trỏ tới `en/PROJECT_INSTRUCTIONS_SNIPPET.md`. Xem thêm `en/README.md`.

Cẩm nang tiếng Anh nằm trong `docs/en/` và `START_HERE.en.html`.

`tools/build_guides_html.py` dựng lại các trang HTML (cả hai ngôn ngữ) từ Markdown khi bạn sửa hướng dẫn
trong `docs/` hoặc `docs/en/` (xem `tools/README.md`). Không cần dùng trong công việc văn phòng hằng ngày.

## Dùng với trợ lý AI

Mở hoặc cấp quyền truy cập thư mục dự án trong ứng dụng bạn đang dùng. Khi trợ lý AI
chưa biết workspace, có thể nói:

> Thư mục này dùng Local Trợ lý AI Workspace. Tham khảo AGENTS.md và ngữ cảnh liên quan
> trong PROJECT.md. Dùng STATE nếu tiếp tục việc đang dở. Chọn công cụ và skill phù
> hợp nhất với yêu cầu; có thể làm trực tiếp khi đã đủ thông tin.

Tên file adapter không đảm bảo mọi ứng dụng tự nạp nó. `skills/local/shared/` là
thư viện file để trợ lý AI tra cứu; bộ công cụ không tự cài các skill này vào danh mục native
của Claude, Codex hay Antigravity. Không thay đổi cấu hình toàn cục của các ứng dụng.

## Thử nhanh, nâng cấp và mở rộng

- Thử trong 10 phút với dữ liệu minh họa: `examples/demo-project/README.md`.
- Góp ý sau khi dùng: `docs/FEEDBACK_FORM_VI_EN.md` (phiếu chủ yếu tích chọn) hoặc GitHub Issues.
- Có bản mới của bộ công cụ: `python tools/upgrade_package.py` (so ba bên, không ghi đè việc của bạn; xem `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`).
- Kiến thức riêng của một lĩnh vực: gói lĩnh vực trong `packs/`, cài bằng `python tools/pack.py add <tên>`.
- Trước khi giao sản phẩm: `python tools/check_output.py <file>` và checklist trong `office-documents`.

## Giấy phép

MIT, xem `LICENSE`. Nội dung hướng dẫn, skill và mẫu đi cùng giấy phép này.

## Giữ nhẹ khi sử dụng

Chỉ tra nguồn và skill có ích. Chỉ cập nhật STATE khi có điều phiên sau cần biết.
Giữ tài liệu gốc; không tự tái tổ chức thư mục hoặc tạo thêm sản phẩm ngoài yêu cầu.
Bản chuẩn nằm ở dự án local không có nghĩa toàn bộ xử lý AI diễn ra offline.

Với dự án đang dùng, giữ nguyên STATE, nguồn, skills và hướng dẫn riêng; đối chiếu
các file trùng tên khi nâng cấp, không ghi đè toàn bộ bằng template mới.
