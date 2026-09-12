"""Structural solvability and referential integrity for a generated run."""

from __future__ import annotations

from .catalog import ELEVATOR, FLOOR_COUNT, MAP_H, MAP_W


def in_bounds(x, y) -> bool:
    return 0 <= x < MAP_W and 0 <= y < MAP_H


def walkable(tile) -> bool:
    return tile is not None and tile["t"] in ("floor", "corridor", "elevator", "door")


def reachable_tiles(grid) -> set:
    seen = set()
    q = []
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x]["t"] == "elevator":
                q.append((x, y))
                seen.add((x, y))
    if not q:
        sx = ELEVATOR["x"] + 1
        sy = min(ELEVATOR["y"] + ELEVATOR["h"], MAP_H - 2)
        q.append((sx, sy))
        seen.add((sx, sy))
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    while q:
        x, y = q.pop()
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in seen:
                continue
            if not walkable(grid[ny][nx]):
                continue
            seen.add((nx, ny))
            q.append((nx, ny))
    return seen


def standing_tile(npc):
    return int(npc["x"]), int(npc["y"]) + 1


def simulate_completion(world) -> dict:
    """Walk the chain as a perfect player: obtain leaf items first, then file."""
    item_ids = {i["id"] for i in world.get("items", [])}
    npc_by_id = {n["id"]: n for n in world.get("npcs", [])}
    inv = set()
    start = world.get("start_doc")
    if start:
        inv.add(start["id"])
    nodes = world.get("nodes") or []
    if not nodes:
        return {"ok": False, "reason": "no nodes"}
    node_by_id = {n["id"]: n for n in nodes}
    file_node = next((n for n in nodes if n["kind"] == "file"), nodes[0])
    order = []
    seen = set()

    def visit(node):
        if not node or node["id"] in seen:
            return
        seen.add(node["id"])
        for rid in node.get("requires") or []:
            visit(node_by_id.get(rid))
        order.append(node)

    visit(file_node)

    for node in order:
        npc = npc_by_id.get(node["npc_id"])
        if not npc:
            return {"ok": False, "reason": f"missing NPC for {node['id']}"}
        for need in npc.get("requires") or []:
            if need not in inv:
                return {"ok": False, "reason": f"{npc['name']} requires {need} which cannot yet be held"}
        for need in node.get("consumes") or []:
            if need not in inv:
                return {"ok": False, "reason": f"cannot satisfy consume {need} at {node['id']}"}
        if node.get("produces"):
            if node["produces"] not in item_ids:
                return {"ok": False, "reason": f"produced item missing {node['produces']}"}
            inv.add(node["produces"])
        if node["kind"] == "file" and start and start["id"] not in inv:
            return {"ok": False, "reason": "lost starting document"}
    return {"ok": True, "reason": None, "obtained": list(inv)}


