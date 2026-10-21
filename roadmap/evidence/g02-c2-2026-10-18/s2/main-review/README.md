# Review S2 delta — 18/10/2026

Verdict: **REVIEW_ACCEPTED_HELPER_ONLY / CANDIDATE_NOT_ACTIVE**.
Sol6.1 High review độc lập và1probe claims/index trong bộ nhớ; Main1probe comparator metadata.
Worker157test/mutation evidence là snapshot trước Main, được dùng lại; không broad rerun.

## Findings đã sửa hẹp

- P2: stale ClaimTable của indexA dùng với indexB đã đổi claim vẫn LINKED/AGREE. Gắn private origin-token và từ chối khác snapshot (ValueError của caller), không verifier/quyền.
- P2: compare_object_sets cho caller gắn basis RECOMPUTED và locator tùy ý. Hạn chế basis/name/locator đúng vocabulary; không đổi projection hay file-byte identity.
- P3: inputs/outputs có mặt null trong record bị coi như absent. Wrapper peer/own binding trả UNSUPPORTED/MALFORMED_RECORD; API standalone None-as-absence giữ.

## Tests Main đã chạy

Workdir LAW; executable thực `C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe`.

```powershell
# Trước sửa:3methods,13failure/subtest assertions
python -B -W error::ResourceWarning -m unittest tests.test_control_check_v2_s2.GrantLinkTests.test_claim_table_must_belong_to_the_current_index tests.test_control_check_v2_s2.ObjectSetTests.test_caller_metadata_cannot_upgrade_basis_or_escape_closed_locator tests.test_control_check_v2_s2.BindingTests.test_present_null_sets_in_records_are_malformed_not_absent -v
# Sau sửa:56methods liên quan
python -B -W error::ResourceWarning -m unittest tests.test_control_check_v2_s2.GrantLinkTests tests.test_control_check_v2_s2.ObjectSetTests tests.test_control_check_v2_s2.BindingTests tests.test_control_check_v2_s2.PointerTests tests.test_control_check_v2_s2.PurityTests -v
```

`delta_red.log`: đỏ hành vi thật, không lỗi API chưa có.
`delta_first_run.log`:56test,1error; fixture order-test ghép claims và index từ2snapshot khác nhau, bị guard mới từ chối đúng. Đổi fixture dùng một index, giữ assertion vị trí.
`delta_green.log`:56/56 đạt,0skip,0.519s. Testlabel x đổi thành scope (vocabulary hợp lệ) vẫn kiểm tên được giữ; không bỏ guard/assertion/pin.
Không rerun157/160 toàn S1+S2,24C1,107G02/v1, fullsuite, mutation hoặc parity. Fullhashes sau delta: HASHES_AFTER.txt.

## Năm lựa chọn Worker

Nhận thứ tự chẩn đoán grant-link, complete fixed relation set (không literal/consistency), depth64 ngoài precondition, import parser loader, và COVER bất đối xứng summary→artifact. Qualifier chỉ có ở artifact được vắng ở summary; hai tập vẫn phải phủ. Không nhận đó là reviewcoverage theo pha.
refs/binding sau delta553/501dòng; vượt estimate là nợ maintainability, chưa buộc tách thêm.

Chưa integration/evaluator/authority/gate/observer, artifact bytes/source authenticity hoặc activation. Entry S1 giữ nguyên, v1/C1 không sửa. S3 còn amendment/thiết kế trước code; không G03PASS/G04/A–D/release. Chưa CI/Python3.8 thật/khácOS; không AI CLI/API/host/admin/stage/commit/push.
