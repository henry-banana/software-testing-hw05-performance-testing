# Checklist HW05

## 1. Chốt phạm vi và môi trường

- [ ] Xem deadline và giới hạn tải tệp trên Moodle. Đọc lại slide performance testing và rubric HW05.
- [ ] Đối chiếu với thành viên nhóm, ghi workflow đã chọn và mapping ba nhóm API auth-heavy, read-heavy, transactional. Ba kịch bản dùng chung một workflow.
- [ ] Cross-review thiết kế với thành viên nhóm. Ghi phản hồi, phần chỉnh sửa và lý do giữ hoặc đổi quyết định.
- [ ] Chốt remote và commit SUT, chạy backend trên bản thử riêng, ghi phiên bản Node.js, Java, JMeter và hostname. Kiểm thử nhanh API đọc và các bước workflow với dữ liệu tổng hợp.
- [ ] Tạo CSV cho tài khoản, sản phẩm và dữ liệu đơn hàng cần dùng. Xác minh account tồn tại, cách gán tài khoản cho VU, cách reset khóa đăng nhập, giỏ hàng và SQLite giữa các lượt chạy.

## 2. Task 1. Thiết kế và đo

- [ ] Ghi từng tương tác AI về workflow, CSV, assertion, think-time, ramp-up, thời lượng và VU. Sinh lần lượt Load, Stress và Spike.
- [ ] Sinh viên review và sửa từng plan. Ghi lỗi hoặc thiếu sót, nguyên nhân và thay đổi. Kiểm response code, dữ liệu nghiệp vụ, token, dữ liệu tạo đơn và cách dừng vòng lặp sau bước lỗi.
- [ ] Đặt ba tên plan theo mẫu `23120262_{ScenarioType}_{YYYYMMDD}.jmx`. Chọn ba listener hoặc report view khác loại nhau, mỗi plan một loại.
- [ ] Chạy smoke nhỏ trên từng plan. Xác nhận đủ ba nhóm endpoint, không gửi lại request ghi khi kết quả chưa rõ, fixture đủ và JTL có thể tạo dashboard HTML.
- [ ] Chạy Load với tải đại diện và giai đoạn ổn định. Lưu nguyên JTL, cả thư mục HTML và ảnh JMeter cùng tài nguyên tiến trình backend trong một khung.
- [ ] Chạy Stress theo các bậc tăng. Lưu cùng bộ bằng chứng và ghi bậc bắt đầu vượt ngưỡng đã định hoặc giới hạn đã thử.
- [ ] Chạy Spike với tải nền, tăng nhanh, hạ và quan sát hồi phục. Lưu cùng bộ bằng chứng và ghi thời gian hồi phục nếu đo được.
- [ ] Nếu Stress hoặc Spike làm khóa tài khoản, ghi kết quả quan sát và reset giữa các lượt. Tách lỗi thật khỏi sai CSV, assertion, quá tải máy phát tải hoặc lockout theo đặc tả.
- [ ] Đo thêm endurance trong khoảng 10 đến 15 phút ở tải duy trì. Chọn mức dựa trên các bậc đã thử, ghi RPS ổn định cao nhất đã xác nhận, p95, tỷ lệ lỗi, CPU, đỉnh và xu hướng RAM. Nếu chưa chạm giới hạn, ghi mức cao nhất đã xác minh và giới hạn phép đo.
- [ ] Lưu ảnh dxdiag hoặc tương đương và bảng thông số. Đối chiếu hostname với máy đã dùng ở bài trước.
- [ ] Ghi lỗi thực tế có bằng chứng lên GitHub Issues của nhóm. Tra trùng, gắn liên kết và lưu ảnh trang issue. Chỉ tính vấn đề hiệu năng có căn cứ; báo lỗi hiệu năng là phần khuyến khích.
- [ ] Quay demo tổng ít nhất 6 phút, tự thuyết minh tiếng Việt, JMeter và màn hình tài nguyên cùng khung. Có thể chia clip theo scenario. Kiểm link YouTube Unlisted.

## 3. Task 2. Phân tích và phản biện AI

- [ ] Đưa các JTL gốc cho AI phân tích và đề xuất ngưỡng. Lưu prompt, đầu ra và phạm vi dữ liệu AI sử dụng.
- [ ] Tự tính lại hoặc kiểm độc lập số mẫu, p95, throughput và tỷ lệ lỗi theo scenario, sampler và khoảng thời gian. Đối chiếu sample request và sample transaction để tránh đếm hai lần.
- [ ] Với mỗi hiểu sai thực tế, ghi nhận định gốc, giá trị đúng, JTL, sampler, khoảng thời gian, cách tính và nguyên nhân. Rà soát nhận định thay vì tạo lỗi AI giả.
- [ ] Phân loại từng đề xuất tối ưu AI là khả thi hay hallucinated. Dẫn bằng chứng từ SUT, giải thích cơ chế và điều kiện áp dụng.

## 4. Task 3. Đề xuất Continuous Performance Testing

- [ ] Vẽ flowchart từ commit SUT, điều kiện chọn chạy, đo trên baseline tương đương, so p95, chạy xác nhận và báo regression.
- [ ] Nêu cách giảm nhiễu và đánh đổi giữa chi phí, độ bao phủ và cảnh báo sai. Ghi đề xuất trong kết luận báo cáo chính.

## 5. Agent Skill

- [ ] Viết skill dùng lại được cho API khác. Đầu vào gồm workflow, môi trường và ngưỡng. Đầu ra gồm thiết kế tải, hướng dẫn thu log và checklist kiểm số liệu.
- [ ] Dùng skill cho một nhóm endpoint hoàn chỉnh và có đoạn video minh họa từ đầu đến cuối. Gắn link trong báo cáo và README.

## 6. Commit, hồ sơ và nộp bài

- [ ] Commit tách theo bước thực tế như setup, fixture, từng plan, thực thi, phân tích AI, đề xuất và Agent Skill. Trích xuất `git-commit-log.txt` khi hoàn tất.
- [ ] Hoàn thiện báo cáo chính, phụ lục AI Audit có tên công cụ, ngày giờ, prompt và output của từng tương tác, và AI Critique 200 đến 300 từ do sinh viên viết. Xuất PDF tương ứng cho cả ba.
- [ ] Điền ba [biểu mẫu AI-03, AI-04 và AI-05](ai-audit/AI-Audit-Report.md#biểu-mẫu-tiếng-việt) theo thực tế, rà các mục cần chữ ký và xuất PDF cùng bộ hồ sơ theo cách đã dùng ở HW04.
- [ ] Cập nhật README với đúng rubric 30, 20, 20, 10, 10, 10. Ghi kịch bản đã chạy, nhóm endpoint, ngưỡng endurance bằng số, số issue và link demo.
- [ ] Đưa JMX và CSV tổng hợp lên repo công khai. Thử liên kết repo, issue, báo cáo và video.
- [ ] Đóng gói `23120262_HW05_AI_Performance_<SelfAssessedGrade>.zip`. Kiểm sau khi giải nén có đủ báo cáo MD và PDF, README, link repo, ba JMX, CSV, ba JTL gốc, ba thư mục HTML, bằng chứng phần cứng và tài nguyên, hồ sơ lỗi nếu có, link video, log Git, và skill nếu thực hiện. Kèm bằng chứng endurance.
- [ ] Kiểm giới hạn dung lượng và deadline trên Moodle rồi nộp. Chuẩn bị giải thích cách đo, số liệu gốc và phần review nếu được gọi vấn đáp 5 đến 7 phút.
