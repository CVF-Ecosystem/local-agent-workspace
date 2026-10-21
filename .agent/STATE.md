# PROJECT STATE

<!-- local-agent-workspace: maintainer-state -->

## Goal

Phát triển LAW thành workspace local dùng lâu dài cho công việc văn phòng; giữ nguồn, quyền và bối cảnh qua các phiên, hoàn thiện MVP bằng feedback thực tế.

## Current phase

21/10/2026: Đã công bố v1.9.0-rc2 để dùng thử/thu feedback, chưa final. Nguồn5335f68 đã review độc lập và build sạch, 4gate passed/1495test6skip. RC2 chứa L19 và fixture portability; RC1 giữ nguyên tag/asset, notes dẫn RC2. Đã ghi nhận publication và nghiệm thu; CI main mới chưa có kết quả.

## Completed

- G-00–G-04 và I1/I2/I3, A-02, A-06–A-11, B-01/B-02 đã nhận đúng subset/WITH_LIMITS trong HANDOFF/roadmap; không nhận host enforcement hoặc toàn R1–R6.
- D-01a–g/SCRIPT-01, M1–M3 đã nhận đúng phạm vi; snapshot M4 và diễn tập mock M5 có sẵn. Người dùng mới/pilot chuyển sau MVP theo operator.
- E07-B/RC1 đã nhận nội bộ và công bố prerelease; historical1492test6skip/2rebuildtimeout giữ nguyên, không thay bằng số liệu RC2.
- L19: sửa diagnostics export allowlist, bảo toàn đúng7rawpin lịch sử, fixture EOL/Windows/parser/Python3.8/mac; không sửa runtimev3/schema/quyền/pin-value.
- RC2: fullsuite1495test/1252.159s/6skip; verify/projection261file/create/upgradeRC1 giữ7file riêng đạt;2archiveprobe cùngSHA. Reviewer độc lập nhận source/budget/artifact.

## Current artifact

- Tải dùng thử: https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc2 ; published2026-10-21T08:07:36Z, prerelease=true/draft=false; source/tag5335f68e6d8ed2460234bc42c810a3050817bda8.
- ZIP1178991byte/261file SHA25653a85eac42982cdb0a422fac4d7b59a644fbc2305d4c677094024120dfa9b323; gatebdc8e182abbdbd442bcded99c840eed995cdc677b778658652d8c7ce105a0de0; checksum4a13523d11d8a0f5d0fefb73eebc4f0180720af11f036a8f3610d5cda5a9fc6f. Baasset tải lại khớp.
- RC1 tag6f39/3asset bytes giữ nguyên; RC1 và stable1.8 notes dẫn RC2. Stable/latest vẫn1.8.0. README VI/EN, changelog, feedback form/issue, About/homepage thống nhất RC2; Issues/nhãn phản hồi sẵn sàng.
- main ngoài phiên đã mergePR7=a5aaf93 (tree bằng46af0ab); đã merge vào nhánh sửa, tree bằng5335 chính xác. Commit sau tag chỉ ghi hồ sơ bảo trì, không đổi projection của gói.

## Open items

- CI39560119618/source901e1d1: Ubuntu3.12 cả job đạt;3.8/mac fixture lỗi; Windows3.12 hành vi1493test40skip/1105.326s đạt nhưng buildtimeout900. Không gọi là CI RC2; CI main mới cần kết quả thật.
- RC2 build đầu30b timeout900, không ZIP; budget1800 được review theo bước WindowsCI1108s. Retry5335 đạt, vẫn fail/noartifact nếu timeout; không skip/nested hoặc hạ assertion.
- Chưa file-symlink thật (5skip1314), visual/nội dung từng trang UI hoặc Word/Excel, usability người mới hoặc hỗ trợ chính thức toàn ma trận. Profile/native chỉ cooperative/advisory, không host sandbox/enforcement.
- Giữ residual A-09/A-10/A-11: conservative hash invalidation, journal không nguyên tử và TOCTOU cuối; adapter receipt không chứng minh invocation. Giới hạn chi tiết nằm HANDOFF; không tự mở lại tranche đã nhận.

## Waiting on user

- Không chờ xác nhận công bố: operator đã giao đồng bộ prerelease và thông tin project, RC2 đã đăng. Chưa có feedback người dùng mới.
- Không có quyền stable/final hoặc host/global/admin/CVF cha từ lần phát hành này.

## Decisions

- MVP trước, feedback sau; không thêm feature/pilot bắt buộc hoặc nhận mock thành usability thật.
- RC dùng VERSION1.9.0 và tag v1.9.0-rc2; không retag/thay asset RC1 hoặc đổi stable/latest1.8.0.
- Project mới bắt đầu PROFILE/grants[]; không tự tạo quyền/model/host. Dòng legacy chỉ bootstrap khi rõ, không suy quyền dispatch.
- Công bố đúng commit/gate sạch; maintainer metadata sau phát hành được chứng minh không đổi package bytes. Không force/CI skip/cancel hoặc refresh pin/MANIFEST kho nguồn.

## Next milestone

Dùng RC2 và gửi feedback qua form/Issues đã có; theo dõi CI main mới. Chỉ sửa finding cụ thể tiếp theo, không dựng thêm roadmap hoặc release khi chưa có căn cứ.
