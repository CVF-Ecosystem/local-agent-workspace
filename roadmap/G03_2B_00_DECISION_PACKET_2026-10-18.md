# G-03/2b-00 — gói quyết định hạ tầng và ranh giới

Ngày: 18/10/2026. Trạng thái Main: **SURVEY_REVIEWED_WITH_LIMITS; U-std CHANGES_REQUIRED**. Chỉ khảo sát và thiết kế; không code, cài đặt,
cấu hình host, tạo account, chạy lab hay model. Đầu vào: `roadmap/DESIGN_G03_2B_2026-10-18.md`
(ACCEPTED_FOR_READ_ONLY_DESIGN), `evidence/g03-2a-2026-10-18/LIVE_REVIEW.md`, `.cvf` contract/rules/checks,
`tools/transaction.py` (chỉ phần commit). Model Worker quan sát: `claude-sonnet-5-5` (theo phiên), effort không quan sát được.

**Review18/10:** xem [REVIEW_G03_2B_00_2026-10-18.md](REVIEW_G03_2B_00_2026-10-18.md).
Nội dung bên dưới là đề xuất Worker, chưa được nhận làm authority/kiến trúc cài đặt. Các đề xuất OPERATOR_ATTESTED,
writer P0, raw-byte binding và ADVISORY chưa thay contract/routing hiện tại; mandatory gates vẫn BLOCKED.
Mục9 chưa phải yêu cầu operator phê duyệt; không mở code/account/admin. Không giao thêm vòng U-std mặc định.

## 0. Kết luận (terminal khảo sát, không phải proof)

**Một ứng viên chưa được nhận, phạm vi thu hẹp: "P0 — vùng gốc tin cậy của quản trị do account OS khác sở hữu".**
Chưa có đường được chứng minh cho claim rộng "cưỡng chế named effect lên tài liệu người dùng" trong ràng buộc khảo sát:
cho cả hai, xem 0.1 và 0.2. Chọn hay không chọn là quyết định của operator (mục 9); không chọn thì kết quả là 0.2.

### 0.1 Đường đề xuất — `U-std` (OS account boundary cho P0)

- **Claim hẹp được hỗ trợ, nếu mọi điều kiện ở mục 9 được chấp nhận:** Main/vai phụ, dù có shell/script/Office/MCP
  tùy ý dưới account làm việc **không phải admin**, không thể ghi/xóa/đổi vùng P0 (grant, receipt, role acceptance,
  EXECUTION_PROFILE, bản policy/schema/checker đã cài) mà không qua một tiến trình khác account, nâng quyền qua
  prompt thông tin đăng nhập admin trên secure desktop và xác nhận trong cửa sổ của chính tiến trình đó.
- **Cơ chế:** Windows user boundary (ACL do account khác sở hữu) + secure-desktop credential prompt + UIPI. Không dùng
  Claude Code managed settings, hook, MCP, daemon, service, cloud, Team plan. Không phụ thuộc host: cùng bảo vệ cho Codex/Gemini
  chạy dưới account làm việc đó.
- **Ngoại lệ hạ tầng tối thiểu cần operator quyết (chi tiết mục 9):** (X1) một account Windows *standard* riêng cho công việc LAW
  được bảo vệ — không hạ quyền account `DELL`, không đụng CVF; (X2) một lần thao tác admin để tạo thư mục cài đặt chỉ-admin-ghi
  và ACL cho P0; (X3) một thành phần "helper xác nhận-và-ghi" bản phát hành, chạy theo lần (không chạy nền), kèm interpreter đóng gói
  đặt trong thư mục chỉ-admin-ghi; (X4) mỗi lần ghi P0 phải có một prompt thông tin đăng nhập admin.
- **Không thay đổi so với hiện trạng:** shell/script tự do của Main trong account làm việc; mặc định văn phòng; native skill.

### 0.2 Không khả thi trong ràng buộc hiện tại — `NO_FEASIBLE_PATH_WITH_CURRENT_CONSTRAINTS` cho claim rộng

