"""Release-candidate regression: fresh seeds, full loop, notebook, logs."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from form_pending.diagnostics import LOG_PATH  # noqa: E402
from form_pending.game import (  # noqa: E402
    CLOSE_MINUTES,
    ELEVATOR_BASE,
    ELEVATOR_PER_FLOOR,
    READ_MINUTES,
    TALK_CHAIN,
    Game,
)
from form_pending.generate import generate_run  # noqa: E402
from form_pending.lunch import apply_failsafe, audit_world  # noqa: E402
from form_pending.validate import simulate_completion, validate_world  # noqa: E402

FRESH_SEEDS = list(range(5000, 5040)) + [
    "release-alpha",
    "blind-play",
    "form-pending-rc",
    "window-4",
    "5pm",
]


def chain_order(world):
    nodes = world["nodes"]
    by = {n["id"]: n for n in nodes}
    file_node = next(n for n in nodes if n["kind"] == "file")
    order = []
    seen = set()

    def visit(node):
        if not node or node["id"] in seen:
            return
        seen.add(node["id"])
        for rid in node.get("requires") or []:
            visit(by.get(rid))
        order.append(node)

    visit(file_node)
    return order


def efficient_route_minutes(world):
    """Sim minutes for intake + chain talks + elevators, no extra wandering."""
    npc_by = {n["id"]: n for n in world["npcs"]}
    minutes = READ_MINUTES + TALK_CHAIN  # opening slip + intake
    prev = 1
    for node in chain_order(world):
        npc = npc_by[node["npc_id"]]
        delta = abs(npc["floor"] - prev)
        if delta:
            minutes += ELEVATOR_BASE + ELEVATOR_PER_FLOOR * delta
        minutes += TALK_CHAIN
        prev = npc["floor"]
    return minutes


def finish_dialogue(game):
    if game.state != "dialogue" or not game.dialogue:
        return
    game.dialogue = None
    if game.pending_filed:
        game.pending_filed = False
        game.begin_ending("success")
    elif game.closed():
        game.begin_ending("fail")
    else:
        game.state = "playing"


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()
        cls.worlds = []
        cls.lunch = 0
        cls.routes = []
        for seed in FRESH_SEEDS:
            world = generate_run(seed)
            cls.worlds.append(world)
            cls.lunch += apply_failsafe(world)
            cls.routes.append(efficient_route_minutes(world))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_all_fresh_seeds_solvable(self):
        failed = []
        for seed, world in zip(FRESH_SEEDS, self.worlds):
            v = validate_world(world)
            sim = simulate_completion(world)
            if world.get("generation_failed") or not v["ok"] or not sim["ok"]:
                failed.append((seed, v.get("errors"), sim.get("reason"), world.get("generation_failed")))
        self.assertFalse(failed, f"unsolvable seeds: {failed[:5]}")

    def test_no_failsafe_on_fresh_seeds(self):
        self.assertEqual(self.lunch, 0)
        for world in self.worlds:
            self.assertFalse(audit_world(world))
            self.assertFalse(world.get("out_to_lunch_events"))

    def test_efficient_routes_leave_afternoon(self):
        for seed, mins in zip(FRESH_SEEDS, self.routes):
            with self.subTest(seed=seed):
                self.assertLess(mins, 120, f"efficient route {mins} sim min")
                self.assertGreater(CLOSE_MINUTES - 8 * 60 - mins, 300)

    def test_runs_differ_across_fresh_seeds(self):
        keys = {
            (w["start_doc"]["code"], w["catastrophe"]["id"], tuple(n["kind"] for n in w["nodes"]))
            for w in self.worlds
        }
        self.assertGreater(len(keys), len(self.worlds) * 0.6)

    def test_success_failure_notebook_restart(self):
        g = self.game
        g.start_run(5000)
        g.notebook.insert("ask intake — then elevator board")
        self.assertIn("intake", g.notebook.text)
        g.state = "playing"
        npc_by = {n["id"]: n for n in g.world["npcs"]}
        for node in chain_order(g.world):
            g.open_dialogue(npc_by[node["npc_id"]])
            finish_dialogue(g)
        self.assertEqual(g.state, "ending")
        self.assertEqual(g.ending["kind"], "success")
        self.assertIn("intake", g.notebook.text)

        g.start_run(5001)
        self.assertEqual(g.notebook.text, "")
        self.assertEqual(g.sim_minutes, 8 * 60)
        g.state = "playing"
        g.sim_minutes = CLOSE_MINUTES
        g.update_playing(0.016)
        self.assertEqual(g.state, "ending")
        self.assertEqual(g.ending["kind"], "fail")

        g.ending["waiting"] = True
        g.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "unicode": "\r", "mod": 0}))
        self.assertEqual(g.state, "document")
        self.assertFalse(g.player["filed"])

    def test_diagnostic_log_only_test_injections_if_present(self):
        genuine = []
        if LOG_PATH.exists():
            for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("reason") != "test_injected_failure":
                    genuine.append(rec)
        self.assertFalse(genuine, f"unexpected OUT TO LUNCH records: {genuine}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
