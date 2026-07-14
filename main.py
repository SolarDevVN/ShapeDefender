# src/main.py

import pygame
import sys
import random
import math

from src.enemy_obj import enemy
from src.turret_obj import turret, draw_shape, load_and_scale_asset
from src.farm_obj import farm  
from src.type import ShapeTurret, Settings
from src.turret_attack_obj import bullet  

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

enemy_types = {
    "circle": {"speed": 130, "damage": 10, "hp": 100, "bounty": 10},
    "square": {"speed": 100, "damage": 15, "hp": 150, "bounty": 15},
    "triangle": {"speed": 160, "damage": 5, "hp": 75, "bounty": 20},
    "pentagon": {"speed": 60, "damage": 25, "hp": 250, "bounty": 35},
    "hexagon": {"speed": 40, "damage": 30, "hp": 500, "bounty": 60}
}

# Entire 2-branch evolutionary pathways mapped out
EVOLUTION_TREE = {
    # --- Eater Tree ---
    ShapeTurret.eater: {
        "next": [ShapeTurret.devourer],
        "cost": 300
    },
    ShapeTurret.devourer: {
        "next": [ShapeTurret.cluster],
        "cost": 600
    },
    ShapeTurret.cluster: {
        "next": [ShapeTurret.omega, ShapeTurret.fracture, ShapeTurret.triple_cluster],
        "cost": 1200
    },
    ShapeTurret.omega: {"next": [], "cost": None},
    ShapeTurret.fracture: {"next": [], "cost": None},
    ShapeTurret.triple_cluster: {"next": [], "cost": None},
    
    # --- Double Tree ---
    ShapeTurret.double: {
        "next": [ShapeTurret.triple, ShapeTurret.tri_way],
        "cost": 300
    },
    ShapeTurret.triple: {
        "next": [ShapeTurret.orchestra],
        "cost": 600
    },
    ShapeTurret.tri_way: {
        "next": [ShapeTurret.five_way, ShapeTurret.six_way],
        "cost": 600
    },
    ShapeTurret.orchestra: {
        "next": [ShapeTurret.super_t],
        "cost": 1200
    },
    ShapeTurret.five_way: {
        "next": [ShapeTurret.scatter],
        "cost": 1200
    },
    ShapeTurret.six_way: {
        "next": [ShapeTurret.eight_way],
        "cost": 1200
    },
    ShapeTurret.eight_way: {
        "next": [ShapeTurret.ultra],
        "cost": 2400
    },
    ShapeTurret.ultra: {
        "next": [ShapeTurret.hyper],
        "cost": 9600  
    },
    ShapeTurret.super_t: {"next": [], "cost": None},
    ShapeTurret.scatter: {"next": [], "cost": None},
    ShapeTurret.hyper: {"next": [], "cost": None}
}

# Base build shop prices (Eater / Double / Farms)
TURRET_PRICES = {
    ShapeTurret.eater: 40,
    ShapeTurret.double: 40,  
    ShapeTurret.farm_t1: 100,
    ShapeTurret.farm_t2: 250
}

# Maximum active farm cap set to 20
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
ui_font = pygame.font.SysFont("Arial", 22)

# --- REFACTORED TO PYGAME SPRITE GROUPS ---
enemies_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
turrets_group = pygame.sprite.Group()
farms_group = pygame.sprite.Group()

spawn_timer = 0.0
spawn_cooldown = 0.5

placing_mode = False          
selected_shape = ShapeTurret.eater    

# Starting money bank set to your massive testing budget (Requirement updated)
money = 100000000000000000000000000000000000000000000000000000000000000000000000

# Base Fortress HP
fortress_hp = 100

# Wave system state variables
current_wave = 1
enemies_spawned_this_wave = 0
wave_size = 5               
wave_state = "spawning"     
wave_timer = 0.0