Claim: "gate cưỡng chế R-MUTATION/R-HIGH_STAKES/R-EXTERNAL... trên file nguồn/tài liệu người dùng, cả Main lẫn vai phụ".
Ràng buộc hiện tại: cùng một danh tính OS người dùng; Main giữ shell/script/Office tùy ý; không account/VM/service mới;
Windows 11 Home (không Hyper-V/Windows Sandbox); không chính sách toàn máy ảnh hưởng CVF; user phổ thông.

| Stop gate | Căn cứ | Ràng buộc cần đổi để mở |
|---|---|---|
| **SG-1 Không có selector phiên LAW nằm ngoài Main** | Managed settings chỉ có phạm vi toàn máy (`C:\Program Files\ClaudeCode`) hoặc toàn organization (server-managed, cần Team/Enterprise, "uniform to all users", "not a security boundary", bỏ qua nếu đặt provider khác/`ANTHROPIC_BASE_URL`). Project/user/local settings Main sửa được và nạp lại khi đang chạy. | Môi trường riêng (máy/VM/account) hoặc chấp nhận policy toàn máy gồm CVF |
| **SG-2 Shell tự do không được chặn bởi bộ lọc đã thử** | 2a live: malformed JSON exit0 và silent/plain đi tiếp theo permission flow; PowerShell ghép chuỗi ghi `denied/`. Điều này chưa bác bỏ managed whole-tool deny/closed-tool profile; native sandbox chưa hỗ trợ trên Windows | Đóng tập công cụ (mất script văn phòng tùy ý) hoặc đổi danh tính ghi; còn cần proof boundary |
| **SG-3 User phổ thông + file người dùng cùng danh tính** | ACL chặn "Main" cũng chặn Excel/VS Code của chính user, vì cùng account/token | Chỉ bảo vệ vùng LAW tự sở hữu (đúng P0), không file nguồn người dùng |
| **SG-4 Reviewer độc lập không đo được bằng máy** | Nhãn `agent_type`, `resolvedModel` quan sát được nhưng prompt/verdict do Main điều phối; reviewer ngoài host (Sol 6.1) chỉ đến qua kênh người | Mức assurance mới `OPERATOR_ATTESTED` (mục 5) thay cho "độc lập quan sát bằng máy" |
| **SG-5 Writer thay file hiện có dưới editor đồng thời** | `transaction.commit`: `sha_file(dst)` rồi `os.replace` trong `held` (handle thư mục, không khóa file); x14 A-06 còn P1 | Không nhận capability này; P0 tránh bằng cách chỉ có một người ghi (mục 6) |

Đường thay thế đã khảo sát và **không** chọn: `M` (hồ sơ Claude Code managed + tập công cụ đóng + adapter MCP stdio). Mục 4.

## 1. Nguồn, phiên bản, ngày kiểm

| Nhãn | Nội dung |
|---|---|
| OBSERVED_LOCAL (18/10, chỉ đọc) | Windows 11 Home Single Language; token của `DELL` là Medium integrity, nhóm Administrators "deny only" (split token); `EnableLUA=1`, `ConsentPromptBehaviorAdmin=5` (chỉ bấm đồng ý, không nhập mật khẩu), `ConsentPromptBehaviorUser=3`, `PromptOnSecureDesktop=1`. Máy đã có tài khoản cục bộ của công cụ khác: `CodexSandboxOffline/Online`, `cvf-g1-*`. Gói này **không** giả định dùng lại chúng (không phải của LAW) và chỉ liệt kê tên để tránh trùng tên/nhầm owner. Đây là truy vấn nhóm/khóa UAC/`Get-LocalUser` rộng hơn mức tối thiểu; không đọc mật khẩu, không đổi gì. |
| VERIFIED_DOC (Claude Code, 18/10) | `code.claude.com/docs/en/{managed-settings,server-managed-settings,permissions,hooks,vs-code,sandboxing}`: managed file chỉ toàn máy; server-managed cần Team/Enterprise, uniform, client-side, bypass bằng provider/base URL; deny>ask>allow, hook allow không thắng ask/deny rule; hook `ask` hiện lý do cho user và buộc prompt kể cả auto; mod có thể duyệt thay ask rule (ngoài plan mode); `mcp__ide__executeCode` chạy Python trong kernel Jupyter (phải chặn theo tên); `allowManagedHooksOnly` chặn mod/hook user; sandbox không chạy native Windows. |
| VERIFIED_DOC (Microsoft, 18/10) | MSRC Windows security servicing criteria: UAC "defense-in-depth, not a boundary"; **user boundary** là boundary được service ("a user cannot access or tamper with the code and data of another user without being authorized"). Learn UAC settings: standard user mặc định bị hỏi thông tin đăng nhập; `PromptOnSecureDesktop` mặc định bật đưa mọi yêu cầu nâng quyền lên secure desktop. Chưa tìm thấy trang MS nêu UIPI trong tiêu chí service; UIPI chỉ được dùng ở đây như lớp phụ, không là căn cứ chính. |
| OBSERVED_LIVE 2a | `LIVE_REVIEW.md`: ghi nhận nêu trên; `SubagentStop` có `agent_transcript_path`+`last_assistant_message`; `PermissionRequest` bắn với mode `default`; **chưa** có quan sát GUI độc lập về prompt `ask`. |
| UNKNOWN | Hành vi nâng quyền standard→admin từ trình khởi chạy của VS Code; biến môi trường mà tiến trình nâng quyền kế thừa; plan Claude của operator; tần suất ghi P0 thực tế; việc cài thành phần quản trị trong phân phối cho user phổ thông. |

