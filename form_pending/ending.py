"""Success and 5:00 PM failure sequences. Catastrophe art is drawn, not animated cinematics."""

from __future__ import annotations


FAIL_PHASES = [
    ("time", 1.3),
    ("closed", 1.8),
    ("beat", 0.9),
    ("event", 3.2),
    ("notice", None),
]

SUCCESS_PHASES = [
    ("stamp", 1.4),
    ("clerk", 1.6),
    ("averted", None),
]


def make_ending(kind, world):
    phases = SUCCESS_PHASES if kind == "success" else FAIL_PHASES
    return {
        "kind": kind,
        "phase": 0,
        "t": 0.0,
        "phases": phases,
        "catastrophe": world["catastrophe"],
        "doc_code": world["start_doc"]["code"],
        "doc_name": world["start_doc"]["name"],
        "waiting": False,
    }


def advance_ending(ending, dt):
    if ending["waiting"]:
        return
    duration = ending["phases"][ending["phase"]][1]
    if duration is None:
        ending["waiting"] = True
        return
    ending["t"] += dt
    if ending["t"] >= duration:
        ending["t"] = 0.0
        ending["phase"] += 1
        if ending["phase"] >= len(ending["phases"]):
            ending["phase"] = len(ending["phases"]) - 1
            ending["waiting"] = True
        elif ending["phases"][ending["phase"]][1] is None:
            ending["waiting"] = True


def current_beat(ending):
    return ending["phases"][ending["phase"]][0]
