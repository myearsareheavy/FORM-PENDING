"""Procedural generation tests for Form Pending."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from form_pending.catalog import FEMININE_NAMES, FLOOR_COUNT, MASCULINE_NAMES
from form_pending.generate import generate_run
from form_pending.interact import resolve_talk
from form_pending.rng import normalize_seed
from form_pending.validate import simulate_completion, validate_world, worlds_differ_meaningfully, walkable

SEEDS = [
    1, 2, 7, 13, 42, 99, 256, 1024, 7777, 12345,
    20260311, 8675309, 314159, 271828, 99991,
    "janet", "intake", "vault", "tuesday", "p91-2x",
    "coffee-recall", "window-4", "form-pending", "hargrove", "annex-c",
]


class SeedTests(unittest.TestCase):
    def test_normalize_seed_stable(self):
        self.assertEqual(normalize_seed("abc"), normalize_seed("abc"))
        self.assertEqual(normalize_seed(42), 42)
        self.assertNotEqual(normalize_seed("abc"), normalize_seed("abd"))
        self.assertTrue(normalize_seed(0))

    def test_same_seed_identical(self):
        a = generate_run(42)
        b = generate_run(42)
        self.assertEqual(a["start_doc"]["code"], b["start_doc"]["code"])
        self.assertEqual(a["catastrophe"]["id"], b["catastrophe"]["id"])
        self.assertEqual([n["name"] for n in a["npcs"]], [n["name"] for n in b["npcs"]])
        self.assertEqual([n["id"] for n in a["nodes"]], [n["id"] for n in b["nodes"]])
        self.assertEqual(a["chain_npc_ids"], b["chain_npc_ids"])


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = []
        cls.failures = []
        for seed in SEEDS:
            world = generate_run(seed)
            cls.worlds.append(world)
            if world.get("generation_failed"):
                cls.failures.append((seed, world.get("validation", {}).get("errors")))

    def test_no_generation_failures(self):
        self.assertFalse(self.failures, f"unresolved seeds: {self.failures}")

    def test_every_seed_valid_and_solvable(self):
        for seed, world in zip(SEEDS, self.worlds):
            with self.subTest(seed=seed):
                v = validate_world(world)
                self.assertTrue(v["ok"], v["errors"])
                sim = simulate_completion(world)
                self.assertTrue(sim["ok"], sim.get("reason"))
                self.assertEqual(len(world["floors"]), FLOOR_COUNT)
                self.assertGreaterEqual(len(world["npcs"]), 30)
                floors_present = {n["floor"] for n in world["npcs"]}
                for i in range(1, FLOOR_COUNT + 1):
                    self.assertIn(i, floors_present, f"no NPCs on floor {i}")
                filer = next(n for n in world["nodes"] if n["kind"] == "file")
                self.assertTrue(any(n["id"] == filer["npc_id"] for n in world["npcs"]))

    def test_seeds_vary(self):
        diffs = 0
        worlds = self.worlds
        pairs = 0
        for i in range(len(worlds)):
            for j in range(i + 1, len(worlds)):
                pairs += 1
                if worlds_differ_meaningfully(worlds[i], worlds[j]):
                    diffs += 1
        self.assertGreater(diffs, pairs * 0.9, f"only {diffs}/{pairs} pairs differed")

    def test_knowledge_matches_state(self):
        for world in self.worlds:
            by_id = {n["id"]: n for n in world["npcs"]}
            for npc in world["npcs"]:
                for k in npc["knowledge"]:
                    fact = k.get("fact") or {}
                    if fact.get("npc_id"):
                        t = by_id.get(fact["npc_id"])
                        self.assertIsNotNone(t, f"{npc['name']} points at missing {fact['npc_id']}")
                        if fact.get("floor") is not None:
                            self.assertEqual(t["floor"], fact["floor"])

    def test_floors_have_elevator_and_desks(self):
        for world in self.worlds[:8]:
            for floor in world["floors"]:
                elev = sum(1 for row in floor["grid"] for t in row if t["t"] == "elevator")
                corr = sum(1 for row in floor["grid"] for t in row if t["t"] == "corridor")
                self.assertGreaterEqual(elev, 4, f"floor {floor['index']} elevator={elev}")
                self.assertGreaterEqual(corr, 20, f"floor {floor['index']} corridor={corr}")
                self.assertGreaterEqual(len(floor["desks"]), 4, f"floor {floor['index']} desks={len(floor['desks'])}")

    def test_memos_and_intake_present(self):
        for world in self.worlds[:8]:
            memos = [p for fl in world["floors"] for p in fl["props"] if p["type"] == "memo"]
            self.assertGreaterEqual(len(memos), 6, "expected wall notices on several floors")
            for m in memos:
                self.assertTrue(m.get("text"))
                if m.get("fact_floor") is not None:
                    dept = next(d for d in world["departments"] if d["name"] == m["fact_dept"])
                    self.assertEqual(dept["floor"], m["fact_floor"])
            intake = next((n for n in world["npcs"] if n.get("is_intake")), None)
            self.assertIsNotNone(intake)
            self.assertEqual(intake["floor"], 1)
            dist = ((intake["x"] - 8.5) ** 2 + (intake["y"] - 18.5) ** 2) ** 0.5
            self.assertLess(dist, 4.0, "intake should be in the lobby")

    def test_handlers_speak_first_person(self):
        for world in self.worlds:
            by_id = {n["id"]: n for n in world["npcs"]}
            for node in world["nodes"]:
                npc = by_id[node["npc_id"]]
                first = npc["name"].split()[0]
                for k in npc["knowledge"]:
                    if k.get("type") != "handles":
                        continue
                    text = k["text"]
                    self.assertFalse(text.startswith(first + " "), f"{npc['name']}: {text}")
                    for pat in (
                        f"{first} in ",
                        f"{first} at ",
                        f"{first} keeps",
                        f"{first} has to",
                        f"{first} will ",
                        f"That's me. {first}",
                    ):
                        self.assertNotIn(pat, text, f"{npc['name']} self-ref: {text}")
                    self.assertTrue(
                        text.startswith("I ") or text.startswith("I'll ") or text.startswith("I'm "),
                        f"expected first person from {npc['name']}: {text}",
                    )

    def test_name_matches_presentation(self):
        fem = set(FEMININE_NAMES)
        masc = set(MASCULINE_NAMES)
        for world in self.worlds:
            for npc in world["npcs"]:
                first = npc["name"].split()[0]
                pres = npc["appearance"].get("presentation")
                if first in fem:
                    self.assertEqual(pres, "feminine", npc["name"])
                elif first in masc:
                    self.assertEqual(pres, "masculine", npc["name"])
                self.assertIn(pres, ("feminine", "masculine", "neutral"))

    def test_spawn_is_walkable(self):
        for world in self.worlds:
            floor = world["floors"][0]
            x, y = int(world["player_start"]["x"]), int(world["player_start"]["y"])
            self.assertTrue(walkable(floor["grid"][y][x]), f"spawn tile {x},{y} is {floor['grid'][y][x]['t']}")

    def test_talk_chain_grants_in_order(self):
        world = self.worlds[0]
        npc_by_id = {n["id"]: n for n in world["npcs"]}
        inv = {world["start_doc"]["id"]}
        # Leaf first (last node) through to file.
        nodes = world["nodes"]
        file_node = next(n for n in nodes if n["kind"] == "file")
        order = []
        seen = set()

        def visit(node):
            if not node or node["id"] in seen:
                return
            seen.add(node["id"])
            by = {n["id"]: n for n in nodes}
            for rid in node.get("requires") or []:
                visit(by.get(rid))
            order.append(node)

        visit(file_node)
        for node in order:
            npc = npc_by_id[node["npc_id"]]
            result = resolve_talk(npc, inv, world)
            if node["kind"] == "file":
                self.assertTrue(result["filed"], result["pages"][-1])
            else:
                self.assertTrue(result["grants"], f"expected grant from {npc['name']}: {result['pages'][-1]}")
                for item in result["grants"]:
                    inv.add(item["id"])
                    npc["given"] = True

    def test_file_refused_without_prereqs(self):
        world = self.worlds[0]
        file_node = next(n for n in world["nodes"] if n["kind"] == "file")
        npc = next(n for n in world["npcs"] if n["id"] == file_node["npc_id"])
        result = resolve_talk(npc, {world["start_doc"]["id"]}, world)
        self.assertFalse(result["filed"])
        self.assertTrue(any("missing" in p.lower() or "can't take" in p.lower() for p in result["pages"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