Không có quan sát nào ở trên là proof cho đường `U-std` trên máy này: chưa tạo account, chưa đặt ACL, chưa chạy helper.

## 2. Bảng ranh giới → owner/API → điều kiện → decision owner

| # | Ranh giới | Owner / API / surface đề xuất | Đã biết | UNKNOWN / điều kiện để kiểm | Decision owner |
|---|---|---|---|---|---|
| 1 | **Selector phiên/dự án** và đường thoát | P0: *không cần selector phiên*. Bảo vệ gắn danh tính ghi (account) và đường dẫn P0 qua ACL; cwd/worktree/phiên mới/host khác không đổi kết quả vì quyền ghi là của OS. `M`: không có selector tin cậy (SG-1) | ACL theo account áp mọi tiến trình của account đó (user boundary, MSRC) | Mọi tiến trình dưới account làm việc đều bị cùng ACL: gồm cả thao tác hợp lệ của chính user trên P0 (phải đi qua helper) | Operator (X1, X2) |
| 2 | **Intent / grant / accepted-task binding** | Helper `apply` (X3) đọc *một request file* (bundle G-01 hiện có, dữ liệu do Main viết, không tin), sao chép không theo link vào thư mục tạm chỉ-admin-ghi, tự dựng bản tóm tắt tác động từ nội dung + bytes hiện hành của đích, hiện trong cửa sổ của chính nó (tiến trình đã nâng quyền); người dùng xác nhận tại đó. Binding là **sha256 byte nguyên văn** của request, của từng record review dẫn chiếu và của bản hiện hành đích; không canonicalization (không cần `law.cvf.digest/1`). Nonce một lần trong kho P0 chống phát lại/late result | Prompt thông tin đăng nhập nằm trên secure desktop (MS Learn); G-01 đã có `trusted_ref`, `binding`; G-02 có điểm chèn verifier | Cửa sổ xác nhận có bị tiến trình cùng account chèn phím không (UIPI) và env kế thừa: phải đo ở 2b-03. Hash theo byte nghĩa là chỉ khác định dạng cũng đổi binding (chấp nhận được, ghi để G-01 amendment xét) | Operator chọn U-std; Main/Reviewer nhận amendment G-01 (2b-01) |
| 3 | **Reviewer eligibility / prompt / verdict** | Verdict là record G-01 (dữ liệu). Helper hiển thị: danh tính reviewer *khai trong record*, hash record, hash đối tượng được review, kết luận; người dùng tại prompt xác nhận "reviewer khác worker và đã thấy đúng đối tượng". Mức mới `OPERATOR_ATTESTED`. Quan sát native (`resolvedModel`, transcript `agent_transcript_path`) chỉ là bằng chứng ADVISORY đính kèm, không là authority | Main không thể ghi qua prompt/secure desktop; verdict bất lợi cùng binding vẫn chặn (G-02 đã triển khai) | Không có cách máy chứng minh reviewer ngoài host độc lập. Nếu operator không chấp nhận mức OPERATOR_ATTESTED thì các hàng cần reviewer độc lập ở P0 giữ BLOCKED | Operator + owner contract G-01 |
| 4 | **Capability/launcher và TCB** | Ba lệnh hẹp của helper: `status` (chỉ đọc), `verify` (chỉ đọc, dùng cho checker), `apply` (ghi P0). Không MCP, không process nền, không hook làm transport. TCB: helper + interpreter đóng gói (dạng embeddable, bỏ biến môi trường/`-I -E -s -B`) + bản policy/schema/checker + writer P0, **tất cả** nằm trong thư mục chỉ-admin-ghi; không import từ repo/project/AppData | Interpreter của user hiện ở `AppData\Local\Programs\Python` (user-writable → không được dùng cho tiến trình đã nâng quyền) | Hành vi môi trường/DLL search khi nâng quyền standard→admin; ký số thành phần; đường nâng quyền từ lối tắt trên desktop của account làm việc (Main sửa được) → chỉ khởi chạy từ mục All-Users (admin sở hữu) | Operator (X2, X3); 2b-02 |
| 5 | **Writer commit / recovery / x14 / race / retention** | P0 chỉ gồm file JSON/text do LAW tự sinh, không Office/xlsx/x14; chỉ helper ghi (một người ghi, tuần tự bằng khóa), ghi tạm cùng thư mục rồi `os.replace`; giữ N bản cũ trong thư mục P0 (chính sách retention cần owner). Writer hiện có (`transaction.py`, `library_sync.py`) **không đổi**, không nhận claim | Không còn cửa sổ hash→replace vì không có editor đồng thời với quyền ghi; recovery đọc journal của helper | `_INDEX.xlsx`, tài liệu người dùng, x14 A-06, race hiện có: **ngoài P0, vẫn BLOCKED/ADVISORY**, không claim đã sửa. Ý tưởng `ReplaceFileW` (replace nguyên tử + bản sao đối tượng bị thay) cho tương lai: UNVERIFIED | Main; A-06 owner |

