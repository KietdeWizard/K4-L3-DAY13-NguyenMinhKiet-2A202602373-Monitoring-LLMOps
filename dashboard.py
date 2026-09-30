from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parent
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
WINDOW_MINUTES = 60


def load_records() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    records: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            record["_time"] = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
            records.append(record)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return records


def percentile(values: list[float], percentile_value: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((percentile_value / 100) * len(ordered) + 0.999) - 1))
    return ordered[index]


def format_window(records: list[dict]) -> tuple[list[dict], str]:
    if not records:
        return [], "No log data"
    end = max(record["_time"] for record in records)
    start = end - timedelta(minutes=WINDOW_MINUTES)
    selected = [record for record in records if start <= record["_time"] <= end]
    label = f"{start.astimezone():%Y-%m-%d %H:%M} - {end.astimezone():%H:%M %Z}"
    return selected, label


def minute_counts(records: list[dict], event: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        if record.get("event") == event:
            counts[record["_time"].astimezone().strftime("%H:%M")] += 1
    return dict(sorted(counts.items()))


def minute_percentile(records: list[dict], field: str, percentile_value: int) -> tuple[list[str], list[float]]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for record in records:
        if record.get("event") != "response_sent" or field not in record:
            continue
        minute = record["_time"].astimezone().strftime("%H:%M")
        buckets[minute].append(float(record[field]))
    labels = sorted(buckets)
    return labels, [percentile(buckets[label], percentile_value) for label in labels]


st.set_page_config(page_title="Day 13 Monitoring Dashboard", layout="wide")
st.title("K4-L3B Day 13 — Monitoring & LLMOps")
st.caption("Runtime source: data/logs.jsonl · time range: 60 minutes · refresh: 30 seconds")

records, window_label = format_window(load_records())
st.info(f"Window: {window_label} · Records: {len(records)} · Source: {LOG_PATH}")
if st.button("Refresh data"):
    st.rerun()

responses = [record for record in records if record.get("event") == "response_sent"]
received = [record for record in records if record.get("event") == "request_received"]
failed = [record for record in records if record.get("event") == "request_failed"]
tool_records = [record for record in records if "tool_success" in record]
latencies = [float(record.get("latency_ms", 0)) for record in responses]
ttft = [float(record.get("ttft_ms", 0)) for record in responses]
costs = [float(record.get("cost_usd", 0)) for record in responses]
tokens_in = [int(record.get("tokens_in", 0)) for record in responses]
tokens_out = [int(record.get("tokens_out", 0)) for record in responses]
quality = [float(record.get("quality_score", 0)) for record in responses]
retrieval_success = sum(record.get("tool_success") is True for record in tool_records)
retrieval_rate = (retrieval_success / len(tool_records) * 100) if tool_records else 0.0
error_rate = (len(failed) / len(received) * 100) if received else 0.0

left, right = st.columns(2)
with left:
    st.subheader("Latency")
    st.metric("P95 latency", f"{percentile(latencies, 95):.0f} ms", "threshold ≤ 3000 ms")
    st.metric("P50 / P99", f"{percentile(latencies, 50):.0f} / {percentile(latencies, 99):.0f} ms")
    st.metric("TTFT P95", f"{percentile(ttft, 95):.0f} ms")
    st.bar_chart({"P50": [percentile(latencies, 50)], "P95": [percentile(latencies, 95)], "P99": [percentile(latencies, 99)]})
    latency_minutes, latency_p95 = minute_percentile(records, "latency_ms", 95)
    if latency_p95:
        st.caption("P95 latency by minute (baseline → incident)")
        st.line_chart(
            {
                "p95_latency_ms": latency_p95,
                "threshold_ms": [3000] * len(latency_p95),
            },
            x_label="minute index",
            y_label="milliseconds",
        )

with right:
    st.subheader("Traffic")
    st.metric("Requests", len(received))
    st.metric("Rate", f"{len(received) / WINDOW_MINUTES:.2f} requests/min", "threshold ≥ 1/min")
    traffic_by_minute = minute_counts(records, "request_received")
    st.bar_chart(traffic_by_minute or {"No data": [0]})

left, right = st.columns(2)
with left:
    st.subheader("Errors")
    st.metric("Error rate", f"{error_rate:.2f}%", "threshold ≤ 2%")
    st.metric("Retrieval success", f"{retrieval_rate:.1f}%", "threshold ≥ 90%")
    errors_by_type = Counter(record.get("error_type", "unknown") for record in failed)
    st.dataframe({"error_type": list(errors_by_type), "count": list(errors_by_type.values())}, hide_index=True, use_container_width=True)

with right:
    st.subheader("Cost")
    st.metric("Total cost", f"${sum(costs):.6f}", "threshold ≤ $2.50")
    st.metric("Average/request", f"${(sum(costs) / len(costs)) if costs else 0:.6f}")
    st.bar_chart({"cost_usd": costs or [0]})

left, right = st.columns(2)
with left:
    st.subheader("Tokens")
    st.metric("Input tokens", f"{sum(tokens_in):,}")
    st.metric("Output tokens", f"{sum(tokens_out):,}")
    st.bar_chart({"input": [sum(tokens_in)], "output": [sum(tokens_out)]})

with right:
    st.subheader("Quality")
    average_quality = sum(quality) / len(quality) if quality else 0.0
    st.metric("Average quality proxy", f"{average_quality:.2f}", "threshold ≥ 0.75")
    st.metric("Responses scored", len(quality))
    st.bar_chart({"quality_score": quality or [0]})

st.caption("SLO: 99.5% fast successful requests (latency ≤ 3000 ms). Error budget: 0.5%.")
