import pygame
import os
import random

# Configuración
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
PLAYER_SPEED = 4
WOLF_SPEED = 2
FRAME_SPEED = 8
WOLF_MOVE_INTERVAL = 60
WOLF_IDLE_DURATION = 90
WOLF_DETECTION_RADIUS = 5 * TILE_SIZE
wolf_chase_timer = 0
WOLF_CHASE_DIRECTION_DURATION = 30  # frames antes de cambiar dirección
wolf_rodeo_timer = 0
WOLF_RODEO_WAIT = 30  # frames de pausa entre movimientos aleatorios
wolf_rodeo_dir = None
wolf_was_moving = False

# Inicializar pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego con decorativos naturales")
clock = pygame.time.Clock()

# Cargar imágenes
try:
    ground = pygame.image.load("assets/tiles/ground.png").convert_alpha()
    nature_sheet = pygame.image.load("assets/tiles/nature_sheet.png").convert_alpha()
    player_sheet = pygame.image.load("assets/player/animation_sheet.png").convert_alpha()
    wolf_sheet = pygame.image.load("assets/player/wolf.png").convert_alpha()
except pygame.error as e:
    print("❌ Error cargando imágenes:", e)
    pygame.quit()
    exit()

# Extraer frames del jugador
def get_player_frames(row, count):
    frame_width = player_sheet.get_width() // 3
    frame_height = player_sheet.get_height() // 4
    return [
        player_sheet.subsurface((col * frame_width, row * frame_height, frame_width, frame_height))
        for col in range(count)
    ]

animations = {
    "up": get_player_frames(0, 3),
    "right": get_player_frames(3, 3),
    "down": get_player_frames(2, 3),
    "left": get_player_frames(3, 3),
}

# Extraer frames del lobo
def get_wolf_frames(sheet):
    frame_w = 48
    frame_h = 48
    return {
        "up":    [sheet.subsurface((i * frame_w, 3 * frame_h, frame_w, frame_h)) for i in range(3)],
        "right": [sheet.subsurface((i * frame_w, 2 * frame_h, frame_w, frame_h)) for i in range(3)],
        "down":  [sheet.subsurface((i * frame_w, 0 * frame_h, frame_w, frame_h)) for i in range(3)],
        "left":  [sheet.subsurface((i * frame_w, 1 * frame_h, frame_w, frame_h)) for i in range(3)],
    }

wolf_animations = get_wolf_frames(wolf_sheet)
wolf_frame_index = 0
wolf_frame_timer = 0

# Extraer decorativos
def get_tile(sheet, col, row, size=32):
    x = col * size
    y = row * size
    tile = pygame.Surface((size, size), pygame.SRCALPHA)
    tile.blit(sheet, (0, 0), (x, y, size, size))
    return tile

decorativos = {
    0: get_tile(nature_sheet, 7, 4),
    2: get_tile(nature_sheet, 7, 5),
    3: get_tile(nature_sheet, 7, 6),
    4: get_tile(nature_sheet, 3, 3),
}

# Generar mapa
def generate_map(width, height):
    map_data = []
    for y in range(height):
        row = []
        for x in range(width):
            r = random.random()
            if r < 0.10:
                row.append(0)
            elif r < 0.15:
                row.append(2)
            elif r < 0.20:
                row.append(3)
            elif r < 0.25:
                row.append(4)
            else:
                row.append(1)
        map_data.append(row)
    return map_data

MAP = generate_map(20, 15)

# Zona libre central
spawn_tile_x, spawn_tile_y = 8, 6
for dy in range(-1, 2):
    for dx in range(-1, 2):
        MAP[spawn_tile_y + dy][spawn_tile_x + dx] = 1

# Jugador
player_x = spawn_tile_x * TILE_SIZE
player_y = spawn_tile_y * TILE_SIZE
direction = "down"
frame_index = 0
frame_timer = 0

# Lobo
wolf_x = 10 * TILE_SIZE
wolf_y = 7 * TILE_SIZE
wolf_dir = random.choice(["up", "down", "left", "right"])
wolf_state = "idle"
wolf_idle_timer = 0
wolf_timer = 0

# Colisión
def is_blocking(tile_value):
    return tile_value == 0

