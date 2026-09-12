"""Diegetic fail-safe logging. Genuine OUT TO LUNCH events only."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "diagnostics" / "out_to_lunch.jsonl"


def log_out_to_lunch(record: dict) -> Path:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, default=str) + "\n")
    return LOG_PATH
