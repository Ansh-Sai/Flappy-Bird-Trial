import pygame
import random
import sys

# ── Constants ────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 400, 600
FPS = 60

# Colors
SKY       = (113, 197, 207)
GROUND_C  = (222, 216, 149)
PIPE_C    = (106, 190, 48)
PIPE_DARK = (75, 150, 32)
BIRD_Y_C  = (255, 215, 0)
BIRD_O_C  = (255, 140, 0)
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
DARK_GRAY = (40,  40,  40)
RED       = (220, 50,  50)

# Physics
GRAVITY       = 0.45
FLAP_STRENGTH = -8.5
PIPE_SPEED    = 3
PIPE_GAP      = 155
PIPE_INTERVAL = 1500   # ms between pipes
GROUND_H      = 80

# Bird geometry
BIRD_X    = 80
BIRD_R    = 18          # radius


# ── Helper: draw a rounded pipe ───────────────────────────────────────────────
def draw_pipe(surface, x, top_h, bot_y):
    cap = 12          # cap height
    cap_w = 8         # extra width on cap

    # Bottom pipe body
    pygame.draw.rect(surface, PIPE_C,    (x, bot_y, 60, SCREEN_H))
    # Bottom pipe cap
    pygame.draw.rect(surface, PIPE_C,    (x - cap_w, bot_y, 60 + cap_w*2, cap))
    # Highlight stripe
    pygame.draw.rect(surface, PIPE_DARK, (x + 10, bot_y + cap, 8, SCREEN_H - bot_y), 0)

    # Top pipe body
    pygame.draw.rect(surface, PIPE_C,    (x, 0, 60, top_h))
    # Top pipe cap
    pygame.draw.rect(surface, PIPE_C,    (x - cap_w, top_h - cap, 60 + cap_w*2, cap))
    # Highlight stripe
    pygame.draw.rect(surface, PIPE_DARK, (x + 10, 0, 8, top_h - cap), 0)


# ── Helper: draw bird ─────────────────────────────────────────────────────────
def draw_bird(surface, cx, cy, vel):
    # Tilt based on velocity
    tilt = max(-30, min(45, vel * 3))

    bird_surf = pygame.Surface((BIRD_R*2+10, BIRD_R*2+10), pygame.SRCALPHA)
    bx, by = BIRD_R + 5, BIRD_R + 5

    # Body
    pygame.draw.circle(bird_surf, BIRD_Y_C, (bx, by), BIRD_R)
    # Wing
    wing_y = by + 4 + int(vel * 0.5)
    pygame.draw.ellipse(bird_surf, BIRD_O_C, (bx - 10, wing_y, 18, 10))
    # Eye
    pygame.draw.circle(bird_surf, WHITE,  (bx + 8, by - 5), 6)
    pygame.draw.circle(bird_surf, BLACK,  (bx + 10, by - 5), 3)
    # Beak
    pygame.draw.polygon(bird_surf, BIRD_O_C, [
        (bx + BIRD_R, by),
        (bx + BIRD_R + 12, by - 3),
        (bx + BIRD_R + 12, by + 3),
    ])

    rotated = pygame.transform.rotate(bird_surf, -tilt)
    rect = rotated.get_rect(center=(cx, cy))
    surface.blit(rotated, rect)


# ── Helper: draw ground ───────────────────────────────────────────────────────
def draw_ground(surface, offset):
    ground_y = SCREEN_H - GROUND_H
    pygame.draw.rect(surface, GROUND_C, (0, ground_y, SCREEN_W, GROUND_H))
    pygame.draw.line(surface, (180, 170, 100), (0, ground_y), (SCREEN_W, ground_y), 3)
    # Scrolling grass tufts
    tuft_spacing = 40
    for i in range(-1, SCREEN_W // tuft_spacing + 2):
        tx = (i * tuft_spacing - offset % tuft_spacing)
        pygame.draw.line(surface, (80, 160, 40),
                         (tx, ground_y), (tx - 4, ground_y - 10), 2)
        pygame.draw.line(surface, (80, 160, 40),
                         (tx + 4, ground_y), (tx + 8, ground_y - 10), 2)


# ── Helper: draw sky & clouds ─────────────────────────────────────────────────
CLOUDS = [(50, 80), (160, 120), (280, 60), (350, 140)]

def draw_background(surface, cloud_offset):
    surface.fill(SKY)
    for (cx, cy) in CLOUDS:
        ox = (cx - cloud_offset * 0.3) % (SCREEN_W + 80) - 40
        for dx, dy, r in [(-20, 0, 22), (0, -10, 28), (20, 0, 22), (40, 5, 18)]:
            pygame.draw.circle(surface, WHITE, (int(ox + dx), cy + dy), r)


# ── Helper: draw score ────────────────────────────────────────────────────────
def draw_score(surface, font, score, best):
    # Current score centered at top
    txt = font.render(str(score), True, WHITE)
    shadow = font.render(str(score), True, DARK_GRAY)
    x = SCREEN_W // 2 - txt.get_width() // 2
    surface.blit(shadow, (x + 2, 32))
    surface.blit(txt, (x, 30))

    # Best in corner
    small_font = pygame.font.SysFont("Arial", 18, bold=True)
    best_txt = small_font.render(f"Best: {best}", True, WHITE)
    surface.blit(best_txt, (10, 10))


# ── Collision detection ───────────────────────────────────────────────────────
def check_collision(bird_y, pipes):
    ground_y = SCREEN_H - GROUND_H
    # Ground / ceiling
    if bird_y + BIRD_R >= ground_y or bird_y - BIRD_R <= 0:
        return True
    # Pipes
    for pipe in pipes:
        px, top_h = pipe["x"], pipe["top_h"]
        bot_y = top_h + PIPE_GAP
        bird_rect = pygame.Rect(BIRD_X - BIRD_R + 4, bird_y - BIRD_R + 4,
                                BIRD_R * 2 - 8, BIRD_R * 2 - 8)
        top_rect = pygame.Rect(px - 8, 0, 60 + 16, top_h)
        bot_rect = pygame.Rect(px - 8, bot_y, 60 + 16, SCREEN_H - bot_y)
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect):
            return True
    return False