def can_move(new_x, new_y):
    w, h = TILE_SIZE, TILE_SIZE
    corners = [
        (new_x, new_y),
        (new_x + w - 1, new_y),
        (new_x, new_y + h - 1),
        (new_x + w - 1, new_y + h - 1)
    ]
    for px, py in corners:
        tile_x = px // TILE_SIZE
        tile_y = py // TILE_SIZE
        if 0 <= tile_y < len(MAP) and 0 <= tile_x < len(MAP[0]):
            if is_blocking(MAP[tile_y][tile_x]):
                return False
    return True

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    new_x, new_y = player_x, player_y
    moving = False

    if keys[pygame.K_LEFT]:
        direction = "left"
        new_x -= PLAYER_SPEED
        moving = True
    elif keys[pygame.K_RIGHT]:
        direction = "right"
        new_x += PLAYER_SPEED
        moving = True
    elif keys[pygame.K_UP]:
        direction = "up"
        new_y -= PLAYER_SPEED
        moving = True
    elif keys[pygame.K_DOWN]:
        direction = "down"
        new_y += PLAYER_SPEED
        moving = True

    if can_move(new_x, new_y):
        player_x, player_y = new_x, new_y

    # Animación del jugador
    if moving:
        frame_timer += 1
        if frame_timer >= FRAME_SPEED:
            frame_index = (frame_index + 1) % len(animations[direction])
            frame_timer = 0
    else:
        frame_index = 1

    # Comportamiento del lobo
    dx = player_x - wolf_x
    dy = player_y - wolf_y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    if distance < WOLF_DETECTION_RADIUS:
        wolf_state = "chasing"
    else:
        if wolf_state == "chasing":
            wolf_state = "idle"
            wolf_idle_timer = 0

    wolf_new_x, wolf_new_y = wolf_x, wolf_y

    if wolf_state == "idle":
        wolf_idle_timer += 1
        if wolf_idle_timer >= WOLF_IDLE_DURATION:
            wolf_state = "patrolling"
            wolf_dir = random.choice(["up", "down", "left", "right"])
            wolf_idle_timer = 0

    elif wolf_state == "patrolling":
        wolf_timer += 1
        if wolf_timer >= WOLF_MOVE_INTERVAL:
            wolf_dir = random.choice(["up", "down", "left", "right"])
            wolf_timer = 0

        if wolf_dir == "left":
            wolf_new_x -= WOLF_SPEED
        elif wolf_dir == "right":
            wolf_new_x += WOLF_SPEED
        elif wolf_dir == "up":
            wolf_new_y -= WOLF_SPEED
        elif wolf_dir == "down":
            wolf_new_y += WOLF_SPEED

    elif wolf_state == "chasing":
        dx = player_x - wolf_x
        dy = player_y - wolf_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Si está muy cerca, rodear con pausas
        if distance < TILE_SIZE * 2:
            wolf_rodeo_timer += 1
            if wolf_rodeo_timer >= WOLF_RODEO_WAIT:
                directions = []
                if dx > 0:
                    directions.append("right")
                elif dx < 0:
                    directions.append("left")
                if dy > 0:
                    directions.append("down")
                elif dy < 0:
                    directions.append("up")

                random.shuffle(directions)
                for dir in directions:
                    temp_x, temp_y = wolf_x, wolf_y
                    if dir == "left":
                        temp_x -= WOLF_SPEED
                    elif dir == "right":
                        temp_x += WOLF_SPEED
                    elif dir == "up":
                        temp_y -= WOLF_SPEED
                    elif dir == "down":
                        temp_y += WOLF_SPEED

                    if can_move(temp_x, temp_y):
                        wolf_x, wolf_y = temp_x, temp_y
                        wolf_dir = dir
                        wolf_rodeo_timer = 0
                        break
        else:
            # Perseguir al jugador normalmente
            directions = []
            if abs(dx) > abs(dy):
                directions = ["right" if dx > 0 else "left", "down" if dy > 0 else "up"]
            else:
                directions = ["down" if dy > 0 else "up", "right" if dx > 0 else "left"]

            for dir in directions:
                temp_x, temp_y = wolf_x, wolf_y
                if dir == "left":
                    temp_x -= WOLF_SPEED
                elif dir == "right":
                    temp_x += WOLF_SPEED
                elif dir == "up":
                    temp_y -= WOLF_SPEED
                elif dir == "down":
                    temp_y += WOLF_SPEED

                if can_move(temp_x, temp_y):
                    wolf_x, wolf_y = temp_x, temp_y
                    wolf_dir = dir
                    wolf_rodeo_timer = 0
                    break

 

    # Animación del lobo
    if (wolf_x != wolf_new_x) or (wolf_y != wolf_new_y):
        wolf_frame_timer += 1
        if wolf_frame_timer >= FRAME_SPEED:
            wolf_frame_index = (wolf_frame_index + 1) % len(wolf_animations[wolf_dir])
            wolf_frame_timer = 0
    else:
        wolf_frame_index = 1  # frame estático si no se movió

    # Actualizar posición si se movió
    if can_move(wolf_new_x, wolf_new_y):
        wolf_x, wolf_y = wolf_new_x, wolf_new_y


    # Scroll centrado
    offset_x = player_x - WIDTH // 2
    offset_y = player_y - HEIGHT // 2

    # Dibujar mapa
    screen.fill((0, 0, 0))
    for y in range(len(MAP)):
        for x in range(len(MAP[0])):
            pos_x = x * TILE_SIZE - offset_x
            pos_y = y * TILE_SIZE - offset_y
            screen.blit(ground, (pos_x, pos_y))
            tile = MAP[y][x]
            if tile in decorativos:
                screen.blit(decorativos[tile], (pos_x, pos_y))

    # Dibujar lobo animado
    wolf_screen_x = wolf_x - offset_x
    wolf_screen_y = wolf_y - offset_y
    wolf_frame = wolf_animations[wolf_dir][wolf_frame_index]
    screen.blit(wolf_frame, (wolf_screen_x, wolf_screen_y))

    # Dibujar jugador
    frame = animations[direction][frame_index]
    if direction == "right":
        frame = pygame.transform.flip(frame, True, False)
    screen.blit(frame, (WIDTH // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
