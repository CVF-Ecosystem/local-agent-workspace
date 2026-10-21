# A-10 core adapter — một host WITH_LIMITS, 19/10/2026

**A10_CORE_ONEHOST_ACCEPTED_WITH_LIMITS.** Reviewer độc lập `a10_scope_review`, dispatch `gpt-6.1-sol`/`high`, nhận delta offline rồi đối chiếu evidence mới. Kết hợp proof Scout đã nhận ở `../a10-scout-native-2026-10-19/`, đây là điểm dừng core adapter trên Claude Code2.1.81; không full R4/role packs/enforcement/official release hoặc user acceptance.

## Review implementation

Reviewer sửa nhỏ đúng hai file native_agents/test: sibling chỉ bỏ bytes khỏi inventory khi receipt+marker+nativehash+expectedname thật managed; foreign/unknown vẫn hash/guard; normal apply kiểm lại inactive slot; post-observe nhận ra active đã đổi; TransactionError sau rename vẫn reconcile; inactive cũng cần marker. Không engine/schema/dependency mới.

Giữ các quyết định Worker: RETIRE_CONFLICT chặn cả apply thường; Reviewer checks thay bullet bảo trì bằng ràng buộc không lấy model/benchmark thay chất lượng; metadata candidate_presets tách product_presets; Native Worker VI/EN, preview và README đã nói Write không cưỡng chế new-only/path sandbox. Không thêm cảnh báo vào luồng văn phòng chỉ để lặp thông tin này.

```text
python -B -W error::ResourceWarning -m unittest -v tests.test_native_agents.RemainingReview
# Trước sửa:6method/8FAIL gồm subtest; sau sửa:6đạt/0.473s.

python -B -W error::ResourceWarning -m unittest -v tests.test_native_agents.ThreeRoles tests.test_native_agents.Retire tests.test_native_agents.RetireRefusesWhereItCannotBeMeasured tests.test_native_agents.RemainingReview
# 32đạt/0skip,12.141s, source cuối.
```

Worker66native/46profile1skip/11release_gate/42package là evidence trước sửa Reviewer. Không cộng thành fullsuite mới, không chạy full module72 sau sửa. Reviewer adapter tăng ròng7dòng thành793; test tăng87 thành1524. Core dùng fixed mapping/preamble và owner hiện có; không mở refactor vì số dòng.

Source cuối: native_agents.py `e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e`; test_native_agents.py `19869c3f3ce7d27fea2f19093674d0f74f4128a784c7e9bcf71d7a7c6ec11cdf`; execution_profile.py `cbfa5ad1b4272b9601e30dbce01694de9fab1a3ed3478b4d97f188bc4f84a323`. Protected source/schema/grants/pins/MANIFEST/actual PROJECTs giữ; không profile/native maintainer.

## Một phiên native Worker → Reviewer

- Lab riêng `C:/Users/DELL/AppData/Local/Temp/law-a10b-native-proof-20261019-duyk5u13/project`, từ current delivery; adapter của chính lab xuất hai native qua preview/apply. Scout không gọi lại. Chỉ nguồn/brief giả, profile fixture chọn model rõ và grants rỗng; quyền thử nghiệm từ PROJECT bảo trì, không là proof quyền sản phẩm.
- `request.json` ghi scope/argv/version/model/effort/giới hạn trước gọi. Một AIattempt, một session, hai child tuần tự; budget CLI yêu cầu0.75USD, timeout300s, không paid retry. Request được cập nhật phase/timestamps sau chạy, không phải log bất biến. Không --agents, tool model override, permission bypass hoặc MCP bên ngoài; không sửa host/account/settings.
- Main Sonnet5.5 chỉ gọi2Agent. Worker ID `toolu_018cn2QYHbTTCWXBMvAwD7jo`, child model Sonnet5.5:2Read/1Glob/1Write tạo candidate. Reviewer ID `toolu_01JcQHMLjvPgovauiwus7E9J`, child model Sonnet5.5:3Read, không Write. Parent IDs khớp, hai vai khác context; không MainRead/Write. Effort requested null, observed NOT_INSPECTED.
- Exit0/success,3turns/62024ms. Telemetry **0.38191935USD**, không phải hóa đơn. Snapshot trước/sau AI: **270file cũ giữ hash, chỉ thêm `working/a10-native-lab/candidate.txt`**. Quan sát này không chứng minh sandbox hoặc mọi race/overwrite đều bị ngăn.
- Artifact giữ CANDIDATE/dữ liệu giả/không phát hành. Mã LAB-A10B-042/nhóm/ngày23/10 giả và SourceID LAB-SRC-A10B-01/revision lab-r1 khớp nguồn. Giờ/địa điểm giữ cần xác nhận. Hai hash ghi trong artifact là do Main cung cấp; các child không tự băm, đã nói rõ. Orchestrator và Reviewer bảo trì đối chiếu lại với bytes thật.
- Reviewer sản phẩm phát hiện nhỏ tại candidate dòng21: nói giờ/địa điểm “không có trong nguồn”, trong khi sources dòng7–8 có trường với giá trị cần xác nhận; đúng hơn là chưa có giá trị cụ thể. Giữ nguyên artifact/finding, không sửa bằng vai Reviewer, không retry hoặc xin user nghiệm thu một bản test. Q1/Q5 về lịch sử không ghi đè/ngoài scope được child để chưa kiểm; snapshot/trace bên ngoài bổ sung quan sát của đúng lần đo này.
- Candidate còn đưa raw hashes vào văn bản dù Q1–Q5 không bắt buộc: chưa nhận bố cục/độ gọn hoặc chất lượng văn phòng/người mới C-02 từ thử nghiệm này. Một vai gọi thành công không là benchmark/chứng nhận model, user acceptance hoặc workflow PASS.

