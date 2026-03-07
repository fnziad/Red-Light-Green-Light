<p align="center">
  <h1 align="center">Squid Game: Red Light, Green Light</h1>
  <p align="center">
    A complete 3D survival game — built from scratch in Python with OpenGL.<br/>
    Freeze. Survive. Reach the finish line.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenGL-PyOpenGL-5586A4?style=for-the-badge&logo=opengl&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Lines_of_Code-3950+-f97316?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Version-4.0-8b5cf6?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-64748b?style=for-the-badge"/>
</p>

---

## About the Game

**Squid Game: Red Light, Green Light** is a real-time 3D survival game written entirely in Python using the OpenGL fixed-function pipeline. All geometry, AI, physics, rendering, and UI are hand-coded from scratch — no game engine, no assets, just pure code.

Race across a dangerous arena to reach the finish line while obeying the doll's commands. Use your weapon to eliminate enemies blocking your path, dodge their bullets, grab power-ups, and advance through increasingly difficult levels.

> Made by **Fahad Nadim Ziad** — 2026

---

## Screenshots

> Add screenshots to `previews/` and link them here.

---

## Features at a Glance

### 🚦 Red Light / Green Light Mechanic

| State      | What Happens                                                     |
| ---------- | ---------------------------------------------------------------- |
| **Green**  | Move freely — the doll faces away                                |
| **Yellow** | Warning — red light is imminent, amber screen tint               |
| **Red**    | **FREEZE!** Any movement = instant elimination, red screen blink |

- Randomised state durations that shorten with each difficulty phase
- Blinking full-screen colour tint overlay for immediate visual feedback
- Doll rotation animation synced to state transitions

### 🔫 Shooting System

- Fire bullets with `Space` to clear enemies blocking your path
- Ammo count shown live in HUD
- Bullet physics with collision detection against all enemy types

### 🏃 Sprint & Stamina

- Hold `Shift` to sprint at 1.5× speed — stamina bar depletes in real time
- **Exhaustion system**: draining the stamina bar triggers a 4-second cooldown at 55% speed
- Speed meter bar in HUD colour-codes your current velocity (blue → green → yellow → red)

### 🦘 Jump

- Press `J` to leap with full gravity physics (`JUMP_FORCE = 450`, `GRAVITY = 900`)
- Jump over enemies and dodge incoming bullets mid-air
- Airborne indicator in HUD

### 🛡️ Power-Ups

| Type            | Shape                 | Effect                                                       |
| --------------- | --------------------- | ------------------------------------------------------------ |
| **Speed Boost** | Yellow lightning bolt | +70% speed for 10 s                                          |
| **Shield**      | Blue diamond          | Absorbs next enemy hit or bullet — destroys enemy on contact |

- Power-ups bob and glow in the arena; new ones spawn every 15 seconds
- Shield timer shown in HUD while active

### 👾 Three Enemy Types

| Type      | Speed  | Health | Behaviour                          |
| --------- | ------ | ------ | ---------------------------------- |
| **Red**   | Fast   | 1 HP   | Aggressive, shoots from Level 2+   |
| **Blue**  | Medium | 2 HP   | Balanced, always shoots            |
| **Black** | Slow   | 5+ HP  | Tanky, large hitbox, always shoots |

- All enemies shoot **slow dodgeable bullets** toward the player with aim jitter
- Enemy count, speed, health, and bullet frequency all scale with level

### 📈 Level Progression

- Reach the finish line → enter your name → score saved to leaderboard
- Press `N` to advance to the next level (score preserved, enemies harder)
- Press `R` to restart from Level 1 (full reset)

### 📊 HUD

| Panel       | Content                                                                         |
| ----------- | ------------------------------------------------------------------------------- |
| Top-left    | Score, Time, Kills, Phase, Level                                                |
| Top-right   | FPS, Ammo, Sprint/Exhaustion status, Shield timer, Speed meter bar, Stamina bar |
| Top-centre  | Light state label + countdown timer                                             |
| Bottom      | Progress bar to finish line                                                     |
| Win overlay | Final stats, name entry, top-5 leaderboard                                      |

---

## Controls

| Key             | Action                         |
| --------------- | ------------------------------ |
| `W` `A` `S` `D` | Move (relative to camera)      |
| `Arrow Keys`    | Rotate / tilt camera           |
| `Z` / `X`       | Zoom in / out                  |
| `Space`         | Shoot                          |
| `Shift` (hold)  | Sprint                         |
| `J`             | Jump                           |
| `R`             | Restart (Level 1, score reset) |
| `N`             | Next level (after winning)     |
| `P`             | Toggle debug info              |
| `ESC`           | Quit                           |

---

## Installation & Running

> Full step-by-step guide: see **[INSTALL.md](INSTALL.md)**

**Quick start:**

```bash
# 1. Clone the repository
git clone https://github.com/fnziad/Red-Light-Green-Light.git
cd Red-Light-Green-Light

# 2. Install dependencies
pip install -r requirements.txt

# 3. Play
python run_game.py
```

**Requirements:** Python 3.8 or later, PyOpenGL 3.x

---

## Project Structure

```
Red-Light-Green-Light/
├── previews/                        # Screenshots and gameplay captures
├── src/
│   └── red_light_green_light.py    # Complete game engine (~3,950 lines)
├── run_game.py                      # Launcher with controls reference
├── requirements.txt                 # PyOpenGL dependency
├── INSTALL.md                       # Full platform installation guide
├── PROJECT_INFO.txt                 # Detailed technical & portfolio overview
├── README.md                        # This file
└── LICENSE                          # MIT License
```

---

## Technical Overview

| Area         | Implementation                                             |
| ------------ | ---------------------------------------------------------- |
| Language     | Python 3                                                   |
| Graphics API | OpenGL 2.x fixed-function via PyOpenGL + GLUT              |
| 3D Models    | Primitives: cubes, spheres, cylinders (no external assets) |
| Physics      | Velocity + friction, delta-time scaled, gravity for jumps  |
| Enemy AI     | State machine: patrol / freeze / shoot per light state     |
| Input        | GLUT keyboard callbacks, Shift via glutGetModifiers()      |
| Exit         | `os._exit(0)` — avoids macOS GLUT segfault on shutdown     |

---

## Author

**Fahad Nadim Ziad**
📧 f.n.ziad@gmail.com
🐙 [@fnziad](https://github.com/fnziad)

---

## License

MIT License — see [LICENSE](LICENSE) for full text.
