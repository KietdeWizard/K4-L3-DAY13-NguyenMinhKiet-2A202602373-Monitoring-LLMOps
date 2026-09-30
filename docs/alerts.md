# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack
- SLI/SLO liên quan: `response_sent.latency_ms`, fast successful requests
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời đến chậm.
- Ba bước kiểm tra đầu tiên: xác nhận panel latency; lọc log theo latency và correlation ID; mở trace để so sánh retrieval/generation.
- Mitigation tạm thời: tắt scenario chậm, giảm tải hoặc rollback prompt nếu trace chứng minh prompt gây regression.
- Owner: `student-oncall`

## Alert 2

- Tên: `ElevatedErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack
- SLI/SLO liên quan: error budget của fast successful requests
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` trong 5 phút.
- Ảnh hưởng tới người dùng: request thất bại hoặc không có câu trả lời.
- Ba bước kiểm tra đầu tiên: xác nhận error panel; lọc `request_failed`; mở trace cùng correlation ID để tìm span lỗi.
- Mitigation tạm thời: tắt incident/tool lỗi, khôi phục cấu hình gần nhất và theo dõi error budget.
- Owner: `student-oncall`

## Alert 3

- Tên: `LowRetrievalSuccess`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack
- SLI/SLO liên quan: retrieval success rate guardrail
- Điều kiện và thời gian duy trì: `retrieval_success_rate_pct < 90%` trong 10 phút.
- Ảnh hưởng tới người dùng: câu trả lời thiếu context hoặc kém chính xác.
- Ba bước kiểm tra đầu tiên: xác nhận tỷ lệ `tool_success`; lọc request lỗi theo correlation ID; mở retrieval span để kiểm tra timeout/failure.
- Mitigation tạm thời: khôi phục vector store/configuration hoặc chuyển sang fallback an toàn.
- Owner: `student-oncall`
