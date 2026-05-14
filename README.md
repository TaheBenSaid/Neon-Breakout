# Neon Breakout

A small 2D Breakout-style game made with Python and Pygame.
Bounce the ball with the paddle, clear all the bricks in each level, and try to beat your best score.

## Requirements

- Python 3.10 or newer
- Pygame

Install Pygame with:

```
pip install pygame
```

## Run

From the project folder:

```
python main.py
```

## Controls

| Action          | Keys                  |
|-----------------|-----------------------|
| Move paddle     | Left / Right arrows, or A / D |
| Launch ball     | Space                 |
| Pause / resume  | P or Escape           |
| Play again      | Enter (on game over / win) |
| Back to menu    | M                     |
| Quit            | Q (or close the window) |

## Features

- Start screen, gameplay screen, pause screen, game over screen, and victory screen.
- Score, level, and lives shown in the HUD.
- 5 levels with increasing ball speed for progressive difficulty.
- Particle effect when a brick is destroyed, plus a short red flash on losing a life.
- Procedurally generated sound effects (paddle, wall, brick, lose, win) - no audio files needed.
- Pause with P or Escape.
- High score saved in `highscore.txt` (created on first run).
- Fixed 800x600 window with a neon-themed color palette.

## Project structure

```
Neon Breakout/
├── main.py          # entry point
├── game.py          # Game class, state machine, drawing
├── entities.py      # Paddle, Ball, Brick
├── particles.py     # Small particle system
├── sounds.py        # Procedural sound effects
├── settings.py      # Constants (window, colors, gameplay)
├── highscore.txt    # Created automatically when you beat your record
├── assets/          # Reserved for future images / fonts
└── README.md
```

## Notes

- All sound effects are synthesized at startup using the standard library, so the game runs without bundled .wav files. If audio can't be initialized (for example on a system without a sound device) the game still runs silently.
- The neon color palette and overall idea (paddle + ball + bricks) follow the classic Breakout / Arkanoid concept.
