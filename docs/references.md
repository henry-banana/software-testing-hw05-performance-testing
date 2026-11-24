# Nguồn tham khảo HW05

Đối chiếu đề PDF HW05, mục 5 đến 15, và quy định bài tập của môn. Rubric trong đề có Load 30, Stress 20, Spike 20, phân tích AI 10, đề xuất 10 và Agent Skill 10. EShop upstream trong đề là `ttbhanh/eshop-sut`. Nơi đăng issue theo lựa chọn của nhóm là `tkob-team/eshop-sut`. [EShop upstream](https://github.com/ttbhanh/eshop-sut), [GitHub Issues của nhóm](https://github.com/tkob-team/eshop-sut/issues)

## Các repo cùng đề

| Repo | Điểm tham khảo cho cấu trúc |
| --- | --- |
| [nphoang-itus/hw05-performance-testing](https://github.com/nphoang-itus/hw05-performance-testing) | Repo của Phúc Hoàng. Có tài liệu chọn endpoint, checklist theo rubric, thư mục kết quả riêng cho từng scenario và các script hỗ trợ prompt log, PDF, Git log, ZIP. |
| [Donavfulish/HW05](https://github.com/Donavfulish/HW05/blob/main/README.md) | Tách JMX, CSV, log, ảnh và skill. Tổ chức các bước trên Windows bằng PowerShell. |
| [ngothoaidev/23127124-HW05-Performance-Testing](https://github.com/ngothoaidev/23127124-HW05-Performance-Testing/blob/master/README.md) | Có bước smoke riêng, ghi điều kiện reset SUT và trình bày VU, RPS, p95, tỷ lệ lỗi, RAM trong phần endurance. |
| [phucnotphuc/eshop-hw05-performance](https://github.com/phucnotphuc/eshop-hw05-performance/blob/main/README.md) | Tách log gốc, HTML, phân tích AI, đề xuất và skill. README ghi điểm tối đa Load là 20, khác với 30 trong đề đang dùng. |
| [nhaajtdajt/eshop-hw05-performance-testing](https://github.com/nhaajtdajt/eshop-hw05-performance-testing/blob/main/README.md) | Đặt SUT cạnh repo bài làm, dùng fixture tổng hợp riêng cho từng lượt đo và runner PowerShell. |

Tham khảo bố cục và cách thu bằng chứng. Workflow, prompt, script, tham số, số liệu và nhận xét của HW05 được làm theo phạm vi của sinh viên.

Trong README, Phúc Hoàng ghi phương án A gồm login, tìm và xem chi tiết sản phẩm, thêm giỏ, checkout. Luồng này trùng phần chính với đề xuất ban đầu của HW05 23120262. Khi thống nhất phạm vi trong nhóm, dùng [phương án đặt hàng và kiểm lịch sử đơn](test-workflow.md#workflow-đang-đề-xuất) để đối chiếu. [README của Phúc Hoàng](https://github.com/nphoang-itus/hw05-performance-testing/blob/main/README.md), [tài liệu chọn endpoint](https://github.com/nphoang-itus/hw05-performance-testing/blob/main/docs/endpoint-proposal.md)

Điểm đáng áp dụng là ghi riêng giả thuyết kỹ thuật và kết quả đo. Repo của Phúc Hoàng cũng tách nhật ký prompt nguyên văn và AI Audit có phần sinh viên nhận xét. Khi chuẩn bị runner cho Windows, áp dụng ý tưởng xác minh backend sau khi khởi động và quản lý PID của đúng bản thử. [Cách ghi prompt log](https://github.com/nphoang-itus/hw05-performance-testing/blob/main/scripts/ailog.py), [script khởi động SUT](https://github.com/nphoang-itus/hw05-performance-testing/blob/main/scripts/start-sut.sh)

## SUT và công cụ

- Mã nhóm tại commit `de0f48f5b40939692e7029943295d44788f617ea` cung cấp API login, products, categories, cart và checkout trên cổng 3000. So sánh blob Git xác nhận `server.js` và `database.js` có cùng nội dung với bản local HW04 tại `85af3ba875c88283615e22cb108f13e2fccaf0e9`. [Backend nhóm](https://github.com/tkob-team/eshop-sut/blob/de0f48f5b40939692e7029943295d44788f617ea/backend/server.js), [SQLite fixture](https://github.com/tkob-team/eshop-sut/blob/de0f48f5b40939692e7029943295d44788f617ea/backend/database.js)
- JMeter có CSV Data Set Config và ba listener được đề gợi ý. Dùng CLI khi đo và mở listener phù hợp để xem mẫu hoặc số liệu. Giữ CSV JTL đủ cột để tạo dashboard HTML về sau. [JMeter components](https://jmeter.apache.org/usermanual/component_reference.html), [JMeter CLI](https://jmeter.apache.org/usermanual/get-started.html#non_gui), [Dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)
