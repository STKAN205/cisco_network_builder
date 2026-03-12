# Cisco Network Builder

Tool GUI (Tkinter) để sinh cấu hình router Cisco cơ bản dựa trên mạng gốc, số router và topology.

## Tính năng

- Chia subnet LAN/WAN tự động từ mạng gốc
- Sinh config cho từng router (LAN + các link WAN)
- Hỗ trợ RIP v2 hoặc OSPF area 0
- Tùy chọn DHCP cho LAN
- Tùy chọn NAT (PAT/Overload) cho 1 router
- Xuất config ra thư mục `configs/`

## Yêu cầu

- Windows
- Python 3.x (khuyến nghị 3.10+)

## Chạy chương trình

```
powershell
py main.py
```

Nếu máy bạn chưa cài Python, cài từ python.org, sau đó chạy lại lệnh trên.

## Cách dùng (GUI)

- `Mạng gốc`: ví dụ `192.168.27.0/24`
- `Số router`: ví dụ `6`
- `Topology`:
  - `Chuỗi`: R1-R2-R3-...
  - `Vòng`: R1-R2-...-Rn-R1
  - `Sao`: R1 là trung tâm nối tới các router còn lại
  - `Lưới`: mọi cặp router đều kết nối với nhau
- `Protocol`: `RIP` hoặc `OSPF`
- `DHCP`: bật để tạo pool DHCP cho LAN của mỗi router
- `NAT (PAT/Overload)`: bật để sinh NAT cho một router
- `NAT router (ID)`: router sẽ bật NAT (mặc định `1`)
- `NAT outside interface`: interface WAN dùng làm outside (mặc định `se2/0`)
- `Default route next-hop (tuỳ chọn)`: next-hop cho default route (nếu có ISP/Internet)
- `Sinh Config`: sinh config và hiển thị trong ô text
- `Xuất file`: ghi file `configs/R1.txt`, `configs/R2.txt`, ...

## Output

Sau khi bấm `Xuất file`, thư mục `configs/` sẽ chứa các file cấu hình theo từng router.

## Giới hạn hiện tại

- Chưa có cơ chế đọc/ghi trực tiếp file Cisco Packet Tracer `.pkt`.
- Số cổng serial hỗ trợ hiện tại là 4 cổng/router (`se2/0`, `se3/0`, `se2/1`, `se3/1`).
  - Với topology `Lưới` và số router lớn, có thể báo lỗi do một router cần nhiều link WAN hơn số cổng hỗ trợ.

## Chuẩn hóa Unicode (tiếng Việt có dấu)

Repo đã có `.editorconfig` để chuẩn hóa `UTF-8`. Một số lưu ý để tránh lỗi kiểu `Máº¡ng`:

- VS Code: kiểm tra góc phải dưới `UTF-8`
  - Nếu đang sai: chọn `Reopen with Encoding...` -> `UTF-8`, rồi `Save with Encoding...` -> `UTF-8`
- Chuẩn hóa dạng Unicode: code dùng `unicodedata.normalize("NFC", ...)` cho tên topology để nhận cả giá trị cũ (ASCII/mojibake).
- Nếu bạn thấy text trong GUI bị lỗi font: Windows nên dùng `Segoe UI` (app đã set mặc định).
- PowerShell: `Get-Content` có thể hiển thị sai nếu file không có BOM
  - Dùng: `Get-Content -Encoding utf8 <file>` hoặc `[IO.File]::ReadAllText(<file>, [Text.Encoding]::UTF8)`

## Cấu trúc thư mục

- `main.py`: entrypoint GUI
- `ui/`: giao diện Tkinter
- `core/`: logic chia subnet, dựng topology, sinh config
- `services/`: xuất file, dịch vụ phụ trợ
- `utils/`: constants và helper
- `configs/`: output sau khi xuất file

## Mở rộng dự án

- Thêm topology mới:
  - Sửa danh sách `TOPOLOGIES` và mapping `TOPOLOGY_WAN_COUNT` trong `utils/constants.py`
  - Cài đặt link/port trong `core/topology.py`
- Thêm protocol mới:
  - Mở rộng `PROTOCOLS` trong `utils/constants.py`
  - Thêm nhánh sinh config trong `core/config_generator.py`

## Tài liệu khác

- `REVIEW.md`: đánh giá nhanh và giới hạn hiện tại