## 3. P0 — vùng được bảo vệ (định nghĩa đề xuất, chờ operator/Main chốt)

Thuộc P0 (quyền gốc của quản trị, LAW tự sở hữu): kho grant/receipt/role acceptance dưới `.agent/runtime/governance/`,
`.agent/EXECUTION_PROFILE.json`, các bản policy/schema/checker/helper *đã cài* (không phải bản nguồn trong repo), nonce/journal của helper.
Không thuộc P0: `references/` và sổ nguồn, tài liệu/Office của user, `working/`, `.cvf/` và `roles/` trong repo (nguồn bảo trì), `tools/`, hướng dẫn.
Hệ quả có chủ ý: `R-AUTHORITY_CHANGE` (đổi quyền/hồ sơ/policy) được cưỡng chế; `R-MUTATION`, `R-HIGH_STAKES`, `R-EXTERNAL`, `R-DELEGATE` trên file ngoài P0
**không được cưỡng chế** — nhãn ADVISORY/cộng tác, không đổi tên thành hoàn tất. Giá trị của claim: Main không tự cấp quyền, không giả receipt, không sửa policy/hồ sơ
của chính mình; chưa ngăn Main ghi đè tài liệu người dùng.

## 4. Đường đã khảo sát và không chọn

| Đường | Lý do không chọn trong gói này |
|---|---|
| `M` — Claude Code managed + tập công cụ đóng (deny Bash/PowerShell/Monitor/Edit trên vùng bảo vệ, `mcp__ide__executeCode`, claude.ai connectors, mod qua `allowManagedHooksOnly`) + adapter MCP stdio vào writer | Cần môi trường riêng (SG-1); mất script văn phòng; thêm process/dependency; `ask` làm kênh đồng ý còn UNKNOWN (2a chưa có quan sát GUI độc lập); mod có thể thay ask rule; managed file/registry yêu cầu admin và ảnh hưởng toàn máy gồm CVF. Là phương án *mở rộng sau*, không phải bước nhỏ nhất |
| Server-managed settings | Cần Team/Enterprise (plan của operator UNKNOWN); tài liệu tự ghi "không phải security boundary"; bypass bằng provider/base URL; cập nhật hook không chặn được |
| Chỉ UAC split-token trên chính account `DELL` | MSRC: UAC không phải boundary; `ConsentPromptBehaviorAdmin=5` chỉ cần một cú bấm; tiến trình cùng admin có thể sửa ACL/chiếm quyền sở hữu. Chỉ là ma sát/phát hiện, **không** được ghi là cưỡng chế |
| WSL2 + sandbox Linux | Sandbox chỉ bọc shell, file tool/hook/MCP ngoài sandbox; tích hợp tiện ích VS Code–WSL, `/etc/claude-code` user-writable theo docs, Excel/Office Windows: chưa đánh giá, nhiều UNKNOWN; không tìm thêm để ép thành supported |
| Giữ hook dự án + bộ lọc chuỗi shell | Đã bị 2a bác bỏ làm cưỡng chế; chỉ giữ như quan sát |

