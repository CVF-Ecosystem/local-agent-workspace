# Phiếu phản hồi sau khi dùng / Feedback form

Mất khoảng 5 phút. Chủ yếu là tích chọn, không cần viết dài. / Takes about 5 minutes. Mostly ticking boxes, no long writing needed.

**Không biết nên nói gì?** Dán lời nhắc này cho agent, nó sẽ hỏi bạn từng câu và điền giúp phần nó biết chắc: / **Not sure what to say?** Paste this prompt to the agent; it will ask you one question at a time and fill in what it knows for certain:

```text
Mở docs/FEEDBACK_FORM_VI_EN.md và giúp tôi điền phiếu phản hồi. Hãy hỏi tôi từng câu một (chủ yếu là chọn đáp án), tự điền phần bạn biết chắc (phiên bản trong VERSION, các file bạn đã mở trong phiên này, khối "Khai báo thực hiện" gần nhất), không trả lời thay tôi và không bịa. Cuối cùng in phiếu đã điền ngay trong cuộc trò chuyện để tôi sao chép; không tạo file.
```

**Che dữ liệu thật** (tên người, số liệu, thông tin nội bộ) trước khi gửi. / **Mask real data** (names, figures, internal information) before sending.

**Gửi ở đâu / Where to send:** dán phiếu đã điền vào nhóm chat do người giao package chỉ định, hoặc mở một issue trên GitHub: https://github.com/CVF-Ecosystem/local-agent-workspace/issues/new?template=phan-hoi.md / paste the filled form into the chat group named by whoever gave you the package, or open a GitHub issue at the link above.

## 1. Thông tin của bạn / About your setup

- Phiên bản package / Package version (file `VERSION`):
- Ứng dụng và mô hình / App and model (ví dụ Claude Desktop, Gemini trong Antigravity, Codex):
- Hệ điều hành / Operating system:
- Bạn đã đi đến đâu / How far you got (tích tất cả mục đúng / tick all that apply):
  - [ ] Đọc `START_HERE` / Read `START_HERE`
  - [ ] Chạy `SETUP` hoặc form khởi tạo / Ran `SETUP` or the setup form
  - [ ] Thử 3 bài demo / Tried the 3 demo exercises
  - [ ] Dùng cho việc thật / Used it for real work
  - [ ] Nâng cấp project / Upgraded a project
  - [ ] Cài gói lĩnh vực / Installed a domain pack

## 2. Bảy câu hỏi / Seven questions

Chọn một đáp án cho mỗi câu. Không chắc thì chọn "Một phần". / Pick one answer per question. If unsure, pick "Partly".

**1. Mục đích.** Sau khi đọc `START_HERE`, bạn hiểu package dùng để làm gì? / After `START_HERE`, did you understand what the package is for?

- [ ] Có / Yes
- [ ] Một phần / Partly
- [ ] Không / No

**2. Khởi tạo.** Bạn tạo được project mà không cần ai hướng dẫn thêm? / Could you set up a project without extra help?

- [ ] Có / Yes
- [ ] Một phần / Partly
- [ ] Không / No

**3. Agent làm theo hướng dẫn.** Agent có mở `AGENTS.md` và đúng skill khi việc khớp? (hỏi agent: "liệt kê mọi file bạn đã mở") / Did the agent open `AGENTS.md` and the matching skill? (ask it: "list every file you opened")

- [ ] Có / Yes
- [ ] Một phần / Partly
- [ ] Không / No

**4. Khai báo thực hiện.** Cuối câu trả lời có khối "Khai báo thực hiện" đủ mục (cách làm, skill, nguồn, file, chưa kiểm)? / Did the reply end with an "Execution declaration" with all items?

- [ ] Có / Yes
- [ ] Một phần / Partly
- [ ] Không / No

**5. Bám nguồn.** Kết quả không bịa số liệu, hạn, người phụ trách; chỗ thiếu ghi "cần xác nhận"? / Did the result avoid invented figures, deadlines and owners, marking gaps "to be confirmed"?

- [ ] Có / Yes
- [ ] Một phần / Partly
- [ ] Không / No

**6. Công sửa lại.** Bạn phải sửa kết quả nhiều không? / How much did you have to fix?

- [ ] Gần như không / Almost nothing
- [ ] Một ít / A little
- [ ] Nhiều / A lot
- [ ] Làm lại / Redid it

**7. Hướng dẫn.** Có chỗ nào khó hiểu hoặc thiếu? (ghi rõ ở mục 4) / Anything unclear or missing? (describe in section 4)

- [ ] Không / No
- [ ] Có / Yes

## 3. Nếu bạn dùng cho việc thật / If you used it for real work

- Loại việc / Kind of work:
  - [ ] Soạn văn bản, quy trình, biểu mẫu / Documents, procedures, forms
  - [ ] Biên bản hoặc tóm tắt họp / Meeting minutes or summary
  - [ ] Kiểm tra bảng số liệu / Checking a data table
  - [ ] So sánh hai phiên bản / Comparing two versions
  - [ ] Báo cáo hoặc dashboard HTML / HTML report or dashboard
  - [ ] Khác / Other:
- Kết quả dùng được ngay không? / Was the result usable?
  - [ ] Dùng được / Yes
  - [ ] Sửa nhẹ / Light edits
  - [ ] Sửa nhiều / Heavy edits
  - [ ] Bỏ / Discarded
- So với tự làm / Compared with doing it yourself:
  - [ ] Nhanh hơn / Faster
  - [ ] Tương đương / About the same
  - [ ] Chậm hơn / Slower
- Bạn đã đối chiếu số liệu, tên, ngày với nguồn chưa? / Did you check figures, names, dates against the source?
  - [ ] Rồi, đúng / Yes, correct
  - [ ] Rồi, phát hiện sai / Yes, found errors
  - [ ] Chưa / Not yet

## 4. Kể lại ngắn / Tell us briefly

Mỗi ý 1 đến 3 dòng. Chép nguyên văn yêu cầu và đoạn sai nếu có, nhưng che dữ liệu thật. / One to three lines each. Quote your request and any wrong passage, with real data masked.

- Việc bạn giao cho agent / What you asked the agent to do:
- Điều agent làm tốt nhất / What the agent did best:
- Chỗ agent làm sai, bịa hoặc bỏ sót / Where the agent was wrong, invented or missed something:
- Điều làm bạn bối rối hoặc khó chịu nhất / What confused or annoyed you most:
- Một điều bạn muốn package có thêm / One thing you wish the package had:

## 5. Đính kèm nên có (không bắt buộc) / Helpful attachments (optional)

- Khối "Khai báo thực hiện" của agent, dán nguyên văn / The agent's "Execution declaration", pasted as is.
- Danh sách file agent đã mở / The list of files the agent opened.
- Kết quả của `python tools/check_output.py --declaration <file>` nếu bạn lưu câu trả lời thành file / Output of `python tools/check_output.py --declaration <file>` if you saved the reply to a file.
