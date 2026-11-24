# Kết quả chạy

Lưu mỗi lượt theo `results/<scenario>/<run-id>/`, với `scenario` là `load`, `stress`, `spike` hoặc `endurance`. Giữ JTL gốc, thư mục HTML chứa cả tài nguyên tĩnh, log JMeter và ghi chú lượt chạy. Ghi commit SUT, test plan, CSV, thời gian, người thực hiện, tải đặt và tải quan sát, p95, tỷ lệ lỗi, tài nguyên và liên kết ảnh.

Đánh dấu lượt smoke, lượt chạy lại và lượt được dùng trong báo cáo. Khi tính throughput, nêu đang đếm request hay transaction, cách loại trùng parent sample và cửa sổ thời gian dùng làm mẫu số.
