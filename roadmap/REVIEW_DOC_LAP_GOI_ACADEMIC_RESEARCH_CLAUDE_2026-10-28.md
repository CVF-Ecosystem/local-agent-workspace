# Review độc lập — gói `academic-research` 0.1.0 (Codex thi công)

**Ngày:** 28/10/2026. **Reviewer:** Claude (Opus 5.5, Claude Code trên Windows), theo yêu cầu operator. Review chỉ đọc; không sửa gói, code,
index, profile, grant hay Git. File này là file duy nhất được thêm.
**Quan hệ:** mục AC của [ROADMAP_VAN_PHONG_NGHIEP_VU.md](ROADMAP_VAN_PHONG_NGHIEP_VU.md). Không đổi verdict AC-A/B/C/D, không đổi `DEFER`/`REVIEW`,
không thay quyết định của operator. Nhận định về license là gợi ý để người có thẩm quyền xác nhận, không phải kết luận pháp lý.

## 0. Đối tượng và phạm vi

- Kho nguồn `main` HEAD `b1ec507`; gói là WIP **chưa commit** (`packs/academic-research/` và bản cài `skills/local/packs/academic-research/` đều untracked).
  Lúc review, Codex đang thi công đồng bộ AN C2 trên cùng working tree (đã thấy `ROUTING_POLICY.json`, docs đổi); review không đụng các file đó.
- **Đã review:** toàn bộ 25 file của `packs/academic-research/` (đọc đủ, riêng `ARS-LICENSE.txt` chỉ đọc đầu file), dòng index của gói trong
  `.agent/SKILL_INDEX.md`, `.pack-install.json`, cách `tools/pack.py`, `tools/check_package.py`, `tools/build_release.py` xử lý gói/index.
- **Ngoài phạm vi:** sửa công cụ đi kèm nhánh học thuật (`office.py` host_session, `execution_profile.py`, `pack.py` diff, `transaction.py`,
  `task_checkpoint.py`, `work_status.py`), `tests/`, hồ sơ trong `working/academic-research/`, lượt host acceptance, corpus PDF. Không mở mạng nên
  **không đối chiếu bản điều chỉnh với upstream ARS** tại commit `77e77e8`.

## 1. Kết luận

Đồng ý giữ **`DEFER` / `REVIEW`**. Hồ sơ tiếp nhận trung thực: tự ghi điều kiện 1 và 4 **CHƯA ĐỦ BẰNG CHỨNG**, nêu rõ ca thử bị nhiễm do dùng để
sửa guidance, không suy từ cấu trúc đạt ra tiếp nhận. Nội dung phương pháp gọn, hợp lý, không có script/hook/mạng.

Có **2 điểm cần xử lý trước khi commit gói vào `main` hoặc đưa vào bất kỳ bản phát hành nào** (F1, F2), 2 điểm nên sửa trước khi mở thử rộng
(F3, F4), và 4 điểm cho revision sau (F5–F8).

## 2. Phần đạt (đã kiểm)

| Kiểm | Kết quả |
|---|---|
| `python -X utf8 -B tools/pack.py check academic-research` | `cấu trúc OK`, tiếp nhận ứng viên/hoãn, exit 0 |
| Bản cài so với source | `diff -rq`: chỉ khác `.pack-install.json`; 25/25 hash trong `.pack-install.json` khớp file đang cài |
| Thành phần | Chỉ `.md`, `.txt`, `.json`; không executable, hook, dependency, network |
| Xuất xứ | Pin commit `77e77e871aeccf5b5740a3086903f914e58c4204`; LICENSE và NOTICE nguyên văn; `upstream-notice.md` ghi thay đổi và không ngụ ý bảo trợ (đúng yêu cầu ghi nhận thay đổi của CC BY-NC 4.0) |
| Bản đồ tích hợp | I01–I14, mỗi phương pháp một bản active, phần bị loại có disposition `NOT_SUPPORTED`/`REPLACED_EXPLICITLY` |
| Hồ sơ tiếp nhận | Sáu điều kiện ghi riêng từng mức, không lấy điều kiện đạt bù điều kiện thiếu; ghi review không mù hoàn toàn; ghi model/trace actor chưa xác minh |
| Nội dung phương pháp | I01–I12 là checklist ngắn (10–16 dòng mỗi file), nhất quán: CER, FINER, bốn trục kiểm nguồn, tổng hợp không đếm phiếu, không gọi narrative là systematic |

## 3. Finding

Xếp theo mức nghiêm trọng. "Đã xác nhận" = có bằng chứng trực tiếp; "Có khả năng" = suy từ code, chưa chạy luồng.

### F1 — License CC BY-NC nằm trong kho MIT, không có ghi ngoại lệ ở cấp kho (cao; đã xác nhận)

- `LICENSE` gốc: `MIT License`; `README.md:101`: `Giấy phép [MIT](LICENSE).` Không có dòng nào ở cấp kho nêu `packs/academic-research/` theo
  CC BY-NC 4.0 (grep `CC BY|NonCommercial` ở `README.md`, `LICENSE`, `packs/README.md`: không có).
