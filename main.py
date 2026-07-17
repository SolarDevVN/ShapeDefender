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
    "hexagon": {"speed": 40, "damage": 30, "hp": 500, "bounty": 60},
    
    # Newly introduced specialized ranks
    "diamond": {"speed": 280, "damage": 10, "hp": 60, "bounty": 25},            
    "star": {"speed": 100, "damage": 20, "hp": 180, "bounty": 40},              
    "octagon": {"speed": 100, "damage": 40, "hp": 800, "bounty": 100},           
    "dodecagon": {"speed": 30, "damage": 100, "hp": 3000, "bounty": 500}        
}

# Unified 4-branch evolutionary pathways mapped out
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
        "cost": 30000  
    },
    ShapeTurret.super_t: {"next": [], "cost": None},
    ShapeTurret.scatter: {"next": [], "cost": None},
    ShapeTurret.hyper: {"next": [], "cost": None},

    # --- Scout Tree ---
    ShapeTurret.scout: {
        "next": [ShapeTurret.hitman],
        "cost": 300
    },
    ShapeTurret.hitman: {
        "next": [ShapeTurret.scoper],
        "cost": 600
    },
    ShapeTurret.scoper: {
        "next": [ShapeTurret.watcher, ShapeTurret.railgun],
        "cost": 1200
    },
    ShapeTurret.watcher: {
        "next": [ShapeTurret.agent],
        "cost": 2400
    },
    ShapeTurret.agent: {"next": [], "cost": None},
    ShapeTurret.railgun: {
        "next": [ShapeTurret.double_railgun],
        "cost": 2400
    },
    ShapeTurret.double_railgun: {
        "next": [ShapeTurret.triple_railgun],
        "cost": 9600
    },
    ShapeTurret.triple_railgun: {"next": [], "cost": None},

    # --- Chaser Tree ---
    ShapeTurret.chaser: {
        "next": [ShapeTurret.banana_chaser, ShapeTurret.triple_chaser],
        "cost": 300
    },
    ShapeTurret.banana_chaser: {
        "next": [ShapeTurret.mega_chaser],
        "cost": 600
    },
    ShapeTurret.mega_chaser: {
        "next": [ShapeTurret.gladiator],
        "cost": 1200
    },
    ShapeTurret.gladiator: {
        "next": [ShapeTurret.fortress],
        "cost": 2400
    },
    ShapeTurret.triple_chaser: {
        "next": [ShapeTurret.ultra_chaser],
        "cost": 600
    },
    ShapeTurret.ultra_chaser: {
        "next": [ShapeTurret.espresso],
        "cost": 1200
    },
    ShapeTurret.espresso: {
        "next": [ShapeTurret.emperor],
        "cost": 2400
    },
    ShapeTurret.fortress: {"next": [], "cost": None},
    ShapeTurret.emperor: {"next": [], "cost": None}
}

# Base build shop prices (Double / Scout / Eater / Chaser / Farms)
TURRET_PRICES = {
    ShapeTurret.double: 40,
    ShapeTurret.scout: 40,
    ShapeTurret.eater: 40,
    ShapeTurret.chaser: 40,  
    ShapeTurret.farm_t1: 100,
    ShapeTurret.farm_t2: 250
}

# Maximum active farm cap set to 20
MAX_FARMS = 20
MAX_TURRETS = 30

def enemy_randomizer(is_boss=False, is_miniboss=False):
    """
    Spawns wave-based mini-bosses or dodecagon raid bosses.
    Dynamically unlocks enemy classes based on wave progression.
    Enforces a strict 5-star active on-screen threshold (Requirement updated).
    """
    if is_boss:
        attributes = enemy_types["dodecagon"]
        return attributes["speed"], attributes["damage"], attributes["hp"], "dodecagon"
    elif is_miniboss:
        attributes = enemy_types["octagon"]
        return attributes["speed"], attributes["damage"], attributes["hp"], "octagon"
        
    # Start with circle and square, then unlock others progressively
    pool = ["circle", "square"]
    if current_wave >= 3:
        pool.extend(["triangle", "pentagon", "hexagon"])
    if current_wave >= 5:
        # Check current active Star count on screen (Requirement updated)
        star_count = sum(1 for e in enemies_group if e.type == "star" and e.alive())
        if star_count < 5:
            pool.extend(["diamond", "star"])
        else:
            pool.append("diamond") # Skip star to prevent endless stun locks!
        
    enemy_type = random.choice(pool)
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

