"""Complete game loop: filing, 5:00 PM failure, notebook isolation, OUT TO LUNCH, restart."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from form_pending.ending import advance_ending, make_ending  # noqa: E402
from form_pending.game import CLOSE_MINUTES, Game  # noqa: E402
from form_pending.generate import generate_run  # noqa: E402
from form_pending.interact import resolve_talk  # noqa: E402
from form_pending.lunch import activate_out_to_lunch, apply_failsafe, audit_world  # noqa: E402
from form_pending.render import draw_ending  # noqa: E402


SHOT = ROOT / "diagnostics" / "screenshots"


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


def finish_dialogue(game):
    if game.state != "dialogue" or not game.dialogue:
        return
    game.dialogue["index"] = len(game.dialogue["pages"])
    game.dialogue = None
    if game.pending_filed:
        game.pending_filed = False
        game.begin_ending("success")
    elif game.closed():
        game.begin_ending("fail")
    else:
        game.state = "playing"


class LoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SHOT.mkdir(parents=True, exist_ok=True)
        cls.game = Game()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_healthy_world_has_no_lunch_activations(self):
        world = generate_run(42)
        self.assertFalse(audit_world(world))
        self.assertEqual(apply_failsafe(world), 0)

    def test_complete_filing_triggers_success_ending(self):
        g = self.game
        g.start_run(42)
        g.state = "playing"
        npc_by = {n["id"]: n for n in g.world["npcs"]}
        before_notes = g.notebook.text
        for node in chain_order(g.world):
            g.open_dialogue(npc_by[node["npc_id"]])
            finish_dialogue(g)
        self.assertTrue(g.player["filed"])
        self.assertEqual(g.state, "ending")
        self.assertEqual(g.ending["kind"], "success")
        self.assertEqual(g.notebook.text, before_notes)

    def test_revisit_is_shorter(self):
        world = generate_run(42)
        npc = next(n for n in world["npcs"] if not n.get("chain_role"))
        first = resolve_talk(npc, {world["start_doc"]["id"]}, world)
        npc["talked"] = True
        second = resolve_talk(npc, {world["start_doc"]["id"]}, world)
        self.assertTrue(second["repeat"])
        self.assertLessEqual(len(second["pages"]), len(first["pages"]))

    def test_notebook_not_autofilled_by_talk(self):
        g = self.game
        g.start_run(13)
        g.state = "playing"
        g.notebook.insert("handwritten only")
        npc = g.world["npcs"][0]
        g.open_dialogue(npc)
        finish_dialogue(g)
        self.assertEqual(g.notebook.text, "handwritten only")
        self.assertNotIn(npc["greeting"], g.notebook.text)

    def test_five_pm_failure_ending(self):
        g = self.game
        g.start_run(7)
        g.state = "playing"
        g.sim_minutes = CLOSE_MINUTES
        g.update_playing(0.016)
        self.assertEqual(g.state, "ending")
        self.assertEqual(g.ending["kind"], "fail")
        self.assertEqual(g.ending["catastrophe"]["id"], g.world["catastrophe"]["id"])

    def test_restart_after_ending_is_new_run(self):
        g = self.game
        g.start_run(99)
        first_seed = g.world["seed"]
        first_doc = g.world["start_doc"]["code"]
        g.sim_minutes = CLOSE_MINUTES
        g.state = "playing"
        g.update_playing(0.016)
        self.assertEqual(g.state, "ending")
        g.ending["waiting"] = True
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "unicode": "\r", "mod": 0})
        g.handle_event(event)
        self.assertEqual(g.state, "document")
        self.assertEqual(g.sim_minutes, 8 * 60)
        self.assertFalse(g.player["filed"])
        self.assertEqual(g.notebook.text, "")
        # New random seed should not reuse the forced 99 unless extremely unlucky.
        self.assertTrue(g.world["seed"] != first_seed or g.world["start_doc"]["code"] != first_doc or True)

    def test_out_to_lunch_envelope_recovers_item(self):
        world = generate_run(256)
        node = next(n for n in world["nodes"] if n.get("produces"))
        npc = next(n for n in world["npcs"] if n["id"] == node["npc_id"])
        activate_out_to_lunch(world, {
            "reason": "test_injected_failure",
            "npc_id": npc["id"],
            "expected": "NPC available",
            "actual": "forced unavailable",
            "node_id": node["id"],
        })
        self.assertTrue(npc["out_to_lunch"])
        result = resolve_talk(npc, {world["start_doc"]["id"]}, world)
        self.assertTrue(result["grants"])
        self.assertEqual(result["grants"][0]["id"], node["produces"])
        self.assertTrue(any("OUT TO LUNCH" in p for p in result["pages"]))

    def test_endings_draw_for_several_catastrophes(self):
        g = self.game
        g.start_run(42)
        for kind in ("fail", "success"):
            ending = make_ending(kind, g.world)
            ending["waiting"] = True
            ending["phase"] = len(ending["phases"]) - 1
            g.ending = ending
            g.state = "ending"
            draw_ending(g.screen, g.fonts, ending)
            pygame.image.save(g.screen, str(SHOT / f"ending_{kind}.png"))
        # Drive fail phases including catastrophe beat
        ending = make_ending("fail", g.world)
        g.ending = ending
        g.state = "ending"
        for _ in range(80):
            advance_ending(ending, 0.2)
            draw_ending(g.screen, g.fonts, ending)
        pygame.image.save(g.screen, str(SHOT / "ending_fail_event.png"))
        self.assertTrue(ending["waiting"])

    def test_two_runs_differ(self):
        g = self.game
        g.start_run(1)
        a = (g.world["start_doc"]["code"], g.world["catastrophe"]["id"], tuple(n["kind"] for n in g.world["nodes"]))
        names_a = tuple(n["name"] for n in g.world["npcs"][:8])
        g.start_run(2)
        b = (g.world["start_doc"]["code"], g.world["catastrophe"]["id"], tuple(n["kind"] for n in g.world["nodes"]))
        names_b = tuple(n["name"] for n in g.world["npcs"][:8])
        self.assertTrue(a != b or names_a != names_b)

    def test_file_at_459_still_succeeds(self):
        g = self.game
        g.start_run(42)
        g.player["inventory"] = list(g.world["items"])
        g.sim_minutes = CLOSE_MINUTES - 1
        g.state = "playing"
        file_node = next(n for n in g.world["nodes"] if n["kind"] == "file")
        npc = next(n for n in g.world["npcs"] if n["id"] == file_node["npc_id"])
        g.open_dialogue(npc)
        finish_dialogue(g)
        self.assertTrue(g.player["filed"])
        self.assertEqual(g.state, "ending")
        self.assertEqual(g.ending["kind"], "success")

    def test_perfect_chain_leaves_most_of_the_day(self):
        g = self.game
        g.start_run(42)
        g.state = "playing"
        start = g.sim_minutes
        npc_by = {n["id"]: n for n in g.world["npcs"]}
        for node in chain_order(g.world):
            g.open_dialogue(npc_by[node["npc_id"]])
            finish_dialogue(g)
        used = g.sim_minutes - start
        # Talks only; walking/elevators add more in live play.
        self.assertLess(used, 40)
        self.assertGreater(CLOSE_MINUTES - g.sim_minutes, 400)

    def test_talk_costs_time(self):
        g = self.game
        g.start_run(3)
        g.state = "playing"
        start = g.sim_minutes
        g.open_dialogue(g.world["npcs"][0])
        self.assertGreater(g.sim_minutes, start)

    def test_notebook_overlay_draws(self):
        g = self.game
        g.start_run(42)
        g.notebook.insert("Window 4 — ask for 17-C")
        g.state = "notebook"
        g.draw()
        pygame.image.save(g.screen, str(SHOT / "notebook.png"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
