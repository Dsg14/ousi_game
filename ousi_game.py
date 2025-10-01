import pygame
import csv

# ---------------- Configuración ----------------
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32  # tamaño real del tileset
MAP_CSV = r"C:\Users\David SG\Desktop\David\ousi_game\mapaokv2.csv"
TILESET_PNG = r"C:\Users\David SG\Desktop\David\ousi_game\assets\tiles\TXTilesetGrass.png"
PLAYER_SHEET = r"C:\Users\David SG\Desktop\David\ousi_game\assets\player\animation_sheet.png"

# IDs transitables (suelo)
WALKABLE = {0, 1, 2, 8, 14, 22, 28}

# ---------------- Inicialización ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mapa tile-based 32x32")
clock = pygame.time.Clock()

# ---------------- Cargar CSV ----------------
MAP = []
with open(MAP_CSV, newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        MAP.append([int(x) for x in row])

MAP_HEIGHT = len(MAP)
MAP_WIDTH = len(MAP[0])

# ---------------- Cargar Tileset ----------------
tileset_img = pygame.image.load(TILESET_PNG).convert_alpha()
tileset = []
tileset_w = tileset_img.get_width() // TILE_SIZE
tileset_h = tileset_img.get_height() // TILE_SIZE

for y in range(tileset_h):
    for x in range(tileset_w):
        rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        tile = tileset_img.subsurface(rect)
        tileset.append(tile)

# ---------------- Cargar Player ----------------
player_sheet = pygame.image.load(PLAYER_SHEET).convert_alpha()
frame_w = player_sheet.get_width() // 3
frame_h = player_sheet.get_height() // 4

def get_frames(row):
    return [player_sheet.subsurface((col*frame_w, row*frame_h, frame_w, frame_h)) for col in range(3)]

animations = {
    "down": get_frames(2),
    "up": get_frames(0),
    "left": get_frames(3),
    "right": get_frames(1),
}

# ---------------- Player ----------------
player_tile_x, player_tile_y = 1, 1  # posición inicial en tiles
direction = "down"
frame_index, frame_timer = 0, 0
FRAME_SPEED = 8

# Movimiento por pasos
moving = False
move_dx, move_dy = 0, 0
pixels_moved = 0
STEP_PIXELS = TILE_SIZE // 4  # velocidad dentro de un tile

def can_walk(tile_x, tile_y):
    """True si el tile es caminable"""
    if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
        return MAP[tile_y][tile_x] in WALKABLE
    return False

# ---------------- Loop principal ----------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not moving:  # Solo aceptar nueva dirección si no está en movimiento
        if keys[pygame.K_LEFT]:
            direction = "left"
            if can_walk(player_tile_x - 1, player_tile_y):
                moving = True
                move_dx, move_dy = -STEP_PIXELS, 0
        elif keys[pygame.K_RIGHT]:
            direction = "right"
            if can_walk(player_tile_x + 1, player_tile_y):
                moving = True
                move_dx, move_dy = STEP_PIXELS, 0
        elif keys[pygame.K_UP]:
            direction = "up"
            if can_walk(player_tile_x, player_tile_y - 1):
                moving = True
                move_dx, move_dy = 0, -STEP_PIXELS
        elif keys[pygame.K_DOWN]:
            direction = "down"
            if can_walk(player_tile_x, player_tile_y + 1):
                moving = True
                move_dx, move_dy = 0, STEP_PIXELS

        if moving:
            pixels_moved = 0

    if moving:
        pixels_moved += abs(move_dx) + abs(move_dy)
        if pixels_moved >= TILE_SIZE:  # terminó de recorrer un tile
            moving = False
            pixels_moved = 0
            player_tile_x += (1 if move_dx > 0 else -1 if move_dx < 0 else 0)
            player_tile_y += (1 if move_dy > 0 else -1 if move_dy < 0 else 0)

    # Animación
    if moving:
        frame_timer += 1
        if frame_timer >= FRAME_SPEED:
            frame_index = (frame_index + 1) % len(animations[direction])
            frame_timer = 0
    else:
        frame_index = 1

    # Dibujar mapa
    map_surface = pygame.Surface((MAP_WIDTH*TILE_SIZE, MAP_HEIGHT*TILE_SIZE), pygame.SRCALPHA)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_id = MAP[y][x]
            if 0 <= tile_id < len(tileset):
                map_surface.blit(tileset[tile_id], (x*TILE_SIZE, y*TILE_SIZE))

    # Posición del player en píxeles
    player_px = player_tile_x * TILE_SIZE + (pixels_moved if move_dx != 0 else 0) * (1 if move_dx > 0 else -1 if move_dx < 0 else 0)
    player_py = player_tile_y * TILE_SIZE + (pixels_moved if move_dy != 0 else 0) * (1 if move_dy > 0 else -1 if move_dy < 0 else 0)

    offset_x = player_px - WIDTH//2
    offset_y = player_py - HEIGHT//2
    screen.fill((0,0,0))
    screen.blit(map_surface, (-offset_x, -offset_y))

    frame = animations[direction][frame_index]
    screen.blit(frame, (WIDTH//2, HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