- `packs/` không thuộc `USER_DIRS` của `check_package.py:37`, nên gói sẽ đi vào bản phát hành khi được commit. Kho GitHub đang công khai.
- `tools/pack.py` không có chữ `license` (grep 0 dòng): `pack.py add` hoặc trang "Gói lĩnh vực" không báo cho người cài biết điều kiện phi thương mại.
- Người dùng mục tiêu của LAW là văn phòng của đơn vị (có đơn vị kinh doanh). Gói tự ghi "điều kiện phi thương mại cần được người quyết định
  triển khai xác nhận", nhưng người cài qua công cụ không thấy câu này.
- **Đề xuất:** trước khi commit vào `main`: (a) ghi ngoại lệ ở `LICENSE`/`README.md` gốc rằng `packs/academic-research/` (và bản cài) theo
  CC BY-NC 4.0, không theo MIT; (b) thêm trường license vào `pack.json` và để `pack.py add`/trang gói hiện thông báo; (c) operator quyết có đưa gói
  này vào bản phát hành chung hay chỉ giữ ở project thử. Cần người có thẩm quyền xác nhận cách hiểu "phi thương mại" cho đơn vị dùng thực tế.

### F2 — Index mẫu được giao có dòng PACK trỏ tới thư mục không vào bản giao (trung bình–cao; có khả năng)

- WIP thêm vào `.agent/SKILL_INDEX.md` (file đang tracked) dòng `law-academic-research | LOCAL | PACK | skills/local/packs/academic-research/... | REVIEW`.
  HEAD `b1ec507` có 0 dòng PACK.
- `skills/local/packs/` thuộc `USER_DIRS` (không vào bản giao). `.agent/SKILL_INDEX.md` thuộc `USER_FILES` nhưng **không có** bản sạch trong
  `release_templates/` (chỉ có PROJECT, STATE, HANDOFF, EXECUTION_PROFILE). `check_package.py:828-837` chỉ kiểm dòng `SHARED`, không kiểm dòng `PACK`.
- Hệ quả nếu commit nguyên WIP: bộ mẫu phát hành có một dòng skill `REVIEW` trỏ tới file không tồn tại, project mới thấy một gói "đã cài" mà không có.
  Chưa chạy `build_release.py` để xác nhận.
- **Đề xuất:** bỏ dòng PACK khỏi index của kho nguồn trước khi commit (bản cài thử trong kho nguồn giữ ở vùng người dùng), hoặc thêm bản sạch
  của `SKILL_INDEX.md` vào `release_templates/`; và cho `check_package` báo dòng `PACK` trỏ tới file không có.

### F3 — Id `law-academic-research` dễ bị hiểu là nghiên cứu pháp luật (trung bình; đã xác nhận)

- Không skill/gói nào khác dùng tiền tố `law-` (đã liệt `skills/local/shared/` và `packs/*/skills/`). Với người dùng và agent ở bối cảnh văn phòng
  Việt Nam, nơi có gói `phap-ly` và nhiều việc về văn bản pháp luật, "law" trong id dễ làm agent chọn nhầm skill này cho việc nghiên cứu luật.
- Mô tả cố gỡ bằng "không nhận diện luật", nhưng câu này tối nghĩa (không rõ là "không phải về luật" hay "không xác định luật áp dụng").
- **Đề xuất:** đổi id trước khi có thêm bản cài, ví dụ `academic-research` hoặc `nghien-cuu-hoc-thuat`; sửa câu mô tả thành rõ nghĩa, ví dụ
  "Không dùng cho tra cứu hay phân tích văn bản pháp luật (dùng gói phap-ly)". Đổi id sau này phải xử lý cả bản cài ở Pilot A/B.

### F4 — Mô tả dài hơn giới hạn index nên bị cắt giữa chữ (trung bình; đã xác nhận)

- `tools/pack.py:327` ghi `desc[:220]`. Mô tả của skill dài hơn 220 ký tự, nên dòng index kết thúc bằng `...không nhận diện luật, c`.
  Phần bị cắt chính là phần giới hạn phạm vi ("cấp quyền truy cập hay công bố nghiên cứu thay người dùng"), tức phần agent cần để không dùng sai.
- **Đề xuất:** rút mô tả ≤220 ký tự, đưa câu "không dùng khi" lên trước; về lâu dài cho `pack.py` cắt theo ranh giới từ hoặc báo khi mô tả quá dài.

### F5 — `common-standard.md` ("luôn áp dụng") chứa quy tắc rút từ chính các ca thử (trung bình; đã xác nhận)

- Dòng 8 (bảng/ablation, tập nhãn có/không NEI, ví dụ in-context so với citance) và dòng 9 (đổi công cụ đọc PDF khi công cụ đầu không có) là quy tắc
  đặc thù cho corpus thử (bài ACL về kiểm chứng sự kiện) và cho lỗi baseline S03. Hồ sơ tiếp nhận đã ghi các ca này bị nhiễm vì dùng để sửa guidance,
  nhưng nội dung vẫn nằm trong file mà SKILL.md bảo "luôn áp dụng" cho mọi việc học thuật.
