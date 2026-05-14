"""Lightweight particle system for visual feedback."""

import math
import random
import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "color", "life", "max_life", "size")

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 5.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = random.randint(25, 45)
        self.max_life = self.life
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.vx *= 0.98
        self.life -= 1

    @property
    def dead(self):
        return self.life <= 0

    def draw(self, surface):
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(255 * ratio)
        d = self.size * 4
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (d // 2, d // 2), self.size)
        surface.blit(s, (self.x - d // 2, self.y - d // 2))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, color, count=18):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
