"""Municipal-modernist renderer: architectural plan with living office furniture."""

from __future__ import annotations

import math

import pygame

from .catalog import FLOOR_COUNT, MAP_H, MAP_W, TILE
from .validate import in_bounds

HUD_TOP = 58
HUD_BOTTOM = 78


def screen_xy(wx, wy, cam):
    """World-pixel to screen-pixel. Round only at this step, never before subtracting cam."""
    return round(wx - cam[0]), round(wy - cam[1] + HUD_TOP)

INK = (36, 32, 28)
PAPER = (236, 226, 204)
PAPER_DARK = (214, 200, 170)
MANILA = (214, 186, 130)
STAMP_RED = (176, 36, 36)
BRASS = (176, 142, 72)
SHADOW = (20, 16, 12)


def _font(name, size, bold=False):
    path = pygame.font.match_font(name, bold=bold)
    if path:
        return pygame.font.Font(path, size)
    return pygame.font.SysFont(name, size, bold=bold)


class Fonts:
    def __init__(self):
        self.title = _font("georgia", 54, True)
        self.title_sm = _font("georgia", 28, True)
        self.ui = _font("segoeui", 18)
        self.ui_b = _font("segoeui", 18, True)
        self.small = _font("segoeui", 14)
        self.tiny = _font("segoeui", 12)
        self.mono = _font("consolas", 16)
        self.mono_sm = _font("consolas", 13)
        self.stamp = _font("georgia", 22, True)
        self.huge = _font("georgia", 72, True)
        self.floor_paint = _font("georgia", 120, True)


def darken(color, amt=0.7):
    return tuple(max(0, int(c * amt)) for c in color)


def lighten(color, amt=0.25):
    return tuple(min(255, int(c + (255 - c) * amt)) for c in color)