# Starting money bank set to your massive testing budget (Adjust for balanced run!)
money = 100000000000000000000000000000000000000000000000000000000000000000000000

# Base Fortress HP
fortress_hp = 100

# Wave system state variables
current_wave = 1
wave_state = "spawning"     
wave_timer = 0.0

# Active spawn queue and automatic skips
spawn_queue = []
auto_skip = False
auto_skip_timer = 0.0

# Tracks current selected turret to evolve
selected_turret = None

# Game state handlers
game_state = "playing"  # Can be: "playing", "gameover", "index"

# UI Font Render Cache variables
last_money = -1
last_wave = -1
last_fortress_hp = -1
last_auto_skip = None

money_surf = None
wave_surf = None
fortress_surf = None
autoskip_surf = None

def queue_wave(wave_num):
    """
    Assembles wave assets and packages them into the active spawn queue.
    """
    size = 5 + (wave_num * 2)
    
    # Raid boss only spawns from Wave 20 onwards, every 10 waves (Requirement updated)
    is_boss_wave = (wave_num >= 20 and wave_num % 10 == 0)
    # Mini-boss only spawns from Wave 10 onwards, at the end of every wave (Requirement updated)
    is_miniboss_wave = (wave_num >= 10)
    
    for i in range(size):
        is_last = (i == size - 1)
        if is_boss_wave and is_last:
            speed, damage, hp, spawning_type = enemy_randomizer(is_boss=True)
        elif is_miniboss_wave and is_last:
            speed, damage, hp, spawning_type = enemy_randomizer(is_miniboss=True)
        else:
            speed, damage, hp, spawning_type = enemy_randomizer()
            
        hp_modifier = 1.0 + (wave_num - 1) * 0.3
        scaled_hp = int(hp * hp_modifier)
        
        speed_modifier = 1.0 + (wave_num - 1) * 0.05
        scaled_speed = int(speed * speed_modifier)
        
        spawn_queue.append({
            "speed": scaled_speed,
            "damage": damage,
            "hp": scaled_hp,
            "type": spawning_type
        })

# Pre-queue Wave 1
queue_wave(current_wave)

clock = pygame.time.Clock()
running = True