# ── Screens ───────────────────────────────────────────────────────────────────
def draw_start_screen(surface, font, big_font):
    draw_background(surface, 0)
    draw_ground(surface, 0)

    # Title
    title = big_font.render("Flappy Bird", True, WHITE)
    shadow = big_font.render("Flappy Bird", True, (0, 100, 0))
    tx = SCREEN_W // 2 - title.get_width() // 2
    surface.blit(shadow, (tx + 3, 153))
    surface.blit(title, (tx, 150))

    draw_bird(surface, BIRD_X + 60, SCREEN_H // 2, 0)

    prompt = font.render("Press SPACE / Tap to start", True, WHITE)
    surface.blit(prompt, (SCREEN_W // 2 - prompt.get_width() // 2, 380))

    hint = pygame.font.SysFont("Arial", 16).render("(SPACE or click to flap)", True, (200, 240, 200))
    surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 420))


def draw_game_over(surface, font, big_font, score, best):
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    # Panel
    panel = pygame.Rect(60, 180, 280, 220)
    pygame.draw.rect(surface, (255, 250, 220), panel, border_radius=16)
    pygame.draw.rect(surface, (200, 180, 80), panel, 3, border_radius=16)

    go = big_font.render("Game Over", True, RED)
    surface.blit(go, (SCREEN_W // 2 - go.get_width() // 2, 195))

    sc = font.render(f"Score: {score}", True, DARK_GRAY)
    surface.blit(sc, (SCREEN_W // 2 - sc.get_width() // 2, 265))

    bs = font.render(f"Best:  {best}", True, (0, 130, 0))
    surface.blit(bs, (SCREEN_W // 2 - bs.get_width() // 2, 305))

    restart = font.render("SPACE / Click to restart", True, DARK_GRAY)
    surface.blit(restart, (SCREEN_W // 2 - restart.get_width() // 2, 355))


# ── Main game loop ─────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()

    font     = pygame.font.SysFont("Arial", 28, bold=True)
    big_font = pygame.font.SysFont("Arial", 46, bold=True)

    # ── State ──────────────────────────────────────────────────────────────────
    state = "start"   # "start" | "playing" | "dead"

    bird_y   = SCREEN_H // 2
    bird_vel = 0
    pipes    = []
    score    = 0
    best     = 0
    ground_offset  = 0
    cloud_offset   = 0
    last_pipe_time = 0
    scored_pipes   = set()

    def reset():
        nonlocal bird_y, bird_vel, pipes, score, ground_offset, cloud_offset
        nonlocal last_pipe_time, scored_pipes
        bird_y         = SCREEN_H // 2
        bird_vel       = 0
        pipes          = []
        score          = 0
        ground_offset  = 0
        cloud_offset   = 0
        last_pipe_time = pygame.time.get_ticks()
        scored_pipes   = set()

    def flap():
        nonlocal bird_vel
        bird_vel = FLAP_STRENGTH

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        # ── Events ─────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                key = getattr(event, "key", None)
                if state == "start":
                    if key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                        reset()
                        state = "playing"
                        flap()
                elif state == "playing":
                    if key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                        flap()
                elif state == "dead":
                    if key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                        reset()
                        state = "playing"
                        flap()
                if key == pygame.K_ESCAPE:
                    running = False

        # ── Update ─────────────────────────────────────────────────────────────
        if state == "playing":
            # Bird physics
            bird_vel += GRAVITY
            bird_vel  = min(bird_vel, 12)
            bird_y   += bird_vel

            # Scroll offsets
            ground_offset += PIPE_SPEED
            cloud_offset  += PIPE_SPEED * 0.4

            # Spawn pipes
            if now - last_pipe_time > PIPE_INTERVAL:
                min_h = 60
                max_h = SCREEN_H - GROUND_H - PIPE_GAP - 60
                top_h = random.randint(min_h, max_h)
                pipes.append({"x": SCREEN_W + 10, "top_h": top_h, "id": now})
                last_pipe_time = now

            # Move pipes
            for pipe in pipes:
                pipe["x"] -= PIPE_SPEED

            # Score
            for pipe in pipes:
                if pipe["x"] + 60 < BIRD_X and pipe["id"] not in scored_pipes:
                    score += 1
                    best = max(best, score)
                    scored_pipes.add(pipe["id"])

            # Remove off-screen pipes
            pipes = [p for p in pipes if p["x"] > -80]

            # Collision
            if check_collision(bird_y, pipes):
                state = "dead"

        # ── Draw ───────────────────────────────────────────────────────────────
        draw_background(screen, cloud_offset)

        for pipe in pipes:
            draw_pipe(screen, pipe["x"], pipe["top_h"], pipe["top_h"] + PIPE_GAP)

        draw_ground(screen, int(ground_offset))

        if state != "start":
            draw_bird(screen, BIRD_X, int(bird_y), bird_vel)

        if state == "start":
            draw_start_screen(screen, font, big_font)
        elif state == "playing":
            draw_score(screen, font, score, best)
        elif state == "dead":
            draw_bird(screen, BIRD_X, int(bird_y), bird_vel)
            draw_score(screen, font, score, best)
            draw_game_over(screen, font, big_font, score, best)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
