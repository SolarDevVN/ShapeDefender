import pygame
import sys
import random

from src.enemy_obj import enemy
from src.turret_obj import turret, draw_shape
from src.type import ShapeTurret, Settings

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
                            
                            if hasattr(new_turret, 'placing'):
                                new_turret.placing(HEX_SIZE)
                                
                            placed_turrets.append(new_turret)
                            placing_mode = False

    spawn_timer += delta_time
    if spawn_timer >= spawn_cooldown and len(enemies) < 10:
        new_enemy = enemy(random.randint(150, 300), 10, pixel_path)
        enemies.append(new_enemy)
        spawn_timer = 0.0

    for current_enemy in enemies[:]: # Dấu [:] giúp tạo bản sao để xóa phần tử an toàn không bị lỗi vòng lặp
        if hasattr(current_enemy, 'move'):
            # Gọi hàm move và kiểm tra xem enemy đã đi hết đường chưa (trả về False)
            van_dang_di_chuyen = current_enemy.move(delta_time)
            
            if not van_dang_di_chuyen:
                enemies.remove(current_enemy) # Xóa kẻ địch khỏi danh sách game khi đi hết đường

    screen.fill((0, 0, 0))

    # Render matrix map tiles
    for row_index in range(ROWS):
        for column_index in range(COLS):
            if map[row_index][column_index] == 1:
                pygame.draw.rect(screen, path_color, (column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Render Placed Turrets & Handle target locking rotation
    for current_turret in placed_turrets:
        enemies_in_range: list[enemy] = current_turret.construct_enemy_list(enemies)
        
        if len(enemies_in_range) > 0:
            # FIX: Lấy phần tử [0] chuẩn xác không bị mất ký tự nữa
            target = enemies_in_range[0]
            current_turret.point_toward(target.x_position, target.y_position)
        
            
        current_turret.draw(screen, HEX_SIZE)

    for current_enemy in enemies:
        if hasattr(current_enemy, 'draw'):
            current_enemy.draw(screen)

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
