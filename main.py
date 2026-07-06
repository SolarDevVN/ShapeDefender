import pygame
import sys
import random

from src.enemy_obj import enemy
from src.turret_obj import turret, draw_shape  # Imported generic draw_shape helper

# --- SCREEN SCALE SETTINGS ---
TILE_SIZE = 50  
COLS = 32                    
ROWS = 18

SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE
HEX_SIZE = int(TILE_SIZE * 0.4) 

path_color = (255, 255, 255)
map = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [1,1,1,1,0,0,0,0,1,1,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

def generate_path_from_map(grid_map):
    rows = len(grid_map)
    cols = len(grid_map[0])
    start_row = -1
    for row_index in range(rows):
        if grid_map[row_index][0] == 1:
            start_row = row_index
            break
            
    if start_row == -1:
        print("Warning: No path starting point (1) found in the first column!")
        return []

    path = [(0, start_row)]
    current = (0, start_row)
    visited = {current}

    while True:
        current_x, current_y = current
        neighbors = [
            (current_x + 1, current_y),
            (current_x, current_y + 1),
            (current_x, current_y - 1),
            (current_x - 1, current_y)
        ]
        
        found_next = False
        for neighbor_x, neighbor_y in neighbors:
            if 0 <= neighbor_x < cols and 0 <= neighbor_y < rows:
                if grid_map[neighbor_y][neighbor_x] == 1 and (neighbor_x, neighbor_y) not in visited:
                    current = (neighbor_x, neighbor_y)
                    path.append(current)
                    visited.add(current)
                    found_next = True
                    break
                    
        if not found_next:
            break
            
    return path

grid_path = generate_path_from_map(map)

pixel_path = []
half_tile = TILE_SIZE // 2
for column_index, row_index in grid_path:
    center_x = column_index * TILE_SIZE + half_tile
    center_y = row_index * TILE_SIZE + half_tile
    pixel_path.append(pygame.math.Vector2(center_x, center_y))

# --- PYGAME INITIALIZATION ---
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ShapeDefender")

# Load image after setting display mode to avoid startup crashes
try:
    circle_img = pygame.image.load("assets/Circle Tank.png")
except pygame.error:
    print("Warning: Could not load assets/Circle Tank.png")

enemies: list[enemy] = []
spawn_timer = 0.0
spawn_cooldown = 1.0

placed_turrets = []
placing_mode = False          # Track if preview mode is active
selected_shape = "hexagon"    # Store currently chosen turret type

clock = pygame.time.Clock()
running = True

while running:
    delta_time = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # Use keys 1-4 to change preview shapes
            elif event.key == pygame.K_1:
                placing_mode = True
                selected_shape = "hexagon"
            elif event.key == pygame.K_2:
                placing_mode = True
                selected_shape = "square"
            elif event.key == pygame.K_3:
                placing_mode = True
                selected_shape = "circle"
            elif event.key == pygame.K_4:
                placing_mode = True
                selected_shape = "triangle"
                
            elif event.key == pygame.K_SPACE:
                if placing_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // TILE_SIZE
                    grid_y = mouse_y // TILE_SIZE
                    
                    if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                        if map[grid_y][grid_x] == 0:
                            center_x = grid_x * TILE_SIZE + half_tile
                            center_y = grid_y * TILE_SIZE + half_tile
                            
                            # Mark the map coordinate as occupied
                            map[grid_y][grid_x] = 3
                            
                            # Create a turret passing in the selected shape type
                            new_turret = turret(center_x, center_y, shape_type=selected_shape)
                            
                            # If your turret class requires a .placing() call, execute it
                            if hasattr(new_turret, 'placing'):
                                new_turret.placing()
                                
                            # Append the newly created turret to our active list
                            placed_turrets.append(new_turret)
                            placing_mode = False

    spawn_timer += delta_time
    if spawn_timer >= spawn_cooldown and len(enemies) < 10:
        new_enemy = enemy(random.randint(150, 300), 10, pixel_path)
        enemies.append(new_enemy)
        spawn_timer = 0.0

    screen.fill((0, 0, 0))

    # Render matrix map tiles
    for row_index in range(ROWS):
        for column_index in range(COLS):
            if map[row_index][column_index] == 1:
                pygame.draw.rect(screen, path_color, (column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Render Placed Turrets
    for current_turret in placed_turrets:
        current_turret.draw(screen, HEX_SIZE)

    # Render Snap-to-Grid Faded Preview
    if placing_mode:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE
        if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
            snap_x = grid_x * TILE_SIZE + half_tile
            snap_y = grid_y * TILE_SIZE + half_tile
            
            # Draws a faded preview of whichever shape is selected
            draw_shape(screen, selected_shape, (0, 255, 255), (snap_x, snap_y), HEX_SIZE, alpha=100)

    # Update & Draw active enemies
    for active_enemy in enemies:
        active_enemy.move(delta_time)
        active_enemy.draw(screen)

    enemies = [active_enemy for active_enemy in enemies if active_enemy.waypoint_index < len(pixel_path)]

    pygame.display.flip()

pygame.quit()
sys.exit()