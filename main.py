# src/main.py

import pygame
import sys
import random
import math

from src.enemy_obj import enemy
from src.turret_obj import turret, draw_shape
from src.farm_obj import farm  # Import our new farm class
from src.type import ShapeTurret, Settings
from src.turret_attack_obj import bullet  # Import our bullet class

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

# Configured custom bounty money drops per enemy shape type (Requirement updated)
enemy_types = {
    "circle": {"speed": 130, "damage": 10, "hp": 100, "bounty": 10},
    "square": {"speed": 100, "damage": 15, "hp": 150, "bounty": 15},
    "triangle": {"speed": 160, "damage": 5, "hp": 75, "bounty": 20},
    "pentagon": {"speed": 60, "damage": 25, "hp": 250, "bounty": 35},
    "hexagon": {"speed": 40, "damage": 30, "hp": 500, "bounty": 60}
}

# Raised buying prices for all turrets and farms
TURRET_PRICES = {
    ShapeTurret.circle: 50,
    ShapeTurret.square: 100,
    ShapeTurret.triangle: 250,
    ShapeTurret.hexagon: 500,
    ShapeTurret.farm_t1: 100,
    ShapeTurret.farm_t2: 250
}

# Maximum active farm cap increased to 20
MAX_FARMS = 20

def enemy_randomizer():
    enemy_type = random.choice(list(enemy_types.keys()))
    attributes = enemy_types[enemy_type]
    return attributes["speed"], attributes["damage"], attributes["hp"], enemy_type

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
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ShapeDefender")
ui_font = pygame.font.SysFont("Arial", 24)

enemies: list[enemy] = []
bullets: list[bullet] = []  # List to track active projectiles (Requirement 4)
spawn_timer = 0.0
spawn_cooldown = 0.5

placed_turrets: list[turret] = []
placed_farms: list[farm] = []  # List to track active income farms
placing_mode = False          
selected_shape = "hexagon"    

# Starting money bank set to 200
money = 200

# Base Fortress HP
fortress_hp = 100

# Wave system state variables
current_wave = 1
enemies_spawned_this_wave = 0
wave_size = 5               # Spawn count starts at 5
wave_state = "spawning"     # Can be: "spawning", "clearing", "intermission"
wave_timer = 0.0

clock = pygame.time.Clock()
running = True

