"""Playable loop: one bureaucratic day, 8:00 to 5:00."""

from __future__ import annotations

import sys

import pygame

from .audio import Audio
from .catalog import FLOOR_COUNT, MAP_H, MAP_W, TILE
from .diagnostics import log_out_to_lunch
from .ending import advance_ending, make_ending
from .generate import generate_run
from .interact import resolve_talk
from .lunch import apply_failsafe
from .notebook import Notebook
from .render import (
    HUD_BOTTOM,
    HUD_TOP,
    SOLID_PROPS,
    Fonts,
    draw_dialogue,
    draw_directory,
    draw_document,
    draw_elevator_panel,
    draw_ending,
    draw_fade,
    draw_hud,
    draw_late_day,
    draw_notebook,
    draw_notice,
    draw_title,
    draw_toast,
    draw_world,
)
from .rng import normalize_seed
from .validate import in_bounds

SCREEN_W = 1280
SCREEN_H = 720
PLAYER_SPEED = 5.4
PLAYER_RADIUS = 0.28
# Idle 8–5 ≈ 54 real minutes. Flavor talks are cheap; mistakes still cost routing.
TIME_SECONDS_PER_SIM_MINUTE = 6.0
TALK_FLAVOR = 2
TALK_CHAIN = 3
TALK_REPEAT = 1
ELEVATOR_BASE = 1
ELEVATOR_PER_FLOOR = 1
READ_MINUTES = 1
CLOSE_MINUTES = 17 * 60

