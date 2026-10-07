# Local Agent Workspace v1.4

Workspace local cho công việc văn phòng với Claude, Codex, Gemini hoặc agent khác.

**Mở `START_HERE.html` để đọc bộ hướng dẫn tiếng Việt (hoặc `START_HERE.en.html` cho bản tiếng Anh; mỗi trang có nút chuyển ngôn ngữ).** Trang này mở trực tiếp
trong trình duyệt, không cần cài đặt, máy chủ, font trực tuyến hay kết nối mạng.

## Cách bắt đầu

Nếu bạn đang xem trang này trên GitHub, package chạy trên máy của bạn nên cần tải về trước:

1. Vào https://github.com/CVF-Ecosystem/local-agent-workspace/releases/latest và tải file `local-agent-workspace-v….zip` (bản gọn, chỉ gồm phần dành cho người dùng). Giải nén ra một thư mục.
2. Chạy `SETUP.bat` (Windows) hoặc `SETUP.command` (macOS); hoặc mở `START_HERE.html` và dùng form "Khởi tạo nhanh".
3. Mở thư mục đó bằng ứng dụng AI bạn dùng (Claude, Codex, Gemini...), rồi thử 3 bài trong `START_HERE.html`.

Dùng nút Code → Download ZIP của GitHub cũng được, nhưng bản đó còn kèm thư mục dành cho người duy trì.

## Dùng để làm gì?

Đây là thư mục mẫu để bắt đầu mỗi dự án công việc văn phòng với trợ lý AI theo cùng một chuẩn. Nó giúp AI nhớ bối cảnh
giữa các phiên (không phải giải thích lại), giữ file gọn và có luật làm việc rõ (không bịa số liệu, không ghi đè file gốc),
kèm mười ba skill cho việc thường gặp; giải nén ở máy nào cũng cùng chuẩn. Phần giới thiệu đầy đủ có ở đầu `START_HERE.html`.

Đọc tài liệu, soạn quy trình, biểu mẫu, báo cáo; xử lý bảng tính khi cần; tiếp tục
công việc qua nhiều phiên; tạo báo cáo HTML gọn nhẹ. Workspace giữ tài liệu và ngữ
cảnh dự án, còn agent lựa chọn cách làm phù hợp với yêu cầu.

Các hướng dẫn là gợi ý tác nghiệp, không phải quy trình bắt buộc cho mọi nhiệm vụ.
Việc nhỏ có thể làm trực tiếp; việc cần nguồn hoặc mẫu thì mở đúng phần hữu ích.
Đây không phải ứng dụng, framework agent hay bộ công cụ phát triển phần mềm.

## Bắt đầu

Giải nén toàn bộ ZIP, đổi tên thư mục thành tên project rồi mở `START_HERE.html`. Không làm việc
trực tiếp bên trong ZIP. Cách dễ nhất: bấm đúp `SETUP.bat` (Windows) hoặc `SETUP.command` (macOS); trình hướng dẫn hỏi vài câu rồi tự khởi tạo và điền `PROJECT.md`. Hoặc dùng lệnh (một lần, cần Python 3.8+; không cài thêm gì):

```text
python tools/init_project.py --name "Tên project" --lang vi
```

`--lang en` chuyển toàn bộ file hướng dẫn agent, skill và README sang tiếng Anh. Không có Python thì làm tay theo
`docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md`. Phiên bản package nằm trong `VERSION`.

- Dự án mới: `docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md` hoặc bản `.html` cùng tên.
- Dự án có sẵn và nâng cấp package: `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md` hoặc `.html`.
- Dùng hằng ngày: `docs/HUONG_DAN_SU_DUNG_VI.md` hoặc `.html`.
- Chọn và dùng skills: `docs/HUONG_DAN_SKILLS_VI.md` hoặc `.html`.

Các bản Markdown và HTML có cùng nội dung hướng dẫn. Agent có thể đọc Markdown,
không cần đọc thêm bản HTML. HTML dành cho người dùng, không phải context mặc định.

## Tài nguyên trong package

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

Mười ba skill nằm trong `skills/local/shared/`, được ghi là `AVAILABLE` trong
`.agent/SKILL_INDEX.md`. Agent chọn skill theo độ phù hợp, không ưu tiên cố định
native hay local. Không dùng skill cũng là lựa chọn hợp lệ.

Các mẫu HTML được viết riêng cho package, với dữ liệu minh họa có nhãn rõ ràng.
Không có template, script, font hoặc skill upstream nào được sao chép nguyên bộ.
Nguồn ý tưởng và phạm vi tham khảo được ghi trong `docs/NGUON_THAM_KHAO_VI.md`.

## Những file cần biết

