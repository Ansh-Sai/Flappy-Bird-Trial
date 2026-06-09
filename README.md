# Flappy Bird — Python Remake

A faithful recreation of the classic **Flappy Bird** game built with Python and Pygame. Features smooth gravity physics, randomized pipe obstacles, collision detection, and score tracking.

---

##  Demo

```
Press SPACE or click to flap → survive as long as possible → beat your best score!
```

---

##  Features

- **Gravity physics** — smooth per-frame acceleration with velocity-based bird tilt
- **Obstacle generation** — randomized pipe gaps spawned on a timer, auto-cleaned when off-screen
- **Collision detection** — pixel-accurate hitbox against pipes, ceiling, and ground
- **Score tracking** — live score + best score tracked per session
- **Continuous gameplay** — start screen, game over panel, instant restart
- **Visual polish** — scrolling ground, parallax clouds, animated bird wing

---

##  Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/flappy-bird.git
cd flappy-bird

# 2. Install dependency
pip install pygame

# 3. Run the game
python flappy_bird.py
```

---

##  Controls

| Action | Input |
|--------|-------|
| Flap   | `SPACE` or Mouse Click |
| Quit   | `ESC` |

---

##  Tech Stack

- **Language:** Python 3
- **Library:** [Pygame](https://www.pygame.org/)

---

##  Physics & Game Config

| Parameter | Value | Description |
|-----------|-------|-------------|
| Gravity | `0.45` px/frame² | Downward acceleration per frame |
| Flap strength | `-8.5` px/frame | Upward velocity on flap |
| Pipe speed | `3` px/frame | Horizontal scroll speed |
| Pipe gap | `155` px | Vertical opening between pipes |
| Pipe interval | `1500` ms | Time between pipe spawns |
| FPS | `60` | Target frame rate |

---


##  License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