## 5. Luồng U-std (state flow) — chưa chạy

```text
[account làm việc: Main tạo request.json (bundle G-01) + record review (dữ liệu)]
   -> user mở helper từ mục All-Users  (không để Main khởi chạy thay)
   -> UAC: nhập thông tin đăng nhập account admin (secure desktop)
   -> helper (đã nâng quyền): sao chép request vào thư mục tạm admin, kiểm schema/binding/nonce/policy đã cài,
      tự dựng tóm tắt tác động + hash, hiện cửa sổ xác nhận
   -> user xác nhận (kể cả OPERATOR_ATTESTED cho reviewer nếu hàng cần)
   -> helper ghi P0 (writer P0), ghi kết quả vào thư mục kết quả đọc được cho account làm việc
   -> checker G-02 (verifier = đầu ra helper, không phải lời khai Main) đọc kết quả khi cần
```

Hủy ở bất kỳ bước nào ⇒ không ghi. Hết hạn/nonce đã dùng/hash lệch ⇒ từ chối. Không có nhánh tự duyệt cho Main.
Bản nháp R-READ_DRAFT trong working/ không đi qua đường này, vẫn grant hợp tác như hiện tại; user phổ thông không viết JSON/trust metadata.

## 6. Thay đổi dự kiến theo lát (không thực hiện ở 2b-00)

| Lát | File/key/process dự kiến | Ghi chú |
|---|---|---|
| 2b-01 (contract) | Amendment G-01: mức assurance `ENFORCED_P0` / `OPERATOR_ATTESTED`; binding theo byte nguyên văn; giao diện verifier cho G-02 (`Verifier`) nhận facts từ đầu ra helper; ex19 giữ nợ riêng | Review độc lập trước khi dùng làm authority; không tạo `law.cvf.digest/1` |
| 2b-02 (helper) | Mã helper + writer P0 + gói interpreter đóng gói; test/fixture offline; nguồn trong repo, **bản cài** ở thư mục chỉ-admin-ghi do G-04 đóng gói | Không MCP, không daemon; không import code repo khi nâng quyền |
| 2b-03 (môi trường thử) | Account thử + ACL thử trên dữ liệu giả; operator chọn máy/VM thử | Không dùng LAW/CVF thật |
| Thao tác máy (X1–X2, operator) | 1 account standard; 1 thư mục chỉ-admin-ghi (ví dụ dưới Program Files hoặc ProgramData) với ACL; ACL P0 đặt trên thư mục con `governance` của dự án; mục Start Menu All-Users | Chưa thực hiện; xem rollback mục 8 |

## 7. Ca proof phải có ở 2b-03 (chưa chạy, không ghi PASS)

Hợp lệ: user xác nhận → P0 đổi đúng một lần; nháp mới trong grant không bị hỏi lại; hủy không ghi; đọc P0 bởi checker từ account làm việc.
Từ chối: ghi P0 bằng `Write/Edit`, PowerShell, Python, Office/COM, xóa, đổi tên/link/junction/ADS/8.3/UNC, thay file bằng link; đặt `PYTHONPATH`/`PATH`/`PYTHONSTARTUP`
lâu dài rồi khởi chạy helper; sửa lối tắt/launcher; thay request giữa lúc hiển thị và lúc ghi; phát lại nonce; chèn phím/click vào cửa sổ xác nhận từ account làm việc;
hủy credential prompt; kill giữa chừng rồi resume/rollback; reviewer tự khai; bỏ finding; hash lệch; policy cài đặt bị đổi; mức UAC (`PromptOnSecureDesktop`) đổi.
Kiểm sau khi cài/gỡ không phá account `DELL`/CVF và host khác.

## 8. Blast radius và rollback (owner-controlled, ngoài agent)

- Ảnh hưởng: account `DELL` và CVF không đổi; không đổi `~/.claude`, managed settings, registry policy của Claude Code; mọi host (Claude/Codex/Gemini) dưới account làm việc cùng chịu ACL P0. Chi phí: đăng nhập/công cụ trong account làm việc (VS Code, tiện ích, Claude login), tần suất ghi P0 (UNKNOWN).
- Trước khi cài: `icacls <đường dẫn> /save` cho từng thư mục sẽ đổi; danh sách exact file/ACL/account/mục menu; ghi owner thực hiện.
- Rollback: xóa account làm việc (hoặc vô hiệu), `icacls /restore` từ bản đã lưu, gỡ thư mục cài và mục All-Users; kênh khôi phục qua account admin, không qua agent. Giữa chừng (cài dở, helper lỗi, update Windows): P0 giữ nguyên trạng đã ghi, ghi bị từ chối cho tới khi helper hợp lệ; không tự chuyển sang cho Main ghi.
- Không dùng tài khoản/thành phần của Codex hoặc CVF hiện có.

## 9. Quyết định operator cần (một lần, sau khi Main/Reviewer nhận gói)

1. **Chấp nhận P0 làm phạm vi claim cưỡng chế** (mục 3) và nhãn ADVISORY cho phần còn lại — hay giữ toàn bộ sản phẩm ở ADVISORY và để G-03 BLOCKED (kết quả 0.2).
2. **X1:** cho phép một account Windows *standard* riêng cho công việc LAW được bảo vệ; account admin hiện có chỉ dùng cho thao tác quản trị.
3. **X2/X3:** cho phép một lần thao tác admin tạo thư mục cài chỉ-admin-ghi (Program Files hoặc ProgramData), ACL P0 và gói helper+interpreter đóng gói do maintainer cung cấp kèm danh sách exact và rollback.
4. **X4/UX:** chấp nhận mỗi lần ghi P0 cần credential prompt; mức `OPERATOR_ATTESTED` cho reviewer trong P0.
5. **Vị trí hiện tại của phân phối:** `U-std` là chế độ "bảo vệ" tùy chọn cho operator/nhóm có quản trị; không là mặc định cho user phổ thông. Mặc định sản phẩm tiếp tục cộng tác, nhãn trung thực.

Không cần hạ tầng nào sau đây: managed settings Claude Code, adapter MCP, VM/Hyper-V, daemon/service, Team plan, cloud.
Nếu operator từ chối X1 hoặc X2: kết luận **NO_FEASIBLE_PATH_WITH_CURRENT_CONSTRAINTS** cho cưỡng chế bất kỳ named effect; G-03 giữ BLOCKED; các hàng routing giữ ADVISORY có nhãn; không dựng gate hook rồi gọi là hoàn tất.

## 10. Còn blocked / chưa kiểm

- Mọi cơ chế `U-std` chưa đo (account, ACL, nâng quyền, UIPI, env, launcher, nonce). Docs Claude/Microsoft là VERIFIED_DOC chứ không phải proof máy này; hai trang được đọc qua tóm tắt công cụ, hooks chỉ đọc đến ký tự 200000/273658.
- Reviewer độc lập bằng máy: không giải được (SG-4); chỉ OPERATOR_ATTESTED.
- File/tài liệu người dùng ngoài P0, sổ nguồn, x14 A-06, race hash→replace, ex19, `law.cvf.digest/1`: giữ nợ riêng; không claim.
- Không đọc settings nhạy cảm, env, credential, transcript; không quét repo/CVF ngoài các file đã nêu.
- Hạ tầng đã có trên máy (account Codex/CVF) chỉ ghi nhận, không đánh giá và không dùng.
