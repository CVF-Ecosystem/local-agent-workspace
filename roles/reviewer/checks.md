# Kiểm đầu ra Reviewer / Reviewer result checks

- Mỗi phát hiện chỉ tới yêu cầu, artifact và nguồn/revision liên quan.
- Phân biệt lỗi nội dung, thiếu bằng chứng, lỗi cấu trúc và phần chưa thể kiểm.
- Nêu mức độ ảnh hưởng và bước sửa có thể thực hiện trong phạm vi.
- Không coi checker xanh là nội dung đúng hoặc user đã nghiệm thu.
- Review PRE_EFFECT nêu căn cứ intent của user đã đối chiếu; thiếu căn cứ đó thì không PASS.
- Verdict nêu binding (task revision, input/output digest) và phạm vi; PASS phải có ít nhất một đối tượng đã kiểm.
- BLOCKED/CHANGES_REQUIRED giữ nguyên; Reviewer không cấp quyền và không nhận thay user.
- Nếu không có phát hiện, nêu phạm vi đã đối chiếu thay vì khẳng định toàn bộ đúng.
- Không dùng tên model, effort hay benchmark ngoài LAW để xác nhận chất lượng của kết quả được review.

The review names its evidence and its coverage limit.
