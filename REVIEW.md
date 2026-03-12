# Cisco Network Builder Review

## Hiện trạng

Ứng dụng hiện là một GUI Tkinter sinh cấu hình router cơ bản từ:

- mạng gốc
- số router
- topology
- giao thức định tuyến
- tùy chọn DHCP

Nó chưa có cơ chế đọc hoặc mô phỏng trực tiếp file Cisco Packet Tracer `.pkt`.

## Lỗi đã thấy rõ

1. Chuỗi giao diện từng bị lỗi mã hóa, làm mất tính dễ dùng.
2. `tao_topology()` trước đó chỉ xử lý `Chuỗi` và `Vòng`, trong khi UI cho phép `Sao` và `Lưới`.
3. `sinh_config()` trước đó bật RIP/OSPF nhưng không thêm `network`, nên định tuyến động không hoạt động đúng mục đích.
4. `export_configs()` từng xóa cả thư mục `configs`, dễ gây mất file ngoài ý muốn nếu sau này thư mục này chứa thêm tài liệu khác.
5. UI từng không bắt lỗi input, nên có thể crash khi nhập sai subnet hoặc số router.

## Giới hạn khi test file `.pkt`

File `D:\FTC\An Ninh Mạng\Buoi4_NATDong.pkt` có tồn tại, nhưng project này không có:

- parser cho `.pkt`
- tích hợp Packet Tracer
- import/export trực tiếp vào topology của `.pkt`

Vì vậy không thể "chạy test trong file `.pkt`" bằng chính mã nguồn hiện tại. Để test được theo hướng này, cần thêm một trong hai cách:

1. Xuất config rồi paste/import thủ công vào Packet Tracer.
2. Xây bộ chuyển đổi topology từ một định dạng trung gian (JSON/YAML) sang bộ config của tool.

## Đề xuất file `.md`

Nên bổ sung ít nhất các file sau:

- `README.md`: mô tả mục đích, cách chạy, input/output, ví dụ.
- `TESTING.md`: checklist test tay và các case biên.
- `ARCHITECTURE.md`: luồng dữ liệu `subnet -> topology -> config -> export`.
- `CHANGELOG.md`: ghi lại các bản sửa đổi.