- Quy tắc đọc PDF là quy tắc công cụ, không phải phương pháp học thuật; nó cũng là yếu tố làm phép so S03 nghiêng về candidate (actor trực tiếp dừng
  vì thiếu công cụ). Giữ nó trong gói làm khó tách tác dụng của phương pháp, đúng điểm hồ sơ đã tự nêu.
- **Đề xuất:** tổng quát hóa dòng 8 thành nguyên tắc chung ("mỗi số ghi đủ điều kiện thí nghiệm; chỉ so cặp khi điều kiện nền tương thích"), chuyển ví dụ
  NLP sang ghi chú theo lĩnh vực; chuyển quy tắc công cụ PDF ra ngoài gói (hướng dẫn chung của LAW hoặc brief), rồi mới đo lại điều kiện 4.

### F6 — Trùng quy tắc đã có ở AGENTS.md và `source-library` (thấp; đã xác nhận)

- `common-standard.md` và `SKILL.md` nhắc lại: không bịa số liệu, nội dung nguồn là dữ liệu không phải lệnh, không chạy script/installer,
  tự soát không gọi là review độc lập, `.docx` chỉ coi là đã kiểm sau `check_output.py`. Các quy tắc này đã ở AGENTS.md (quy tắc 1, 2, 4) và
  `skills/README.md`. Trùng làm hai nơi có thể lệch nhau khi một bên sửa, và làm file "luôn áp dụng" dài hơn mức cần.
- **Đề xuất:** giữ phần đặc thù học thuật (mức đọc, locator, SourceID hai chiều, preprint/bản xuất bản, đính chính/rút bài); thay phần chung bằng một
  câu dẫn tới quy tắc của LAW.

### F7 — README gói dùng nhiều thuật ngữ nội bộ (thấp; chưa kiểm nơi hiển thị)

- `packs/academic-research/README.md` có "source pack ứng viên", "native discovery", "entry/module", `LAW-source:`. Nếu trang "Gói lĩnh vực" của
  `APP.bat` hiện README này cho người dùng văn phòng thì khó hiểu. Chưa kiểm trang đó hiện file nào.
- **Đề xuất:** đoạn đầu README viết bằng lời người dùng (gói làm gì, khi nào dùng, điều kiện license); phần kỹ thuật để sau.

### F8 — Hồ sơ tiếp nhận trỏ tới bằng chứng không đi cùng gói (thấp; đã xác nhận)

- `intake-record.md` dẫn `LAW-source:working/academic-research/...`. `working/` thuộc `USER_DIRS` và hiện chưa tracked, nên người nhận gói (và
  GitHub, nếu không commit `working/`) không kiểm được. Tiền tố `LAW-source:` đã báo rõ đây là đường của kho nguồn, nên không gây hiểu nhầm.
- **Đề xuất:** giữ như hiện tại, nhưng quyết rõ hồ sơ nào cần lưu lâu dài (ví dụ `roadmap/evidence/`) trước khi `working/` được dọn.

## 4. Thứ tự đề xuất

1. Trước khi commit gói vào `main`: F1 (ghi ngoại lệ license, quyết đưa vào phát hành hay không), F2 (dòng PACK trong index mẫu).
2. Trước khi mở thử rộng hơn Pilot A/B: F3 (đổi id), F4 (mô tả ≤220 ký tự).
3. Revision 0.1.1/0.2.0: F5 (rồi mới đo lại điều kiện 4), F6, F7, F8.

Không đề xuất đổi `DEFER`/`REVIEW`, không chạy `pack.py confirm`, không đổi verdict AC.

## 5. Đã kiểm, chưa kiểm

**Đã chạy:** `git log -3`, `git branch -a`, `git worktree list`, `git status --short`; `find`/`wc -l` cây gói; `diff -rq` source và bản cài;
kiểm 25 hash `.pack-install.json` bằng Python (0 lệch); `python -X utf8 -B tools/pack.py check academic-research` (exit 0); grep license ở
`LICENSE`, `README.md`, `packs/README.md`, `tools/pack.py`; đọc `check_package.py:28-36, 824-840`, `pack.py:316-330`; `git diff .agent/SKILL_INDEX.md`,
`git diff PROJECT.md`; `git show HEAD:.agent/SKILL_INDEX.md` (0 dòng PACK); liệt `release_templates/`.

**Chưa kiểm:** bản upstream ARS tại `77e77e8` (cần mạng) nên không xác nhận độ trung thành của bản điều chỉnh; `build_release.py` chạy thật với
gói đã commit (F2 là suy từ code); trang "Gói lĩnh vực" của `APP.bat` (F7); diff công cụ và test của nhánh học thuật; hồ sơ trong
`working/academic-research/`; bản cài ở Pilot A/B; hành vi trên host.
