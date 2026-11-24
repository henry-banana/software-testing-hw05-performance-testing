# Fixture CSV

[workflow.csv](workflow.csv) có 384 dòng tài khoản tổng hợp cho EShop cục bộ. Mỗi dòng chứa `email`, `password`, `product_id`, `total_amount` và `shipping_address`. Tài khoản xoay vòng giữa năm sản phẩm seed và mỗi lượt mua số lượng 1. Mật khẩu và địa chỉ là dữ liệu thử.

`scripts/build_plans.py` tạo file. `scripts/run_scenario.py` đối chiếu sản phẩm và giá qua API, kiểm email duy nhất và đăng ký tài khoản ngoài khoảng đo. Tại đầu vòng đầu tiên, JMeter lấy một dòng từ CSV theo số thread và offset nhóm. Các nhóm chạy đồng thời có vùng dòng rời nhau. VU dùng lại cùng dữ liệu cho các vòng sau, theo mục tiêu kiểm ảnh hưởng của giỏ và lịch sử tích lũy.