```text
project/
├── START_HERE.html          Hướng dẫn cho người dùng (tiếng Việt)
├── START_HERE.en.html       Hướng dẫn cho người dùng (tiếng Anh)
├── SETUP.bat / SETUP.command  Bấm đúp để khởi tạo project (trình hướng dẫn tự chạy)
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
├── examples/demo-project/   Project mẫu (dữ liệu giả) để thử trong 10 phút
├── packs/                   Gói lĩnh vực (cài theo nhu cầu bằng tools/pack.py)
├── .agent/                  STATE, HANDOFF, INDEX, SKILL_INDEX, PENDING_LESSONS
├── skills/
│   ├── local/shared/        Mười ba skill và các mẫu đi kèm
│   ├── local/project/       Hướng dẫn riêng của dự án, nếu cần
│   ├── external/            Skill bên ngoài do người dùng thêm
│   └── inbox/               Chỗ tạm, không bắt buộc
├── references/              Nguồn và mẫu nghiệp vụ của bạn
├── working/                 Bản đang làm
├── output/                  Bản giao hiện hành
└── archive/                 Bản cũ cần giữ
```

## Phiên bản tiếng Anh và công cụ bảo trì

Thư mục `en/` chứa bản tiếng Anh của toàn bộ nội dung chỉ có tiếng Việt: file hướng dẫn agent
(`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `PROJECT.md`), ghi chú `.agent/`, mười ba skill kèm tài liệu,
mẫu và script, README các thư mục, và bản README tiếng Anh này. Tên file và thư mục giống hệt bản
tiếng Việt, chỉ khác ngôn ngữ nội dung, nên `python tools/init_project.py --lang en` chép đè `en/` lên
thư mục gốc (trừ `en/PROJECT_INSTRUCTIONS_SNIPPET.md`, dùng để dán vào hướng dẫn Project). Giữ nguyên
thư mục `en/`: các file tiếng Anh trỏ tới `en/PROJECT_INSTRUCTIONS_SNIPPET.md`. Xem thêm `en/README.md`.

Cẩm nang tiếng Anh nằm trong `docs/en/` và `START_HERE.en.html`.

`tools/build_guides_html.py` dựng lại các trang HTML (cả hai ngôn ngữ) từ Markdown khi bạn sửa hướng dẫn
trong `docs/` hoặc `docs/en/` (xem `tools/README.md`). Không cần dùng trong công việc văn phòng hằng ngày.

## Dùng với agent

Mở hoặc cấp quyền truy cập thư mục dự án trong ứng dụng bạn đang dùng. Khi agent
chưa biết workspace, có thể nói:

> Thư mục này dùng Local Agent Workspace. Tham khảo AGENTS.md và ngữ cảnh liên quan
> trong PROJECT.md. Dùng STATE nếu tiếp tục việc đang dở. Chọn công cụ và skill phù
> hợp nhất với yêu cầu; có thể làm trực tiếp khi đã đủ thông tin.

Tên file adapter không đảm bảo mọi ứng dụng tự nạp nó. `skills/local/shared/` là
thư viện file để agent tra cứu; package không tự cài các skill này vào danh mục native
của Claude, Codex hay Antigravity. Không thay đổi cấu hình toàn cục của các ứng dụng.

## Thử nhanh, nâng cấp và mở rộng

- Thử trong 10 phút với dữ liệu giả: `examples/demo-project/README.md`.
- Góp ý sau khi dùng: `docs/FEEDBACK_FORM_VI_EN.md` (phiếu chủ yếu tích chọn) hoặc GitHub Issues.
- Có bản mới của package: `python tools/upgrade_package.py` (so ba bên, không ghi đè việc của bạn; xem `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`).
- Kiến thức riêng của một lĩnh vực: gói lĩnh vực trong `packs/`, cài bằng `python tools/pack.py add <tên>`.
- Trước khi giao sản phẩm: `python tools/check_output.py <file>` và checklist trong `office-documents`.

## Giấy phép

MIT, xem `LICENSE`. Nội dung hướng dẫn, skill và mẫu đi cùng giấy phép này.

## Giữ nhẹ khi sử dụng

Chỉ tra nguồn và skill có ích. Chỉ cập nhật STATE khi có điều phiên sau cần biết.
Giữ tài liệu gốc; không tự tái tổ chức thư mục hoặc tạo thêm sản phẩm ngoài yêu cầu.
Bản chuẩn nằm ở project local không có nghĩa toàn bộ xử lý AI diễn ra offline.

Với dự án đang dùng, giữ nguyên STATE, nguồn, skills và hướng dẫn riêng; đối chiếu
các file trùng tên khi nâng cấp, không ghi đè toàn bộ bằng template mới.