while running:
    delta_time = clock.tick(60) / 1000.0

    # --- GAME OVER STATE HANDLER ---
    if game_state == "gameover":
        screen.fill((20, 20, 20))
        game_over_label = ui_font.render("GAME OVER - The Fortress has Fallen!", True, (255, 50, 50))
        exit_label = ui_font.render("Press any key to exit.", True, (150, 150, 150))
        screen.blit(game_over_label, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20))
        screen.blit(exit_label, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()
        
        # Halt standard iteration but allow key events to terminate the game safely
        for event in pygame.event.get():
            if event.type in [pygame.QUIT, pygame.KEYDOWN]:
                running = False
        continue

    # --- INTERACTIVE INDEX GUIDE MENU OVERLAY ---
    elif game_state == "index":
        screen.fill((15, 15, 15))
        title_lbl = ui_font.render("=== shape evolution index ===", True, (255, 215, 0))
        screen.blit(title_lbl, (SCREEN_WIDTH // 2 - 120, 20))
        
        col1_y = 70
        screen.blit(ui_font.render("[ EATER BRANCH ]", True, (0, 191, 255)), (50, col1_y))
        screen.blit(ui_font.render("Eater -> Devourer ($300) -> Cluster ($600) -> Omega/Fracture/Triple ($1200)", True, (200, 200, 200)), (50, col1_y + 30))
        
        screen.blit(ui_font.render("[ DOUBLE BRANCH ]", True, (255, 165, 0)), (50, col1_y + 90))
        screen.blit(ui_font.render("Double -> Triple / Tri-Way ($300)", True, (200, 200, 200)), (50, col1_y + 120))
        screen.blit(ui_font.render("Triple -> Orchestra ($600) -> Super ($1200)", True, (200, 200, 200)), (50, col1_y + 150))
        screen.blit(ui_font.render("Tri-Way -> Five-Way / Six-Way ($600) | Five-Way -> Scatter ($1200)", True, (200, 200, 200)), (50, col1_y + 180))
        screen.blit(ui_font.render("Six-Way -> Eight-Way ($1200) -> Ultra ($2400) -> Hyper ($30000)", True, (200, 200, 200)), (50, col1_y + 210))
        
        screen.blit(ui_font.render("[ SCOUT BRANCH ]", True, (154, 205, 50)), (50, col1_y + 270))
        screen.blit(ui_font.render("Scout -> Hitman ($300) -> Scoper ($600) -> Watcher / Railgun ($1200)", True, (200, 200, 200)), (50, col1_y + 300))
        screen.blit(ui_font.render("Watcher -> Agent ($2400) | Railgun -> Double Railgun ($2400) -> Triple Railgun ($9600)", True, (200, 200, 200)), (50, col1_y + 330))
        
        screen.blit(ui_font.render("[ CHASER BRANCH ]", True, (255, 105, 180)), (50, col1_y + 390))
        screen.blit(ui_font.render("Chaser -> Banana Chaser / Triple Chaser ($300)", True, (200, 200, 200)), (50, col1_y + 420))
        screen.blit(ui_font.render("Banana Chaser -> Mega Chaser ($600) -> Gladiator ($1200) -> Fortress ($2400)", True, (200, 200, 200)), (50, col1_y + 450))
        screen.blit(ui_font.render("Triple Chaser -> Ultra Chaser ($600) -> Espresso ($1200) -> Emperor ($2400)", True, (200, 200, 200)), (50, col1_y + 480))
        
        esc_lbl = ui_font.render("Press 'I' to exit index guide", True, (255, 50, 50))
        screen.blit(esc_lbl, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 40))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                game_state = "playing"
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left-click triggers placement OR selection depending on placing mode
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if placing_mode:
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    if map[grid_y][grid_x] == 0:
                        cost = TURRET_PRICES[selected_shape]
                        is_placing_farm = selected_shape in [ShapeTurret.farm_t1, ShapeTurret.farm_t2]
                        
                        # Restrict placement if trying to exceed maximum turret limits (Requirement updated)
                        if not is_placing_farm and len(turrets_group) >= MAX_TURRETS:
                            continue
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
            else:
                # Left-click selection on placed turrets
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
            
            # Index Guide toggling
            elif event.key == pygame.K_i:
                game_state = "index"
            
            # Key bindings targeting base shop placements (Double, Scout, Eater, Chaser, Farms)
            elif event.key == pygame.K_1:
                placing_mode = True
                selected_shape = ShapeTurret.double  
            elif event.key == pygame.K_2:
                placing_mode = True
                selected_shape = ShapeTurret.scout  
            elif event.key == pygame.K_3:
                placing_mode = True
                selected_shape = ShapeTurret.eater
            elif event.key == pygame.K_4:
                placing_mode = True
                selected_shape = ShapeTurret.chaser  
            elif event.key == pygame.K_5:
                placing_mode = True
                selected_shape = ShapeTurret.farm_t1
            elif event.key == pygame.K_6:
                placing_mode = True
                selected_shape = ShapeTurret.farm_t2
                
            # Press 'A' key to toggle Auto-Skip ON or OFF
            elif event.key == pygame.K_a:
                auto_skip = not auto_skip

            # Press 'N' key to manually SKIP wave immediately (High Risk)
            elif event.key == pygame.K_n:
                current_wave += 1
                queue_wave(current_wave)
                auto_skip_timer = 0.0

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

            # Unified evolutionary branching triggers bound to keyboard events (Requirement updated)
            elif selected_turret is not None:
                current_type = selected_turret.shape_type
                node = EVOLUTION_TREE.get(current_type)
                
                if node and len(node["next"]) > 0:
                    evolve_cost = node["cost"]
                    if money >= evolve_cost:
                        next_type = None
                        
                        # Unified conditional branching assignments
                        if current_type == ShapeTurret.cluster:
                            if event.key == pygame.K_7: next_type = ShapeTurret.omega
                            elif event.key == pygame.K_8: next_type = ShapeTurret.fracture
                            elif event.key == pygame.K_9: next_type = ShapeTurret.triple_cluster
                        elif current_type == ShapeTurret.double:
                            if event.key == pygame.K_7: next_type = ShapeTurret.triple
                            elif event.key == pygame.K_8: next_type = ShapeTurret.tri_way
                        elif current_type == ShapeTurret.tri_way:
                            if event.key == pygame.K_7: next_type = ShapeTurret.five_way
                            elif event.key == pygame.K_8: next_type = ShapeTurret.six_way
                        elif current_type == ShapeTurret.scoper:
                            if event.key == pygame.K_7: next_type = ShapeTurret.watcher
                            elif event.key == pygame.K_8: next_type = ShapeTurret.railgun
                        elif current_type == ShapeTurret.chaser:
                            if event.key == pygame.K_7: next_type = ShapeTurret.banana_chaser
                            elif event.key == pygame.K_8: next_type = ShapeTurret.triple_chaser
                        elif current_type in [
                            ShapeTurret.eater, ShapeTurret.devourer, 
                            ShapeTurret.scout, ShapeTurret.hitman,  # Added Scout and Hitman (Requirement updated)
                            ShapeTurret.banana_chaser, ShapeTurret.mega_chaser, ShapeTurret.gladiator, 
                            ShapeTurret.triple_chaser, ShapeTurret.ultra_chaser, ShapeTurret.espresso, 
                            ShapeTurret.triple, ShapeTurret.orchestra, ShapeTurret.five_way, 
                            ShapeTurret.six_way, ShapeTurret.eight_way, ShapeTurret.ultra, 
                            ShapeTurret.watcher, ShapeTurret.railgun, ShapeTurret.double_railgun
                        ] and event.key == pygame.K_u:
                            next_type = node["next"][0]
                            
                        # Perform the actual evolution update if a type is set
                        if next_type:
                            money -= evolve_cost
                            selected_turret.shape_type = next_type
                            selected_turret.original_image = None

    # --- WAVE QUEUE SPAWNER ---
    if len(spawn_queue) > 0:
        spawn_timer += delta_time
        if spawn_timer >= spawn_cooldown:
            # Spawn multiple enemies if the queue builds up (High Risk!)
            spawns_this_tick = min(len(spawn_queue), 1 + len(spawn_queue) // 5)
            for _ in range(spawns_this_tick):
                enemy_data = spawn_queue.pop(0)
                new_enemy = enemy(enemy_data["speed"], enemy_data["damage"], pixel_path, select_type=enemy_data["type"], hp=enemy_data["hp"])
                enemies_group.add(new_enemy)
            spawn_timer = 0.0
            wave_state = "spawning"
    else:
        # If queue empty and all active enemies on screen are cleared
        if len(enemies_group) == 0:
            if wave_state != "intermission":
                wave_state = "intermission"
                wave_timer = 5.0
        else:
            wave_state = "clearing"

    # Handle standard Wave Intermission Delay
    if wave_state == "intermission":
        # Auto-skip toggle immediately bypasses the intermission delay
        if auto_skip:
            wave_timer = 0.0
            
        wave_timer -= delta_time
        if wave_timer <= 0.0:
            current_wave += 1
            queue_wave(current_wave)
            wave_state = "spawning"

    # --- CONTINUOUS 5-SECOND AUTO-SKIP TIMER ---
    if auto_skip:
        auto_skip_timer += delta_time
        if auto_skip_timer >= 5.0:
            auto_skip_timer = 0.0
            current_wave += 1
            queue_wave(current_wave)  # Stack new wave into queue every 5 seconds
    else:
        auto_skip_timer = 0.0

    # --- UPDATE POSITIONS USING GROUPS ---
    for current_enemy in list(enemies_group):
        van_dang_di_chuyen = current_enemy.move(delta_time)
        
        # Star enemy stun projectile shooting logic loop
        if current_enemy.type == "star" and current_enemy.alive():
            if not hasattr(current_enemy, "stun_timer_clock"):
                current_enemy.stun_timer_clock = 0.0
            current_enemy.stun_timer_clock += delta_time
            if current_enemy.stun_timer_clock >= 3.0:  
                current_enemy.stun_timer_clock = 0.0
                
                # Target nearest active combat turret
                nearest_t = None
                min_dist = 999999
                for t in turrets_group:
                    dist = math.hypot(t.x_position - current_enemy.x_position, current_enemy.y_position - current_enemy.y_position)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_t = t
                if nearest_t:
                    angle = -math.degrees(math.atan2(nearest_t.y_position - current_enemy.y_position, nearest_t.x_position - current_enemy.x_position))
                    stun_ball = bullet(current_enemy.x_position, current_enemy.y_position, angle, speed=120, damage=0, bullet_type="stun")
                    bullets_group.add(stun_ball)
                    
        if not van_dang_di_chuyen:
            fortress_hp -= current_enemy.damage
            current_enemy.kill()
            if fortress_hp <= 0:
                game_state = "gameover"

    # Move bullets and pass group references for robust homing tracking (Silent bug fixed!) (Requirement updated)
    for current_bullet in list(bullets_group):
        current_bullet.move(delta_time, bullets_group, enemies_group)
        if current_bullet.x_position < 0 or current_bullet.x_position > SCREEN_WIDTH or current_bullet.y_position < 0 or current_bullet.y_position > SCREEN_HEIGHT:
            current_bullet.kill()

    # Passive Farm Earnings Loop
    for current_farm in farms_group:
        income = current_farm.update(delta_time)
        money += income

    # Target finding and cooling updates for Turrets group
    for current_turret in turrets_group:
        if not hasattr(current_turret, "stun_timer"):
            current_turret.stun_timer = 0.0
            
        # Count down active stun effects
        if current_turret.stun_timer > 0:
            current_turret.stun_timer -= delta_time
            continue  
            
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
        # Process Stun Projectile hits against Turrets
        if current_bullet.bullet_type == "stun":
            collided_turrets = pygame.sprite.spritecollide(current_bullet, turrets_group, False)
            if len(collided_turrets) > 0:
                hit_turret = collided_turrets[0]
                hit_turret.stun_timer = 3.0  
                current_bullet.kill()
            continue

        # Optimize collisions with squared distance math
        for current_enemy in enemies_group:
            dx = current_bullet.x_position - current_enemy.x_position
            dy = current_bullet.y_position - current_enemy.y_position
            dist_squared = dx * dx + dy * dy
            
            if dist_squared < 400:  # 20 * 20 = 400 (collision radius squared)
                if current_bullet.bullet_type == "slow":
                    current_enemy.slow_timer = 2.0
                
                current_enemy.hp -= current_bullet.damage
                
                # Triggers explode mini-bullets if this is an evolution class projectile (unless it is piercing Hyper/Laser)
                if current_bullet.bullet_type in ["hyper", "laser"]:
                    current_bullet.pixel_limit = 5 if current_bullet.bullet_type == "hyper" else 999999
                    current_bullet.pierce_limit -= 1  
                    if current_bullet.pierce_limit <= 0:
                        current_bullet.kill()
                else:
                    current_bullet.trigger_explosion(bullets_group)
                    current_bullet.kill()
                
                if current_enemy.hp <= 0:
                    bounty = enemy_types.get(current_enemy.type, {}).get("bounty", 10)
                    money += bounty
                    current_enemy.kill()
                break

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

    # Render Enemies Health Bars and update rainbow textures dynamically
    for current_enemy in enemies_group:
        current_enemy.draw(screen)  
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

    # --- DRAW ON-SCREEN UI PANELS (UI Font Render Cache) ---
    if money != last_money:
        money_surf = ui_font.render(f"Money: ${int(money)}", True, (255, 215, 0))
        last_money = money
    screen.blit(money_surf, (10, 10))
    
    if current_wave != last_wave:
        wave_surf = ui_font.render(f"Wave: {current_wave}", True, (255, 255, 255))
        last_wave = current_wave
    screen.blit(wave_surf, (10, 40))
    
    if fortress_hp != last_fortress_hp:
        fortress_surf = ui_font.render(f"Fortress HP: {fortress_hp}", True, (255, 50, 50))
        last_fortress_hp = fortress_hp
    screen.blit(fortress_surf, (10, 70))
    
    if auto_skip != last_auto_skip:
        autoskip_state_txt = "ON" if auto_skip else "OFF"
        autoskip_col = (0, 255, 0) if auto_skip else (150, 150, 150)
        autoskip_surf = ui_font.render(f"Auto-Skip: {autoskip_state_txt} (Press 'A')", True, autoskip_col)
        last_auto_skip = auto_skip
    screen.blit(autoskip_surf, (10, 100))
    
    skip_lbl = ui_font.render("Press 'N' to Skip Wave (High Risk!)", True, (255, 215, 0))
    screen.blit(skip_lbl, (SCREEN_WIDTH - 320, 10))
    
    index_lbl = ui_font.render("Press 'I' for Evolution Index Guide", True, (255, 255, 255))
    screen.blit(index_lbl, (SCREEN_WIDTH - 320, 40))
    
    # Render thin range indicator around selected turrets
    if selected_turret is not None and selected_turret.alive():
        pygame.draw.circle(screen, (0, 255, 255), selected_turret.rect.center, Settings.tile_size * selected_turret.range_factor, 1)

    # 5-second pause intermission visual warning countdown
    if wave_state == "intermission":
        pause_label = ui_font.render(f"Next Wave in: {int(wave_timer + 1)}s", True, (0, 255, 255))
        screen.blit(pause_label, (SCREEN_WIDTH // 2 - 100, 10))
        
    # Render 5-second Auto-Skip active stacking warning
    if auto_skip:
        warn_lbl = ui_font.render(f"Auto-Skip Active: Next Wave Stack in {int(5.0 - auto_skip_timer + 1)}s!", True, (255, 165, 0))
        screen.blit(warn_lbl, (SCREEN_WIDTH // 2 - 180, 40))

    if placing_mode:
        price = TURRET_PRICES[selected_shape]
        color = (0, 255, 0) if money >= price else (255, 50, 50)
        is_placing_farm = selected_shape in [ShapeTurret.farm_t1, ShapeTurret.farm_t2]
        
        # Enforce both active farm and turret caps
        if is_placing_farm and len(farms_group) >= MAX_FARMS:
            cost_label = ui_font.render(f"FARM LIMIT REACHED ({MAX_FARMS} Max)", True, (255, 50, 50))
        elif not is_placing_farm and len(turrets_group) >= MAX_TURRETS:
            cost_label = ui_font.render(f"TURRET LIMIT REACHED ({MAX_TURRETS} Max)", True, (255, 50, 50))
        else:
            cost_label = ui_font.render(f"Cost: ${price} (Left-Click to place)", True, color)
        screen.blit(cost_label, (10, 130))

    # --- DRAW INTERACTIVE EVOLUTION UI PANEL ---
    if selected_turret is not None and selected_turret.alive():
        current_type = selected_turret.shape_type
        node = EVOLUTION_TREE.get(current_type)
        
        # Draw translucent grey background UI box
        pygame.draw.rect(screen, (30, 30, 30), (0, 500, SCREEN_WIDTH, 100))
        pygame.draw.rect(screen, (100, 100, 100), (0, 500, SCREEN_WIDTH, 100), 2)
        
        del_lbl = ui_font.render("Press '0' to Delete Structure", True, (255, 100, 100))
        screen.blit(del_lbl, (SCREEN_WIDTH - 280, 560))
        
        if selected_turret.stun_timer > 0:
            name_lbl = ui_font.render(f"Selected: {current_type} (STUNNED - {int(selected_turret.stun_timer + 1)}s)", True, (255, 165, 0))
        else:
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
                    screen.blit(preview_img, (SCREEN_WIDTH - 430, 515))
            
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
                
                if img_o: screen.blit(img_o, (SCREEN_WIDTH - 530, 515))
                if img_f: screen.blit(img_f, (SCREEN_WIDTH - 450, 515))
                if img_tc: screen.blit(img_tc, (SCREEN_WIDTH - 370, 515))
                
            elif current_type == ShapeTurret.double:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_triple = ui_font.render("[7] Triple", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_triway = ui_font.render("[8] Tri-Way", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_triple, (20, 570))
                screen.blit(lbl_triway, (150, 570))
                
                img_tr = load_and_scale_asset(ShapeTurret.triple, 15)
                img_tw = load_and_scale_asset(ShapeTurret.tri_way, 15)
                
                if img_tr: screen.blit(img_tr, (SCREEN_WIDTH - 450, 515))
                if img_tw: screen.blit(img_tw, (SCREEN_WIDTH - 370, 515))
                
            elif current_type == ShapeTurret.tri_way:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_five = ui_font.render("[7] Five-Way", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_six = ui_font.render("[8] Six-Way", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_five, (20, 570))
                screen.blit(lbl_six, (150, 570))
                
                img_five = load_and_scale_asset(ShapeTurret.five_way, 15)
                img_six = load_and_scale_asset(ShapeTurret.six_way, 15)
                
                if img_five: screen.blit(img_five, (SCREEN_WIDTH - 450, 515))
                if img_six: screen.blit(img_six, (SCREEN_WIDTH - 370, 515))
                
            elif current_type == ShapeTurret.scoper:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_watcher = ui_font.render("[7] Watcher", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_rail = ui_font.render("[8] Railgun", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_watcher, (20, 570))
                screen.blit(lbl_rail, (150, 570))
                
                img_wa = load_and_scale_asset(ShapeTurret.watcher, 15)
                img_ra = load_and_scale_asset(ShapeTurret.railgun, 15)
                
                if img_wa: screen.blit(img_wa, (SCREEN_WIDTH - 450, 515))
                if img_ra: screen.blit(img_ra, (SCREEN_WIDTH - 370, 515))

            elif current_type == ShapeTurret.chaser:
                branch_lbl = ui_font.render(f"Branches: Cost: ${evolve_cost}", True, (255, 255, 255))
                screen.blit(branch_lbl, (20, 540))
                
                lbl_banana = ui_font.render("[7] Banana", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                lbl_triple_c = ui_font.render("[8] Triple Chaser", True, (0, 255, 0) if money >= evolve_cost else (255, 50, 50))
                
                screen.blit(lbl_banana, (20, 570))
                screen.blit(lbl_triple_c, (150, 570))
                
                img_ba = load_and_scale_asset(ShapeTurret.banana_chaser, 15)
                img_tc = load_and_scale_asset(ShapeTurret.triple_chaser, 15)
                
                if img_ba: screen.blit(img_ba, (SCREEN_WIDTH - 450, 515))
                if img_tc: screen.blit(img_tc, (SCREEN_WIDTH - 370, 515))
        else:
            max_lbl = ui_font.render("Evolution Path: MAX TIER REACHED!", True, (0, 255, 0))
            screen.blit(max_lbl, (20, 550))

    pygame.display.flip()

pygame.quit()
sys.exit()