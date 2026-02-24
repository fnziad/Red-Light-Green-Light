# Squid Game: Red Light, Green Light

A 3D game built from scratch in **Python** using **PyOpenGL** and **GLUT**, inspired by the iconic "Red Light, Green Light" challenge from *Squid Game* — with added combat, power-ups, enemy AI, level progression, and more.

> **Version 4.0** — Solo project by **Ziad**

---

## Gameplay

Race across a dangerous arena to reach the finish line while obeying the doll's commands:

| Light State | What Happens |
|-------------|-------------|
| **Green** | Move freely — the doll faces away |
| **Yellow** | Warning — red light is imminent, the doll starts turning |
| **Red** | **FREEZE!** Any movement = instant elimination |

### Core Mechanics

- **Shooting** — Fire bullets to eliminate enemies blocking your path (Space)
- **Sprint** — Hold Shift for a speed burst; overuse triggers a 4-second exhaustion cooldown with 55% speed penalty
- **Jump** — Press J to leap over enemies and dodge bullets (with full gravity physics)
- **Shield Power-up** — Absorbs one enemy collision or bullet hit, destroying the enemy on contact
- **Speed Power-up** — Temporary +70% movement speed boost
- **Enemy Bullets** — Enemies fire slow, dodgeable projectiles; jump or strafe to avoid them
- **Level Progression** — After winning, press N to advance to harder levels with more enemies, faster AI, and shorter light intervals

### Enemies

| Type | Speed | Health | Behavior |
|------|-------|--------|----------|
| **Red** | Fast | 1 HP | Aggressive, shoots from Level 2+ |
| **Blue** | Medium | 2 HP | Balanced, shoots bullets |
| **Black** | Slow | 5+ HP | Tanky, large hitbox, always shoots |

### Win / Lose Conditions

- **Win**: Reach the finish line (progress >= 95%)
- **Lose**: Move during red light, get touched by an enemy, or get hit by an enemy bullet

---

## Controls

| Key | Action |
|-----|--------|
| `W` `A` `S` `D` | Move (relative to camera) |
| `Arrow Keys` | Rotate / tilt camera |
| `Z` / `X` | Zoom in / out |
| `Space` | Shoot |
| `Shift` (hold) | Sprint |
| `J` | Jump |
| `R` | Restart game (Level 1) |
| `N` | Next level (after winning) |
| `P` | Toggle debug info |
| `ESC` | Exit |

---

## Features

- Classic Red Light / Green Light state machine with Green, Yellow, Red cycling
- Third-person camera with smooth interpolation and player-relative movement
- Shooting system with ammo management and bullet trails
- Three enemy types with distinct AI (movement speed, health, red-light risk behavior)
- Sprint with stamina bar, exhaustion state, and cooldown system
- Jump mechanic with gravity physics — dodge enemies and bullets mid-air
- Shield and Speed power-ups with visual effects (glowing orbs, bobbing animation)
- Enemy bullet system — enemies shoot slow projectiles you can dodge
- Level progression with scaling difficulty (enemy count, speed, health, shoot frequency)
- High score system with name entry on win
- Dynamic difficulty that increases over time (shorter light intervals per phase)
- Procedurally generated forest environment surrounding the playfield
- Full HUD: score, time, kills, phase, level, stamina bar, shield timer, FPS, ammo
- Game over and win overlays with stats, leaderboard, and next-level prompt
- Screen shake on hits
- Segmented 3D character models for player, doll, and enemies (no external assets)

---

## How to Run

### Prerequisites

- **Python 3.8+**
- **PyOpenGL** with GLUT support

### Install Dependencies

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

On **macOS**, GLUT is included with the system. On **Linux**, you may need:

```bash
sudo apt-get install freeglut3-dev
```

### Run the Game

```bash
git clone https://github.com/fnziad/Red-Light-Green-Light.git
cd Red-Light-Green-Light
python3 project_group.py
```

Press **Enter** on the start screen to begin.

---

## Project Structure

```
Red-Light-Green-Light/
├── project_group.py      # Main game — all logic, rendering, and UI
├── LICENSE               # MIT License
├── README.md             # This file
└── STABLE_NOTES.md       # Development / stability notes
```

> The `OpenGL/` directory is the bundled PyOpenGL library for portability.
> `project_group_backup.py` and `pygame_version/` are legacy files not required to run the game.

---

## Code Architecture

The entire game is contained in a single file (`project_group.py`) organized into these sections:

| Section | Description |
|---------|-------------|
| **Global Constants** | Window config, arena dimensions, physics, timing, entity settings |
| **Setup Functions** | `setup_enemies()`, `setup_powerups()`, `setup_fixed_environment()` |
| **Drawing Functions** | `draw_player()`, `draw_enemy()`, `draw_doll()`, `draw_bullet()`, `draw_powerup()`, `draw_shield_effect()`, HUD rendering |
| **Game Logic** | `update_state()` (main loop), `update_enemies()`, `update_bullets()`, `update_enemy_bullets()`, `check_collisions()` |
| **Camera** | `setup_camera()` with third-person orbit, zoom, and screen shake |
| **Input Handlers** | `key_pressed()`, `key_released()`, `special_key_*()` — WASD, sprint, jump, shoot, name entry |
| **Game Flow** | `start_game()`, `restart_game()`, `next_level()` |
| **Main** | GLUT initialization, callback registration, `glutMainLoop()` |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

**Ziad** — Design, programming, and everything else.
