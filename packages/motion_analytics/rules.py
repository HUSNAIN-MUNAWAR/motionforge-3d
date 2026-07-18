from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class MovementEvent:
    event_type: str
    severity: str
    start_s: float
    end_s: float
    joint: str | None
    side: str | None
    measured_value: float
    threshold: float
    unit: str
    confidence: float
    explanation: str
    rule_version: str = "1.0"


def evaluate_threshold(
    metric_name,
    values,
    timestamps,
    threshold,
    comparator="greater",
    severity="warning",
    unit="degrees",
):
    events = []
    active = None
    for value, t in zip(values, timestamps):
        triggered = value > threshold if comparator == "greater" else value < threshold
        if triggered and active is None:
            active = [t, t, value]
        elif triggered:
            active[1] = t
            active[2] = max(active[2], value) if comparator == "greater" else min(active[2], value)
        elif active:
            events.append(
                MovementEvent(
                    metric_name,
                    severity,
                    *active[:2],
                    metric_name.split("_")[0],
                    None,
                    float(active[2]),
                    threshold,
                    unit,
                    0.9,
                    f"{metric_name} measured {active[2]:.1f} {unit}; configured threshold is {comparator} than {threshold:.1f} {unit}.",
                )
            )
            active = None
    if active:
        events.append(
            MovementEvent(
                metric_name,
                severity,
                *active[:2],
                metric_name.split("_")[0],
                None,
                float(active[2]),
                threshold,
                unit,
                0.9,
                f"{metric_name} measured {active[2]:.1f} {unit}; configured threshold is {comparator} than {threshold:.1f} {unit}.",
            )
        )
    return events
