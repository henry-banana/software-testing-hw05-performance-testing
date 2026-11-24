# JMeter test plans

| Scenario | File khi tạo | Report view đề xuất |
| --- | --- | --- |
| Load | `23120262_Load_YYYYMMDD.jmx` | Summary Report |
| Stress | `23120262_Stress_YYYYMMDD.jmx` | Aggregate Report |
| Spike | `23120262_Spike_YYYYMMDD.jmx` | View Results Tree |

Thay `YYYYMMDD` bằng ngày thực tế khi đặt tên file. Cả ba plan có cùng workflow và sampler label. Tắt listener nặng trong lượt đo CLI. Dùng View Results Tree với một phần dữ liệu của chính lượt Spike để kiểm tra, đồng thời giữ nguyên log đầy đủ. Ảnh mỗi scenario phải khớp với lượt đo và lưu đủ ba thư mục dashboard HTML.

Mẫu lệnh PowerShell từ repo bài làm sau khi test plan đã có. Dùng tên và thư mục mới cho từng lượt.

```powershell
$plan = '23120262_Load_YYYYMMDD'
$run = 'results/load/run-01'
New-Item -ItemType Directory -Path $run | Out-Null
jmeter.bat -n -t "test-plans/$plan.jmx" -l "$run/$plan.jtl" -j "$run/jmeter.log" -e -o "$run/html"
```

[JMeter CLI](https://jmeter.apache.org/usermanual/get-started.html#non_gui), [Hướng dẫn tạo dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)
