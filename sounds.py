"""Procedural sound effects generated at startup.

No external .wav files are needed; small tones are synthesized with the
standard library and handed to pygame.mixer as raw PCM buffers.
"""

import array
import math

import pygame


class SoundManager:
    SAMPLE_RATE = 22050

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.pre_init(self.SAMPLE_RATE, -16, 1, 512)
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            return
        self._build()

    def _tone(self, freq, duration, volume=0.35, wave="sine"):
        n = max(1, int(self.SAMPLE_RATE * duration))
        amp = int(32767 * max(0.0, min(1.0, volume)))
        samples = array.array("h")
        attack = max(1, int(n * 0.05))
        release = max(1, int(n * 0.35))
        for i in range(n):
            t = i / self.SAMPLE_RATE
            phase = 2 * math.pi * freq * t
            if wave == "square":
                v = 1.0 if math.sin(phase) >= 0 else -1.0
            else:
                v = math.sin(phase)
            if i < attack:
                v *= i / attack
            elif i > n - release:
                v *= max(0.0, (n - i) / release)
            samples.append(int(v * amp))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _build(self):
        try:
            self.sounds["paddle"] = self._tone(440, 0.06, 0.30)
            self.sounds["wall"] = self._tone(320, 0.05, 0.22)
            self.sounds["brick"] = self._tone(660, 0.08, 0.35)
            self.sounds["lose"] = self._tone(180, 0.40, 0.40)
            self.sounds["win"] = self._tone(880, 0.30, 0.35)
            self.sounds["start"] = self._tone(520, 0.15, 0.30)
        except (pygame.error, ValueError):
            self.enabled = False
            self.sounds = {}

    def play(self, name):
        if not self.enabled:
            return
        s = self.sounds.get(name)
        if s is not None:
            try:
                s.play()
            except pygame.error:
                pass
