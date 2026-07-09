import pygame
import sys
import random
import math

from src.enemy_obj import enemy
from src.turret_obj import turret, draw_shape
from src.type import ShapeTurret, Settings
from src.turret_attack_obj import bullet  # Import our new bullet class

# --- SCREEN SCALE SETTINGS ---
TILE_SIZE = Settings.tile_size
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

enemies: list[enemy] = []
bullets: list[bullet] = []  # List to track active projectiles (Requirement 4)
spawn_timer = 0.0
spawn_cooldown = 1.0

placed_turrets: list[turret] = []
placing_mode = False          
selected_shape = "hexagon"    

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
            
            elif event.key == pygame.K_1:
                placing_mode = True
                selected_shape = ShapeTurret.hexagon
            elif event.key == pygame.K_2:
                placing_mode = True
                selected_shape = ShapeTurret.square
            elif event.key == pygame.K_3:
                placing_mode = True
                selected_shape = ShapeTurret.circle
            elif event.key == pygame.K_4:
                placing_mode = True
                selected_shape = ShapeTurret.triangle
                
            elif event.key == pygame.K_SPACE:
                if placing_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // TILE_SIZE
                    grid_y = mouse_y // TILE_SIZE
                    
                    if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                        if map[grid_y][grid_x] == 0:
                            center_x = grid_x * TILE_SIZE + half_tile
                            center_y = grid_y * TILE_SIZE + half_tile
                            
                            map[grid_y][grid_x] = 3
                            
                            new_turret = turret(center_x, center_y, shape_type=selected_shape)
                            
                            # Give placed turrets a cooldown timer
                            new_turret.cooldown_timer = 0.0
                            
                            if hasattr(new_turret, 'placing'):
                                new_turret.placing(HEX_SIZE)
                                
                            placed_turrets.append(new_turret)
                            placing_mode = False

    # Spawn enemies
    spawn_timer += delta_time
    if spawn_timer >= spawn_cooldown and len(enemies) < 10:
        new_enemy = enemy(random.randint(150, 300), 10, pixel_path)
        # Dynamically set health properties to avoid breaking other files
        new_enemy.max_hp = 100
        new_enemy.hp = 100
        enemies.append(new_enemy)
        spawn_timer = 0.0

    # Move enemies & remove if dead or path is finished (Requirement 4)
    for current_enemy in enemies[:]:
        if hasattr(current_enemy, 'move'):
            van_dang_di_chuyen = current_enemy.move(delta_time)
            
            # Remove enemy if path is finished OR if current HP drops to 0 (Requirement 4)
            if not van_dang_di_chuyen or (hasattr(current_enemy, 'hp') and current_enemy.hp <= 0):
                enemies.remove(current_enemy)

    # Move bullets & process collisions (Requirement 4)
    for current_bullet in bullets[:]:
        current_bullet.move(delta_time)
        
        # Safe memory boundary cleanup
        if current_bullet.x_position < 0 or current_bullet.x_position > SCREEN_WIDTH or current_bullet.y_position < 0 or current_bullet.y_position > SCREEN_HEIGHT:
            bullets.remove(current_bullet)
            continue
            
        # Check collision with enemies (Requirement 4)
        for current_enemy in enemies[:]:
            distance = math.hypot(current_bullet.x_position - current_enemy.x_position, current_bullet.y_position - current_enemy.y_position)
            if distance < 20:
                current_enemy.hp -= current_bullet.damage
                if current_bullet in bullets:
                    bullets.remove(current_bullet)
                break

    screen.fill((0, 0, 0))

    # Render matrix map tiles
    for row_index in range(ROWS):
        for column_index in range(COLS):
            if map[row_index][column_index] == 1:
                pygame.draw.rect(screen, path_color, (column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Render Placed Turrets & Handle target locking rotation with prediction
    for current_turret in placed_turrets:
        if not hasattr(current_turret, "cooldown_timer"):
            current_turret.cooldown_timer = 0.0
            
        # Count down cooldown timer using delta_time (Requirement 2)
        if current_turret.cooldown_timer > 0:
            current_turret.cooldown_timer -= delta_time

        enemies_in_range: list[enemy] = current_turret.construct_enemy_list(enemies)
        
        # ONLY rotate and shoot when cooldown is finished and an enemy is in range
        if len(enemies_in_range) > 0 and current_turret.cooldown_timer <= 0:
            target = enemies_in_range[0]
            
            # Predict targeting angle based on enemy speed and position (Requirement 1 & 2)
            predicted_angle = current_turret.predict_target_position(target, bullet_speed=400)
            
            # Turn turret to face the prediction spot only when shooting
            current_turret.direction = predicted_angle
            if current_turret.have_place and current_turret.original_image is not None:
                current_center = current_turret.rect.center
                current_turret.image = pygame.transform.rotozoom(current_turret.original_image, predicted_angle, 1)
                current_turret.rect = current_turret.image.get_rect(center=current_center)
            
            # Shooting mechanics (Requirement 2)
            new_bullet = bullet(current_turret.x_position, current_turret.y_position, predicted_angle, speed=400, damage=25)
            bullets.append(new_bullet)
            current_turret.cooldown_timer = current_turret.cooldown
        
        current_turret.draw(screen, HEX_SIZE)

    # Draw Enemies and Health Bars
    for current_enemy in enemies:
        if hasattr(current_enemy, 'draw'):
            current_enemy.draw(screen)
            
            # Requirement 3: Draw Black Background and smaller Green Foreground Health Bar
            if hasattr(current_enemy, 'hp') and hasattr(current_enemy, 'max_hp'):
                bar_width = 30
                bar_height = 5
                health_ratio = max(0.0, min(1.0, current_enemy.hp / current_enemy.max_hp))
                
                # 1 Black rectangle and 1 smaller Green rectangle
                pygame.draw.rect(screen, (0, 0, 0), (current_enemy.x_position - 15, current_enemy.y_position - 25, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 255, 0), (current_enemy.x_position - 15, current_enemy.y_position - 25, bar_width * health_ratio, bar_height))

    # Draw Bullets
    for current_bullet in bullets:
        current_bullet.draw(screen)

    # Render Snap-to-Grid Faded Preview
    if placing_mode:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE
        if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
            snap_x = grid_x * TILE_SIZE + half_tile
            snap_y = grid_y * TILE_SIZE + half_tile
            
            draw_shape(screen, selected_shape, (0, 255, 255), (snap_x, snap_y), HEX_SIZE, alpha=100)

    pygame.display.flip()

pygame.quit()
sys.exit()