## Retire trên code cuối

Sau snapshot AI, Orchestrator preview-retire/retire mỗi vai đúng một lần bằng adapter cuối. Cả hai báo RETIRED; active vắng, inactive hashes khớp receipt, receipt giữ nguyên, candidate hash không đổi. Listing CLI mới chỉ còn4built-in, không project roles. Native files trong evidence được copy nguyên bytes từ inactive slots, không phải định nghĩa đang đăng ký trong repo.

Driver đầu dừng sau retire Worker thành công vì status RETIRED chủ đích thoát1 (không callable). Đã đọc saved outcome, tiếp tục Reviewer, không lặp rename Worker hoặc AI. `retire-analysis.json` ghi rõ; không biến exit1 thành lỗi sản phẩm hoặc giả thao tác chưa xảy ra. Không claim session cũ unload, task bị cancel hay grant bị thu hồi.

## Hash evidence giữ trong kho

| File | SHA256 |
|---|---|
| request.json | 7a1dc7fd945caa71feb109b13a496b002d67e44a2fad8560005e13498f004525 |
| stream.jsonl | a0434fb4c0c5d979fdf668a72ac8a7dc2dd19d09a1e5210a44cbc08d23fb9701 |
| sources.txt | 93191e4bbb6f99f8b1ec819d0eee0319ec74da47907f25a60b2120e859a1285e |
| user-basis.txt | 4595ed5617f5c45c8654ca6e33cd327ef331b1df89f66e628e4ad557f27ffbfb |
| candidate.txt | 12606146a806bc0d269fe26684f7ff61f63843bce262a38094d39b4d16a1d890 |
| native-worker.md | 79ad3bc25841b46d53fb117fccf8a72224601b4ffc5bfefcfbcc28e14855dd53 |
| native-reviewer.md | 9b79a8250235098ab7270d9e8703fdf3671fb58a0ac9bfbc13b04021d1d10971 |
| retire-analysis.json | f78f23d63c7a893ea385fdf303c018468ae445282a36862888c21302c5b3a16a |
| agents-after-retire.log | f80896d4f1b978f5bcdf8c8fd3ae54c947c7d762f3ead2098d005842148714ba |
| reviewer_remaining_red.log | d5b74ec6a1a1db14e5228cf38434c208a377fc75d390c7bf666f39d7e0041070 |
| reviewer_remaining_green.log | 2b100c5b1df1d007ae1d048a665052e49e72f995176b762466adb6c04318f205 |
| reviewer_a10b_targeted.log | 7a0ae509a952c3113fade70d3bf304a2c301c7b3b3f39de25a7ae1694c6da3c1 |

Raw bytes được giữ, chỉ dữ liệu giả/technical metadata. Full lab, analysis trước retire, run-result và CLI logs riêng còn ở Temp có thể dọn. Evidence hợp tác, không attestation chống giả. Chưa fullsuite/fullgate/Office/CI/ZIP chính thức/POSIX/host khác hoặc live cancellation. A-11/B-03 tiếp tục sở hữu dispatch authority, task/result binding, stale integration, retry/stop; role-pack intake/full R4 và release còn theo roadmap.