# Tracks current selected turret to evolve
selected_turret = None

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
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check left clicks to interactively select a turret for upgrades
            mouse_x, mouse_y = pygame.mouse.get_pos()
            clicked_any = False
            for t in turrets_group:
                if t.rect.collidepoint(mouse_x, mouse_y):
                    selected_turret = t
                    clicked_any = True
                    break
            if not clicked_any:
                selected_turret = None  # Deselect if clicked elsewhere

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # Key bindings targeting base shop placements (Eater, Double, Farms)
            elif event.key == pygame.K_1:
                placing_mode = True
                selected_shape = ShapeTurret.double  
            elif event.key == pygame.K_3:
                placing_mode = True
                selected_shape = ShapeTurret.eater
            elif event.key == pygame.K_5:
                placing_mode = True
                selected_shape = ShapeTurret.farm_t1
            elif event.key == pygame.K_6:
                placing_mode = True
                selected_shape = ShapeTurret.farm_t2
                
            # Press '0' key to delete/sell selected assets
            elif event.key == pygame.K_0:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    if map[grid_y][grid_x] == 3:
                        map[grid_y][grid_x] = 0  
                        cx = grid_x * TILE_SIZE + half_tile
                        cy = grid_y * TILE_SIZE + half_tile
                        
                        # Remove from Sprite Groups
                        for t in list(turrets_group):
                            if t.x_position == cx and t.y_position == cy:
                                t.kill()
                                if selected_turret == t:
                                    selected_turret = None
                        for f in list(farms_group):
                            if f.x_position == cx and f.y_position == cy:
                                f.kill()
                
            elif event.key == pygame.K_SPACE:
                if placing_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // TILE_SIZE
                    grid_y = mouse_y // TILE_SIZE
                    
                    if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                        if map[grid_y][grid_x] == 0:
                            cost = TURRET_PRICES[selected_shape]
                            
                            is_placing_farm = selected_shape in [ShapeTurret.farm_t1, ShapeTurret.farm_t2]
                            if is_placing_farm and len(farms_group) >= MAX_FARMS:
                                continue
                                
                            if money >= cost:
                                money -= cost
                                center_x = grid_x * TILE_SIZE + half_tile
                                center_y = grid_y * TILE_SIZE + half_tile
                                
                                map[grid_y][grid_x] = 3
                                
                                # Instantiations append directly into Groups
                                if is_placing_farm:
                                    new_farm = farm(center_x, center_y, selected_shape)
                                    farms_group.add(new_farm)
                                else:
                                    new_turret = turret(center_x, center_y, shape_type=selected_shape)
                                    new_turret.cooldown_timer = 0.0
                                    new_turret.placing(HEX_SIZE)
                                    turrets_group.add(new_turret)
                                    
                                placing_mode = False

            # Unified evolutionary branching triggers bound to keyboard events
            elif selected_turret is not None:
                current_type = selected_turret.shape_type
                node = EVOLUTION_TREE.get(current_type)
                
                if node and len(node["next"]) > 0:
                    evolve_cost = node["cost"]
                    if money >= evolve_cost:
                        # --- Eater Branch Triggers ---
                        if current_type == ShapeTurret.eater and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.devourer
                            selected_turret.original_image = None  
                        elif current_type == ShapeTurret.devourer and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.cluster
                            selected_turret.original_image = None
                        elif current_type == ShapeTurret.cluster:
                            if event.key == pygame.K_7:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.omega
                                selected_turret.original_image = None
                            elif event.key == pygame.K_8:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.fracture
                                selected_turret.original_image = None
                            elif event.key == pygame.K_9:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.triple_cluster
                                selected_turret.original_image = None
                                
                        # --- Double Branch Triggers ---
                        elif current_type == ShapeTurret.double:
                            if event.key == pygame.K_7:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.triple
                                selected_turret.original_image = None
                            elif event.key == pygame.K_8:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.tri_way
                                selected_turret.original_image = None
                                
                        elif current_type == ShapeTurret.triple and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.orchestra
                            selected_turret.original_image = None
                            
                        elif current_type == ShapeTurret.tri_way:
                            if event.key == pygame.K_7:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.five_way
                                selected_turret.original_image = None
                            elif event.key == pygame.K_8:
                                money -= evolve_cost
                                selected_turret.shape_type = ShapeTurret.six_way
                                selected_turret.original_image = None
                                
                        elif current_type == ShapeTurret.orchestra and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.super_t
                            selected_turret.original_image = None
                            
                        elif current_type == ShapeTurret.five_way and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.scatter
                            selected_turret.original_image = None
                            
                        elif current_type == ShapeTurret.six_way and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.eight_way
                            selected_turret.original_image = None
                            
                        elif current_type == ShapeTurret.eight_way and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.ultra
                            selected_turret.original_image = None
                            
                        elif current_type == ShapeTurret.ultra and event.key == pygame.K_u:
                            money -= evolve_cost
                            selected_turret.shape_type = ShapeTurret.hyper
                            selected_turret.original_image = None

    # --- WAVE SYSTEM STATE MACHINE ---
    if wave_state == "spawning":
        spawn_timer += delta_time
        if spawn_timer >= spawn_cooldown and enemies_spawned_this_wave < wave_size:
            speed, damage, hp, spawning_type = enemy_randomizer()
            hp_modifier = 1.0 + (current_wave - 1) * 0.3
            scaled_hp = int(hp * hp_modifier)
            
            new_enemy = enemy(speed, damage, pixel_path, select_type=spawning_type, hp=scaled_hp)
            enemies_group.add(new_enemy)
            enemies_spawned_this_wave += 1
            spawn_timer = 0.0
            
        if enemies_spawned_this_wave >= wave_size:
            wave_state = "clearing"

    elif wave_state == "clearing":
        if len(enemies_group) == 0:
            wave_state = "intermission"
            wave_timer = 5.0  

    elif wave_state == "intermission":
        wave_timer -= delta_time
        if wave_timer <= 0.0:
            current_wave += 1
            wave_size = 5 + (current_wave * 2)  
            enemies_spawned_this_wave = 0
            wave_state = "spawning"

    # --- UPDATE POSITIONS USING GROUPS ---
    for current_enemy in list(enemies_group):
        van_dang_di_chuyen = current_enemy.move(delta_time)
        if not van_dang_di_chuyen:
            fortress_hp -= current_enemy.damage
            current_enemy.kill()

    # Move bullets and pass group reference
    for current_bullet in list(bullets_group):
        current_bullet.move(delta_time, bullets_group)
        if current_bullet.x_position < 0 or current_bullet.x_position > SCREEN_WIDTH or current_bullet.y_position < 0 or current_bullet.y_position > SCREEN_HEIGHT:
            current_bullet.kill()

    # Passive Farm Earnings Loop
    for current_farm in farms_group:
        income = current_farm.update(delta_time)
        money += income

    # Target finding and cooling updates for Turrets group
    for current_turret in turrets_group:
        if current_turret.cooldown_timer > 0:
            current_turret.cooldown_timer -= delta_time

        if current_turret.cooldown_timer <= 0:
            enemies_in_range = current_turret.construct_enemy_list(enemies_group)

            if len(enemies_in_range) > 0:
                target = enemies_in_range[0]
                predicted_angle = current_turret.predict_target_position(target, bullet_speed=400)
                current_turret.point_toward(target.x_position, target.y_position)
                
                current_turret.shoot(bullets_group, predicted_angle)
                current_turret.cooldown_timer = current_turret.cooldown

    # Collision updates utilizing Group methods
    for current_bullet in list(bullets_group):
        collided_enemies = pygame.sprite.spritecollide(current_bullet, enemies_group, False)
        if len(collided_enemies) > 0:
            hit_target = collided_enemies[0]
            hit_target.hp -= current_bullet.damage
            
            # Triggers explode mini-bullets if this is an evolution class projectile (unless it is piercing Hyper)
            if current_bullet.bullet_type != "hyper":
                current_bullet.trigger_explosion(bullets_group)
                current_bullet.kill()
            else:
                # If Hyper bullet, don't delete on first hit (Piercing mechanics)
                pass
            
            if hit_target.hp <= 0:
                bounty = enemy_types.get(hit_target.type, {}).get("bounty", 10)
                money += bounty
                hit_target.kill()

    # --- DRAW BACKGROUND (Reverted to classic vector path render) ---
    screen.fill((0, 0, 0))
    for row_index in range(ROWS):
        for column_index in range(COLS):
            if map[row_index][column_index] == 1:
                pygame.draw.rect(screen, path_color, (column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # --- DRAW ALL SPRITE GROUPS ---
    farms_group.draw(screen)
    enemies_group.draw(screen)
    bullets_group.draw(screen)
    
    # Manually draw turrets because we handle rendering self-placed sprites
    for current_turret in turrets_group:
        current_turret.draw(screen, HEX_SIZE)

    # Render Enemies Health Bars
    for current_enemy in enemies_group:
        bar_width = 30
        bar_height = 5
        health_ratio = max(0.0, min(1.0, current_enemy.hp / current_enemy.max_hp))
        pygame.draw.rect(screen, (0, 0, 0), (current_enemy.x_position - 15, current_enemy.y_position - 25, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (current_enemy.x_position - 15, current_enemy.y_position - 25, bar_width * health_ratio, bar_height))

    # Render Snap-to-Grid Placing Preview
    if placing_mode:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE
        if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
            snap_x = grid_x * TILE_SIZE + half_tile
            snap_y = grid_y * TILE_SIZE + half_tile
            draw_shape(screen, selected_shape, (0, 255, 255), (snap_x, snap_y), HEX_SIZE, alpha=100)

    # --- DRAW ON-SCREEN UI PANELS ---
    money_label = ui_font.render(f"Money: ${int(money)}", True, (255, 215, 0))
    screen.blit(money_label, (10, 10))
    
    # Render Wave & Base Fortress Health Displays
    wave_label = ui_font.render(f"Wave: {current_wave}", True, (255, 255, 255))
    screen.blit(wave_label, (10, 40))
    
    fortress_label = ui_font.render(f"Fortress HP: {fortress_hp}", True, (255, 50, 50))
    screen.blit(fortress_label, (10, 70))
    
    if wave_state == "intermission":
        pause_label = ui_font.render(f"Next Wave in: {int(wave_timer + 1)}s", True, (0, 255, 255))
        screen.blit(pause_label, (SCREEN_WIDTH // 2 - 100, 10))
    
    if placing_mode:
        price = TURRET_PRICES[selected_shape]
        color = (0, 255, 0) if money >= price else (255, 50, 50)
        is_placing_farm = selected_shape in [ShapeTurret.farm_t1, ShapeTurret.farm_t2]
        if is_placing_farm and len(farms_group) >= MAX_FARMS:
            cost_label = ui_font.render(f"FARM LIMIT REACHED ({MAX_FARMS} Max)", True, (255, 50, 50))
        else:
            cost_label = ui_font.render(f"Cost: ${price} (Place with SPACE)", True, color)
        screen.blit(cost_label, (10, 100))

    # --- DRAW INTERACTIVE EVOLUTION UI PANEL ---
    if selected_turret is not None:
        current_type = selected_turret.shape_type
        node = EVOLUTION_TREE.get(current_type)
        
        # Draw translucent grey background UI box
        pygame.draw.rect(screen, (30, 30, 30), (0, 500, SCREEN_WIDTH, 100))
        pygame.draw.rect(screen, (100, 100, 100), (0, 500, SCREEN_WIDTH, 100), 2)
        
        name_lbl = ui_font.render(f"Selected: {current_type}", True, (0, 255, 255))
        screen.blit(name_lbl, (20, 510))
        
        if node and len(node["next"]) > 0:
            evolve_cost = node["cost"]
            color = (0, 255, 0) if money >= evolve_cost else (255, 50, 50)
            
            # Render evolution options
            if len(node["next"]) == 1:
                next_class = node["next"][0]
                cost_lbl = ui_font.render(f"Evolve to: {next_class} | Cost: ${evolve_cost} (Press 'U')", True, color)
                screen.blit(cost_lbl, (20, 550))
                
                # Render a small scaled preview image of the next class
                preview_img = load_and_scale_asset(next_class, 15)
                if preview_img:
                    screen.blit(preview_img, (SCREEN_WIDTH - 150, 515))
            
            elif current_type == ShapeTurret.cluster:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_omega = ui_font.render("[7] Omega", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_frac = ui_font.render("[8] Fracture", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_triple = ui_font.render("[9] Triple Cluster", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_omega, (20, 570))
                screen.blit(lbl_frac, (150, 570))
                screen.blit(lbl_triple, (300, 570))
                
                # Render previews of all three branch choices
                img_o = load_and_scale_asset(ShapeTurret.omega, 15)
                img_f = load_and_scale_asset(ShapeTurret.fracture, 15)
                img_tc = load_and_scale_asset(ShapeTurret.triple_cluster, 15)
                
                if img_o: screen.blit(img_o, (SCREEN_WIDTH - 250, 515))
                if img_f: screen.blit(img_f, (SCREEN_WIDTH - 170, 515))
                if img_tc: screen.blit(img_tc, (SCREEN_WIDTH - 90, 515))
                
            elif current_type == ShapeTurret.double:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_triple = ui_font.render("[7] Triple", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_triway = ui_font.render("[8] Tri-Way", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_triple, (20, 570))
                screen.blit(lbl_triway, (150, 570))
                
                img_tr = load_and_scale_asset(ShapeTurret.triple, 15)
                img_tw = load_and_scale_asset(ShapeTurret.tri_way, 15)
                
                if img_tr: screen.blit(img_tr, (SCREEN_WIDTH - 170, 515))
                if img_tw: screen.blit(img_tw, (SCREEN_WIDTH - 90, 515))
                
            elif current_type == ShapeTurret.tri_way:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_five = ui_font.render("[7] Five-Way", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_six = ui_font.render("[8] Six-Way", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_five, (20, 570))
                screen.blit(lbl_six, (150, 570))
                
                img_five = load_and_scale_asset(ShapeTurret.five_way, 15)
                img_six = load_and_scale_asset(ShapeTurret.six_way, 15)
                
                if img_five: screen.blit(img_five, (SCREEN_WIDTH - 170, 515))
                if img_six: screen.blit(img_six, (SCREEN_WIDTH - 90, 515))
        else:
            max_lbl = ui_font.render("Evolution Path: MAX TIER REACHED!", True, (0, 255, 0))
            screen.blit(max_lbl, (20, 550))

    pygame.display.flip()

pygame.quit()
sys.exit()