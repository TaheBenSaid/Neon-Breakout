"""Main game class for Neon Breakout."""

import math
import os
import sys
import pygame

from settings import (
    WIDTH, HEIGHT, FPS, TITLE,
    BG_COLOR, GRID_COLOR, WHITE,
    NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN, NEON_PURPLE,
    BRICK_COLORS,
    PADDLE_Y_OFFSET,
    BALL_SPEED, BALL_SPEED_PER_LEVEL,
    BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, BRICK_GAP, BRICK_TOP_OFFSET,
    STARTING_LIVES, MAX_LEVEL, HIGH_SCORE_FILE, HUD_HEIGHT,
)
from entities import Paddle, Ball, Brick
from particles import ParticleSystem
from sounds import SoundManager


STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_PAUSE = "pause"
STATE_GAMEOVER = "gameover"
STATE_VICTORY = "victory"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arialblack,arial", 64, bold=True)
        self.font_big = pygame.font.SysFont("arialblack,arial", 36, bold=True)
        self.font_med = pygame.font.SysFont("arial,helvetica", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial,helvetica", 17)

        self.sounds = SoundManager()
        self.particles = ParticleSystem()

        self.high_score = self._load_high_score()
        self.state = STATE_MENU
        self.title_t = 0
        self.flash_timer = 0

        self.reset_game()

    # ----- setup -----

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.score = 0
        self.lives = STARTING_LIVES
        self.level = 1
        self._build_level()

    def _build_level(self):
        self.bricks = []
        total_w = BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP
        start_x = (WIDTH - total_w) // 2
        for r in range(BRICK_ROWS):
            for c in range(BRICK_COLS):
                x = start_x + c * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_OFFSET + r * (BRICK_HEIGHT + BRICK_GAP)
                color = BRICK_COLORS[r % len(BRICK_COLORS)]
                points = (BRICK_ROWS - r) * 10
                self.bricks.append(Brick(x, y, color, points=points))
        # Difficulty: ball speeds up per level.
        self.ball.set_speed(BALL_SPEED + (self.level - 1) * BALL_SPEED_PER_LEVEL)
        self.ball.reset(self.paddle)

    # ----- high score -----

    def _load_high_score(self):
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    return int(raw) if raw else 0
        except (ValueError, OSError):
            pass
        return 0

    def _save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
                    f.write(str(self.high_score))
            except OSError:
                pass

    # ----- main loop -----

    def run(self):
        try:
            while True:
                dt = self.clock.tick(FPS)
                self.title_t += dt
                if not self._handle_events():
                    break
                self._update()
                self._draw()
        finally:
            pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type != pygame.KEYDOWN:
                continue
            key = event.key

            if self.state == STATE_MENU:
                if key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_game()
                    self.state = STATE_PLAY
                    self.sounds.play("start")
                elif key == pygame.K_ESCAPE:
                    return False

            elif self.state == STATE_PLAY:
                if key == pygame.K_SPACE:
                    self.ball.launch()
                elif key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = STATE_PAUSE

            elif self.state == STATE_PAUSE:
                if key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = STATE_PLAY
                elif key == pygame.K_m:
                    self.state = STATE_MENU
                elif key == pygame.K_q:
                    return False

            elif self.state in (STATE_GAMEOVER, STATE_VICTORY):
                if key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_game()
                    self.state = STATE_PLAY
                elif key == pygame.K_m:
                    self.state = STATE_MENU
                elif key == pygame.K_q:
                    return False
        return True

    # ----- update -----

    def _update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            self.paddle.update(keys)
            events = self.ball.update(self.paddle)
            for tag in events:
                if tag == "paddle":
                    self.sounds.play("paddle")
                elif tag == "wall":
                    self.sounds.play("wall")

            if self.ball.launched:
                self._check_brick_collisions()

            for b in self.bricks:
                b.update()

            if self.ball.is_lost():
                self.lives -= 1
                self.flash_timer = 15
                self.sounds.play("lose")
                if self.lives <= 0:
                    self._save_high_score()
                    self.state = STATE_GAMEOVER
                else:
                    self.ball.reset(self.paddle)

            if all(not b.alive for b in self.bricks):
                if self.level >= MAX_LEVEL:
                    self._save_high_score()
                    self.state = STATE_VICTORY
                else:
                    self.level += 1
                    self.sounds.play("win")
                    self._build_level()

        self.particles.update()

    def _check_brick_collisions(self):
        ball_rect = self.ball.rect
        for brick in self.bricks:
            if not brick.alive:
                continue
            if not ball_rect.colliderect(brick.rect):
                continue

            overlap_left = ball_rect.right - brick.rect.left
            overlap_right = brick.rect.right - ball_rect.left
            overlap_top = ball_rect.bottom - brick.rect.top
            overlap_bottom = brick.rect.bottom - ball_rect.top
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap in (overlap_left, overlap_right):
                self.ball.vx *= -1
            else:
                self.ball.vy *= -1

            brick.hit()
            self.score += brick.points
            self.particles.spawn(brick.rect.centerx, brick.rect.centery, brick.color, count=18)
            self.sounds.play("brick")
            break  # one brick per frame keeps physics clean

    # ----- draw -----

    def _draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_grid()

        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_PLAY:
            self._draw_game()
        elif self.state == STATE_PAUSE:
            self._draw_game(dim=True)
            self._draw_pause_overlay()
        elif self.state == STATE_GAMEOVER:
            self._draw_game(dim=True)
            self._draw_end_screen("GAME OVER", NEON_PINK)
        elif self.state == STATE_VICTORY:
            self._draw_game(dim=True)
            self._draw_end_screen("YOU WIN", NEON_GREEN)

        if self.flash_timer > 0 and self.state == STATE_PLAY:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 60, 120, int(80 * (self.flash_timer / 15))))
            self.screen.blit(overlay, (0, 0))

        pygame.display.flip()

    def _draw_grid(self):
        for x in range(0, WIDTH, 40):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y))

    def _draw_game(self, dim=False):
        for b in self.bricks:
            b.draw(self.screen)
        self.particles.draw(self.screen)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self._draw_hud()
        if dim:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))

    def _draw_hud(self):
        bar = pygame.Surface((WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 110))
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, NEON_CYAN, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 1)

        score = self.font_med.render(f"SCORE  {self.score:05d}", True, WHITE)
        self.screen.blit(score, (20, 14))

        level = self.font_med.render(f"LEVEL  {self.level}/{MAX_LEVEL}", True, NEON_YELLOW)
        self.screen.blit(level, (WIDTH // 2 - level.get_width() // 2, 14))

        hs = self.font_small.render(f"BEST  {self.high_score:05d}", True, NEON_PURPLE)
        self.screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, 36))

        lives_label = self.font_small.render("LIVES", True, WHITE)
        self.screen.blit(lives_label, (WIDTH - 130, 18))
        for i in range(self.lives):
            x = WIDTH - 60 + i * 18
            pygame.draw.circle(self.screen, NEON_PINK, (x, 25), 6)
            pygame.draw.circle(self.screen, WHITE, (x - 2, 23), 2)

        if self.state == STATE_PLAY and not self.ball.launched:
            hint = self.font_small.render("Press SPACE to launch the ball", True, WHITE)
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 28))

    def _draw_menu(self):
        # Decorative bricks in background
        for i, color in enumerate(BRICK_COLORS):
            r = pygame.Rect(70 + i * 110, 80, 70, 18)
            glow = pygame.Surface((r.width + 20, r.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*color, 50), glow.get_rect(), border_radius=6)
            self.screen.blit(glow, (r.x - 10, r.y - 10))
            pygame.draw.rect(self.screen, color, r, border_radius=4)

        # Title with soft glow
        title_text = "NEON  BREAKOUT"
        pulse = (math.sin(self.title_t / 350.0) + 1) / 2
        glow_color = NEON_PURPLE if pulse < 0.5 else NEON_PINK
        glow_surf = self.font_title.render(title_text, True, glow_color)
        glow_surf.set_alpha(110)
        for off in (-4, -2, 2, 4):
            rect = glow_surf.get_rect(center=(WIDTH // 2 + off, 200 + off))
            self.screen.blit(glow_surf, rect)
        title = self.font_title.render(title_text, True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 200)))

        sub = self.font_med.render("a polished arkanoid-style game", True, NEON_CYAN)
        self.screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 260)))

        # Controls block
        controls = [
            ("MOVE", "<-  ->   or   A  D"),
            ("LAUNCH BALL", "SPACE"),
            ("PAUSE", "P   or   ESC"),
        ]
        y = 330
        for label, key in controls:
            l = self.font_small.render(label, True, WHITE)
            k = self.font_small.render(key, True, NEON_YELLOW)
            self.screen.blit(l, (WIDTH // 2 - 150, y))
            self.screen.blit(k, (WIDTH // 2 + 20, y))
            y += 28

        # Blinking start prompt
        if (self.title_t // 500) % 2 == 0:
            start = self.font_big.render("PRESS ENTER TO PLAY", True, NEON_GREEN)
            self.screen.blit(start, start.get_rect(center=(WIDTH // 2, 470)))

        hs = self.font_small.render(f"HIGH SCORE   {self.high_score:05d}", True, NEON_PINK)
        self.screen.blit(hs, hs.get_rect(center=(WIDTH // 2, 540)))

    def _draw_pause_overlay(self):
        title = self.font_title.render("PAUSED", True, NEON_CYAN)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

        h1 = self.font_med.render("Press P or ESC to resume", True, WHITE)
        self.screen.blit(h1, h1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        h2 = self.font_small.render("M  menu        Q  quit", True, NEON_YELLOW)
        self.screen.blit(h2, h2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    def _draw_end_screen(self, label, color):
        title = self.font_title.render(label, True, color)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

        score = self.font_big.render(f"Score   {self.score}", True, WHITE)
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        hs = self.font_med.render(f"Best   {self.high_score}", True, NEON_YELLOW)
        self.screen.blit(hs, hs.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        hint = self.font_small.render("ENTER  play again        M  menu        Q  quit", True, NEON_CYAN)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)))
