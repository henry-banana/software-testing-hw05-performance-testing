# Setup và quy trình chạy HW05

## Môi trường đề xuất

Trên máy hiện tại, PowerShell thấy Node.js 24.16.0 và Java Temurin 25.0.2 qua PATH. Cần cài hoặc trỏ đến Apache JMeter, sau đó xác minh phiên bản Java và JMeter hoạt động cùng nhau. Task Manager dùng để chụp tiến trình Node của backend và dxdiag dùng để thu thông số máy.

Đề chỉ định SUT gốc `ttbhanh/eshop-sut`. Đề xuất lấy bản fork của nhóm làm baseline thử và ghi quan hệ với upstream trong báo cáo. Tại thời điểm chuẩn bị, mã hai file `backend/server.js` và `backend/database.js` của fork trùng với bản local HW04. Xem [ghi chú nguồn](references.md).

Từ thư mục `hw05`, tạo bản SUT riêng khi bắt đầu Task 1.

```powershell
git clone https://github.com/tkob-team/eshop-sut.git eshop-sut
Set-Location eshop-sut/backend
git rev-parse HEAD
npm.cmd ci
node server.js
```

Thử API đọc trong một terminal khác. Chỉ đo trên bản thử cục bộ đang kiểm soát.

```powershell
Invoke-RestMethod 'http://127.0.0.1:3000/api/products'
java -version
jmeter.bat --version
```

Nếu JMeter chưa nằm trên PATH, chạy `jmeter.bat` bằng đường dẫn tới thư mục `bin` của bản JMeter đã cài. Nếu cổng 3000 đã được dùng, xác định tiến trình và chạy trên môi trường thử riêng trước khi gửi tải. Đối chiếu startup thực tế và fixture của commit đã chốt.

## Workflow đang đề xuất

Phương án để đối chiếu với nhóm là đặt hàng và xác nhận đơn mới xuất hiện trong lịch sử. Luồng tìm sản phẩm rồi checkout đã được Phúc Hoàng ghi trong README của bạn ấy. [Workflow của Phúc Hoàng](https://github.com/nphoang-itus/hw05-performance-testing/blob/main/README.md#workflow-under-test-endpoint-option-a)

| Nhóm | API ứng viên | Điều kiện đúng cần kiểm |
| --- | --- | --- |
| Auth-heavy | `POST /api/login` | Tài khoản thử đăng nhập thành công và trích được token |
| Read-heavy | `GET /api/products`, `GET /api/products/:id` | Danh sách có sản phẩm fixture và chi tiết khớp ID |
| Transactional | `POST /api/cart`, `POST /api/checkout` | Dùng token của chính VU, kiểm nội dung phản hồi và `orderId` |
| Kiểm tra sau giao dịch | `GET /api/orders/my-orders` | Lịch sử của tài khoản thử có đúng `orderId` vừa tạo |

Xác nhận workflow với nhóm trước khi sinh JMX. Điền dữ liệu theo fixture thực tế. Kiểm số lượng tài khoản cho số VU đồng thời, tách request mồi khỏi kết quả đo, và đặt lại trạng thái ban đầu khi thay mức tải. Checkout ghi đơn trong SQLite và mã backend hiện tại giữ giỏ theo user trong bộ nhớ. Cần xác nhận giỏ và số đơn giữa lượt chạy để giữ điều kiện đo so sánh được.

Đề mô tả khóa sau ba lần đăng nhập sai. Đọc mã cho thấy nhánh sai mật khẩu cộng 2 vào bộ đếm mỗi lần. Kiểm hành vi thực tế trên fixture riêng và lưu bằng chứng trước khi kết luận. Dùng tài khoản hợp lệ trong workload chính và ghi cách reset nếu khóa phát sinh giữa các lượt. [Mã API login](https://github.com/tkob-team/eshop-sut/blob/de0f48f5b40939692e7029943295d44788f617ea/backend/server.js#L32-L65)

## Thiết kế phép đo

1. Smoke xác nhận từng bước với 1 VU và fixture tổng hợp.
2. Chọn Load với ramp và plateau, Stress với các bậc tăng, Spike với tải nền, đỉnh và phục hồi. Dùng chung mẫu request. Ghi VU, ramp, thời lượng, think-time, timeout và lý do.
3. Chốt tiêu chí ổn định trước khi đo. Xét p95, tỷ lệ lỗi, throughput và tài nguyên của backend lẫn máy phát tải.
4. Chạy chính thức bằng CLI, lưu JTL và sinh dashboard theo hướng dẫn trong [test-plans](../test-plans/README.md).
5. Chọn mức sát ngưỡng đã quan sát để chạy endurance khoảng 10 đến 15 phút. Giữ riêng log, dashboard và ảnh. Diễn giải kết quả theo máy, commit, fixture và workflow đã đo.

[Hướng dẫn setup EShop](https://github.com/tkob-team/eshop-sut/blob/main/setup_guide.md), [JMeter CLI](https://jmeter.apache.org/usermanual/get-started.html#non_gui), [JMeter Dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)
