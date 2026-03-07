#!/usr/bin/env python3
"""
Squid Game: Red Light, Green Light — Launcher
Author : Fahad Nadim Ziad
Email  : f.n.ziad@gmail.com
Year   : 2026
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from red_light_green_light import main

if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║        SQUID GAME: RED LIGHT, GREEN LIGHT           ║")
    print("  ║         3D Survival Game  •  Python / OpenGL        ║")
    print("  ║              Fahad Nadim Ziad — 2026                ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    print("  MOVEMENT")
    print("    W / A / S / D       Move (relative to camera)")
    print("    Arrow Keys          Rotate / tilt camera")
    print("    Z / X               Zoom in / out")
    print()
    print("  ACTIONS")
    print("    Space               Shoot")
    print("    Shift (hold)        Sprint  (uses stamina bar)")
    print("    J                   Jump")
    print()
    print("  GAME")
    print("    R                   Restart (back to Level 1)")
    print("    N                   Next level (after winning)")
    print("    P                   Toggle debug info")
    print("    ESC                 Quit")
    print()
    print("  RULES")
    print("    Green Light  — Move freely toward the finish line")
    print("    Yellow Light — Warning! Red light incoming")
    print("    Red Light    — FREEZE completely or be eliminated")
    print()

    main()
