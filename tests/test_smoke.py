"""Headless pygame smoke test: launch, draw floors, ride elevator, talk."""

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

from form_pending.game import Game  # noqa: E402


SHOT_DIR = ROOT / "diagnostics" / "screenshots"


class SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SHOT_DIR.mkdir(parents=True, exist_ok=True)
        cls.game = Game()
        cls.game.start_run(42)
        cls.game.state = "playing"

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_run_starts_on_floor_one(self):
        g = self.game
        self.assertEqual(g.player["floor"], 1)
        self.assertEqual(g.world["seed"], 42)
        self.assertTrue(g.player["inventory"])
        self.assertEqual(g.player["inventory"][0]["id"], "item_start")
        self.assertEqual(len(g.world["floors"]), 6)

    def test_draw_each_floor(self):
        g = self.game
        for floor in range(1, 7):
            g.player["floor"] = floor
            g.player["x"] = 8.5
            g.player["y"] = 18.2
            g.state = "playing"
            g.draw()
            path = SHOT_DIR / f"floor_{floor}.png"
            pygame.image.save(g.screen, str(path))
            self.assertTrue(path.exists() and path.stat().st_size > 1000)

    def test_title_and_overlays(self):
        g = self.game
        g.state = "title"
        g.draw()
        pygame.image.save(g.screen, str(SHOT_DIR / "title.png"))
        g.state = "document"
        g.draw()
        pygame.image.save(g.screen, str(SHOT_DIR / "document.png"))
        g.state = "elevator"
        g.elevator_sel = 4
        g.draw()
        pygame.image.save(g.screen, str(SHOT_DIR / "elevator.png"))
        g.state = "directory"
        g.player["floor"] = 1
        g.draw()
        pygame.image.save(g.screen, str(SHOT_DIR / "directory.png"))
        npc = g.world["npcs"][0]
        g.open_dialogue(npc)
        g.draw()
        pygame.image.save(g.screen, str(SHOT_DIR / "dialogue.png"))
        g.state = "playing"

    def test_elevator_moves_player(self):
        g = self.game
        g.player["floor"] = 1
        g.ride_elevator(5)
        self.assertEqual(g.player["floor"], 5)
        self.assertEqual(g.state, "playing")

    def test_movement_does_not_enter_walls(self):
        g = self.game
        g.player["floor"] = 1
        g.player["x"] = 8.5
        g.player["y"] = 18.2
        # Charge west into the outer wall for a while.
        class FakeKeys(dict):
            def __getitem__(self, key):
                return dict.get(self, key, False)

        # Directly apply blocked movement.
        for _ in range(120):
            nx = g.player["x"] - 0.2
            if not g.blocked(nx, g.player["y"]):
                g.player["x"] = nx
        self.assertGreater(g.player["x"], 1.0)
        self.assertFalse(g.blocked(g.player["x"], g.player["y"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
