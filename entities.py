"""Game entities: paddle, ball, brick."""

import math
import random
import pygame

from settings import (
    WIDTH, HEIGHT, WHITE, NEON_CYAN,
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_Y_OFFSET,
    BALL_RADIUS, BALL_SPEED, BALL_MAX_SPEED,
    BRICK_WIDTH, BRICK_HEIGHT, HUD_HEIGHT,
)


def _glow_rect(surface, rect, color, layers=4, radius=6):
    """Soft additive glow around a rectangle."""
    for i in range(layers, 0, -1):
        size = (rect.width + i * 8, rect.height + i * 8)
        glow = pygame.Surface(size, pygame.SRCALPHA)
        alpha = max(0, 50 - i * 10)
        pygame.draw.rect(glow, (*color, alpha), glow.get_rect(), border_radius=radius + i)
        surface.blit(glow, (rect.x - i * 4, rect.y - i * 4))


class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - PADDLE_Y_OFFSET
        self.speed = PADDLE_SPEED
        self.color = NEON_CYAN

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        self.rect.x += dx
        self.rect.x = max(0, min(WIDTH - self.width, self.rect.x))

    def draw(self, surface):
        _glow_rect(surface, self.rect, self.color, layers=4, radius=6)
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        highlight = pygame.Rect(self.rect.x + 4, self.rect.y + 2, self.width - 8, 3)
        pygame.draw.rect(surface, WHITE, highlight, border_radius=2)


class Ball:
    def __init__(self, paddle):
        self.radius = BALL_RADIUS
        self.color = NEON_CYAN
        self.trail = []
        self.speed = BALL_SPEED
        self.reset(paddle)

    def reset(self, paddle):
        self.x = float(paddle.rect.centerx)
        self.y = float(paddle.rect.top - self.radius - 2)
        self.vx = 0.0
        self.vy = 0.0
        self.launched = False
        self.trail.clear()

    def launch(self):
        if self.launched:
            return
        angle = math.radians(-90 + random.uniform(-35, 35))
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.launched = True

    def set_speed(self, speed):
        speed = min(speed, BALL_MAX_SPEED)
        self.speed = speed
        cur = math.hypot(self.vx, self.vy)
        if cur > 0:
            self.vx = self.vx / cur * speed
            self.vy = self.vy / cur * speed

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           self.radius * 2, self.radius * 2)

    def update(self, paddle):
        """Move the ball; return a list of collision tags for this frame."""
        events = []
        if not self.launched:
            self.x = float(paddle.rect.centerx)
            self.y = float(paddle.rect.top - self.radius - 2)
            return events

        self.x += self.vx
        self.y += self.vy

        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        # Side walls
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -1
            events.append("wall")
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -1
            events.append("wall")

        # Top (just below HUD)
        if self.y - self.radius <= HUD_HEIGHT:
            self.y = HUD_HEIGHT + self.radius
            self.vy *= -1
            events.append("wall")

        # Paddle
        if self.vy > 0 and paddle.rect.collidepoint(self.x, self.y + self.radius):
            offset = (self.x - paddle.rect.centerx) / (paddle.width / 2)
            offset = max(-1.0, min(1.0, offset))
            angle = offset * math.radians(60)
            self.vx = math.sin(angle) * self.speed
            self.vy = -math.cos(angle) * self.speed
            self.y = paddle.rect.top - self.radius
            events.append("paddle")

        return events

    def is_lost(self):
        return self.y - self.radius > HEIGHT

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            ratio = (i + 1) / len(self.trail) if self.trail else 0
            r = max(1, int(self.radius * ratio))
            alpha = int(100 * ratio)
            glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, alpha), (r * 2, r * 2), r * 2)
            surface.blit(glow, (tx - r * 2, ty - r * 2))

        # Halo
        for i in range(3, 0, -1):
            size = self.radius * 6
            glow = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, 35 - i * 8),
                               (size // 2, size // 2), self.radius + i * 3)
            surface.blit(glow, (self.x - size // 2, self.y - size // 2))

        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius, 2)


class Brick:
    def __init__(self, x, y, color, points=10):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.points = points
        self.alive = True
        self.flash = 0

    def hit(self):
        self.alive = False
        self.flash = 4

    def update(self):
        if self.flash > 0:
            self.flash -= 1

    def draw(self, surface):
        if not self.alive:
            return
        body_color = WHITE if self.flash > 0 else self.color
        _glow_rect(surface, self.rect, self.color, layers=2, radius=4)
        pygame.draw.rect(surface, body_color, self.rect, border_radius=4)
        hl = pygame.Rect(self.rect.x + 4, self.rect.y + 3, self.rect.width - 8, 3)
        pygame.draw.rect(surface, WHITE, hl, border_radius=2)
