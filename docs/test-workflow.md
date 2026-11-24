# Setup và quy trình chạy HW05

## Môi trường

Lượt đo dùng Windows 11, Node.js 24.16.0, Apache JMeter 5.6.3 và Eclipse Temurin 21.0.10. Link tải và kiểm SHA512 nằm tại trang phát hành Apache. Smoke ban đầu cho thấy JMeter có thể in version với Java 25, nhưng Groovy của plan lỗi class-file version 69 khi chạy. Chọn Java 21 trong runner. Script dùng `psutil` để ghi CPU và working set theo PID. [Apache JMeter 5.6.3](https://jmeter.apache.org/download_jmeter.cgi)

Đề chỉ định SUT gốc `ttbhanh/eshop-sut`. Lượt đo dùng fork nhóm tại `de0f48f5b40939692e7029943295d44788f617ea`. Hai file backend dùng để đo trùng blob với bản local HW04 tại commit upstream đã dẫn trong ghi chú nguồn. [Ghi chú nguồn](references.md)

Chuẩn bị một bản clone riêng bên ngoài repo bài làm. Backend seed lại SQLite mỗi lần khởi động, vì vậy phải dùng dữ liệu thử có thể bỏ.

```powershell
$lab = Join-Path $env:TEMP 'csc13003-hw05-23120262'
New-Item -ItemType Directory -Path $lab -Force | Out-Null
$sut = Join-Path $lab 'eshop-sut'
git clone https://github.com/tkob-team/eshop-sut.git $sut
git -C $sut switch --detach de0f48f5b40939692e7029943295d44788f617ea
Push-Location (Join-Path $sut 'backend')
npm.cmd ci
node -e "require('sqlite3')"
Pop-Location
```

Nếu npm 12 báo đã chặn script cài native SQLite và kiểm tra bằng Node thất bại, chạy `npm.cmd install-scripts approve sqlite3` và `npm.cmd rebuild sqlite3` trong backend của bản thử, sau đó nhập lại mô-đun để xác nhận.

## Workflow đã dùng để đo

Mục tiêu là đặt hàng và xác nhận đơn mới xuất hiện trong lịch sử. Luồng tìm sản phẩm rồi checkout đã xuất hiện trong README của thành viên Phúc Hoàng. Xác nhận phạm vi với cả nhóm và lưu phản hồi cross-review trước khi nộp. [Workflow của Phúc Hoàng](https://github.com/nphoang-itus/hw05-performance-testing/blob/main/README.md#workflow-under-test-endpoint-option-a)

| Nhóm | API | Điều kiện đúng |
| --- | --- | --- |
| Auth-heavy | `POST /api/login` | Token hợp lệ và tài khoản trả về khớp CSV |
| Read-heavy | `GET /api/products`, `GET /api/products/:id` | Danh sách có sản phẩm fixture, detail khớp ID và giá |
| Transactional | `POST /api/cart`, `POST /api/checkout` | Có xác nhận thêm giỏ và nhận được `orderId` dương |
| Kiểm tra sau giao dịch | `GET /api/orders/my-orders` | Đơn mới nhất của chính tài khoản này khớp ID, giá và trạng thái pending |

Mỗi VU dùng một tài khoản tổng hợp cố định. Đăng ký tài khoản trước lượt đo. Khởi động lại backend giữa các lượt để reset SQLite, khóa tài khoản và giỏ trong bộ nhớ. Ghi các kiểm tra sai mật khẩu riêng khỏi kết quả đo. Mã cộng 2 vào bộ đếm sai mật khẩu, ảnh hưởng đến điều kiện khóa. [Mã login](https://github.com/tkob-team/eshop-sut/blob/de0f48f5b40939692e7029943295d44788f617ea/backend/server.js#L32-L65)

## Chạy từ repo bài làm

Sau khi giải nén JMeter đã xác minh, chỉnh hai biến đường dẫn công cụ theo máy. Cổng 3000 cần dành cho SUT thử. Runner mở tiến trình riêng, chỉ gửi request tới loopback, dừng đúng PID mình đã tạo và dùng thư mục kết quả mới cho từng lượt.

```powershell
$java = 'C:/Program Files/Eclipse Adoptium/jdk-21.0.10.7-hotspot/bin/java.exe'
$jmeter = Join-Path $lab 'tools/apache-jmeter-5.6.3'
python -m pip install -r scripts/requirements.txt
python -B scripts/build_plans.py
python -B scripts/run_scenario.py --sut $sut --java $java --jmeter $jmeter --mode smoke --run-id demo-smoke
python -B scripts/run_scenario.py --sut $sut --java $java --jmeter $jmeter --scenario Load --run-id demo-load
python -B scripts/run_scenario.py --sut $sut --java $java --jmeter $jmeter --scenario Stress --run-id demo-stress
python -B scripts/run_scenario.py --sut $sut --java $java --jmeter $jmeter --scenario Spike --run-id demo-spike
python -B scripts/analyze_jtl.py results/load/demo-load results/stress/demo-stress results/spike/demo-spike
```

Chọn VU cho endurance từ các bậc Stress đã đo. Ví dụ lệnh 96 VU, 720 giây plateau là `python -B scripts/run_scenario.py --sut $sut --java $java --jmeter $jmeter --mode endurance --vus 96 --seconds 720 --run-id demo-endurance`.

Bằng chứng nguồn nằm trong `results/<scenario>/<run-id>/`. Mở `console.log` để xem tiến độ và `resources.csv` để đối chiếu PID. Sau khi có log, mở JMX bằng đúng Java 21, bật listener khi xem file JTL đã thu và dùng mẫu nhỏ với View Results Tree. Ảnh live lấy trong lúc runner đang chạy.

[Điều kiện đo](measurement-protocol.md), [JMeter CLI](https://jmeter.apache.org/usermanual/get-started.html#non_gui), [JMeter Dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)
