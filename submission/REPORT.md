# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Minh Kiệt
- **MSSV:** 2A202602373 
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/KietdeWizard/K4-L3-DAY13-NguyenMinhKiet-2A202602373-Monitoring-LLMOps
- **Commit SHA cuối:**
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602373`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Not captured before code changes | 100/100 | 0 missing fields, 0 PII leaks |
| `validate_dashboard.py` | Not captured | 6/6 panels | Dashboard contract valid |
| `pytest` | Not captured | 24 passed | Runtime test suite passed |
| Số traces hợp lệ | | | |
| Số PII leak | | | |
| Latency P95 / TTFT P95 | | | |
| Retrieval success rate | | | |

> Baseline note: CP0 health and Langfuse tracing were verified. The original starter validator score was not captured before code changes, so no baseline number is invented here. Runtime validator output, trace IDs, and challenge evidence must be added from the student's environment before submission.

Runtime metrics from the current 10-request load test: latency P95 1639 ms, TTFT P95 50 ms, retrieval success 100% (10/10). Langfuse trace count and prompt/challenge evidence remain to be confirmed in the personal project.

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
- **Các metadata được ghi vào structured log:**
- **Cách bảo đảm PII được scrub trước khi ghi:**
- **Cách kiểm chứng kết quả:**

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
- **Cấu trúc root/retrieval/generation observations:**
- **Cách nối trace với log:**
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1, label `baseline`; correlation ID `req-29a4ba70`.
- **Version/label candidate:** Version 2, label `candidate`; correlation ID `req-29b03aff`.
- **Trace ID của mỗi version:** Version 1: `9ad00a7f3172651782077398f11c42bc` (correlation ID `req-29a4ba70`); Version 2: `baec2d5e8fa1989463faf980639f9cc4` (correlation ID `req-29b03aff`).
- **Cách promote và rollback `production`:** Promote `production` từ Version 1 sang Version 2, xác nhận bằng trace mới; sau đó rollback `production` về Version 1 và xác nhận lại bằng trace mới.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
- **SLO và lý do chọn:**
- **Cách tính error budget:**
- **Ba alert và runbook tương ứng:**

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:** `response_sent`, `correlation_id=req-cab99b4a`, `latency_ms=2652`, `tool_success=true`; baseline average latency was 237 ms.
- **Trace ID và span gây ảnh hưởng:** `6e3169bf7adb8e8b6e022f3b6c55e616`; the `retrieval` span was the affected slow span.
- **Root cause:** The retrieval step was slowed by the active `rag_slow` incident; generation TTFT remained 50 ms.
- **Fix action:** Disable `rag_slow` and restore normal retrieval behavior.
- **Preventive measure:** Keep the `HighLatencyP95` alert and inspect the retrieval span using the same correlation ID during incidents.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
