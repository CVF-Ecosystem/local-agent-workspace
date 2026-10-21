# Review G-01-C1 — 18/10/2026

Verdict: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED** sau sửa hẹp Main. Candidate v2 chưa kích hoạt; không có loader/checker/workflow v2 chạy.
Reviewer độc lập: `review_g03_2a_prep`, gpt-6.1-sol/high. Worker báo24test đạt; Reviewer đọc và dùng bằng chứng đó, không chạy lại.
Main không suy effort thực của Worker từ brief Sonnet5.5 High; Worker chỉ quan sát model claude-sonnet-5-5.

## Delta đã kiểm

- P2: làm rõ khi nào UNSUPPORTED chặn, giữ căn cứ nguồn/reviewer/context hợp tác và không giả proof xác thực mạnh.
- P2: guard hiện hành ngoài digest; digest khớp không tái cấp quyền/tư cách cũ.
- P2: EXPECTED counterfactual riêng; bundle nguyên trạng không có grant hoạt động, workflow NOT_RUN.
- P3: Main có thể ghi lại xác nhận user; schema kiểm lời khai kênh/lớp, không chống giả. Hai schema descriptions được sửa, constraints không đổi.
- Hàm canonical dùng fullmatch thay match để từ chối khóa có newline cuối. Thêm u11; canonical vectors19→20, UNSUPPORTED10→11.
- Chỉ đổi status của rules Markdown; policy v2, projections và22bundle giữ nguyên. V1 hash prefixes khớp6pin, full hashes sau kiểm trong HASHES_AFTER.txt.

## Lệnh Main đã chạy

Workdir: LAW. Python3.11.9 đã có sẵn:
`C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe`.

Sau thêm vector, trước sửa helper:

```powershell
& 'C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe' -B -W error::ResourceWarning -m unittest tests.test_control_v2_candidate.Vectors.test_canonical_vectors_recomputed -v
```

`newline_red.log`:1test/1subtest FAIL (`Unsupported not raised`). Đây là đỏ do lệch định nghĩa, không phải lỗi import.

Sau sửa helper và tài liệu:

```powershell
& 'C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe' -B -W error::ResourceWarning -m unittest tests.test_control_v2_candidate.Vectors tests.test_control_v2_candidate.Examples.test_binding_recomputation_matches_expectation tests.test_control_v2_candidate.Examples.test_examples_are_fake_and_inactive tests.test_control_v2_candidate.Examples.test_schema_validity_matches_expected tests.test_control_v2_candidate.SchemaAndPolicy.test_schema_is_valid_draft_2020_12 tests.test_control_v2_candidate.V1Untouched.test_v1_owner_hashes_unchanged -v
```

`main_delta_green.log`:13/13 đạt,0skip,0.252s. Gồm8Vectors và5test schema/examples/v1pins. Không full24C1,107G02 hoặc project fullsuite.

## Giới hạn

Không proof workflow/host, activation/migration, receipt/grant thật, CI/Python3.8 hoặc byte observation của C2.
Không sửa writer/x14/race/ex19, không stage/commit/push. Status candidate được nhận không cấp quyền effect.
NEXT: G-02-C2 thiết kế trước code theo brief HANDOFF; baseline G-03 vẫn IMPLEMENTATION_PENDING.
