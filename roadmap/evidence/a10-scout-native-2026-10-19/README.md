# A-10 Scout — review offline và proof file-native hẹp, 19/10/2026

Trạng thái: **SCOUT_ACCEPTED_WITH_LIMITS**. Reviewer độc lập `a10_scope_review`, dispatch `gpt-6.1-sol`/`high`, nhận offline implementation rồi soát evidence phiên thật; không chạy lại AI. Toàn A-10/R4, Worker/Reviewer native, effort, deactivation và release còn mở.

## Bằng chứng phiên thật

- Orchestrator chạy theo ngoại lệ lab trong PROJECT ngày18/10; không chuyển quyền này vào sản phẩm. Lab riêng: `C:/Users/DELL/AppData/Local/Temp/law-a10-native-proof-20261019-zysilzk5/project`. Nguồn giả, profile fixture không có grant, không sửa profile/native maintainer.
- `request.json` ghi version, argv/prompt, scope, requested model/effort, giới hạn và hashes trước khi gọi. Một fresh session, một AI attempt, một Scout task; CLI budget yêu cầu tối đa0.50USD, timeout240s, không retry trả phí. File request được cập nhật phase/timestamps sau lần gọi; không phải log bất biến/chống giả.
- Claude Code CLI **2.1.81**; adapter được copy từ source đã review, SHA256 `91915c09f083964203bc02acb71637c54bf6e6be9a9889fd8289ff6bcb8760a5`. Native do chính adapter trong lab sinh, status CURRENT trước chạy. Không `--agents` override, không permission bypass; settings nguồn project, MCP rỗng, tool set Agent/Read/Grep/Glob.
- `stream.jsonl`: session init có `law-scout`; Main `claude-sonnet-5-5` gọi Agent với `subagent_type=law-scout`, ID `toolu_01W7XkHpLvWskWSLqC8Eh4LY`. Child `claude-haiku-5-5` gọi Read đúng `references/lab/scout-source.txt`, parent ID khớp. Không thấy Main tự Read hoặc tool ghi. Kết quả giữ SourceID/revision/mã/ngày/thiếu giờ và địa điểm cùng locator đúng nguồn.
- Exit0, result success,2turns,16543ms. Telemetry **0.1817421USD**; đây không là xác nhận hóa đơn thực trả. Effort requested null, hiệu lực effort NOT_INSPECTED. Hash cây **266file không đổi, không thêm file** sau lần gọi.
- **Giới hạn reporting:** file có7dòng nội dung và terminal newline; Read trình bày thêm dòng trống số8. Scout/Main ghi “đủ8dòng” theo trình bày đó. Không nhận câu này làm bằng chứng đếm dòng hoặc chất lượng model. Không sửa output gốc, không retry để làm đẹp kết quả.
- Chỉ nhận file-native invocation/model/locator trong lab/CLI này. Không nhận sandbox công cụ/đường dẫn, chặn mọi thao tác trái phép, grant authenticity, profile_ref, effort hoặc activation. Một Read hợp lệ không chứng minh mọi tool khác đã bị chặn.

## Kiểm Reviewer và sửa nhỏ

Reviewer sửa sourcebytes stale dù native giống nhau, hash/recheck PACKAGE_INFO chọn ngôn ngữ, marker+receipt binding, identity collision project-local và parent-link guard trước đọc. Collision parser chỉ nhận scalar subset hữu hạn; nested/không diễn giải chắc → UNSUPPORTED, không tự sửa hoặc nhận quản lý file riêng của user. `_write_group` chỉ ghi nhận operation thật, giữ mọi lời gọi add/expected_before.

```text
python -B -W error::ResourceWarning -m unittest -v tests.test_native_agents
# 39 đạt/0skip,12.269s; trước sửa diagnostic cuối, log reviewer_test_native_agents.log

python -B -W error::ResourceWarning -m unittest -v tests.test_native_agents.ReviewRegressions.test_receipt_only_refresh_failure_before_write_reports_no_native_write tests.test_native_agents.CreateAndUpdate.test_unrelated_profile_edit_requires_a_fresh_confirmation_even_when_native_bytes_match
# Đỏ2FAIL trước sửa diagnostic; xanh2đạt/0skip,0.343s sau sửa, log reviewer_receipt_only.log
```

Không cộng các lượt trùng thành fullsuite mới; chưa chạy lại module đầy đủ sau sửa diagnostic cuối. Nhóm corrective trước có red→green4method (3FAIL→4đạt) và5method (11subtestFAIL→5đạt); chi tiết lệnh/log trong HANDOFF/Temp Reviewer. Worker33native +46profile/1skip +11gate +42package là evidence trước sửa Reviewer, không gán cho source cuối.

## Hash bản giữ trong kho

| File | SHA256 |
|---|---|
| request.json | 21fff98042692c524fd4c99eaef6d7096894e469041113eaa004f5a9a02ee146 |
| stream.jsonl | 5400c702a5d9d51cd02896a4ca53a89ba86c441f86a128b2f50bd943061cf66c |
| source.txt | 55a55efbae22522d7ebf2fb8d5ca9f3850c766ade2a229259a20c20c8107ada5 |
| native-scout.md | 4b5aba5158bc911500e41836dfed871a597b6165a4c083d941d626cc3ca979d0 |
| reviewer_test_native_agents.log | 50ad33e4bc634a306a30833c189e9a5a9a10116fd2b6cfd2c297c8d9c638e29b |
| reviewer_receipt_only.log | 5b0ab9d846c63a074cf115bbea9c91371f1ffa0dbe6aa6671da973b31dcadd9e |

Các file giữ raw bytes; native-scout.md ở đây là evidence, không là file đăng ký host. Lab đầy đủ/analysis/run-result/agents listing vẫn ở Temp có thể bị dọn. Đây là evidence hợp tác, không host attestation chống sửa. MANIFEST/RC3 không refresh; không fullsuite/fullgate/Office/CI/ZIP chính thức/POSIX hoặc host khác.
