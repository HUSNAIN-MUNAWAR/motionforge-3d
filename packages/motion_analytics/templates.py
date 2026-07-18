from __future__ import annotations
import json
from pathlib import Path


def load_template(name: str, root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[2] / "configs" / "movements"
    path = root / f"{name}.json"
    if not path.exists():
        raise KeyError(f"Unknown movement template: {name}")
    data = json.loads(path.read_text())
    required = {"name", "version", "primary_signal", "joint_family", "required_landmarks"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"Template missing: {sorted(missing)}")
    return data
