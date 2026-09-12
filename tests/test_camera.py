"""Camera follow should be stable, monotonic while walking, and still when idle."""

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

from form_pending.catalog import TILE  # noqa: E402
from form_pending.game import HUD_BOTTOM, SCREEN_H, SCREEN_W, Game  # noqa: E402
from form_pending.render import HUD_TOP, screen_xy  # noqa: E402


DT = 1.0 / 60.0


class CameraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()
        cls.game.start_run(42)
        cls.game.state = "playing"
        cls.game.fade = 0

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _walk(self, dx, dy, frames):
        g = self.game
        xs, ys = [], []
        for _ in range(frames):
            mag = (dx * dx + dy * dy) ** 0.5 or 1.0
            nx = g.player["x"] + (dx / mag) * 5.4 * DT
            ny = g.player["y"] + (dy / mag) * 5.4 * DT
            if not g.blocked(nx, g.player["y"]):
                g.player["x"] = nx
            if not g.blocked(g.player["x"], ny):
                g.player["y"] = ny
            g.cam = g._target_cam()
            xs.append(g.cam[0])
            ys.append(g.cam[1])
        return xs, ys

    def test_idle_camera_is_bit_stable(self):
        g = self.game
        g.player["x"], g.player["y"] = 12.0, 18.0
        g.cam = g._target_cam()
        first = tuple(g.cam)
        for _ in range(45):
            g.cam = g._target_cam()
            self.assertEqual(tuple(g.cam), first)

    def test_hard_follow_matches_target(self):
        g = self.game
        g.player["x"], g.player["y"] = 14.25, 16.5
        g.cam = g._target_cam()
        self.assertEqual(g.cam, g._target_cam())

    def test_horizontal_walk_is_monotonic(self):
        g = self.game
        # Map is only a little wider than the screen; pan starts near x≈20.
        g.player["x"], g.player["y"] = 20.2, 15.5
        g.cam = g._target_cam()
        xs, _ = self._walk(1, 0, 90)
        reversals = sum(1 for i in range(1, len(xs)) if xs[i] + 1e-6 < xs[i - 1])
        self.assertEqual(reversals, 0, f"horizontal reversals={reversals} xs={xs[:5]}..{xs[-3:]}")
        self.assertGreaterEqual(xs[-1], xs[0])

    def test_vertical_walk_is_monotonic(self):
        g = self.game
        floor = g.current_floor()
        start = None
        for x in range(2, 40):
            for y in range(14, 20):
                if floor["grid"][y][x]["t"] not in ("corridor", "floor", "door"):
                    continue
                if g.blocked(x + 0.5, y + 0.5):
                    continue
                if all(
                    floor["grid"][y - k][x]["t"] in ("corridor", "floor", "door")
                    for k in range(1, 6)
                ):
                    start = (x + 0.5, y + 0.5)
                    break
            if start:
                break
        self.assertIsNotNone(start, "no vertical corridor found")
        g.player["x"], g.player["y"] = start
        g.cam = g._target_cam()
        _, ys = self._walk(0, -1, 200)
        reversals = sum(1 for i in range(1, len(ys)) if ys[i] - 1e-6 > ys[i - 1])
        self.assertEqual(reversals, 0, f"vertical reversals={reversals} y0={ys[0]} y1={ys[-1]}")
        self.assertNotEqual(ys[-1], ys[0])

    def test_direction_change_does_not_oscillate(self):
        g = self.game
        g.player["x"], g.player["y"] = 8.5, 18.0
        g.cam = g._target_cam()
        self._walk(0, 1, 50)
        mid = g.cam[1]
        self._walk(0, -1, 50)
        self.assertLess(g.cam[1], mid)
        self.assertEqual(g.cam, g._target_cam())

    def test_unclamped_player_screen_is_stable(self):
        g = self.game
        view_h = SCREEN_H - HUD_TOP - HUD_BOTTOM
        expected_x = round(SCREEN_W / 2)
        expected_y = round(HUD_TOP + view_h / 2)
        xs, ys = [], []
        # Vertical range is unclamped for y around 12–20; x around 20.5 is unclamped.
        for i in range(80):
            g.player["x"] = 20.4 + i * 0.02
            g.player["y"] = 15.2 + i * 0.015
            g.cam = g._target_cam()
            sx, sy = screen_xy(g.player["x"] * TILE, g.player["y"] * TILE, g.cam)
            xs.append(sx)
            ys.append(sy)
        self.assertEqual(set(xs), {expected_x}, f"player screen x hitch {set(xs)}")
        self.assertEqual(set(ys), {expected_y}, f"player screen y hitch {set(ys)}")

    def test_clamped_player_screen_has_no_two_pixel_jumps(self):
        g = self.game
        g.player["x"], g.player["y"] = 8.5, 18.5
        g.cam = g._target_cam()
        prev = screen_xy(g.player["x"] * TILE, g.player["y"] * TILE, g.cam)
        jumps = []
        for i in range(200):
            g.player["x"] = 8.5 + i * 0.01
            g.cam = g._target_cam()
            cur = screen_xy(g.player["x"] * TILE, g.player["y"] * TILE, g.cam)
            dx = abs(cur[0] - prev[0])
            dy = abs(cur[1] - prev[1])
            if dx > 1 or dy > 1:
                jumps.append((i, prev, cur, dx, dy))
            prev = cur
        self.assertFalse(jumps, f"subpixel walk jumped >1px: {jumps[:5]}")

    def test_world_and_player_share_transform(self):
        g = self.game
        g.player["x"], g.player["y"] = 13.37, 17.81
        g.cam = g._target_cam()
        ps = screen_xy(g.player["x"] * TILE, g.player["y"] * TILE, g.cam)
        # A tile at integer coords uses the same function.
        ts = screen_xy(13 * TILE, 17 * TILE, cam=g.cam)
        # Player is 0.37 tiles east of tile 13 → about 12px, not a rounding wild card.
        self.assertAlmostEqual(ps[0] - ts[0], 0.37 * TILE, delta=1.01)

    def test_idle_player_screen_is_bit_stable(self):
        g = self.game
        g.player["x"], g.player["y"] = 12.25, 18.0
        g.cam = g._target_cam()
        first = screen_xy(g.player["x"] * TILE, g.player["y"] * TILE, g.cam)
        for _ in range(40):
            g.cam = g._target_cam()
            self.assertEqual(screen_xy(g.player["x"] * TILE, g.player["y"] * TILE, g.cam), first)


if __name__ == "__main__":
    unittest.main(verbosity=2)
