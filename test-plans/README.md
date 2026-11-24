# JMeter test plans

| Scenario | Test plan | Listener |
| --- | --- | --- |
| Load | [23120262_Load_20261124.jmx](23120262_Load_20261124.jmx) | Summary Report |
| Stress | [23120262_Stress_20261124.jmx](23120262_Stress_20261124.jmx) | Aggregate Report |
| Spike | [23120262_Spike_20261124.jmx](23120262_Spike_20261124.jmx) | View Results Tree |

Cả ba plan dùng cùng sáu HTTP sampler và assertion. Generator dùng một định nghĩa workflow rồi lắp vào các nhóm thread của mỗi profile. File JMX chứa listener tương ứng ở trạng thái tắt để hạn chế ảnh hưởng lên số đo CLI. Khi xem kết quả, mở đúng JMX, bật listener trong GUI và nạp JTL của lượt tương ứng. Với View Results Tree, đọc mẫu nhỏ để giữ giao diện ổn định. JTL đo chỉ có dữ liệu thời gian, mã phản hồi, assertion và thông tin sample, không chứa body hay token.

Runner sinh dashboard HTML độc lập với listener. Công cụ kiểm số liệu tạo ba kiểu đầu ra dẫn xuất là `summary-report.csv`, `aggregate-report.csv` và `sample-details.json`.

[Quy trình chạy](../docs/test-workflow.md), [Điều kiện đo](../docs/measurement-protocol.md)
