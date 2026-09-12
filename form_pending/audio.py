"""Tiny procedural WAV blips. No external audio files."""

from __future__ import annotations

import io
import math
import os
import struct
import wave

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None

SR = 22050


def _wav(samples):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        frames = b"".join(struct.pack("<h", max(-32767, min(32767, int(s)))) for s in samples)
        wf.writeframes(frames)
    buf.seek(0)
    return buf


def _beep(freq, ms, vol=0.18, decay=True):
    n = max(1, int(SR * ms / 1000))
    out = []
    for i in range(n):
        env = (1.0 - i / n) if decay else 1.0
        out.append(32767 * vol * env * math.sin(2 * math.pi * freq * i / SR))
    return out


def _noise(ms, vol=0.08):
    n = max(1, int(SR * ms / 1000))
    # Cheap deterministic crunch, not crypto.
    x = 1234567
    out = []
    for i in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        env = 1.0 - i / n
        out.append(((x / 0x7FFFFFFF) * 2 - 1) * 32767 * vol * env)
    return out


class Audio:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        if pygame is None:
            return
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            return
        try:
            pygame.mixer.init(frequency=SR, size=-16, channels=1, buffer=512)
            self.sounds = {
                "click": pygame.mixer.Sound(_wav(_beep(880, 45, 0.12))),
                "paper": pygame.mixer.Sound(_wav(_noise(90, 0.07))),
                "ding": pygame.mixer.Sound(_wav(_beep(1318, 160, 0.16) + _beep(1760, 120, 0.1))),
                "stamp": pygame.mixer.Sound(_wav(_noise(40, 0.2) + _beep(140, 80, 0.18))),
                "step": pygame.mixer.Sound(_wav(_beep(170, 28, 0.04))),
                "warn": pygame.mixer.Sound(_wav(_beep(392, 220, 0.1))),
                "fail": pygame.mixer.Sound(_wav(_beep(98, 400, 0.2))),
            }
            self.enabled = True
        except Exception:
            self.enabled = False

    def play(self, name):
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get(name)
        if snd is not None:
            snd.play()

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted
