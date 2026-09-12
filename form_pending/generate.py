"""Procedural building, population, and bureaucratic dependency chain."""

from __future__ import annotations

from copy import deepcopy

from .catalog import (
    DEPT_FLAVOR,
    ELEVATOR,
    FLOOR_COUNT,
    FLOOR_DEFS,
    GREETINGS,
    HOME_DEPARTMENTS,
    IDLE_LINES,
    MAP_H,
    MAP_W,
    MEMOS,
    PAPER_COLORS,
    PROVIDER,
    REVISITS,
    ROLES,
    STAMP_COLORS,
    STEP_KINDS,
    CATASTROPHES,
    FORM_TITLES,
    make_appearance,
    make_form_code,
    unique_name,
)
from .rng import Rng, normalize_seed
from .validate import reachable_tiles, validate_world, walkable


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < MAP_W and 0 <= y < MAP_H


def neighbors4(x, y):
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def fill_rect(grid, x, y, w, h, fn):
    for j in range(y, y + h):
        for i in range(x, x + w):
            if in_bounds(i, j):
                fn(grid[j][i], i, j)


def make_grid():
    return [[{"t": "wall", "room": 0, "dept": None} for _ in range(MAP_W)] for _ in range(MAP_H)]


def generate_floor_layout(rng: Rng, floor_index: int, departments: list) -> dict:
    defn = FLOOR_DEFS[floor_index - 1]
    grid = make_grid()

    def set_floor(tile, _i, _j):
        tile["t"] = "floor"
        tile["room"] = 0

    fill_rect(grid, 1, 1, MAP_W - 2, MAP_H - 2, set_floor)

    def set_lobby(tile, _i, _j):
        tile["t"] = "corridor"
        tile["room"] = 1

    fill_rect(grid, 1, 11, 8, 8, set_lobby)

    def set_elev(tile, _i, _j):
        tile["t"] = "elevator"
        tile["room"] = 1

    fill_rect(grid, ELEVATOR["x"], ELEVATOR["y"], ELEVATOR["w"], ELEVATOR["h"], set_elev)

    hall_y = 14

    def set_hall(tile, _i, _j):
        tile["t"] = "corridor"
        tile["room"] = 1

    fill_rect(grid, 8, hall_y, MAP_W - 10, 3, set_hall)

    vxs = [11 + rng.int(0, 2), 20 + rng.int(0, 3), 30 + rng.int(0, 2)]
    for vx in vxs:
        fill_rect(grid, vx, 2, 2, MAP_H - 4, set_hall)

    rooms = [{"id": 1, "name": "Elevator Lobby", "dept": None, "floor": floor_index}]
    room_id = 2
    assigned = [[0] * MAP_W for _ in range(MAP_H)]

    for y in range(1, MAP_H - 1):
        for x in range(1, MAP_W - 1):
            if grid[y][x]["t"] != "floor" or assigned[y][x]:
                continue
            cells = []
            stack = [(x, y)]
            assigned[y][x] = room_id
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for nx, ny in neighbors4(cx, cy):
                    if not in_bounds(nx, ny) or assigned[ny][nx]:
                        continue
                    if grid[ny][nx]["t"] != "floor":
                        continue
                    assigned[ny][nx] = room_id
                    stack.append((nx, ny))
            if len(cells) < 10:
                for cx, cy in cells:
                    grid[cy][cx]["t"] = "corridor"
                    grid[cy][cx]["room"] = 1
                    assigned[cy][cx] = 1
                continue
            dept = departments[(room_id - 2) % max(1, len(departments))] if departments else None
            rooms.append({
                "id": room_id,
                "name": dept["name"] if dept else "Office",
                "dept": dept["id"] if dept else None,
                "floor": floor_index,
                "cells": len(cells),
            })
            for cx, cy in cells:
                grid[cy][cx]["room"] = room_id
                grid[cy][cx]["dept"] = dept["id"] if dept else None
            room_id += 1

    door_candidates = {}
    for y in range(1, MAP_H - 1):
        for x in range(1, MAP_W - 1):
            tile = grid[y][x]
            if tile["t"] != "floor":
                continue
            touches_corridor = False
            touches_other = False
            for nx, ny in neighbors4(x, y):
                n = grid[ny][nx]
                if n["t"] == "corridor":
                    touches_corridor = True
                if n["t"] == "floor" and n["room"] != tile["room"]:
                    touches_other = True
            if touches_corridor:
                door_candidates.setdefault(tile["room"], []).append((x, y))
            if touches_other and not touches_corridor:
                tile["t"] = "wall"

    for room in rooms:
        if room["id"] == 1:
            continue
        candidates = door_candidates.get(room["id"], [])
        if not candidates:
            continue
        wanted = 2 if len(candidates) > 18 else 1
        doors = set(rng.pick_n(candidates, min(wanted, len(candidates))))
        for x, y in candidates:
            grid[y][x]["t"] = "door" if (x, y) in doors else "wall"

    desks = []
    props = []
    used = set()

    def occ(x, y):
        return (x, y) in used

    def take(x, y):
        used.add((x, y))

    def can_desk(x, y):
        if not in_bounds(x, y) or not in_bounds(x + 1, y) or not in_bounds(x, y + 1):
            return False
        if grid[y][x]["t"] != "floor":
            return False
        if occ(x, y) or occ(x + 1, y):
            return False
        if grid[y][x]["room"] == 1:
            return False
        if not walkable(grid[y + 1][x]):
            return False
        return True

    for room in rooms:
        if room["id"] == 1:
            continue
        cells = [
            (x, y)
            for y in range(2, MAP_H - 2)
            for x in range(2, MAP_W - 2)
            if grid[y][x]["room"] == room["id"] and grid[y][x]["t"] == "floor"
        ]
        rng.shuffle(cells)
        want = min(6, max(2, len(cells) // 8))
        placed = 0
        for x, y in cells:
            if placed >= want:
                break
            if not can_desk(x, y):
                continue
            grid[y][x]["t"] = "desk"
            take(x, y)
            take(x + 1, y)
            desks.append({
                "x": x,
                "y": y,
                "room": room["id"],
                "dept": room["dept"],
                "floor": floor_index,
            })
            placed += 1

    # Top up sparse floors so each storey feels staffed.
    if len(desks) < 8:
        extras = [
            (x, y)
            for y in range(2, MAP_H - 3)
            for x in range(2, MAP_W - 3)
            if can_desk(x, y)
        ]
        rng.shuffle(extras)
        for x, y in extras:
            if len(desks) >= 8:
                break
            if not can_desk(x, y):
                continue
            grid[y][x]["t"] = "desk"
            take(x, y)
            take(x + 1, y)
            tile = grid[y][x]
            desks.append({
                "x": x,
                "y": y,
                "room": tile["room"],
                "dept": tile["dept"],
                "floor": floor_index,
            })

    def place_prop(ptype, prefer_corridor=True):
        for _ in range(100):
            x = rng.int(2, MAP_W - 3)
            y = rng.int(2, MAP_H - 3)
            t = grid[y][x]
            if occ(x, y):
                continue
            if prefer_corridor and t["t"] != "corridor":
                continue
            if not prefer_corridor and t["t"] != "floor":
                continue
            if t["t"] in ("elevator", "desk"):
                continue
            take(x, y)
            prop = {"type": ptype, "x": x, "y": y, "floor": floor_index}
            props.append(prop)
            return prop
        return None

    if grid[12][7]["t"] != "elevator":
        take(7, 12)
        props.append({"type": "directory", "x": 7, "y": 12, "floor": floor_index})

    landmarks = {
        1: [("counter", False), ("plant", True), ("chairs", True)],
        2: [("copier", False), ("cabinet", False), ("cabinet", False), ("boxes", False)],
        3: [("window_counter", False), ("stanchion", True), ("plant", True)],
        4: [("shelves", False), ("boxes", False), ("plant", True)],
        5: [("whiteboard", False), ("table", False), ("cabinet", False)],
        6: [("vault", False), ("plant", True), ("portrait", False)],
    }
    for ptype, corr in landmarks.get(floor_index, []):
        place_prop(ptype, corr)
    place_prop("cooler", True)
    if rng.bool(0.7):
        place_prop("plant", True)
    if rng.bool(0.5):
        place_prop("chairs", True)
    extra_room = ["boxes", "cabinet", "plant", "table"]
    for _ in range(rng.int(1, 3)):
        place_prop(rng.pick(extra_room), False)

    # Wall memos — some flavor, some truthful floor pointers.
    for _ in range(rng.int(2, 4)):
        memo = place_prop("memo", True)
        if not memo:
            continue
        if rng.bool(0.4) and departments:
            d = rng.pick(departments)
            memo["text"] = f"{d['name'].upper()}  —  currently Floor {d['floor']}"
            memo["fact_floor"] = d["floor"]
            memo["fact_dept"] = d["name"]
        else:
            memo["text"] = rng.pick(MEMOS)

    if floor_index == 1:
        # Reception counter near spawn so the first clerk is findable.
        if not occ(7, 16) and grid[16][7]["t"] in ("corridor", "floor"):
            take(7, 16)
            props.append({"type": "counter", "x": 7, "y": 16, "floor": 1, "reception": True})

    # Guarantee a path from the elevator to every desk standing-spot.
    reachable = reachable_tiles(grid)
    for desk in desks:
        sx, sy = desk["x"], desk["y"] + 1
        if (sx, sy) in reachable:
            continue
        x, y = sx, sy
        while y < hall_y:
            if in_bounds(x, y) and grid[y][x]["t"] == "wall":
                grid[y][x]["t"] = "door"
            y += 1
        y = sy
        while y > hall_y + 2:
            if in_bounds(x, y) and grid[y][x]["t"] == "wall":
                grid[y][x]["t"] = "door"
            y -= 1
        x = sx
        while x > 8:
            if in_bounds(x, hall_y + 1) and grid[hall_y + 1][x]["t"] == "wall":
                grid[hall_y + 1][x]["t"] = "door"
            x -= 1

    reachable = reachable_tiles(grid)
    desks = [d for d in desks if (d["x"], d["y"] + 1) in reachable]

    return {
        "index": floor_index,
        "def": defn,
        "grid": grid,
        "rooms": rooms,
        "desks": desks,
        "props": props,
        "departments": departments,
        "elevator": {
            "tx": ELEVATOR["x"],
            "ty": ELEVATOR["y"],
            "tw": ELEVATOR["w"],
            "th": ELEVATOR["h"],
        },
        "spawn": {"x": 8.5, "y": 18.5},
    }


def assign_departments(rng: Rng) -> list:
    depts = deepcopy(HOME_DEPARTMENTS)
    for _ in range(rng.int(1, 3)):
        a = rng.pick(depts)
        neighbors = [b for b in depts if abs(b["floor"] - a["floor"]) == 1 and b["id"] != a["id"]]
        if not neighbors:
            continue
        b = rng.pick(neighbors)
        a["floor"], b["floor"] = b["floor"], a["floor"]
    return depts


def item_from_step(rng: Rng, kind: str, index: int) -> dict:
    code = make_form_code(rng)
    if kind == "stamp":
        stamp = rng.pick(STAMP_COLORS)
        return {
            "id": f"item_stamp_{stamp['id']}_{index}",
            "kind": "stamp",
            "code": stamp["name"].upper(),
            "name": f"{stamp['name']} stamp",
            "stamp_id": stamp["id"],
            "ink": stamp["ink"],
        }
    if kind == "copy":
        return {
            "id": f"item_copy_{index}",
            "kind": "copy",
            "code": f"COPY {code}",
            "name": f"Photocopy of {code}",
        }
    if kind == "sign":
        return {"id": f"item_signed_{index}", "kind": "signature", "code": code, "name": f"Signed {code}"}
    if kind == "notary":
        return {"id": f"item_notary_{index}", "kind": "signature", "code": code, "name": f"Notarized {code}"}
    if kind == "approve":
        return {"id": f"item_approve_{index}", "kind": "signature", "code": code, "name": f"Approved {code}"}
    if kind == "correct":
        paper = rng.pick(PAPER_COLORS)
        return {
            "id": f"item_corrected_{index}",
            "kind": "form",
            "code": code,
            "name": f"{code} on {paper} paper",
            "paper": paper,
        }
    if kind == "verify":
        return {
            "id": f"item_verify_{index}",
            "kind": "badge",
            "code": "VISITOR VERIFIED",
            "name": "Verified visitor slip",
        }
    if kind == "prior":
        return {
            "id": f"item_prior_{index}",
            "kind": "form",
            "code": f"PRIOR {code}",
            "name": f"Prior-year copy {code}",
        }
    return {"id": f"item_form_{index}", "kind": "form", "code": code, "name": f"Form {code}"}


def npc_for_step(shuffled, used, kind, floors_used):
    handles, fallback = PROVIDER.get(kind, ("issue", ["records"]))
    unused = [n for n in shuffled if n["id"] not in used]
    by_handle = [n for n in unused if n["handles"] == handles]
    by_dept = [n for n in unused if n["department_id"] in fallback]
    pool = by_handle or by_dept or unused
    if floors_used:
        spread = [n for n in pool if n["floor"] not in floors_used]
        if spread:
            pool = spread
    return pool[0] if pool else None


def describe_need(node, npc, start_doc):
    first = npc["name"].split()[0]
    kind = node["kind"]
    if kind == "file":
        return (
            f"{first} at {npc['department']} files {start_doc['code']} "
            "once every prerequisite is attached."
        )
    if kind == "stamp":
        return f"{first} keeps the stamp. {npc['department']}, Floor {npc['floor']}."
    if kind == "issue":
        return f"{first} issues the required form from {npc['department']}."
    if kind == "sign":
        return f"{first} has to sign it. {npc['role']}, {npc['department']}."
    if kind == "copy":
        return f"You need a photocopy. {first} in {npc['department']} will run it."
    if kind == "correct":
        return f"{first} will put it on the correct color paper."
    if kind == "verify":
        return f"Security has to initial a visitor slip. {first} handles that."
    if kind == "notary":
        return f"It has to be notarized. {first} at {npc['department']} is on duty."
    if kind == "approve":
        return f"{first} in {npc['department']} has to initial an approval."
    if kind == "prior":
        return f"Archives wants the prior-year copy. {first} can pull it."
    return f"{first} handles the next step."


def generate_npcs(rng: Rng, floors, departments) -> list:
    used_names = set()
    npcs = []
    n = 0
    for floor in floors:
        floor_depts = [d for d in departments if d["floor"] == floor["index"]]
        desks = list(floor["desks"])
        rng.shuffle(desks)
        count = min(len(desks), rng.int(7, 11))
        for i in range(count):
            desk = desks[i]
            dept = next((d for d in floor_depts if d["id"] == desk["dept"]), None)
            if dept is None:
                dept = rng.pick(floor_depts) if floor_depts else rng.pick(departments)
            npc = {
                "id": f"npc_{n}",
                "name": unique_name(rng, used_names),
                "appearance": make_appearance(rng),
                "department_id": dept["id"],
                "department": dept["name"],
                "handles": dept["handles"],
                "role": rng.pick(ROLES),
                "floor": floor["index"],
                "x": desk["x"] + 0.5,
                "y": desk["y"] + 0.15,
                "desk": desk,
                "knowledge": [],
                "chain_role": None,
                "provides": None,
                "requires": [],
                "greeting": rng.pick(GREETINGS),
                "revisit": rng.pick(REVISITS),
                "is_intake": False,
                "given": False,
                "talked": False,
            }
            npcs.append(npc)
            n += 1
    return npcs


def generate_chain(rng: Rng, npcs, start_doc):
    length = rng.int(5, 7)
    kinds = ["file"]
    bag = list(STEP_KINDS)
    rng.shuffle(bag)
    for i in range(length):
        kinds.append(bag[i % len(bag)])

    items = [start_doc]
    nodes = []
    used = set()
    floors_used = []
    shuffled = list(npcs)
    rng.shuffle(shuffled)

    for i, kind in enumerate(kinds):
        npc = npc_for_step(shuffled, used, kind, floors_used)
        if npc is None:
            break
        used.add(npc["id"])
        floors_used.append(npc["floor"])
        produces = None if kind == "file" else item_from_step(rng, kind, i)
        if produces:
            items.append(produces)
        node = {
            "id": f"node_{i}_{kind}",
            "kind": kind,
            "npc_id": npc["id"],
            "consumes": [],
            "produces": produces["id"] if produces else None,
            "requires": [],
            "label": "",
        }
        npc["chain_role"] = kind
        npc["provides"] = produces["id"] if produces else "FILE"
        nodes.append(node)

    for i, node in enumerate(nodes):
        node["requires"] = [nodes[i + 1]["id"]] if i + 1 < len(nodes) else []
        node["consumes"] = []
        if i + 1 < len(nodes) and nodes[i + 1]["produces"]:
            node["consumes"].append(nodes[i + 1]["produces"])
        if node["kind"] == "file":
            node["consumes"].append(start_doc["id"])

    for i, node in enumerate(nodes):
        npc = next(n for n in npcs if n["id"] == node["npc_id"])
        if i + 1 < len(nodes) and nodes[i + 1]["produces"]:
            npc["requires"] = [nodes[i + 1]["produces"]]
        else:
            npc["requires"] = []
        if node["kind"] == "file":
            npc["requires"] = [c for c in node["consumes"] if c != start_doc["id"]]

    return {"nodes": nodes, "items": items, "chain_npc_ids": list(used)}


def assign_knowledge(rng: Rng, npcs, chain, start_doc):
    by_id = {n["id"]: n for n in npcs}
    chain_npcs = [by_id[i] for i in chain["chain_npc_ids"] if i in by_id]

    for i, node in enumerate(chain["nodes"]):
        npc = by_id[node["npc_id"]]
        nxt = chain["nodes"][i + 1] if i + 1 < len(chain["nodes"]) else None
        next_npc = by_id[nxt["npc_id"]] if nxt else None
        node["label"] = describe_need(node, npc, start_doc)
        if node["kind"] == "file":
            npc["knowledge"].append({
                "type": "handles",
                "text": (
                    f"This window files {start_doc['code']} — once the attachments "
                    "are complete. Not before."
                ),
                "fact": {"npc_id": npc["id"], "node_id": node["id"]},
            })
        else:
            npc["knowledge"].append({
                "type": "handles",
                "text": rng.pick([
                    f"This desk does that. {node['label']}",
                    f"That's me. {node['label']}",
                    f"You're in the right pile. {node['label']}",
                ]),
                "fact": {"npc_id": npc["id"], "node_id": node["id"]},
            })
        if next_npc:
            vague = rng.bool(0.45)
            landmark = FLOOR_DEFS[next_npc["floor"] - 1]["landmark"]
            first = next_npc["name"].split()[0]
            text = (
                f"You'll need {first} for the rest. {next_npc['department']}, I think. Floor {next_npc['floor']}."
                if vague
                else (
                    f"{next_npc['name']} in {next_npc['department']} on Floor {next_npc['floor']}. "
                    f"Near {landmark}."
                )
            )
            npc["knowledge"].append({
                "type": "referral",
                "text": text,
                "fact": {
                    "npc_id": next_npc["id"],
                    "floor": next_npc["floor"],
                    "department": next_npc["department"],
                },
            })

    intake = next((n for n in npcs if n["department_id"] == "intake" and n["floor"] == 1 and not n["chain_role"]), None)
    if intake is None:
        intake = next((n for n in npcs if n["floor"] == 1 and not n["chain_role"]), None)
    first_work = next((n for n in chain_npcs if n["chain_role"] and n["chain_role"] != "file"), None)
    if first_work is None and chain_npcs:
        first_work = chain_npcs[0]
    if intake and first_work:
        intake["knowledge"].insert(0, {
            "type": "referral",
            "text": (
                f"Intake doesn't process this form type. You'll want {first_work['name']}. "
                f"{first_work['department']}, Floor {first_work['floor']}."
            ),
            "fact": {
                "npc_id": first_work["id"],
                "floor": first_work["floor"],
                "department": first_work["department"],
            },
        })
        intake["is_intake"] = True
        intake["greeting"] = rng.pick([
            "Intake. That's the whole introduction.",
            "If you can hold it, I can refuse it.",
            "Visitor? Put the paper where I can see the number.",
        ])
        # Park them at the lobby counter so the opening beat actually happens.
        intake["floor"] = 1
        intake["x"] = 7.5
        intake["y"] = 17.15
        intake["desk"] = {"x": 7, "y": 16, "room": 1, "dept": "intake", "floor": 1}

    for npc in npcs:
        if npc["chain_role"] or npc["is_intake"]:
            continue
        local = [c for c in chain_npcs if c["floor"] == npc["floor"] and c["id"] != npc["id"]]
        adjacent = [c for c in chain_npcs if abs(c["floor"] - npc["floor"]) == 1]
        if local and rng.bool(0.7):
            t = rng.pick(local)
            npc["knowledge"].append({
                "type": "location",
                "text": f"{t['name'].split()[0]}? That's {t['name']}. Desk in {t['department']}, this floor.",
                "fact": {"npc_id": t["id"], "floor": t["floor"]},
            })
        elif adjacent and rng.bool(0.5):
            t = rng.pick(adjacent)
            npc["knowledge"].append({
                "type": "location",
                "text": (
                    f"If you're looking for {t['department']}, try Floor {t['floor']}. "
                    f"{t['name'].split()[0]} used to sit near there."
                ),
                "fact": {"npc_id": t["id"], "floor": t["floor"], "department": t["department"]},
            })
        else:
            flavor = DEPT_FLAVOR.get(npc["department_id"])
            npc["knowledge"].append({
                "type": "idle",
                "text": rng.pick(flavor) if flavor and rng.bool(0.55) else rng.pick(IDLE_LINES),
                "fact": None,
            })
        if rng.bool(0.18):
            npc["knowledge"].append({
                "type": "nav",
                "text": rng.pick([
                    "If you're counting floors, the board by the elevator is less wrong than people are.",
                    "Directory's next to the elevator. It's current as of this morning. That's the claim, anyway.",
                    "I don't do directions. The board by the shaft does directions.",
                ]),
                "fact": None,
            })
        if not npc["knowledge"]:
            npc["knowledge"].append({
                "type": "negative",
                "text": f"We don't handle those on this desk. {npc['department']} only.",
                "fact": {"department": npc["department"]},
            })


def hash_attempt(seed: int, attempt: int) -> int:
    return (seed ^ ((attempt + 1) * 0x9E3779B9)) & 0xFFFFFFFF


def try_generate(seed: int, attempt: int) -> dict:
    rng = Rng(hash_attempt(seed, attempt))
    catastrophe = rng.pick(CATASTROPHES)
    start_doc = {
        "id": "item_start",
        "kind": "form",
        "code": make_form_code(rng),
        "name": rng.pick(FORM_TITLES),
        "starting": True,
    }
    departments = assign_departments(rng)
    floors = []
    for i in range(1, FLOOR_COUNT + 1):
        floor_depts = [d for d in departments if d["floor"] == i]
        floors.append(generate_floor_layout(rng.fork(f"floor{i}"), i, floor_depts))
    npcs = generate_npcs(rng.fork("npcs"), floors, departments)
    chain = generate_chain(rng.fork("chain"), npcs, start_doc)
    assign_knowledge(rng.fork("talk"), npcs, chain, start_doc)
    return {
        "seed": seed,
        "attempt": attempt,
        "catastrophe": catastrophe,
        "start_doc": start_doc,
        "items": chain["items"],
        "nodes": chain["nodes"],
        "chain_npc_ids": chain["chain_npc_ids"],
        "departments": departments,
        "floors": floors,
        "npcs": npcs,
        "player_start": {"floor": 1, "x": 8.5, "y": 18.5},
        "generation_failed": False,
        "diagnostics": [],
        "out_to_lunch": None,
    }


def generate_run(seed_input=None) -> dict:
    """Generate a complete run. Retries on validation failure using a derived stream."""
    seed = normalize_seed(seed_input)
    diagnostics = []
    last = None
    last_validation = None
    for attempt in range(12):
        world = try_generate(seed, attempt)
        validation = validate_world(world)
        last = world
        last_validation = validation
        if validation["ok"]:
            world["validation"] = validation
            world["diagnostics"] = diagnostics
            return world
        diagnostics.append({"attempt": attempt, "errors": list(validation["errors"])})
    last["generation_failed"] = True
    last["validation"] = last_validation
    last["diagnostics"] = diagnostics
    last["out_to_lunch"] = {
        "reason": "generation_unresolved",
        "seed": seed,
        "errors": last_validation["errors"] if last_validation else ["unknown"],
    }
    return last
