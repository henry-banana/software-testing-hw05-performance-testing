# Điều kiện đo và tiêu chí đọc kết quả

Đo backend EShop tại `127.0.0.1:3000`. Mỗi lượt dùng process Node mới, SQLite seed lại từ cùng commit và 384 tài khoản tổng hợp từ một CSV. Chuẩn bị fixture trước khi đo. Một VU giữ một dòng CSV trong cả vòng đời, khác tài khoản với các VU đang chạy ở mọi nhóm thread.

| Kịch bản | Tải thiết kế | Vì sao |
| --- | --- | --- |
| Load | 16 VU, ramp 15 giây, chạy 100 giây | Có giai đoạn tải giữ nguyên đủ để đọc baseline |
| Stress | 16, 48, 96, 192 và 384 VU. Mỗi bậc 40 giây, ramp tăng thêm 6 giây | Tăng bậc để tìm vùng p95 hoặc error rate vượt mục tiêu. Cửa sổ phân tích bắt đầu giây 10 và kết thúc trước giây 38 của mỗi bậc |
| Spike | Tải nền 16 VU, thêm 112 VU từ giây 30 trong 2 giây, bỏ nhóm thêm vào khoảng giây 56. Tổng 100 giây | Quan sát trước đỉnh, lúc đỉnh và sau khi trở về 16 VU |
| Endurance | Dùng plan Load với số VU xác định sau Stress và plateau 12 phút | Kiểm tra độ ổn định sau khi số đơn và giỏ tăng theo thời gian |

Pace 850 đến 1150 ms ở đầu mỗi workflow, mô phỏng khoảng nghỉ giữa hai lần mua ở client API. Các bước cùng một lần mua đi nối tiếp. Tắt retry HTTP và sang vòng tiếp theo khi sampler lỗi. Timeout kết nối 2 giây, timeout nhận phản hồi 5 giây. Kiểm token, sản phẩm, xác nhận giỏ, orderId và đúng đơn vừa tạo trong lịch sử.

Ngưỡng dùng cho phép đo này là p95 của **từng sampler** tối đa 250 ms và tỷ lệ lỗi toàn cửa sổ tối đa 1%. Đây là tiêu chí đánh giá thử nghiệm. Đọc thêm RPS ở các bucket 10 giây và so đầu, cuối endurance để nhận ra suy giảm. Nếu RAM trống xuống dưới 1200 MiB hoặc backend vượt 1400 MiB working set, runner dừng để giữ máy còn hoạt động. Báo giới hạn nếu Java và backend cùng chiếm tài nguyên máy.

P95 kiểm lại bằng nearest rank trên cột `elapsed`. Phân tích cửa sổ theo thời điểm hoàn thành bằng `timeStamp + elapsed`. RPS đếm toàn bộ HTTP sample đã hoàn thành trong cửa sổ. Workflow hoàn tất được đại diện bằng sampler lịch sử đơn thành công và đếm riêng. Tool lấy CPU theo phần trăm một core, RAM theo working set và dung lượng tính theo MiB.
