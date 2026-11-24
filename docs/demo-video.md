# Kịch bản quay demo HW05

Quay khoảng 7 phút. Mở PowerShell hoặc JMeter cạnh Task Manager. Chọn tiến trình Node có PID khớp cột `backend_pid` trong `resources.csv` của lượt đang quay. Đặt tiêu đề cửa sổ và zoom để đọc được cả CLI lẫn tài nguyên trong cùng khung. Dùng giọng tiếng Việt của sinh viên.

| Thời lượng | Nội dung cần trình bày |
| --- | --- |
| 0:00 đến 0:50 | Giới thiệu MSSV, EShop, commit, Node, Java, JMeter, máy và fixture tổng hợp |
| 0:50 đến 2:15 | Áp dụng Agent Skill cho nhóm transactional. Chỉ CSV, token, add-to-cart, checkout và kiểm orderId trong lịch sử. Chạy smoke thật và so JTL với assertion |
| 2:15 đến 3:20 | Load. Chỉ profile 16 VU, CLI và tiến trình Node trong cùng khung. Mở Summary Report và JTL đã thu |
| 3:20 đến 4:25 | Stress. Giải thích các bậc VU và bậc nào đạt hoặc vượt tiêu chí. Chỉ Aggregate Report, CPU và RAM |
| 4:25 đến 5:35 | Spike. Giải thích tải nền, đỉnh, hạ tải và kết quả kiểm hồi phục. Chỉ View Results Tree với mẫu từ lượt Spike |
| 5:35 đến 6:30 | Endurance. Chỉ cửa sổ 12 phút, RPS, p95, peak working set và thay đổi kích thước lịch sử đơn |
| 6:30 đến 7:00 | Một nhận định AI đã kiểm lại từ JTL, một đề xuất khả thi và điểm còn giới hạn |

Nếu quay lượt mới, nói rõ đâu là lượt demo và đâu là số liệu trong báo cáo. Để video ở chế độ YouTube Unlisted. Ghi link và mốc minh họa skill vào README và báo cáo. Chụp riêng ba ảnh trong lúc mỗi lượt Load, Stress, Spike chạy và một ảnh dxdiag để nộp cùng hồ sơ.
