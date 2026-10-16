# assets/

Nơi đặt logo và tên đơn vị để bảng điều khiển (`APP.bat` / `APP.command`) và các trang hướng dẫn (`START_HERE.html`, `docs/*.html`) hiển thị thay cho biểu tượng mặc định "LW" và dòng chữ *Local Agent Workspace*. Không bắt buộc.

## 1. Logo

Đặt file ảnh vào thư mục này với tên `logo.png` (hoặc `logo.svg`, `logo.jpg`, `logo.webp`), dung lượng tối đa 2 MB. Logo hiển thị trong ô vuông nền trắng, nên dùng ảnh vuông hoặc gần vuông.

## 2. Tên đơn vị (tùy chọn)

Tạo file `branding.json` trong thư mục này với nội dung:

```json
{
  "title": "Tên đơn vị",
  "subtitle": "Agent Workspace",
  "logo": "logo.png"
}
```

- `title`: tên đơn vị hoặc tác giả, thay cho *Local Agent Workspace*. Tên dài được thu nhỏ chữ cho vừa một dòng.
- `subtitle`: dòng phụ bên dưới, thay cho *Bảng điều khiển*.
- `logo`: tên file logo, khi không đặt tên là `logo.*`.

## 3. Trang hướng dẫn

Trang hướng dẫn mở trực tiếp từ file nên không đọc được `branding.json`. Mỗi lần mở bảng điều khiển, nó ghi lại `assets/branding.js` từ `branding.json` để các trang hướng dẫn dùng. Sau khi sửa `branding.json`, mở APP một lần rồi tải lại trang hướng dẫn.

*Thư mục này thuộc về người dùng: nâng cấp bộ công cụ không ghi đè file ở đây.*
