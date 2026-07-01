import pygame
import sys
import random

from src.enemy_obj import enemy

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


# --- AUTO-PATHFINDER FUNCTION ---
def generate_path_from_map(grid_map):
    """
    Scans the grid map, finds the start (left column), 
    and automatically traces the sequence of 1s to the end.
    """
    rows = len(grid_map)
    cols = len(grid_map[0])
    
    # 1. Find where the path starts in the leftmost column (Col 0)
    start_row = -1
    for r in range(rows):
        if grid_map[r][0] == 1:
            start_row = r
            break
            
    if start_row == -1:
        print("Warning: No path starting point (1) found in the first column!")
        return []

    path = [(0, start_row)]
    current = (0, start_row)
    visited = {current} # Keeps track of where we have been so we don't back-track

    while True:
        cx, cy = current
        
        # Check adjacent neighbors in 4 directions: Right, Down, Up, Left
        neighbors = [
            (cx + 1, cy),  # Right
            (cx, cy + 1),  # Down
            (cx, cy - 1),  # Up
            (cx - 1, cy)   # Left
        ]
        
        found_next = False
        for nx, ny in neighbors:
            # Check grid bounds
            if 0 <= nx < cols and 0 <= ny < rows:
                # If neighbor is a path tile (1) and we haven't visited it yet
                if grid_map[ny][nx] == 1 and (nx, ny) not in visited:
                    current = (nx, ny)
                    path.append(current)
                    visited.add(current)
                    found_next = True
                    break # Break neighbor check loop to advance on the path
                    
        # If we couldn't find any unvisited path tile adjacent to us, we reached the end
        if not found_next:
            break
            
    return path


# Auto-discover the path at startup
grid_path = generate_path_from_map(map)

# Convert the automatically generated grid path into pixel coordinates
pixel_path = []
for col, row in grid_path:
    center_x = col * 50 + 25
    center_y = row * 50 + 25
    pixel_path.append(pygame.math.Vector2(center_x, center_y))


pygame.init()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ShapeDefender")

# Active enemy list and configuration
enemies: list[enemy] = []
spawn_timer = 0.0
spawn_cooldown = 1.0  # Spawn an enemy every 1.0 second

clock = pygame.time.Clock()
running = True

while running:
    # Use dt to keep physics independent from framerate
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn timing
    spawn_timer += dt
    if spawn_timer >= spawn_cooldown and len(enemies) < 10:
        new_enemy = enemy(random.randint(150 , 300), 10, pixel_path)
        enemies.append(new_enemy)
        spawn_timer = 0.0

    screen.fill((0, 0, 0))

    # Render matrix map tiles
    for delta_y in range(len(map)):
        for delta_x in range(len(map[0])):
            if map[delta_y][delta_x] == 1:
                pygame.draw.rect(screen, path_color, (delta_x * 50, delta_y * 50, 50, 50))

    # Update & Draw active enemies
    for e in enemies:
        e.move(dt)
        e.draw(screen)

    # Remove enemies that reach the exit of the map
    enemies = [e for e in enemies if e.waypoint_index < len(pixel_path)]

    pygame.display.flip()

pygame.quit()
sys.exit()