# Kiểm thử, đánh giá độc lập và đóng gói

## Kiểm thử tối thiểu

Dùng dữ liệu giả hoặc đã che. Sinh ca từ quy tắc và cấu hình đã xác nhận; mỗi phép kiểm phù hợp cần ca hợp lệ, vi phạm, thiếu dữ liệu và ngoài phạm vi. Bộ ca dưới đây là khung, không thay cho yêu cầu riêng của project.

| Nhóm | Ca cần bao quát |
|---|---|
| Đọc vị trí | Thành phần Block-Bay-Row-Tier, dấu phân cách, số thiếu hoặc sai; tiền tố block chỉ được bổ sung khi có ánh xạ đã duyệt |
| Phạm vi và đối chiếu | Incoming, Outgoing, hàng nhập/rỗng xuất, lưu lâu, ngoài bãi, mã thiếu và các nhóm còn lại; bảng đối chiếu dòng phải khớp |
| Trạng thái ở ô | Theo mapping TOS đã xác nhận, bản ghi đã rời ô không tạo trùng ô hoặc cảnh báo lẫn tàu/lót pháo với cont đang chiếm ô |
| Cảnh báo | Các ca lót pháo mà project xác nhận (snapshot nhắc năm loại nhưng không liệt kê đủ); RTG cùng/khác Row; lẫn tàu ở block thường/RTG; một cont lệch kế hoạch |
| ISO và cỡ | Hàng/rỗng theo bảng được duyệt, mã đặc biệt, cont lạnh và quy ước TEU; ví dụ nguồn phải được xác nhận trước khi thành dữ liệu kỳ vọng |
| Mốc dữ liệu | Mốc nhập, tên file theo mẫu được duyệt, ngày sửa file nếu được chấp nhận, nguồn mâu thuẫn, giá trị cũ và ngưỡng chưa cấu hình |
| Báo cáo | Tổng và đơn vị đối chiếu được với dòng nguồn; liên kết tới sheet/dòng có thật; HTML ngoại tuyến hiển thị dữ liệu như văn bản an toàn |
| Cấu hình | Thiếu khóa bắt buộc, sai kiểu, giá trị chưa duyệt hoặc đơn vị không tương thích phải dừng phép kiểm phụ thuộc và nêu rõ lý do |

Không dùng một tổng số ca để thay cho độ bao phủ theo quy tắc. Test ứng dụng chỉ cho biết ứng dụng xử lý ca thử thế nào; không chứng minh mọi quy tắc nghiệp vụ đúng hoặc skill có hiệu quả.

## Đánh giá độc lập một ứng dụng có sẵn

1. Đọc đường đi của dữ liệu: đọc file, nhận diện cột, chuẩn hóa, phân tích; kiểm có giới hạn phần xuất báo cáo, liên kết và cách hiển thị dữ liệu HTML.
2. Chạy bộ kiểm thử của ứng dụng và ghi đúng kết quả, môi trường cùng phần chưa chạy.
3. Chỉ chạy dữ liệu thật khi được phép; xuất vào thư mục tạm riêng, không đụng báo cáo, lịch sử hay thư mục nguồn.
4. Đối chiếu từng mã kiểm soát, mẫu vị trí lỗi, bảng Trạng thái × Hướng và ISO × F/E; kiểm cảnh báo có phụ thuộc vào trạng thái chưa xác nhận hay không.
5. Lượng hóa từng nghi vấn bằng lần chạy có và không có đúng một điều kiện cấu hình; ghi đơn vị, đầu vào và thay đổi ở đầu ra. Ví dụ số lượng trong nguồn cũ chỉ là ví dụ, không phải tiêu chí của project hiện tại.
6. Báo cáo lỗi theo ảnh hưởng, kèm vị trí mã, ca dữ liệu, kết quả đầu ra và đề xuất; ghi phần chưa kiểm như giao diện, Excel thực tế hoặc file đóng gói.
7. Hỏi người dùng về trạng thái, tên block, mã ISO hoặc quy tắc khác còn mơ hồ. Không tự sửa quy tắc nghiệp vụ khi chưa có câu trả lời.

## Mẫu spec PyInstaller

Đây là khung tham khảo, không phải lệnh đã được thử trong project. Xác nhận phiên bản, dependency, quyền cài đặt và cách chạy trước khi build. Chỉ loại thư viện sau khi kiểm mã và thử bản đóng gói.

    import os
    from PyInstaller.utils.hooks import collect_submodules

    root = SPECPATH
    hidden = collect_submodules("<package>")
    excludes = ["<unused_module_confirmed_by_review>"]
    a = Analysis(
        [os.path.join(root, "<entry>.py")],
        pathex=[root],
        binaries=[],
        datas=[],
        hiddenimports=hidden,
        hookspath=[],
        runtime_hooks=[],
        excludes=excludes,
        noarchive=False,
    )
    pyz = PYZ(a.pure)
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name="<AppName>",
        debug=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
    )

Không chép nguyên danh sách loại trừ từ ứng dụng khác. Một module nạp muộn có thể cần hiddenimports; dependency được dùng gián tiếp phải được giữ lại.

## Thử bản đóng gói

Build thử vào thư mục tạm riêng bằng đường dẫn build/output được hỗ trợ. Kiểm theo hợp đồng của ứng dụng:

- Chạy `--input <file> --output <thu_muc_tam>` nếu ứng dụng hỗ trợ các cờ này; đối chiếu mã thoát, số liệu, sheet và HTML với lần chạy trực tiếp.
- Nếu có chế độ tự tìm file như --auto, kiểm tra vị trí tìm file và báo rõ file được chọn.
- Thử file đầu vào không tồn tại; cần thông báo dễ hiểu, mã thoát lỗi theo hợp đồng và file lỗi nếu ứng dụng hỗ trợ.
- Nếu có giao diện, mở và đóng ứng dụng thử trong môi trường riêng; kiểm tiêu đề, trạng thái và lỗi khởi động.
- Với console=False, cửa sổ console không hiển thị; xác nhận log, mã thoát và báo lỗi vẫn có thể kiểm tra.
- Chỉ đưa bản đạt vào thư mục phân phối theo yêu cầu của người dùng; không xóa các bản thử nếu chưa được giao.

## Bẫy kỹ thuật

- Chuỗi tiếng Việt có thể khác chuẩn Unicode NFC/NFD; kiểm dữ liệu trước khi thay chuỗi bằng công cụ tự động.
- Sao chép file có thể đổi ngày sửa; ca thử cần giữ mốc thì dùng `cp -p` hoặc đặt `os.utime` có chủ đích. Không dùng thời gian file làm mốc nghiệp vụ nếu chưa xác nhận.
- Kiểm pandas với `-W error::FutureWarning` trước khi nâng phiên bản; `fillna` trên chuỗi map toàn rỗng từng sinh FutureWarning, có thể tra từ điển bằng list comprehension sau khi kiểm kết quả.
- Console Windows cp1252 có thể làm lỗi `--help` tiếng Việt; kiểm cách chạy thực tế với `-X utf8` hoặc cấu hình UTF-8 cho stdout/stderr khi khởi động.

## Bàn giao

Ghi phiên bản ứng dụng và cấu hình, nguồn cùng mốc dữ liệu, số liệu kèm đơn vị, phép kiểm đã chạy, cảnh báo được người dùng đối chiếu và phần còn chưa xác nhận. Nêu đường dẫn đầu ra đã kiểm. Giữ nguyên nguồn và báo cáo gốc.
