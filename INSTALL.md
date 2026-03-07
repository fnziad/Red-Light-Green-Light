# Installation Guide — Squid Game: Red Light, Green Light

This guide walks you through installing and running the game on macOS, Windows, and Linux.

---

## Requirements

| Requirement     | Version | Notes                           |
| --------------- | ------- | ------------------------------- |
| Python          | 3.8+    | 3.10+ recommended               |
| pip             | Any     | Comes with Python                |
| PyOpenGL        | 3.x     | Only external dependency         |
| OpenGL / GLUT   | System  | Pre-installed on macOS; see below |

---

## Quick Install (All Platforms)

```bash
git clone https://github.com/fnziad/Red-Light-Green-Light.git
cd Red-Light-Green-Light
pip install -r requirements.txt
python run_game.py
```

---

## Platform-Specific Setup

### macOS

1. **Install Python** (if not already installed):

   ```bash
   brew install python
   ```

   Or download from [python.org](https://www.python.org/downloads/).

2. **Install PyOpenGL:**

   ```bash
   pip3 install PyOpenGL PyOpenGL_accelerate
   ```

3. **GLUT** is built into macOS — no extra install needed.

4. **Run the game:**

   ```bash
   python3 run_game.py
   ```

---

### Linux (Ubuntu / Debian)

1. **Install Python and pip:**

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Install freeglut (GLUT for Linux):**

   ```bash
   sudo apt install freeglut3-dev
   ```

3. **Install PyOpenGL:**

   ```bash
   pip3 install PyOpenGL PyOpenGL_accelerate
   ```

4. **Run the game:**

   ```bash
   python3 run_game.py
   ```

---

### Windows

1. **Install Python** from [python.org](https://www.python.org/downloads/).
   - Check **"Add Python to PATH"** during installation.

2. **Install PyOpenGL:**

   ```bash
   pip install PyOpenGL PyOpenGL_accelerate
   ```

3. **GLUT on Windows** — PyOpenGL includes a bundled `freeglut.dll` for Windows, so no additional install is typically needed.

4. **Run the game:**

   ```bash
   python run_game.py
   ```

---

## Troubleshooting

| Problem | Solution |
| ------- | -------- |
| `No module named 'OpenGL'` | Run `pip install PyOpenGL PyOpenGL_accelerate` |
| `glutInit() error` on Linux | Run `sudo apt install freeglut3-dev` |
| Black screen / no window | Update GPU drivers and ensure OpenGL 2.0+ is supported |
| `Unable to import numpymodule` warning | Harmless — install `numpy` optionally to suppress it |
| Game exits immediately | Check terminal output for Python errors |

---

## Optional: numpy

numpy is not required, but PyOpenGL will print a warning without it. To suppress:

```bash
pip install numpy
```

---

## Contact

**Fahad Nadim Ziad** — f.n.ziad@gmail.com