def validate_world(world) -> dict:
    errors = []
    if not world:
        return {"ok": False, "errors": ["world is null"]}
    floors = world.get("floors") or []
    npcs = world.get("npcs") or []
    nodes = world.get("nodes") or []
    items = world.get("items") or []

    if len(floors) != FLOOR_COUNT:
        errors.append(f"expected {FLOOR_COUNT} floors, got {len(floors)}")
    if len(npcs) < 24:
        errors.append(f"too few NPCs ({len(npcs)})")
    if not world.get("start_doc") or not world["start_doc"].get("code"):
        errors.append("missing starting document")
    if not world.get("catastrophe"):
        errors.append("missing catastrophe")
    if len(nodes) < 4:
        errors.append(f"dependency chain too short ({len(nodes)})")

    npc_by_id = {n["id"]: n for n in npcs}
    item_by_id = {i["id"]: i for i in items}
    node_by_id = {n["id"]: n for n in nodes}
    names = set()

    for npc in npcs:
        if npc["name"] in names:
            errors.append(f"duplicate NPC name {npc['name']}")
        names.add(npc["name"])
        if not 1 <= npc["floor"] <= FLOOR_COUNT:
            errors.append(f"{npc['name']} has invalid floor {npc['floor']}")
        if not npc.get("department"):
            errors.append(f"{npc['id']} missing department")
        if not npc.get("appearance"):
            errors.append(f"{npc['id']} missing appearance")

    for nid in world.get("chain_npc_ids") or []:
        if nid not in npc_by_id:
            errors.append(f"chain NPC {nid} does not exist")

    seen_node = set()
    for node in nodes:
        if node["id"] in seen_node:
            errors.append(f"duplicate node {node['id']}")
        seen_node.add(node["id"])
        if node["npc_id"] not in npc_by_id:
            errors.append(f"node {node['id']} references missing NPC {node['npc_id']}")
        for rid in node.get("requires") or []:
            if rid not in node_by_id:
                errors.append(f"node {node['id']} requires missing node {rid}")
        for cid in node.get("consumes") or []:
            if cid not in item_by_id:
                errors.append(f"node {node['id']} consumes missing item {cid}")
        if node.get("produces") and node["produces"] not in item_by_id:
            errors.append(f"node {node['id']} produces missing item {node['produces']}")

    file_nodes = [n for n in nodes if n["kind"] == "file"]
    if len(file_nodes) != 1:
        errors.append(f"expected exactly one FILE node, got {len(file_nodes)}")
    start = world.get("start_doc")
    if file_nodes and start and start["id"] not in (file_nodes[0].get("consumes") or []):
        errors.append("FILE node does not consume the starting document")

    visiting = set()
    visited = set()

    def walk(nid, stack):
        if nid in visiting:
            errors.append("cycle in dependency chain: " + " -> ".join(stack + [nid]))
            return
        if nid in visited:
            return
        visiting.add(nid)
        node = node_by_id.get(nid)
        if node:
            for rid in node.get("requires") or []:
                walk(rid, stack + [nid])
        visiting.discard(nid)
        visited.add(nid)

    if file_nodes:
        walk(file_nodes[0]["id"], [])

    completable = simulate_completion(world)
    if not completable["ok"]:
        errors.append(f"chain is not completable: {completable['reason']}")

    for floor in floors:
        reachable = reachable_tiles(floor["grid"])
        for npc in (n for n in npcs if n["floor"] == floor["index"] and n.get("chain_role")):
            sx, sy = standing_tile(npc)
            nearby = [
                (sx, sy),
                (int(npc["x"]), int(npc["y"])),
                (int(npc["x"]), int(npc["y"]) + 1),
                (int(npc["x"]) - 1, int(npc["y"]) + 1),
                (int(npc["x"]) + 1, int(npc["y"]) + 1),
            ]
            if not any(p in reachable for p in nearby if in_bounds(*p)):
                errors.append(
                    f"chain NPC {npc['name']} on floor {npc['floor']} is not reachable from the elevator"
                )
        elev = sum(1 for row in floor["grid"] for tile in row if tile["t"] == "elevator")
        if elev < 4:
            errors.append(f"floor {floor['index']} missing elevator cabin")

    for npc in npcs:
        for k in npc.get("knowledge") or []:
            fact = k.get("fact")
            if not fact or not fact.get("npc_id"):
                continue
            target = npc_by_id.get(fact["npc_id"])
            if not target:
                errors.append(f"{npc['name']} refers to missing NPC {fact['npc_id']}")
                continue
            if fact.get("floor") is not None and fact["floor"] != target["floor"]:
                errors.append(f"{npc['name']} misstates {target['name']}'s floor")
            if fact.get("department") and fact["department"] != target["department"]:
                errors.append(f"{npc['name']} misstates {target['name']}'s department")

    start_pos = world.get("player_start")
    if start_pos and start_pos.get("floor") != 1:
        errors.append("player does not start on floor 1")

    return {"ok": len(errors) == 0, "errors": errors, "completable": completable}


def worlds_differ_meaningfully(a, b) -> bool:
    if not a or not b:
        return True
    return (
        [n["kind"] for n in a["nodes"]] != [n["kind"] for n in b["nodes"]]
        or [n["name"] for n in a["npcs"]] != [n["name"] for n in b["npcs"]]
        or a["start_doc"]["code"] != b["start_doc"]["code"]
        or a["catastrophe"]["id"] != b["catastrophe"]["id"]
    )