def wrap_text(font, text, width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if font.size(trial)[0] <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def blit_text(surf, font, text, pos, color=INK, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)
    return rect


SOLID_PROPS = {
    "copier", "cabinet", "vault", "shelves", "counter", "window_counter",
    "whiteboard", "portrait", "table", "directory", "cooler",
}


def draw_hair(surf, hx, hy, style, color):
    c = color
    dark = darken(c, 0.65)
    if style == "bald":
        pygame.draw.arc(surf, (90, 70, 60), (hx - 7, hy - 8, 14, 10), 3.2, 6.2, 1)
        return
    if style == "afro":
        pygame.draw.circle(surf, c, (hx, hy - 5), 12)
        pygame.draw.circle(surf, dark, (hx, hy - 5), 12, 1)
        return
    if style == "bun":
        pygame.draw.ellipse(surf, c, (hx - 8, hy - 9, 16, 11))
        pygame.draw.circle(surf, c, (hx, hy - 12), 5)
        pygame.draw.circle(surf, dark, (hx, hy - 12), 5, 1)
        return
    if style == "bob":
        pygame.draw.ellipse(surf, c, (hx - 10, hy - 8, 20, 18))
        pygame.draw.ellipse(surf, c, (hx - 9, hy - 2, 7, 12))
        pygame.draw.ellipse(surf, c, (hx + 2, hy - 2, 7, 12))
        return
    if style == "ponytail":
        pygame.draw.ellipse(surf, c, (hx - 8, hy - 9, 16, 11))
        pygame.draw.ellipse(surf, c, (hx + 5, hy - 1, 7, 16))
        pygame.draw.circle(surf, dark, (hx + 7, hy + 2), 2)
        return
    if style == "slick":
        pygame.draw.ellipse(surf, c, (hx - 8, hy - 10, 16, 9))
        pygame.draw.line(surf, dark, (hx - 6, hy - 6), (hx + 6, hy - 8), 1)
        return
    if style == "part":
        pygame.draw.ellipse(surf, c, (hx - 8, hy - 9, 16, 11))
        pygame.draw.line(surf, darken(c, 0.4), (hx - 1, hy - 9), (hx - 1, hy - 2), 1)
        return
    pygame.draw.ellipse(surf, c, (hx - 8, hy - 9, 16, 10))


def draw_accessory(surf, hx, hy, bx, by, acc, shirt):
    if acc == "glasses":
        pygame.draw.circle(surf, INK, (hx - 3, hy), 3, 1)
        pygame.draw.circle(surf, INK, (hx + 3, hy), 3, 1)
        pygame.draw.line(surf, INK, (hx - 1, hy), (hx + 1, hy), 1)
    elif acc == "tie":
        pygame.draw.polygon(surf, (120, 24, 28), [(bx, by - 6), (bx - 3, by + 8), (bx, by + 12), (bx + 3, by + 8)])
    elif acc == "mug":
        pygame.draw.rect(surf, (220, 220, 220), (bx + 8, by - 2, 6, 7))
        pygame.draw.arc(surf, (200, 200, 200), (bx + 12, by - 1, 5, 5), 4.7, 1.5, 1)
    elif acc == "clipboard":
        pygame.draw.rect(surf, (210, 196, 150), (bx - 14, by, 8, 11))
        pygame.draw.rect(surf, STAMP_RED, (bx - 12, by + 1, 4, 2))
    elif acc == "badge":
        pygame.draw.rect(surf, (40, 70, 140), (bx + 5, by - 8, 6, 8))
        pygame.draw.rect(surf, (220, 180, 60), (bx + 6, by - 7, 4, 3))
    elif acc == "headphones":
        pygame.draw.arc(surf, (30, 30, 30), (hx - 9, hy - 8, 18, 14), 3.3, 6.1, 2)
        pygame.draw.rect(surf, (30, 30, 30), (hx - 10, hy - 2, 4, 6))
        pygame.draw.rect(surf, (30, 30, 30), (hx + 6, hy - 2, 4, 6))
    elif acc == "pencil":
        pygame.draw.line(surf, (80, 50, 20), (bx + 8, by - 8), (bx + 12, by + 4), 2)


def draw_person(surf, px, py, appearance, visitor=False, facing=0, bob=0):
    """Feet at (px, py)."""
    py = py + int(bob)
    pygame.draw.ellipse(surf, (18, 16, 14), (px - 11, py - 5, 22, 8))
    pres = appearance.get("presentation", "neutral")
    body = (62, 88, 132) if visitor else appearance["shirt"]
    skin = (236, 204, 176) if visitor else appearance["skin"]
    if visitor:
        tw = 18
    elif pres == "masculine":
        tw = 18
    elif pres == "feminine":
        tw = 14
    else:
        tw = 16
    # legs
    pygame.draw.rect(surf, darken(body, 0.5), (px - 6, py - 13, 5, 11))
    pygame.draw.rect(surf, darken(body, 0.5), (px + 1, py - 13, 5, 11))
    pygame.draw.rect(surf, (30, 28, 26), (px - 6, py - 4, 5, 3))
    pygame.draw.rect(surf, (30, 28, 26), (px + 1, py - 4, 5, 3))
    # skirt / coat hem
    if not visitor and pres == "feminine":
        pygame.draw.polygon(
            surf,
            darken(body, 0.85),
            [(px - tw // 2 - 2, py - 14), (px + tw // 2 + 2, py - 14), (px + tw // 2 + 5, py - 6), (px - tw // 2 - 5, py - 6)],
        )
    # torso
    torso = pygame.Rect(px - tw // 2, py - 28, tw, 16)
    pygame.draw.rect(surf, body, torso, border_radius=4)
    pygame.draw.rect(surf, (20, 16, 14), torso, 1, border_radius=4)
    # head + outline
    pygame.draw.circle(surf, (20, 16, 14), (px, py - 34), 9)
    pygame.draw.circle(surf, skin, (px, py - 34), 8)
    pygame.draw.circle(surf, (30, 24, 20), (px - 3, py - 34), 1)
    pygame.draw.circle(surf, (30, 24, 20), (px + 3, py - 34), 1)
    draw_hair(surf, px, py - 34, appearance.get("hair_style", "short"), appearance.get("hair_color", (40, 30, 20)))
    if visitor:
        pygame.draw.line(surf, (210, 210, 214), (px, py - 28), (px, py - 20), 1)
        pygame.draw.rect(surf, STAMP_RED, (px - 5, py - 22, 10, 11), border_radius=1)
        pygame.draw.rect(surf, (250, 230, 90), (px - 3, py - 20, 6, 4))
        pygame.draw.rect(surf, (20, 16, 14), (px - tw // 2 - 1, py - 29, tw + 2, 18), 1, border_radius=4)
    else:
        draw_accessory(surf, px, py - 34, px, py - 22, appearance.get("accessory", "none"), body)


def draw_prop(surf, prop, cam, defn):
    x, y = screen_xy(prop["x"] * TILE, prop["y"] * TILE, cam)
    t = prop["type"]
    if t == "plant":
        pygame.draw.rect(surf, (120, 72, 40), (x + 10, y + 18, 12, 10))
        pygame.draw.circle(surf, (46, 110, 62), (x + 16, y + 14), 10)
        pygame.draw.circle(surf, (36, 90, 50), (x + 12, y + 10), 6)
    elif t == "cooler":
        pygame.draw.rect(surf, (200, 210, 214), (x + 6, y + 4, 20, 26), border_radius=2)
        pygame.draw.rect(surf, (160, 200, 210), (x + 10, y + 8, 12, 10))
        pygame.draw.rect(surf, (80, 90, 96), (x + 14, y + 20, 4, 6))
    elif t == "copier":
        pygame.draw.rect(surf, (70, 74, 80), (x + 2, y + 6, 28, 22), border_radius=2)
        pygame.draw.rect(surf, (40, 44, 48), (x + 6, y + 10, 20, 8))
        pygame.draw.rect(surf, (180, 40, 40), (x + 8, y + 12, 4, 3))
        pygame.draw.rect(surf, PAPER, (x + 16, y + 20, 10, 6))
    elif t == "cabinet":
        pygame.draw.rect(surf, (92, 74, 52), (x + 4, y + 2, 24, 28))
        pygame.draw.line(surf, (60, 46, 32), (x + 4, y + 16), (x + 28, y + 16), 2)
        pygame.draw.circle(surf, BRASS, (x + 16, y + 10), 2)
        pygame.draw.circle(surf, BRASS, (x + 16, y + 22), 2)
    elif t == "boxes":
        pygame.draw.rect(surf, (166, 124, 72), (x + 4, y + 12, 18, 14))
        pygame.draw.rect(surf, (150, 110, 64), (x + 10, y + 6, 16, 12))
    elif t == "shelves":
        pygame.draw.rect(surf, (90, 70, 50), (x + 2, y + 2, 28, 28), 2)
        for i in range(3):
            pygame.draw.line(surf, (90, 70, 50), (x + 2, y + 8 + i * 8), (x + 30, y + 8 + i * 8), 2)
    elif t == "counter" or t == "window_counter":
        pygame.draw.rect(surf, (150, 130, 100), (x + 0, y + 8, 32, 16))
        pygame.draw.rect(surf, (90, 70, 50), (x + 0, y + 8, 32, 4))
        if t == "window_counter":
            blit_text(surf, pygame.font.SysFont("consolas", 10), "WNDW", (x + 4, y + 14), INK)
    elif t == "whiteboard":
        pygame.draw.rect(surf, (230, 232, 236), (x + 2, y + 4, 28, 22))
        pygame.draw.rect(surf, (80, 80, 90), (x + 2, y + 4, 28, 22), 2)
        pygame.draw.line(surf, (80, 110, 170), (x + 6, y + 10), (x + 24, y + 16), 1)
    elif t == "table":
        pygame.draw.rect(surf, (140, 118, 88), (x + 2, y + 8, 28, 16), border_radius=2)
    elif t == "vault":
        pygame.draw.rect(surf, (70, 74, 78), (x + 2, y + 2, 28, 28), border_radius=3)
        pygame.draw.circle(surf, BRASS, (x + 16, y + 16), 7, 2)
        pygame.draw.circle(surf, BRASS, (x + 16, y + 16), 2)
    elif t == "portrait":
        pygame.draw.rect(surf, (90, 60, 30), (x + 8, y + 4, 16, 20))
        pygame.draw.rect(surf, (180, 170, 150), (x + 10, y + 6, 12, 16))
    elif t == "directory":
        pygame.draw.rect(surf, (62, 52, 40), (x + 6, y + 2, 20, 28))
        pygame.draw.rect(surf, PAPER, (x + 8, y + 6, 16, 20))
        for i in range(4):
            pygame.draw.line(surf, INK, (x + 10, y + 10 + i * 4), (x + 22, y + 10 + i * 4), 1)
    elif t == "chairs":
        pygame.draw.rect(surf, darken(defn["accent"], 0.8), (x + 4, y + 10, 10, 10), border_radius=2)
        pygame.draw.rect(surf, darken(defn["accent"], 0.8), (x + 16, y + 10, 10, 10), border_radius=2)
    elif t == "stanchion":
        pygame.draw.circle(surf, BRASS, (x + 16, y + 22), 4)
        pygame.draw.line(surf, STAMP_RED, (x + 16, y + 8), (x + 16, y + 22), 2)
    elif t == "memo":
        pygame.draw.rect(surf, (90, 70, 48), (x + 10, y + 4, 12, 24))
        pygame.draw.rect(surf, PAPER, (x + 12, y + 6, 8, 18))
        pygame.draw.line(surf, STAMP_RED, (x + 14, y + 10), (x + 18, y + 10), 1)


def draw_desk(surf, desk, cam, defn):
    x, y = screen_xy(desk["x"] * TILE, desk["y"] * TILE, cam)
    variant = desk.get("variant", 0)
    woods = [(142, 108, 70), (168, 132, 88), (96, 86, 78), (120, 78, 52)]
    wood = woods[variant % 4]
    pygame.draw.rect(surf, darken(wood, 0.45), (x + 2, y + 8, 44, 22), border_radius=2)
    pygame.draw.rect(surf, wood, (x + 1, y + 2, 44, 24), border_radius=2)
    pygame.draw.rect(surf, darken(wood, 0.7), (x + 1, y + 2, 44, 24), 1, border_radius=2)
    pygame.draw.rect(surf, PAPER, (x + 5, y + 7, 14, 10))
    pygame.draw.rect(surf, STAMP_RED, (x + 7, y + 9, 7, 3))
    if variant == 1:
        pygame.draw.rect(surf, (48, 50, 56), (x + 24, y + 7, 16, 11), border_radius=2)
        pygame.draw.rect(surf, (90, 160, 150), (x + 26, y + 9, 12, 6))
    elif variant == 2:
        pygame.draw.rect(surf, (70, 74, 80), (x + 26, y + 6, 14, 14), border_radius=1)
        pygame.draw.rect(surf, (200, 80, 70), (x + 28, y + 8, 10, 3))
        pygame.draw.rect(surf, PAPER, (x + 28, y + 12, 10, 5))
    elif variant == 3:
        pygame.draw.rect(surf, (40, 44, 48), (x + 28, y + 5, 11, 12), border_radius=1)
        pygame.draw.rect(surf, (80, 150, 140), (x + 30, y + 7, 7, 6))
        pygame.draw.circle(surf, (46, 110, 62), (x + 16, y + 16), 4)
    else:
        pygame.draw.rect(surf, (40, 44, 48), (x + 26, y + 5, 13, 12), border_radius=1)
        pygame.draw.rect(surf, (70, 160, 150), (x + 28, y + 7, 9, 6))


def draw_world(surf, world, floor_index, player, cam, fonts: Fonts):
    floor = world["floors"][floor_index - 1]
    defn = floor["def"]
    grid = floor["grid"]

    surf.fill(defn["corridor"])

    # tiles (+1 overlap hides residual round() gaps between neighbors)
    for y in range(MAP_H):
        for x in range(MAP_W):
            t = grid[y][x]["t"]
            px, py = screen_xy(x * TILE, y * TILE, cam)
            if t == "wall":
                continue
            if t == "elevator":
                pygame.draw.rect(surf, (42, 40, 38), (px, py, TILE + 1, TILE + 1))
                continue
            if t == "door":
                pygame.draw.rect(surf, lighten(defn["corridor"], 0.08), (px, py, TILE + 1, TILE + 1))
                continue
            if t == "corridor":
                pygame.draw.rect(surf, defn["corridor"], (px, py, TILE + 1, TILE + 1))
                if y == 15:
                    pygame.draw.rect(surf, darken(defn["accent"], 0.55), (px, py + 13, TILE + 1, 5))
                continue
            pygame.draw.rect(surf, defn["carpet"], (px, py, TILE + 1, TILE + 1))
            if ((x * 7 + y * 3) % 5) == 0:
                pygame.draw.rect(surf, defn["carpet_alt"], (px + 9, py + 11, 4, 3))

    # painted floor number in lobby
    num = fonts.floor_paint.render(str(floor_index), True, defn["accent"])
    num.set_alpha(40)
    nx, ny = screen_xy(9 * TILE, 12 * TILE, cam)
    surf.blit(num, (nx, ny))

    # elevator cabin
    ex, ey = screen_xy(floor["elevator"]["tx"] * TILE, floor["elevator"]["ty"] * TILE, cam)
    ew = floor["elevator"]["tw"] * TILE
    eh = floor["elevator"]["th"] * TILE
    pygame.draw.rect(surf, (32, 30, 28), (ex - 2, ey - 2, ew + 4, eh + 4))
    pygame.draw.rect(surf, (58, 56, 52), (ex, ey, ew, eh))
    pygame.draw.rect(surf, BRASS, (ex + 3, ey + 3, ew - 6, eh - 6), 3)
    pygame.draw.line(surf, (90, 86, 78), (ex + ew // 2, ey + 8), (ex + ew // 2, ey + eh - 8), 3)
    pygame.draw.rect(surf, (20, 18, 16), (ex + 8, ey + 10, ew - 16, 16))
    blit_text(surf, fonts.tiny, f"FL {floor_index}", (ex + ew // 2, ey + 18), BRASS, center=True)

    # walls as solid partitions (north highlight only — no stacked-lip stripes)
    wall = defn["trim"]
    lip = lighten(defn["wall"], 0.18)
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x]["t"] != "wall":
                continue
            px, py = screen_xy(x * TILE, y * TILE, cam)
            pygame.draw.rect(surf, wall, (px, py, TILE + 1, TILE + 1))
            if y == 0 or grid[y - 1][x]["t"] != "wall":
                pygame.draw.rect(surf, lip, (px, py, TILE + 1, 5))
            # baseboard where the wall faces open floor
            if y + 1 < MAP_H and grid[y + 1][x]["t"] in ("floor", "corridor", "desk", "door"):
                pygame.draw.rect(surf, darken(wall, 0.65), (px, py + TILE - 5, TILE + 1, 5))

    # doors: jamb + a half-open slab
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x]["t"] != "door":
                continue
            px, py = screen_xy(x * TILE, y * TILE, cam)
            pygame.draw.rect(surf, lighten(defn["corridor"], 0.1), (px, py, TILE + 1, TILE + 1))
            pygame.draw.rect(surf, wall, (px, py, TILE + 1, TILE + 1), 3)
            pygame.draw.rect(surf, darken(defn["wall"], 0.85), (px + 4, py + 3, 10, TILE - 6), border_radius=1)
            pygame.draw.circle(surf, BRASS, (px + 12, py + TILE // 2), 2)

    # desks + cubicle rails
    npc_at = {}
    for npc in world["npcs"]:
        if npc["floor"] == floor_index and npc.get("desk"):
            npc_at[(npc["desk"]["x"], npc["desk"]["y"])] = npc
    for desk in floor["desks"]:
        dx, dy = screen_xy(desk["x"] * TILE, desk["y"] * TILE, cam)
        pygame.draw.rect(surf, darken(defn["trim"], 0.85), (dx - 2, dy - 2, TILE * 2 - 4, 6))
        pygame.draw.rect(surf, darken(defn["trim"], 0.85), (dx - 2, dy - 2, 6, TILE - 4))
        draw_desk(surf, desk, cam, defn)
        npc = npc_at.get((desk["x"], desk["y"]))
        if npc:
            last = npc["name"].split()[-1].upper()
            blit_text(surf, fonts.tiny, last[:10], (dx + 6, dy + TILE - 6), PAPER)
            if npc.get("chain_role"):
                pygame.draw.rect(surf, (210, 80, 70), (dx + 8, dy + 6, 10, 8))
                pygame.draw.rect(surf, PAPER, (dx + 9, dy + 7, 8, 6))

    # props
    for prop in floor["props"]:
        draw_prop(surf, prop, cam, defn)

    # room plaques near the center of each department
    sums = {}
    for y in range(MAP_H):
        for x in range(MAP_W):
            tile = grid[y][x]
            if tile["t"] not in ("floor", "desk") or not tile["dept"]:
                continue
            rec = sums.setdefault(tile["dept"], [0, 0, 0])
            rec[0] += x
            rec[1] += y
            rec[2] += 1
    for dept, (sx, sy, n) in sums.items():
        cx, cy = sx // n, sy // n
        name = next((r["name"] for r in floor["rooms"] if r.get("dept") == dept), dept)
        label = fonts.tiny.render(name.upper(), True, defn["trim"])
        px, py = screen_xy(cx * TILE, cy * TILE, cam)
        pygame.draw.rect(surf, PAPER, (px + 2, py + 2, label.get_width() + 8, 14), border_radius=2)
        pygame.draw.rect(surf, defn["trim"], (px + 2, py + 2, label.get_width() + 8, 14), 1, border_radius=2)
        surf.blit(label, (px + 6, py + 3))

    # y-sorted people
    people = []
    for npc in world["npcs"]:
        if npc["floor"] != floor_index:
            continue
        people.append(("npc", npc["y"], npc))
    people.append(("player", player["y"], player))
    people.sort(key=lambda p: p[1])
    for kind, _y, obj in people:
        px, py = screen_xy(obj["x"] * TILE, obj["y"] * TILE, cam)
        if kind == "player":
            draw_person(surf, px, py, obj["appearance"], visitor=True)
        else:
            if obj.get("out_to_lunch"):
                sign = pygame.Rect(px - 28, py - 22, 56, 16)
                pygame.draw.rect(surf, PAPER, sign)
                pygame.draw.rect(surf, STAMP_RED, sign, 1)
                blit_text(surf, fonts.tiny, "OUT TO LUNCH", (sign.centerx, sign.centery), STAMP_RED, center=True)
                continue
            draw_person(surf, px, py, obj["appearance"], visitor=False)
            dx = obj["x"] - player["x"]
            dy = obj["y"] - player["y"]
            if dx * dx + dy * dy < 3.5:
                name = obj["name"].split()[0]
                img = fonts.tiny.render(name, True, INK)
                tag = img.get_rect()
                tag.midbottom = (px, py - 44)
                pygame.draw.rect(surf, PAPER, tag.inflate(8, 4), border_radius=2)
                surf.blit(img, tag)

    # north windows
    wx, wy = screen_xy(TILE, 2, cam)
    pygame.draw.rect(surf, (40, 70, 90), (wx, wy, (MAP_W - 2) * TILE, 8))
    for x in range(2, MAP_W - 2, 3):
        wx, wy = screen_xy(x * TILE, 3, cam)
        pygame.draw.rect(surf, (170, 200, 214), (wx, wy, TILE + 8, 6))

    return floor


def draw_hud(surf, fonts, world, player, clock_hm, prompt, debug=False):
    w, h = surf.get_size()
    pygame.draw.rect(surf, (48, 40, 32), (0, 0, w, HUD_TOP))
    pygame.draw.rect(surf, MANILA, (0, 0, w, HUD_TOP - 6))
    pygame.draw.line(surf, STAMP_RED, (0, HUD_TOP - 6), (w, HUD_TOP - 6), 3)
    floor = world["floors"][player["floor"] - 1]
    blit_text(surf, fonts.ui_b, "FORM PENDING", (16, 8), INK)
    blit_text(surf, fonts.mono, world["start_doc"]["code"], (16, 30), STAMP_RED)
    hh, mm = clock_hm
    suffix = "AM" if hh < 12 else "PM"
    display = hh % 12
    if display == 0:
        display = 12
    clock_col = INK
    if hh >= 16:
        clock_col = STAMP_RED
    elif hh >= 15:
        clock_col = (120, 40, 28)
    blit_text(surf, fonts.title_sm, f"{display}:{mm:02d} {suffix}", (w // 2, 22), clock_col, center=True)
    # Day bar: 8:00 to 5:00
    bar = pygame.Rect(w // 2 - 90, 42, 180, 6)
    pygame.draw.rect(surf, PAPER_DARK, bar)
    elapsed = max(0, min(1.0, ((hh * 60 + mm) - 8 * 60) / (9 * 60)))
    fill = pygame.Rect(bar.x, bar.y, int(bar.w * elapsed), bar.h)
    pygame.draw.rect(surf, STAMP_RED if hh >= 16 else BRASS, fill)
    pygame.draw.rect(surf, INK, bar, 1)
    blit_text(
        surf,
        fonts.small,
        f"FLOOR {player['floor']}  —  {floor['def']['name'].upper()}",
        (w - 16 - fonts.small.size(f"FLOOR {player['floor']}  —  {floor['def']['name'].upper()}")[0], 10),
        darken(floor["def"]["accent"], 0.7),
    )
    blit_text(surf, fonts.tiny, f"SEED {world['seed']}", (w - 140, 32), (90, 80, 70))

    pygame.draw.rect(surf, (48, 40, 32), (0, h - HUD_BOTTOM, w, HUD_BOTTOM))
    pygame.draw.rect(surf, PAPER, (0, h - HUD_BOTTOM + 4, w, HUD_BOTTOM - 4))
    pygame.draw.line(surf, BRASS, (0, h - HUD_BOTTOM + 4), (w, h - HUD_BOTTOM + 4), 2)

    items = player["inventory"]
    x = 16
    blit_text(surf, fonts.tiny, "IN HAND", (x, h - HUD_BOTTOM + 10), (110, 90, 70))
    blit_text(surf, fonts.tiny, "N  notebook   R  papers   M  mute", (w - 248, h - HUD_BOTTOM + 10), (110, 90, 70))
    show = items[:7]
    box_w = 148 if len(show) > 5 else 190
    for it in show:
        box = pygame.Rect(x, h - HUD_BOTTOM + 26, box_w, 42)
        pygame.draw.rect(surf, PAPER_DARK, box, border_radius=3)
        pygame.draw.rect(surf, INK, box, 1, border_radius=3)
        blit_text(surf, fonts.mono_sm, it["code"][:16], (box.x + 6, box.y + 6), STAMP_RED)
        blit_text(surf, fonts.tiny, it["name"][:22], (box.x + 6, box.y + 22), INK)
        x += box_w + 8
    extra = len(items) - len(show)
    if extra > 0:
        blit_text(surf, fonts.tiny, f"+{extra}", (x, h - HUD_BOTTOM + 38), (110, 90, 70))

    if prompt:
        img = fonts.ui_b.render(prompt, True, PAPER)
        pad = 12
        rect = img.get_rect()
        rect.center = (w // 2, h - HUD_BOTTOM - 22)
        bg = rect.inflate(pad * 2, pad)
        pygame.draw.rect(surf, (36, 30, 24), bg, border_radius=4)
        pygame.draw.rect(surf, BRASS, bg, 1, border_radius=4)
        surf.blit(img, rect)

    if debug:
        lines = [
            f"pos {player['x']:.1f},{player['y']:.1f}  floor {player['floor']}",
            f"npcs {len(world['npcs'])}  chain {len(world['nodes'])}",
            f"attempt {world.get('attempt')}  failed {world.get('generation_failed')}",
        ]
        y = HUD_TOP + 8
        for line in lines:
            blit_text(surf, fonts.mono_sm, line, (12, y), (255, 240, 180))
            y += 16


def draw_dialogue(surf, fonts, npc, pages, page_index):
    w, h = surf.get_size()
    box = pygame.Rect(80, h - 280, w - 160, 188)
    pygame.draw.rect(surf, (40, 32, 24), box.move(4, 4), border_radius=6)
    pygame.draw.rect(surf, PAPER, box, border_radius=6)
    pygame.draw.rect(surf, INK, box, 2, border_radius=6)
    pygame.draw.rect(surf, STAMP_RED, (box.right - 110, box.y + 12, 90, 36), 2, border_radius=2)
    blit_text(surf, fonts.tiny, "OFFICIAL", (box.right - 92, box.y + 22), STAMP_RED)

    blit_text(surf, fonts.ui_b, npc["name"].upper(), (box.x + 20, box.y + 14), INK)
    blit_text(
        surf,
        fonts.small,
        f"{npc['role']}  ·  {npc['department']}  ·  Floor {npc['floor']}",
        (box.x + 20, box.y + 38),
        (90, 74, 58),
    )
    pygame.draw.line(surf, PAPER_DARK, (box.x + 20, box.y + 60), (box.right - 20, box.y + 60), 2)

    text = pages[page_index]
    y = box.y + 72
    for line in wrap_text(fonts.ui, text, box.width - 50):
        blit_text(surf, fonts.ui, line, (box.x + 22, y), INK)
        y += 22
    blit_text(
        surf,
        fonts.tiny,
        f"{page_index + 1}/{len(pages)}    E / SPACE  continue",
        (box.right - 210, box.bottom - 22),
        (110, 90, 70),
    )


def draw_elevator_panel(surf, fonts, current, highlight):
    w, h = surf.get_size()
    box = pygame.Rect(w // 2 - 160, h // 2 - 210, 320, 420)
    pygame.draw.rect(surf, (30, 24, 18), box.move(5, 5), border_radius=8)
    pygame.draw.rect(surf, (72, 64, 52), box, border_radius=8)
    pygame.draw.rect(surf, BRASS, box, 4, border_radius=8)
    blit_text(surf, fonts.ui_b, "ELEVATOR", (box.centerx, box.y + 24), PAPER, center=True)
    blit_text(surf, fonts.tiny, "SELECT FLOOR", (box.centerx, box.y + 48), BRASS, center=True)
    for i in range(FLOOR_COUNT, 0, -1):
        r = pygame.Rect(box.x + 70, box.y + 70 + (FLOOR_COUNT - i) * 50, 180, 42)
        on = i == current
        col = BRASS if on else (40, 36, 30)
        pygame.draw.rect(surf, col, r, border_radius=4)
        pygame.draw.rect(surf, PAPER if i == highlight else (120, 110, 90), r, 2, border_radius=4)
        label = f"{i}   {['', 'INTAKE', 'RECORDS', 'PERMITS', 'PERSONNEL', 'COMPLIANCE', 'EXECUTIVE'][i]}"
        blit_text(surf, fonts.ui_b, label, (r.centerx, r.centery), PAPER if not on else INK, center=True)
    blit_text(surf, fonts.tiny, "1–6  select    E / ENTER  go    ESC  close", (box.centerx, box.bottom - 22), PAPER, center=True)


def draw_directory(surf, fonts, world, floor_index):
    w, h = surf.get_size()
    box = pygame.Rect(w // 2 - 260, 90, 520, 500)
    pygame.draw.rect(surf, (40, 32, 24), box.move(4, 4), border_radius=4)
    pygame.draw.rect(surf, PAPER, box, border_radius=4)
    pygame.draw.rect(surf, INK, box, 2, border_radius=4)
    blit_text(surf, fonts.ui_b, f"FLOOR {floor_index} DIRECTORY", (box.centerx, box.y + 24), INK, center=True)
    blit_text(surf, fonts.small, "Municipal Building — You Are Here", (box.centerx, box.y + 50), (90, 74, 58), center=True)
    depts = [d for d in world["departments"] if d["floor"] == floor_index]
    y = box.y + 90
    for d in depts:
        pygame.draw.rect(surf, PAPER_DARK, (box.x + 40, y, box.width - 80, 36), border_radius=2)
        blit_text(surf, fonts.ui, d["name"], (box.x + 56, y + 8), INK)
        y += 44
    y += 8
    blit_text(surf, fonts.tiny, "Other floors (building index)", (box.x + 40, y), (90, 74, 58))
    y += 22
    for i, defn in enumerate(world["floors"]):
        mark = "  ←" if defn["index"] == floor_index else ""
        blit_text(surf, fonts.small, f"Floor {defn['index']}  {defn['def']['name']}{mark}", (box.x + 56, y), INK)
        y += 22
    blit_text(surf, fonts.tiny, "E / ESC  close", (box.centerx, box.bottom - 24), (110, 90, 70), center=True)


def draw_document(surf, fonts, world):
    w, h = surf.get_size()
    box = pygame.Rect(w // 2 - 280, 70, 560, 540)
    pygame.draw.rect(surf, (40, 32, 24), box.move(5, 5))
    pygame.draw.rect(surf, PAPER, box)
    pygame.draw.rect(surf, INK, box, 2)
    blit_text(surf, fonts.tiny, "CITY OF ORDINARY AFFAIRS  ·  VISITOR TRANSMITTAL", (box.x + 24, box.y + 18), (110, 90, 70))
    blit_text(surf, fonts.ui_b, world["start_doc"]["code"], (box.x + 24, box.y + 44), STAMP_RED)
    blit_text(surf, fonts.ui, world["start_doc"]["name"], (box.x + 24, box.y + 72), INK)
    pygame.draw.line(surf, PAPER_DARK, (box.x + 24, box.y + 104), (box.right - 24, box.y + 104), 2)
    body = (
        f"The bearer is instructed to file the attached document before 5:00 PM. "
        f"Failure to complete ordinary processing may result in the following: "
        f"{world['catastrophe']['line']}."
    )
    y = box.y + 124
    for line in wrap_text(fonts.ui, body, box.width - 60):
        blit_text(surf, fonts.ui, line, (box.x + 28, y), INK)
        y += 24
    y += 12
    for line in wrap_text(fonts.small, world["catastrophe"]["detail"], box.width - 60):
        blit_text(surf, fonts.small, line, (box.x + 28, y), (90, 74, 58))
        y += 20
    stamp = pygame.Rect(box.right - 180, box.bottom - 140, 150, 70)
    pygame.draw.rect(surf, STAMP_RED, stamp, 3, border_radius=6)
    blit_text(surf, fonts.stamp, "FILE BY", (stamp.centerx, stamp.y + 22), STAMP_RED, center=True)
    blit_text(surf, fonts.stamp, "5:00 PM", (stamp.centerx, stamp.y + 48), STAMP_RED, center=True)
    blit_text(surf, fonts.tiny, "R / ESC  fold away", (box.centerx, box.bottom - 24), (110, 90, 70), center=True)


def draw_title(surf, fonts, seed_text, pulse):
    w, h = surf.get_size()
    surf.fill((48, 42, 34))
    # paper sheet
    sheet = pygame.Rect(w // 2 - 340, 50, 680, 620)
    pygame.draw.rect(surf, (30, 24, 18), sheet.move(8, 8))
    pygame.draw.rect(surf, PAPER, sheet)
    pygame.draw.rect(surf, INK, sheet, 2)
    for i in range(18):
        pygame.draw.line(surf, (220, 210, 190), (sheet.x + 30, sheet.y + 160 + i * 22), (sheet.right - 30, sheet.y + 160 + i * 22), 1)

    blit_text(surf, fonts.tiny, "MUNICIPAL BUILDING  ·  ONE DAY ONLY", (sheet.centerx, sheet.y + 28), (110, 90, 70), center=True)
    blit_text(surf, fonts.huge, "FORM", (sheet.centerx, sheet.y + 88), INK, center=True)
    blit_text(surf, fonts.huge, "PENDING", (sheet.centerx, sheet.y + 158), INK, center=True)

    stamp = pygame.Rect(sheet.centerx - 130, sheet.y + 210, 260, 64)
    pygame.draw.rect(surf, STAMP_RED, stamp, 3, border_radius=8)
    blit_text(surf, fonts.stamp, "FILE BY 5:00 PM", (stamp.centerx, stamp.centery), STAMP_RED, center=True)

    blit_text(
        surf,
        fonts.small,
        "A seemingly trivial document. A six-story building. Closing time is 5:00.",
        (sheet.centerx, sheet.y + 300),
        (90, 74, 58),
        center=True,
    )

    field = pygame.Rect(sheet.centerx - 160, sheet.y + 360, 320, 40)
    pygame.draw.rect(surf, (250, 246, 236), field)
    pygame.draw.rect(surf, INK, field, 1)
    shown = seed_text if seed_text else "random seed"
    col = INK if seed_text else (160, 150, 140)
    blit_text(surf, fonts.mono, shown, (field.x + 12, field.y + 10), col)
    blit_text(surf, fonts.tiny, "SEED (optional)", (field.x, field.y - 18), (110, 90, 70))

    blit_text(surf, fonts.ui_b, "ENTER  begin shift", (sheet.centerx, sheet.y + 430), INK, center=True)
    blit_text(
        surf,
        fonts.small,
        "WASD move   E interact   N notebook   R papers   1–6 elevator   M mute",
        (sheet.centerx, sheet.y + 470),
        (90, 74, 58),
        center=True,
    )
    blit_text(
        surf,
        fonts.tiny,
        "There is no quest log. If it matters, write it down.",
        (sheet.centerx, sheet.y + 510),
        (120, 100, 80),
        center=True,
    )
    blit_text(surf, fonts.tiny, "ESC  quit", (sheet.centerx, sheet.bottom - 28), (110, 90, 70), center=True)


def draw_toast(surf, fonts, toast):
    if not toast:
        return
    w, _h = surf.get_size()
    img = fonts.ui_b.render(toast["text"], True, PAPER)
    rect = img.get_rect(center=(w // 2, HUD_TOP + 36))
    bg = rect.inflate(24, 14)
    pygame.draw.rect(surf, (36, 30, 24), bg, border_radius=4)
    pygame.draw.rect(surf, BRASS, bg, 1, border_radius=4)
    surf.blit(img, rect)


def draw_fade(surf, amount):
    if amount <= 0:
        return
    overlay = pygame.Surface(surf.get_size())
    overlay.fill((8, 8, 8))
    overlay.set_alpha(int(min(1.0, amount) * 255))
    surf.blit(overlay, (0, 0))


def draw_notice(surf, fonts, title, body, footer="E / ENTER  continue"):
    w, h = surf.get_size()
    box = pygame.Rect(w // 2 - 300, h // 2 - 160, 600, 320)
    pygame.draw.rect(surf, (30, 24, 18), box.move(6, 6))
    pygame.draw.rect(surf, PAPER, box)
    pygame.draw.rect(surf, STAMP_RED, box, 4)
    blit_text(surf, fonts.title_sm, title, (box.centerx, box.y + 40), STAMP_RED, center=True)
    y = box.y + 100
    for line in wrap_text(fonts.ui, body, box.width - 80):
        blit_text(surf, fonts.ui, line, (box.centerx, y), INK, center=True)
        y += 26
    blit_text(surf, fonts.tiny, footer, (box.centerx, box.bottom - 36), (110, 90, 70), center=True)


def draw_late_day(surf, hour, minute):
    if hour < 16:
        return
    past = (hour - 16) * 60 + minute
    alpha = min(90, 28 + past // 2)
    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill((80, 20, 12, alpha))
    surf.blit(overlay, (0, 0))
    if hour >= 16:
        w, _h = surf.get_size()
        msg = "BUILDING CLOSES AT 5:00 PM"
        img = pygame.font.SysFont("segoeui", 14, bold=True).render(msg, True, PAPER)
        rect = img.get_rect(center=(w // 2, HUD_TOP + 14))
        pygame.draw.rect(surf, STAMP_RED, rect.inflate(16, 8), border_radius=2)
        surf.blit(img, rect)


def draw_notebook(surf, fonts, notebook, blink):
    w, h = surf.get_size()
    pad = pygame.Rect(w // 2 - 320, 70, 640, h - 160)
    pygame.draw.rect(surf, (40, 32, 24), pad.move(6, 6))
    pygame.draw.rect(surf, (232, 220, 168), pad)
    pygame.draw.rect(surf, (90, 60, 40), pad, 3)
    pygame.draw.rect(surf, STAMP_RED, (pad.x, pad.y, 18, pad.h))
    blit_text(surf, fonts.tiny, "GOVERNMENT ISSUE  ·  PERSONAL NOTES  ·  NOT A FILE", (pad.centerx, pad.y + 14), (90, 74, 58), center=True)
    blit_text(surf, fonts.ui_b, "NOTEBOOK", (pad.centerx, pad.y + 34), INK, center=True)
    blit_text(
        surf,
        fonts.tiny,
        "Nothing is copied here for you.  ESC  close",
        (pad.centerx, pad.bottom - 18),
        (90, 74, 58),
        center=True,
    )

    inner = pygame.Rect(pad.x + 36, pad.y + 58, pad.w - 56, pad.h - 90)
    pygame.draw.rect(surf, (244, 236, 196), inner)
    visible = max(1, inner.h // 22)
    notebook.ensure_scroll(visible)
    lines = notebook.lines()
    li, col, _s, _e = notebook._cursor_line()
    y = inner.y + 4
    for i in range(notebook.scroll, min(len(lines), notebook.scroll + visible)):
        line = lines[i]
        pygame.draw.line(surf, (210, 190, 140), (inner.x + 8, y + 18), (inner.right - 8, y + 18), 1)
        shown = line[:72]
        blit_text(surf, fonts.mono_sm, shown, (inner.x + 10, y + 2), INK)
        if i == li and blink:
            prefix = line[:col][:72]
            cx = inner.x + 10 + fonts.mono_sm.size(prefix)[0]
            pygame.draw.rect(surf, INK, (cx, y + 2, 2, 16))
        y += 22


def _center_card(surf, fonts, title, body, footer=None, stamp=None):
    w, h = surf.get_size()
    box = pygame.Rect(w // 2 - 320, h // 2 - 170, 640, 340)
    pygame.draw.rect(surf, (20, 16, 12), box.move(8, 8))
    pygame.draw.rect(surf, PAPER, box)
    pygame.draw.rect(surf, INK, box, 2)
    blit_text(surf, fonts.title_sm, title, (box.centerx, box.y + 40), STAMP_RED, center=True)
    y = box.y + 100
    for line in wrap_text(fonts.ui, body, box.width - 80):
        blit_text(surf, fonts.ui, line, (box.centerx, y), INK, center=True)
        y += 26
    if stamp:
        r = pygame.Rect(box.centerx - 90, box.bottom - 110, 180, 56)
        pygame.draw.rect(surf, STAMP_RED, r, 3, border_radius=6)
        blit_text(surf, fonts.stamp, stamp, (r.centerx, r.centery), STAMP_RED, center=True)
    if footer:
        blit_text(surf, fonts.tiny, footer, (box.centerx, box.bottom - 28), (110, 90, 70), center=True)


def draw_catastrophe(surf, fonts, catastrophe, t):
    w, h = surf.get_size()
    cid = catastrophe["id"]
    if cid == "nuclear":
        flash = int(180 + 70 * abs((t * 8) % 2 - 1))
        surf.fill((flash, flash, flash - 20))
        pygame.draw.circle(surf, (40, 40, 36), (w // 2, h // 2 + 80), 90)
        pygame.draw.ellipse(surf, (60, 56, 48), (w // 2 - 140, h // 2 - 40, 280, 80))
        pygame.draw.circle(surf, (80, 70, 50), (w // 2, h // 2 - 70), 70)
    elif cid == "moon":
        surf.fill((12, 14, 28))
        y = int(120 + t * 80)
        pygame.draw.circle(surf, (220, 220, 200), (w // 2, y), 70)
        pygame.draw.circle(surf, (180, 180, 160), (w // 2 - 20, y - 10), 18)
        blit_text(surf, fonts.small, "REPOSSESSED", (w // 2, y), STAMP_RED, center=True)
    elif cid == "tuesday":
        surf.fill((40, 36, 30))
        cal = pygame.Rect(w // 2 - 160, h // 2 - 120, 320, 240)
        pygame.draw.rect(surf, PAPER, cal)
        blit_text(surf, fonts.ui_b, "THIS WEEK", (cal.centerx, cal.y + 24), INK, center=True)
        days = ["MON", "TUE", "WED", "THU", "FRI"]
        for i, d in enumerate(days):
            r = pygame.Rect(cal.x + 20 + (i % 5) * 56, cal.y + 70, 50, 50)
            pygame.draw.rect(surf, PAPER_DARK, r)
            col = STAMP_RED if d == "TUE" else INK
            blit_text(surf, fonts.small, d, (r.centerx, r.centery), col, center=True)
        pygame.draw.line(surf, STAMP_RED, (cal.x + 70, cal.y + 70), (cal.x + 130, cal.y + 130), 4)
        blit_text(surf, fonts.stamp, "REVOKED", (cal.centerx, cal.bottom - 40), STAMP_RED, center=True)
    elif cid == "temporal":
        surf.fill((24, 20, 28))
        blit_text(surf, fonts.huge, "8:00", (w // 2 - 80, h // 2 - 40), PAPER, center=True)
        blit_text(surf, fonts.huge, "5:00", (w // 2 + 90, h // 2 + 30), STAMP_RED, center=True)
        blit_text(surf, fonts.ui, "already / still / not yet", (w // 2, h // 2 + 100), BRASS, center=True)
    elif cid == "parking":
        surf.fill((50, 50, 48))
        pygame.draw.rect(surf, (80, 80, 78), (w // 2 - 200, h // 2 - 40, 400, 160))
        for i in range(6):
            pygame.draw.line(surf, (220, 200, 80), (w // 2 - 180 + i * 64, h // 2 - 30), (w // 2 - 180 + i * 64, h // 2 + 110), 3)
        blit_text(surf, fonts.stamp, "PERMIT PARKING ONLY", (w // 2, h // 2 - 80), PAPER, center=True)
    elif cid == "vowels":
        surf.fill(PAPER)
        blit_text(surf, fonts.huge, "TH  LTT R  IS G N", (w // 2, h // 2), INK, center=True)
        blit_text(surf, fonts.stamp, "E  RECALLED", (w // 2, h // 2 + 80), STAMP_RED, center=True)
    elif cid == "elevator":
        surf.fill((20, 20, 22))
        pygame.draw.rect(surf, (50, 46, 40), (w // 2 - 60, 40, 120, h - 80), 4)
        cab_y = int(80 + min(h - 200, t * 140))
        pygame.draw.rect(surf, (70, 66, 58), (w // 2 - 50, cab_y, 100, 80))
        blit_text(surf, fonts.tiny, "DECORATIVE", (w // 2, cab_y + 40), BRASS, center=True)
    elif cid == "coffee":
        surf.fill((36, 28, 22))
        pygame.draw.rect(surf, (80, 50, 30), (w // 2 - 40, h // 2 - 20, 80, 90), border_radius=8)
        pygame.draw.circle(surf, (40, 24, 16), (w // 2, h // 2 + 10), 28)
        blit_text(surf, fonts.stamp, "RECALL", (w // 2, h // 2 + 120), STAMP_RED, center=True)
    elif cid == "sky":
        surf.fill((180, 200, 214))
        for i in range(8):
            pygame.draw.rect(surf, (220, 220, 214), (80 + i * 140, 40, 120, 40))
            pygame.draw.rect(surf, (160, 160, 150), (80 + i * 140, 40, 120, 40), 2)
        blit_text(surf, fonts.ui, "fluorescent inventory, rolling install", (w // 2, h // 2 + 40), INK, center=True)
    elif cid == "names":
        surf.fill((30, 30, 32))
        blit_text(surf, fonts.huge, "CASE 000-00", (w // 2, h // 2), PAPER, center=True)
        blit_text(surf, fonts.small, "please answer only when called by number", (w // 2, h // 2 + 70), BRASS, center=True)
    elif cid == "ocean":
        surf.fill((20, 40, 70))
        recede = int(t * 40)
        pygame.draw.rect(surf, (180, 170, 140), (0, h // 2 + recede, w, h))
        blit_text(surf, fonts.ui, "boxes in transit", (w // 2, h // 2 - 40), PAPER, center=True)
    elif cid == "weekend":
        surf.fill(PAPER)
        blit_text(surf, fonts.huge, "SAT/SUN", (w // 2, h // 2 - 20), INK, center=True)
        blit_text(surf, fonts.stamp, "UNPAID  ·  MANDATORY", (w // 2, h // 2 + 70), STAMP_RED, center=True)
    elif cid == "bees":
        surf.fill((40, 50, 30))
        blit_text(surf, fonts.huge, "FURLOUGH", (w // 2, h // 2), PAPER, center=True)
        blit_text(surf, fonts.small, "pollination pending agricultural review", (w // 2, h // 2 + 70), BRASS, center=True)
    elif cid == "floor":
        surf.fill((48, 42, 34))
        blit_text(surf, fonts.huge, "4", (w // 2, h // 2 - 20), (80, 70, 60), center=True)
        blit_text(surf, fonts.stamp, "NEVER ADOPTED", (w // 2, h // 2 + 70), STAMP_RED, center=True)
    elif cid == "newts":
        surf.fill((30, 40, 32))
        blit_text(surf, fonts.huge, "·", (w // 2, h // 2 - 40), (180, 200, 120), center=True)
        pygame.draw.line(surf, STAMP_RED, (w // 2 - 80, h // 2 - 80), (w // 2 + 80, h // 2 + 20), 6)
        blit_text(surf, fonts.stamp, "DISCONTINUED", (w // 2, h // 2 + 80), STAMP_RED, center=True)
    elif cid == "please":
        surf.fill(PAPER)
        blit_text(surf, fonts.huge, "PLEASE", (w // 2, h // 2 - 20), (200, 190, 170), center=True)
        pygame.draw.line(surf, STAMP_RED, (w // 2 - 160, h // 2 - 10), (w // 2 + 160, h // 2 - 10), 6)
        blit_text(surf, fonts.stamp, "UNBUDGETED", (w // 2, h // 2 + 70), STAMP_RED, center=True)
    elif cid == "pencils":
        surf.fill((36, 32, 28))
        pygame.draw.line(surf, (220, 180, 80), (w // 2 - 20, h // 2 - 100), (w // 2 + 40, h // 2 + 80), 8)
        pygame.draw.polygon(surf, (40, 40, 40), [(w // 2 + 40, h // 2 + 80), (w // 2 + 55, h // 2 + 100), (w // 2 + 28, h // 2 + 92)])
        blit_text(surf, fonts.stamp, "CONTROLLED", (w // 2, h // 2 + 140), STAMP_RED, center=True)
    elif cid == "clocks":
        surf.fill((24, 22, 30))
        blit_text(surf, fonts.huge, "7:00", (w // 2 - 100, h // 2), PAPER, center=True)
        blit_text(surf, fonts.huge, "9:00", (w // 2 + 110, h // 2 + 40), STAMP_RED, center=True)
        blit_text(surf, fonts.small, "applied twice", (w // 2, h // 2 + 110), BRASS, center=True)
    else:
        surf.fill((20, 16, 12))
        blit_text(surf, fonts.huge, "—", (w // 2, h // 2), PAPER, center=True)
    blit_text(surf, fonts.tiny, catastrophe["headline"], (w // 2, 36), PAPER, center=True)


def draw_ending(surf, fonts, ending):
    from .ending import current_beat

    beat = current_beat(ending)
    cat = ending["catastrophe"]
    footer = "ENTER  another shift     ESC  title" if ending.get("waiting") else ""
    if ending["kind"] == "success":
        surf.fill((48, 42, 34))
        if beat == "stamp":
            _center_card(surf, fonts, "RECEIVED", ending["doc_code"], stamp="FILED")
        elif beat == "clerk":
            _center_card(
                surf,
                fonts,
                "FILED",
                "The clerk does not look up. A small bell rings in another room. That is all.",
            )
        else:
            _center_card(
                surf,
                fonts,
                "ORDINARY AFFAIRS CONTINUE",
                f"The following will not occur: {cat['line']}. {cat['detail']}",
                footer=footer,
                stamp="FILED",
            )
        return

    if beat == "time":
        surf.fill((16, 14, 12))
        blit_text(surf, fonts.huge, "5:00 PM.", (surf.get_width() // 2, surf.get_height() // 2), PAPER, center=True)
    elif beat == "closed":
        surf.fill((30, 26, 22))
        _center_card(surf, fonts, "CLOSED", "The clerk calmly flips the sign.", stamp="CLOSED")
    elif beat == "beat":
        surf.fill((8, 8, 8))
    elif beat == "event":
        draw_catastrophe(surf, fonts, cat, ending["t"])
    else:
        surf.fill((16, 14, 12))
        _center_card(
            surf,
            fonts,
            cat["headline"],
            f"{ending['doc_code']} WAS NOT PROCESSED. Consequently, {cat['line']}.",
            footer=footer,
        )
