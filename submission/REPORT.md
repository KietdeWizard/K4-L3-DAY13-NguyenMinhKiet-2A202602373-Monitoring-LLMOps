# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Minh Kiệt
- **MSSV:** 2A202602373
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/KietdeWizard/K4-L3-DAY13-NguyenMinhKiet-2A202602373-Monitoring-LLMOps
- **Commit SHA cuối:** `9c56652`
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse:** `day13-k4-l3b-2A202602373`

## 2. Evidence index

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
| Prompt promote | `evidence/10a-prompt-promote.png` |
| Prompt rollback | `evidence/10b-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---:|---:|---|
| `validate_logs.py` | Chưa capture trước khi sửa code | **100/100** | 0 missing fields, 0 missing enrichment, 0 PII leaks |
| `validate_dashboard.py` | Chưa capture | **6/6 panels** | Dashboard contract hợp lệ |
| `pytest` | Chưa capture | **24 passed** | Test suite pass |
| Số traces hợp lệ | Chưa capture | **Ít nhất 10** | Có trace list và waterfall trong Langfuse cá nhân |
| Số PII leak | Chưa capture | **0** | Validator không phát hiện PII thô |
| Latency P95 / TTFT P95 | Chưa capture | **1639 ms / 50 ms** | Từ workload 10 request trước challenge |
| Retrieval success rate | Chưa capture | **100% (10/10)** | Từ các event có `tool_success` |

Baseline validator không được capture trước khi sửa starter code, nên không ghi số ước đoán.

## 4. Logging và PII

- **Correlation ID:** Middleware xóa context cũ, nhận `x-request-id` hợp lệ hoặc sinh ID dạng `req-` + 8 ký tự hex, bind vào structlog và trả lại qua response header.
- **Response headers:** Mỗi response có `x-request-id` và `x-response-time-ms`.
- **Log enrichment:** Log có `user_id_hash`, `session_id`, `feature`, `model`, `env`, `latency_ms`, TTFT, tokens, cost, quality, tool status và correlation ID.
- **PII scrubbing:** `scrub_event` chạy trước JSONL file writer/JSON renderer và scrub đệ quy email, số điện thoại Việt Nam, CCCD và thẻ thanh toán.
- **Verification:** `validate_logs.py` đạt 100/100; evidence 04–05 chứng minh structured log và redaction.

## 5. Tracing và prompt versioning

- **Project:** Traces được kiểm tra trong project cá nhân `day13-k4-l3b-2A202602373`.
- **Span tree:** Root `lab-agent-run` có child `retrieval` và `generation`. Raw prompt/output không được capture.
- **Generation:** Generation có model, input/output usage và cost; prompt managed object được propagate để liên kết prompt version.
- **Liên kết log-trace:** Dùng cùng `correlation_id` giữa structured log và metadata của trace.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1, label `baseline`; correlation ID `req-29a4ba70`.
- **Version/label candidate:** Version 2, label `candidate`; correlation ID `req-29b03aff`.
- **Trace ID Version 1:** `9ad00a7f3172651782077398f11c42bc`.
- **Trace ID Version 2:** `baec2d5e8fa1989463faf980639f9cc4`.
- **Promote:** Label `production` được chuyển từ Version 1 sang Version 2; evidence `10a-prompt-promote.png`.
- **Rollback:** Label `production` được chuyển lại về Version 1; evidence `10b-prompt-rollback.png`.

## 6. Dashboard, SLO và alerts

- **Dashboard:** `dashboard.py` đọc `data/logs.jsonl` và hiển thị 6 panel: latency, traffic, errors, cost, tokens và quality. Runtime evidence ở ảnh 11.
- **Latency panel:** P50/P95/P99 và TTFT, có threshold 3000 ms.
- **Errors panel:** Error rate và retrieval success từ `tool_success` trên response/error events.
- **SLO:** 99.5% fast successful requests trong cửa sổ 28 ngày, với latency không quá 3000 ms.
- **Error budget:** 0.5%. Với reference volume 10,000 requests, error budget là 50 requests (`config/slo.yaml`).
- **Alerts:** `HighLatencyP95`, `ElevatedErrorRate`, `LowRetrievalSuccess`; mỗi alert có condition, duration, severity, owner `student-2A202602373`, Slack channel và runbook.
- **Runbook:** `docs/alerts.md` giữ nguyên heading `## Alert 1/2/3` và hướng dẫn Metrics → Logs → Traces → mitigation.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian:** khoảng `2026-09-30T04:29:11Z`–`2026-09-30T04:29:34Z` trong log CP3.
- **Triệu chứng metrics:** Baseline average latency khoảng **237 ms**; challenge average khoảng **2651 ms**, challenge P95 **2652 ms**; TTFT P95 vẫn **50 ms**. Có 5/5 challenge responses chậm và không có request failure.
- **Log line/correlation ID:** Event `response_sent`, `correlation_id=req-cab99b4a`, `latency_ms=2652`, `tool_success=true`.
- **Trace ID/span:** Trace `6e3169bf7adb8e8b6e022f3b6c55e616`; span `retrieval` là span chậm bất thường.
- **Root cause:** Incident `rag_slow` làm retrieval chậm; generation TTFT vẫn 50 ms, nên evidence chỉ về retrieval chứ không phải generation.
- **Fix action:** Tắt `rag_slow` và khôi phục retrieval bình thường.
- **Preventive measure:** Giữ alert `HighLatencyP95`, theo dõi retrieval span và dùng correlation ID để điều tra Metrics → Logs → Traces.

## 8. Giải thích và tự đánh giá

- **Quyết định kỹ thuật:** Scrub PII ngay trước khi ghi log và tắt raw prompt/output trong trace để bảo vệ dữ liệu nhưng vẫn giữ metadata vận hành.
- **Blocker:** Môi trường ban đầu thiếu Python packages; đã dùng Python 3.11/venv và cài dependencies theo requirements.
- **Cách tìm root cause:** Dùng metrics để xác định latency regression, chọn request từ log bằng correlation ID, rồi mở đúng trace để xác định span retrieval chậm.
- **Metrics → Logs → Traces:** Metrics chỉ ra triệu chứng; logs chọn request; traces định vị bước chậm/lỗi; root cause chỉ được kết luận khi cả ba khớp.
- **Prompt/token/cost/SLO:** Prompt version và label cho phép truy vết/rollback; token và cost cho biết hiệu quả; SLO/error budget định lượng độ tin cậy.
- **Bài học chính:** HTTP 200 không đồng nghĩa hệ thống khỏe; cần quan sát latency, retrieval, token/cost và quality cùng lúc.
- **Hạn chế:** Baseline validator trước khi sửa starter code không được capture; mọi runtime evidence sau đó đã được lưu trong `submission/evidence/`.

## 9. Checklist trước khi nộp

- [x] Evidence 01–14 đã có trong repo.
- [x] Pytest 24 passed.
- [x] Log validator 100/100 và 0 PII leak.
- [x] Dashboard validator 6/6.
- [x] Trace tree, prompt v1/v2, promote và rollback có evidence.
- [x] Incident nối đúng metric → log → trace bằng correlation ID.
- [x] Không commit `.env`, `data/logs.jsonl` hoặc `config/challenge.json`.
- [x] Commit cuối: `9c56652`.
- [ ] Nộp repository URL và commit SHA trên LMS/Codelabs.
