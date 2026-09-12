"""NPC talk resolution. Pure data — no pygame."""

from .catalog import GRANT_LINES


def item_by_id(world, iid):
    for it in world["items"]:
        if it["id"] == iid:
            return it
    return None


def resolve_talk(npc, inventory_ids, world):
    """Return dialogue pages and any inventory/filing changes."""
    held = set(inventory_ids)
    grants = []
    filed = False
    kind = npc.get("chain_role")

    if npc.get("out_to_lunch"):
        pages = [
            "The chair is empty. The monitor is still on.",
            "A tent card on the blotter reads OUT TO LUNCH.",
        ]
        item = npc.get("lunch_recovery_item") or (
            item_by_id(world, npc["provides"]) if npc.get("provides") and npc["provides"] != "FILE" else None
        )
        if npc.get("given"):
            pages.append("The envelope is already gone.")
        elif item:
            pages.append(
                "Someone left a manila envelope under the stapler, addressed to whoever is standing here."
            )
            grants.append(item)
        elif npc.get("chain_role") == "file":
            pages.append(
                "A covering clerk has taped a note: drop complete packets in the slot. Do not wait."
            )
            missing = [iid for iid in npc.get("requires") or [] if iid not in held]
            if missing:
                names = ", ".join((item_by_id(world, i) or {"name": i})["name"] for i in missing)
                pages.append(f"The slot rejects incomplete packets. Still missing: {names}.")
            else:
                pages.append("The slot accepts the stack with a muffled clank.")
                filed = True
        else:
            pages.append("There is nothing else on the desk.")
        return {"pages": pages, "grants": grants, "filed": filed, "repeat": False}

    missing = [iid for iid in npc.get("requires") or [] if iid not in held]
    can_act = False

    if npc.get("chain_role") == "file":
        if not missing:
            can_act = True
            filed = True
    elif npc.get("provides") and npc["provides"] != "FILE":
        item = item_by_id(world, npc["provides"])
        if npc.get("given"):
            pass
        elif not missing and item:
            can_act = True
            grants.append(item)

    if npc.get("talked") and not can_act:
        pages = [npc.get("revisit") or "I already said."]
        if npc.get("knowledge"):
            pages.append(npc["knowledge"][0]["text"])
        if missing:
            names = ", ".join((item_by_id(world, i) or {"name": i})["name"] for i in missing)
            pages.append(f"Still missing: {names}.")
        elif npc.get("given"):
            pages.append("I already gave you what this desk issues.")
        return {"pages": pages, "grants": grants, "filed": filed, "repeat": True}

    pages = [npc["greeting"]]
    for k in npc.get("knowledge") or []:
        pages.append(k["text"])

    if npc.get("chain_role") == "file":
        if missing:
            names = ", ".join((item_by_id(world, i) or {"name": i})["name"] for i in missing)
            pages.append(f"I can't take this yet. Still missing: {names}.")
        else:
            pages.append(GRANT_LINES.get("file", f"{world['start_doc']['code']} is accepted."))
    elif npc.get("provides") and npc["provides"] != "FILE":
        item = item_by_id(world, npc["provides"])
        if npc.get("given"):
            pages.append("I already gave you what this desk issues.")
        elif missing:
            names = ", ".join((item_by_id(world, i) or {"name": i})["name"] for i in missing)
            pages.append(f"I can do that once you have {names}.")
        elif item:
            line = GRANT_LINES.get(kind or "", "")
            pages.append(f"{item['name']}. {line}" if line else f"Fine. Here's {item['name']}. Don't lose the original.")

    return {"pages": pages, "grants": grants, "filed": filed, "repeat": False}