SOLID_TILES = {"wall", "desk"}


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("FORM PENDING")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.running = True
        self.state = "title"
        self.seed_text = ""
        self.pulse = 0.0
        self.world = None
        self.player = None
        self.cam = [0.0, 0.0]
        self.sim_minutes = 8 * 60
        self.time_accum = 0.0
        self.prompt = ""
        self.debug = False
        self.nearby = None
        self.dialogue = None
        self.elevator_sel = 1
        self.notice = None
        self.notebook = Notebook()
        self.ending = None
        self.pending_filed = False
        self._skip_text = False
        self.audio = Audio()
        self.toast = None
        self.fade = 0.0
        self.sign = None
        self.warn_4pm = False
        self.step_cd = 0.0
        self.last_tile = (0, 0)

    def start_run(self, seed_input):
        seed = normalize_seed(seed_input) if seed_input else normalize_seed(None)
        world = generate_run(seed)
        if world.get("generation_failed"):
            log_out_to_lunch({
                "seed": world["seed"],
                "npc_or_dependency": "generation",
                "expected": "valid solvable world",
                "actual": world.get("validation", {}).get("errors"),
                "reason": "generation_unresolved",
                "recovery": "OUT TO LUNCH envelopes on chain desks",
            })
        apply_failsafe(world)
        self.world = world
        start = world["player_start"]
        self.player = {
            "x": start["x"],
            "y": start["y"],
            "floor": start["floor"],
            "inventory": [world["start_doc"]],
            "appearance": {
                "presentation": "neutral",
                "skin": (236, 204, 176),
                "hair_style": "short",
                "hair_color": (42, 32, 24),
                "shirt": (62, 88, 132),
                "accessory": "badge",
            },
            "filed": False,
        }
        self.sim_minutes = 8 * 60
        self.time_accum = 0.0
        self.cam = self._target_cam()
        self.nearby = None
        self.dialogue = None
        self.notice = None
        self.elevator_sel = 1
        self.notebook.clear()
        self.ending = None
        self.pending_filed = False
        self.toast = None
        self.fade = 0.0
        self.sign = None
        self.warn_4pm = False
        self.player["moving"] = False
        self.player["walk_t"] = 0.0
        self.state = "document"

    def _target_cam(self):
        px = self.player["x"] * TILE
        py = self.player["y"] * TILE
        view_h = SCREEN_H - HUD_TOP - HUD_BOTTOM
        cx = px - SCREEN_W / 2
        cy = py - view_h / 2
        max_x = MAP_W * TILE - SCREEN_W
        max_y = MAP_H * TILE - view_h
        cx = max(0, min(cx, max(0, max_x)))
        cy = max(0, min(cy, max(0, max_y)))
        return [cx, cy]

    def current_floor(self):
        return self.world["floors"][self.player["floor"] - 1]

    def tile_at(self, x, y):
        tx, ty = int(x), int(y)
        if not in_bounds(tx, ty):
            return {"t": "wall"}
        return self.current_floor()["grid"][ty][tx]

    def is_solid(self, x, y) -> bool:
        tx, ty = int(x), int(y)
        if not in_bounds(tx, ty):
            return True
        t = self.current_floor()["grid"][ty][tx]["t"]
        if t in SOLID_TILES:
            return True
        for p in self.current_floor()["props"]:
            if p["x"] == tx and p["y"] == ty and p["type"] in SOLID_PROPS:
                return True
        return False

    def blocked(self, x, y) -> bool:
        r = PLAYER_RADIUS
        return (
            self.is_solid(x - r, y - r)
            or self.is_solid(x + r, y - r)
            or self.is_solid(x - r, y + r)
            or self.is_solid(x + r, y + r)
        )

    def on_elevator(self) -> bool:
        return self.tile_at(self.player["x"], self.player["y"])["t"] == "elevator"

    def near_directory(self):
        px, py = self.player["x"], self.player["y"]
        for p in self.current_floor()["props"]:
            if p["type"] != "directory":
                continue
            if abs(p["x"] + 0.5 - px) < 1.2 and abs(p["y"] + 0.5 - py) < 1.2:
                return p
        return None

    def nearest_npc(self):
        best = None
        best_d = 1.35
        for npc in self.world["npcs"]:
            if npc["floor"] != self.player["floor"]:
                continue
            dx = npc["x"] - self.player["x"]
            dy = (npc["y"] + 0.7) - self.player["y"]
            d = (dx * dx + dy * dy) ** 0.5
            if d < best_d:
                best, best_d = npc, d
        return best

    def has_item(self, iid) -> bool:
        return any(it["id"] == iid for it in self.player["inventory"])

    def give_item(self, item):
        if item and not self.has_item(item["id"]):
            self.player["inventory"].append(item)

    def advance_time(self, minutes):
        if self.player and self.player.get("filed"):
            return
        self.sim_minutes = min(CLOSE_MINUTES, self.sim_minutes + minutes)

    def clock_hm(self):
        total = int(self.sim_minutes)
        return total // 60, total % 60

    def closed(self) -> bool:
        return self.sim_minutes >= CLOSE_MINUTES and not (self.player and self.player.get("filed"))

    def begin_ending(self, kind):
        self.ending = make_ending(kind, self.world)
        self.state = "ending"
        pygame.key.stop_text_input()
        pygame.key.set_repeat()
        self.audio.play("stamp" if kind == "success" else "fail")

    def show_toast(self, text, seconds=2.4):
        self.toast = {"text": text, "t": seconds}

    def near_memo(self):
        px, py = self.player["x"], self.player["y"]
        for p in self.current_floor()["props"]:
            if p["type"] != "memo":
                continue
            if abs(p["x"] + 0.5 - px) < 1.15 and abs(p["y"] + 0.5 - py) < 1.15:
                return p
        return None

    def open_notebook(self):
        self.state = "notebook"
        self._skip_text = True
        pygame.key.set_repeat(400, 35)
        pygame.key.start_text_input()

    def close_notebook(self):
        pygame.key.stop_text_input()
        pygame.key.set_repeat()
        self.state = "playing"

    def interact(self):
        if self.closed():
            self.begin_ending("fail")
            return
        if self.on_elevator():
            self.elevator_sel = self.player["floor"]
            self.state = "elevator"
            return
        if self.near_directory():
            self.advance_time(READ_MINUTES)
            self.audio.play("paper")
            self.state = "directory"
            return
        memo = self.near_memo()
        if memo:
            self.advance_time(READ_MINUTES)
            self.audio.play("paper")
            self.sign = {"title": "NOTICE", "body": memo.get("text") or "The tape has peeled. The message is gone."}
            self.state = "sign"
            return
        npc = self.nearest_npc()
        if npc:
            self.open_dialogue(npc)

    def open_dialogue(self, npc):
        held = [it["id"] for it in self.player["inventory"]]
        result = resolve_talk(npc, held, self.world)
        for item in result["grants"]:
            self.give_item(item)
            npc["given"] = True
            self.show_toast(f"Received: {item['name']}")
            self.audio.play("paper")
        if result["filed"]:
            npc["given"] = True
            self.player["filed"] = True
            self.pending_filed = True
            self.audio.play("stamp")
        if result.get("repeat"):
            cost = TALK_REPEAT
        elif npc.get("chain_role") or npc.get("is_intake"):
            cost = TALK_CHAIN
        else:
            cost = TALK_FLAVOR
        self.advance_time(cost)
        npc["talked"] = True
        self.audio.play("click")
        self.dialogue = {"npc": npc, "pages": result["pages"], "index": 0}
        self.state = "dialogue"

    def ride_elevator(self, dest):
        dest = max(1, min(FLOOR_COUNT, dest))
        if dest == self.player["floor"]:
            self.state = "playing"
            return
        delta = abs(dest - self.player["floor"])
        self.advance_time(ELEVATOR_BASE + ELEVATOR_PER_FLOOR * delta)
        self.player["floor"] = dest
        self.fade = 1.0
        self.audio.play("ding")
        self.player["x"] = 8.2
        self.player["y"] = 18.2
        if self.blocked(self.player["x"], self.player["y"]):
            self.player["x"] = 8.5
            self.player["y"] = 17.5
        self.cam = self._target_cam()
        self.state = "playing"
        if self.closed():
            self.begin_ending("fail")

    def handle_title_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_RETURN:
                self.start_run(self.seed_text.strip() or None)
            elif event.key == pygame.K_BACKSPACE:
                self.seed_text = self.seed_text[:-1]
            else:
                ch = event.unicode
                if ch and ch.isprintable() and len(self.seed_text) < 24:
                    self.seed_text += ch

    def handle_notebook_event(self, event):
        nb = self.notebook
        if event.type == pygame.TEXTINPUT:
            if self._skip_text:
                self._skip_text = False
                return
            if event.text and event.text not in ("\n", "\r"):
                nb.insert(event.text)
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.close_notebook()
        elif event.key == pygame.K_BACKSPACE:
            nb.backspace()
        elif event.key == pygame.K_DELETE:
            nb.delete()
        elif event.key == pygame.K_RETURN:
            nb.newline()
        elif event.key == pygame.K_LEFT:
            nb.move_left()
        elif event.key == pygame.K_RIGHT:
            nb.move_right()
        elif event.key == pygame.K_UP:
            nb.move_up()
        elif event.key == pygame.K_DOWN:
            nb.move_down()
        elif event.key == pygame.K_HOME:
            nb.move_home()
        elif event.key == pygame.K_END:
            nb.move_end()

    def handle_playing_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.notice = {
                "title": "LEAVE BUILDING?",
                "body": "Shift is still open. Enter returns to the title page. ESC stays.",
                "kind": "quit_confirm",
            }
            self.state = "notice"
        elif event.key in (pygame.K_e, pygame.K_SPACE):
            self.interact()
        elif event.key == pygame.K_n:
            self.open_notebook()
            self.audio.play("paper")
        elif event.key == pygame.K_m:
            muted = self.audio.toggle_mute()
            self.show_toast("Muted" if muted else "Sound on")
        elif event.key == pygame.K_r:
            self.advance_time(READ_MINUTES)
            self.state = "document"
        elif event.key == pygame.K_F3:
            self.debug = not self.debug
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
            if self.on_elevator():
                self.ride_elevator(event.key - pygame.K_0)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if self.state == "title":
            self.handle_title_event(event)
        elif self.state == "playing":
            self.handle_playing_event(event)
        elif self.state == "notebook":
            self.handle_notebook_event(event)
        elif self.state == "dialogue":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                self.dialogue["index"] += 1
                if self.dialogue["index"] >= len(self.dialogue["pages"]):
                    self.dialogue = None
                    if self.pending_filed:
                        self.pending_filed = False
                        self.begin_ending("success")
                    elif self.closed():
                        self.begin_ending("fail")
                    else:
                        self.state = "playing"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.dialogue = None
                if self.pending_filed:
                    self.pending_filed = False
                    self.begin_ending("success")
                else:
                    self.state = "playing"
        elif self.state == "elevator":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "playing"
                elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                    self.ride_elevator(self.elevator_sel)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
                    self.elevator_sel = event.key - pygame.K_0
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.elevator_sel = min(FLOOR_COUNT, self.elevator_sel + 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.elevator_sel = max(1, self.elevator_sel - 1)
        elif self.state in ("directory", "document", "sign"):
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_e, pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN, pygame.K_r
            ):
                self.state = "playing"
                self.sign = None
        elif self.state == "notice":
            if event.type == pygame.KEYDOWN:
                kind = (self.notice or {}).get("kind")
                if kind == "quit_confirm":
                    if event.key == pygame.K_RETURN:
                        self.state = "title"
                        self.notice = None
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                        self.notice = None
                elif event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    self.state = "playing"
                    self.notice = None
        elif self.state == "ending":
            if event.type == pygame.KEYDOWN and self.ending and self.ending.get("waiting"):
                if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                    self.seed_text = ""
                    self.start_run(None)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "title"
                    self.ending = None

    def update_playing(self, dt):
        keys = pygame.key.get_pressed()
        vx = vy = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy += 1
        moving = bool(vx or vy)
        self.player["moving"] = moving
        if moving:
            mag = (vx * vx + vy * vy) ** 0.5
            vx, vy = vx / mag, vy / mag
            nx = self.player["x"] + vx * PLAYER_SPEED * dt
            ny = self.player["y"] + vy * PLAYER_SPEED * dt
            if not self.blocked(nx, self.player["y"]):
                self.player["x"] = nx
            if not self.blocked(self.player["x"], ny):
                self.player["y"] = ny
            self.player["x"] = max(1.2, min(MAP_W - 1.2, self.player["x"]))
            self.player["y"] = max(1.2, min(MAP_H - 1.2, self.player["y"]))
            self.player["walk_t"] = self.player.get("walk_t", 0) + dt
            tile = (int(self.player["x"]), int(self.player["y"]))
            self.step_cd = max(0.0, self.step_cd - dt)
            if tile != self.last_tile and self.step_cd <= 0:
                self.audio.play("step")
                self.step_cd = 0.16
                self.last_tile = tile
        else:
            self.player["walk_t"] = 0.0

        # Hard-follow the player. Quantizing or lerping here made the world
        # hitch 1px while the sprite moved in floats.
        self.cam = self._target_cam()

        self.tick_clock(dt)

        npc = self.nearest_npc()
        self.nearby = npc
        if self.on_elevator():
            self.prompt = "E  elevator     1–6  floor"
        elif self.near_directory():
            self.prompt = "E  read directory"
        elif self.near_memo():
            self.prompt = "E  read notice"
        elif npc and npc.get("out_to_lunch"):
            self.prompt = f"E  inspect {npc['name']}'s desk"
        elif npc:
            self.prompt = f"E  talk to {npc['name']}"
        else:
            self.prompt = ""

        hh, mm = self.clock_hm()
        if hh >= 16 and not self.warn_4pm:
            self.warn_4pm = True
            self.audio.play("warn")
            self.show_toast("Building closes at 5:00 PM")

        if self.closed():
            self.begin_ending("fail")

    def tick_clock(self, dt):
        if self.player and self.player.get("filed"):
            return
        self.time_accum += dt
        while self.time_accum >= TIME_SECONDS_PER_SIM_MINUTE:
            self.time_accum -= TIME_SECONDS_PER_SIM_MINUTE
            self.advance_time(1)

    def draw(self):
        if self.state == "title":
            draw_title(self.screen, self.fonts, self.seed_text, self.pulse)
            pygame.display.flip()
            return
        if self.state == "ending" and self.ending:
            draw_ending(self.screen, self.fonts, self.ending)
            pygame.display.flip()
            return

        draw_world(self.screen, self.world, self.player["floor"], self.player, self.cam, self.fonts)
        hh, mm = self.clock_hm()
        draw_late_day(self.screen, hh, mm)
        draw_hud(self.screen, self.fonts, self.world, self.player, (hh, mm), self.prompt, self.debug)

        if self.state == "dialogue" and self.dialogue:
            draw_dialogue(self.screen, self.fonts, self.dialogue["npc"], self.dialogue["pages"], self.dialogue["index"])
        elif self.state == "elevator":
            draw_elevator_panel(self.screen, self.fonts, self.player["floor"], self.elevator_sel)
        elif self.state == "directory":
            draw_directory(self.screen, self.fonts, self.world, self.player["floor"])
        elif self.state == "document":
            draw_document(self.screen, self.fonts, self.world)
        elif self.state == "sign" and self.sign:
            draw_notice(self.screen, self.fonts, self.sign["title"], self.sign["body"])
        elif self.state == "notebook":
            draw_notebook(self.screen, self.fonts, self.notebook, blink=(int(self.pulse * 2) % 2 == 0))
        elif self.state == "notice" and self.notice:
            draw_notice(self.screen, self.fonts, self.notice["title"], self.notice["body"])

        draw_toast(self.screen, self.fonts, self.toast)
        draw_fade(self.screen, self.fade)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.pulse += dt
            for event in pygame.event.get():
                self.handle_event(event)
            if self.state == "playing":
                self.update_playing(dt)
            elif self.state == "notebook":
                self.tick_clock(dt)
            elif self.state == "ending" and self.ending:
                advance_ending(self.ending, dt)
            if self.fade > 0:
                self.fade = max(0.0, self.fade - dt * 2.2)
            if self.toast:
                self.toast["t"] -= dt
                if self.toast["t"] <= 0:
                    self.toast = None
            self.draw()
        pygame.quit()


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    game = Game()
    if argv:
        game.start_run(argv[0])
    game.run()


if __name__ == "__main__":
    main()
