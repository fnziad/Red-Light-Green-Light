# Squid Game: Red Light Green Light (Python/OpenGL)

![Gameplay Screenshot Placeholder](screenshot.png) <!-- It's highly recommended to add a screenshot or GIF here -->

A 3D game implemented in Python using PyOpenGL, inspired by the "Red Light, Green Light" challenge from *Squid Game*, with added shooting mechanics and power-ups.

## Overview

Race against the clock and other contestants (enemies) to reach the finish line. Follow the commands of the giant doll: move during "Green Light", anticipate the stop during "Yellow Light", and freeze *completely* during "Red Light". Any movement during Red Light means elimination!

Use your weapon to shoot down enemy contestants blocking your path, but watch your ammo count. Collect power-ups to gain an edge. Can you survive and reach the finish line?

## Gameplay

*   **Objective:** Cross the playing field from the start to the finish zone before time runs out or you get caught.
*   **Red Light, Green Light:**
    *   **Green Light:** Move freely! The doll faces away.
    *   **Yellow Light:** Warning! Red light is coming soon. The doll starts turning. Enemies slow down.
    *   **Red Light:** FREEZE! Do not move your character at all. The doll faces you. Movement detected = Game Over.
*   **Shooting:**
    *   Press `Spacebar` to shoot.
*   **Enemies:**
    *   **Red:** Fast, low health (1 hit). More likely to move on Red Light.
    *   **Blue:** Medium speed, medium health (2 hits).
    *   **Black:** Slow, high health (5 hits), larger size. More cautious on Red Light.
*   **Power-ups:**
    *   **Speed Boost:** Grants a temporary significant speed increase.
*   **Difficulty:** The time intervals for Green/Red light phases become shorter as the game progresses (based on survival time).
*   **Winning:** Reach the finish zone (marked with white flashing ground and a FINISH sign).
*   **Losing:** Move during Red Light, or get touched by an enemy.

## Controls

*   **Movement:** `W` `A` `S` `D` (Relative to camera direction)
*   **Camera Tilt:** `Arrow Up` / `Arrow Down`
*   **Camera Rotate:** `Arrow Left` / `Arrow Right`
*   **Camera Zoom:** `Z` (Zoom In) / `X` (Zoom Out)
*   **Shoot:** `Spacebar`
*   **Restart Game:** `R`
*   **Toggle Debug Info:** `P`
*   **Exit Game:** `ESC`

## Features

*   Classic "Red Light, Green Light" mechanic with timed states (Green, Yellow, Red).
*   Third-person camera system with player-relative movement.
*   Shooting mechanic with ammo management.
*   Multiple enemy types with distinct AI behaviors (movement, health, red light risk).
*   Power-up system (Speed Boost, Ammo).
*   Dynamic difficulty scaling based on survival time.
*   Procedurally generated forest environment surrounding the playfield.
*   Basic physics for player movement (velocity/friction).
*   Smooth camera and player movement using interpolation.
*   Clear UI/HUD displaying game state, timers, score, ammo, progress, etc.
*   Segmented character models for player, doll, and enemies.
*   Visual effects for speed boost, bullet trails, hit indicators, etc.

## How to Run

1.  **Dependencies:**
    *   Python 3.x
    *   PyOpenGL (`pip install PyOpenGL PyOpenGL_accelerate`)
    *   GLUT (Usually included with PyOpenGL or needs to be installed separately depending on your OS - e.g., `sudo apt-get install freeglut3-dev` on Debian/Ubuntu, or download pre-compiled libraries for Windows).
2.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
3.  **Run the script:**
    ```bash
    python project_group.py
    ```
4.  Press `Spacebar` on the start screen to begin the game.

## Code Structure Overview

*   **Global Constants:** (Top of the file) Configuration for window, game rules, timings, physics, visuals, entities.
*   **Utility & Setup Functions:** `draw_text`, `setup_fixed_environment`, `setup_enemies`, `setup_powerups`.
*   **Drawing Functions:** `draw_*` functions responsible for rendering specific game elements (sky, field, doll, player, enemies, bullets, UI).
*   **Game Logic Functions:** `update_state` (main game loop logic), `start_game`, `fire_weapon`, `update_bullets`, `update_enemies`, `update_powerups`, `check_collisions`, `spawn_powerup`.
*   **Camera Setup:** `setup_camera` configures the `gluPerspective` and `gluLookAt` matrices.
*   **Event Handlers:** `key_*`, `special_key_*` functions manage user input. `restart_game` handles game reset.
*   **Main Function (`main`):** Initializes GLUT and OpenGL, sets up the initial game state, registers callbacks, and starts the main game loop (`glutMainLoop`).

## Potential Improvements

*   More sophisticated enemy AI (pathfinding, evasion).
*   More power-up types.
*   Sound effects and background music.
*   More detailed 3D models / animations.
*   Networked multiplayer mode.
*   Persistent high scores.

## still working on this 