while running:
    delta_time = clock.tick(60) / 1000.0

    # --- GAME OVER STATE HANDLER ---
    if fortress_hp <= 0:
        screen.fill((20, 20, 20))
        game_over_label = ui_font.render("GAME OVER - The Fortress has Fallen!", True, (255, 50, 50))
        exit_label = ui_font.render("Press any key to exit.", True, (150, 150, 150))
        screen.blit(game_over_label, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20))
        screen.blit(exit_label, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()
        
        # Halt execution, wait for key input to cleanly terminate
        waiting_for_exit = True
        while waiting_for_exit:
            for event in pygame.event.get():
                if event.type in [pygame.QUIT, pygame.KEYDOWN]:
                    pygame.quit()
                    sys.exit()
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # Key bindings for selecting placeable assets
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
            elif event.key == pygame.K_5:
                placing_mode = True
                selected_shape = ShapeTurret.farm_t1
            elif event.key == pygame.K_6:
                placing_mode = True
                selected_shape = ShapeTurret.farm_t2
                
            # Press '0' key to delete/sell turret or farm on mouse hover
            elif event.key == pygame.K_0:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    if map[grid_y][grid_x] == 3:
                        map[grid_y][grid_x] = 0  # Revert grid tile back to empty
                        cx = grid_x * TILE_SIZE + half_tile
                        cy = grid_y * TILE_SIZE + half_tile
                        
                        # In-place clean matching structures from list
                        placed_turrets[:] = [t for t in placed_turrets if not (t.x_position == cx and t.y_position == cy)]
                        placed_farms[:] = [f for f in placed_farms if not (f.x_position == cx and f.y_position == cy)]
                
            elif event.key == pygame.K_SPACE:
                if placing_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // TILE_SIZE
                    grid_y = mouse_y // TILE_SIZE
                    
                    if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                        if map[grid_y][grid_x] == 0:
                            cost = TURRET_PRICES[selected_shape]
                            
                            is_placing_farm = selected_shape in [ShapeTurret.farm_t1, ShapeTurret.farm_t2]
                            if is_placing_farm and len(placed_farms) >= MAX_FARMS:
                                # Block placing if farm threshold has reached 20
                                continue
                                
                            if money >= cost:
                                money -= cost
                                center_x = grid_x * TILE_SIZE + half_tile
                                center_y = grid_y * TILE_SIZE + half_tile
                                
                                map[grid_y][grid_x] = 3
                                
                                # Decide if we should place a farm or a combat turret
                                if is_placing_farm:
                                    new_farm = farm(center_x, center_y, selected_shape)
                                    placed_farms.append(new_farm)
                                else:
                                    new_turret = turret(center_x, center_y, shape_type=selected_shape)
                                    new_turret.cooldown_timer = 0.0
                                    new_turret.placing(HEX_SIZE)
                                    placed_turrets.append(new_turret)
                                    
                                placing_mode = False

    # --- WAVE SYSTEM STATE MACHINE ---
    if wave_state == "spawning":
        spawn_timer += delta_time
        if spawn_timer >= spawn_cooldown and enemies_spawned_this_wave < wave_size:
            speed, damage, hp, spawning_type = enemy_randomizer()
            
            # Enemy HP increases by 30% per wave to make it harder
            hp_modifier = 1.0 + (current_wave - 1) * 0.3
            scaled_hp = int(hp * hp_modifier)
            
            new_enemy = enemy(speed, damage, pixel_path, select_type=spawning_type, hp=scaled_hp)
            enemies.append(new_enemy)
            enemies_spawned_this_wave += 1
            spawn_timer = 0.0
            
        if enemies_spawned_this_wave >= wave_size:
            wave_state = "clearing"

    elif wave_state == "clearing":
        # Wait until all active spawned enemies are fully destroyed
        if len(enemies) == 0:
            wave_state = "intermission"
            wave_timer = 5.0  # Reset intermission countdown to exactly 5 seconds

    elif wave_state == "intermission":
        wave_timer -= delta_time
        if wave_timer <= 0.0:
            # Advance wave progression and reset states
            current_wave += 1
            wave_size = 5 + (current_wave * 2)  # Scale up spawning volumes
            enemies_spawned_this_wave = 0
            wave_state = "spawning"

    # Move enemies & check if they leaked
    for current_enemy in enemies[:]:
        van_dang_di_chuyen = current_enemy.move(delta_time)
        if not van_dang_di_chuyen:
            # Enemy leaked! Deduct base Fortress Health
            fortress_hp -= current_enemy.damage
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
                if current_enemy.hp <= 0:
                    # Grant bounty reward money based on enemy shape (Requirement updated)
                    bounty = enemy_types.get(current_enemy.type, {}).get("bounty", 10)
                    money += bounty
                    enemies.remove(current_enemy)
                break

    screen.fill((0, 0, 0))

    # Render matrix map tiles
    for row_index in range(ROWS):
        for column_index in range(COLS):
            if map[row_index][column_index] == 1:
                pygame.draw.rect(screen, path_color, (column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Update and draw placed Farms
    for current_farm in placed_farms:
        income = current_farm.update(delta_time)
        money += income
        current_farm.draw(screen)

    # Render Placed Turrets & Handle targeting
    for current_turret in placed_turrets:
        # Count down cooldown timer using delta_time (Requirement 2)
        if current_turret.cooldown_timer > 0:
            current_turret.cooldown_timer -= delta_time

        # If turret is ready to shoot, look for a target
        if current_turret.cooldown_timer <= 0:
            enemies_in_range: list[enemy] = current_turret.construct_enemy_list(enemies)

            if len(enemies_in_range) > 0:
                target = enemies_in_range[0]
                
                # Predict targeting angle based on enemy speed and position (Requirement 1 & 2)
                predicted_angle = current_turret.predict_target_position(target, bullet_speed=400)
                
                # Turn turret to face the prediction spot only when shooting
                current_turret.direction = predicted_angle
                if current_turret.have_place and current_turret.original_image is not None:
                    current_center = current_turret.rect.center
                    current_turret.image = pygame.transform.rotozoom(current_turret.original_image, predicted_angle, 1)
                    current_turret.rect = current_turret.image.get_rect(center=current_center)
                
                # Trigger the unique firing pattern (Requirement 2 updated)
                current_turret.shoot(bullets, predicted_angle)
                current_turret.cooldown_timer = current_turret.cooldown
        
        current_turret.draw(screen, HEX_SIZE)

    # Draw Enemies and Health Bars
    for current_enemy in enemies:
        current_enemy.draw(screen)
        
        # Requirement 3: Draw Black Background and smaller Green Foreground Health Bar
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

    # --- RENDER ON-SCREEN UI COUNTER ---
    money_label = ui_font.render(f"Money: ${int(money)}", True, (255, 215, 0))
    screen.blit(money_label, (10, 10))
    
    # Render Wave & Base Fortress Health Displays
    wave_label = ui_font.render(f"Wave: {current_wave}", True, (255, 255, 255))
    screen.blit(wave_label, (10, 40))
    
    fortress_label = ui_font.render(f"Fortress HP: {fortress_hp}", True, (255, 50, 50))
    screen.blit(fortress_label, (10, 70))
    
    # 5-second pause intermission visual warning countdown
    if wave_state == "intermission":
        pause_label = ui_font.render(f"Next Wave in: {int(wave_timer + 1)}s", True, (0, 255, 255))
        screen.blit(pause_label, (SCREEN_WIDTH // 2 - 100, 10))
    
    if placing_mode:
        # Display the price of the active placement preview
        price = TURRET_PRICES[selected_shape]
        color = (0, 255, 0) if money >= price else (255, 50, 50)
        
        # Check if currently blocked by the farm cap
        is_placing_farm = selected_shape in [ShapeTurret.farm_t1, ShapeTurret.farm_t2]
        if is_placing_farm and len(placed_farms) >= MAX_FARMS:
            cost_label = ui_font.render(f"FARM LIMIT REACHED ({MAX_FARMS} Max)", True, (255, 50, 50))
        else:
            cost_label = ui_font.render(f"Cost: ${price} (Place with SPACE)", True, color)
            
        screen.blit(cost_label, (10, 100))

    pygame.display.flip()

pygame.quit()
sys.exit()