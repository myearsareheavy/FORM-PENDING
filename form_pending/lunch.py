"""OUT TO LUNCH — diegetic fail-safe for invalid procedural/runtime state.

Normal authored jokes about lunch must not go through this module.
"""

from __future__ import annotations

from .diagnostics import log_out_to_lunch
from .interact import item_by_id


def audit_world(world) -> list:
    """Return structural problems that would make the live run unwinnable."""
    issues = []
    npc_by = {n["id"]: n for n in world.get("npcs") or []}
    item_ids = {i["id"] for i in world.get("items") or []}
    for node in world.get("nodes") or []:
        npc = npc_by.get(node.get("npc_id"))
        if npc is None:
            issues.append({
                "reason": "missing_chain_npc",
                "node_id": node.get("id"),
                "npc_id": node.get("npc_id"),
                "expected": f"NPC {node.get('npc_id')} exists",
                "actual": "npc missing",
            })
            continue
        if node.get("produces") and node["produces"] not in item_ids:
            issues.append({
                "reason": "missing_produced_item",
                "node_id": node.get("id"),
                "npc_id": npc["id"],
                "npc_name": npc.get("name"),
                "expected": f"item {node['produces']}",
                "actual": "item not in world.items",
            })
        for cid in node.get("consumes") or []:
            if cid not in item_ids:
                issues.append({
                    "reason": "missing_consumed_item",
                    "node_id": node.get("id"),
                    "npc_id": npc["id"],
                    "npc_name": npc.get("name"),
                    "expected": f"item {cid}",
                    "actual": "item not in world.items",
                })
    return issues


def activate_out_to_lunch(world, issue, recovery="desk envelope with the missing or produced item"):
    """Mark the implicated NPC out, log diagnostics, leave a recovery envelope."""
    npc_by = {n["id"]: n for n in world.get("npcs") or []}
    npc = npc_by.get(issue.get("npc_id"))
    item = None
    if npc and npc.get("provides") and npc["provides"] != "FILE":
        item = item_by_id(world, npc["provides"])
    if npc:
        npc["out_to_lunch"] = True
        npc["lunch_reason"] = issue.get("reason")
        npc["lunch_recovery_item"] = item
    record = {
        "seed": world.get("seed"),
        "run_id": world.get("seed"),
        "npc_or_dependency": (npc or {}).get("name") or issue.get("npc_id") or issue.get("node_id"),
        "npc_id": issue.get("npc_id"),
        "expected": issue.get("expected"),
        "actual": issue.get("actual"),
        "reason": issue.get("reason"),
        "recovery": recovery if npc else "no NPC to recover; filing window may be blocked",
        "node_id": issue.get("node_id"),
    }
    path = log_out_to_lunch(record)
    world.setdefault("out_to_lunch_events", []).append(record)
    return path, npc


def apply_failsafe(world) -> int:
    """Activate OUT TO LUNCH for every live integrity issue. Returns activation count."""
    n = 0
    seen = set()
    for issue in audit_world(world):
        key = (issue.get("npc_id"), issue.get("reason"), issue.get("node_id"))
        if key in seen:
            continue
        seen.add(key)
        activate_out_to_lunch(world, issue)
        n += 1
    if world.get("generation_failed"):
        # Last-resort: every chain NPC leaves their item in an envelope.
        npc_by = {n["id"]: n for n in world.get("npcs") or []}
        for nid in world.get("chain_npc_ids") or []:
            npc = npc_by.get(nid)
            if not npc or npc.get("out_to_lunch"):
                continue
            activate_out_to_lunch(world, {
                "reason": "generation_unresolved",
                "npc_id": npc["id"],
                "npc_name": npc["name"],
                "expected": "valid solvable world",
                "actual": (world.get("validation") or {}).get("errors"),
                "node_id": None,
            }, recovery="generation failed; envelope left on desk")
            n += 1
    return n
