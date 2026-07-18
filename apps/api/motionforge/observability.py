from __future__ import annotations

from threading import Lock

_lock = Lock()
_request_total = 0
_error_total = 0
_latency_seconds_sum = 0.0


def record_request(status_code: int, duration_seconds: float) -> None:
    global _request_total, _error_total, _latency_seconds_sum
    with _lock:
        _request_total += 1
        _latency_seconds_sum += duration_seconds
        if status_code >= 500:
            _error_total += 1


def prometheus_text() -> str:
    with _lock:
        total = _request_total
        errors = _error_total
        latency = _latency_seconds_sum
    return "\n".join(
        [
            "# HELP motionforge_api_requests_total Total API HTTP requests.",
            "# TYPE motionforge_api_requests_total counter",
            f"motionforge_api_requests_total {total}",
            "# HELP motionforge_api_errors_total Total API 5xx responses.",
            "# TYPE motionforge_api_errors_total counter",
            f"motionforge_api_errors_total {errors}",
            "# HELP motionforge_api_request_duration_seconds_sum Cumulative API request duration.",
            "# TYPE motionforge_api_request_duration_seconds_sum counter",
            f"motionforge_api_request_duration_seconds_sum {latency:.6f}",
            "",
        ]
    )
