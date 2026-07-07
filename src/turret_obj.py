# src/turret_obj.py

import pygame
import math

def draw_shape(surface, shape_type, color, center, size, alpha=255):
    """
    Draws a colored shape (hexagon, circle, square, or triangle).
    Supports transparency via the alpha parameter (0-255).
    """
    center_x, center_y = center
    
    # Create temporary surface with transparency support
    temp_surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
    local_center = (size + 1, size + 1)
    
    if shape_type == "hexagon":
        points = []
        for vertex_index in range(6):
            angle_rad = math.radians(60 * vertex_index)
            vertex_x = local_center[0] + size * math.cos(angle_rad)
            vertex_y = local_center[1] + size * math.sin(angle_rad)
            points.append((vertex_x, vertex_y))
        pygame.draw.polygon(temp_surface, color + (alpha,), points)
        
    elif shape_type == "circle":
        try:
            img = pygame.image.load("assets/Circle Tank.png").convert_alpha()
            img = pygame.transform.scale(img, (size * 2, size * 2))
            img_rect = img.get_rect(center=local_center)
            temp_surface.blit(img, img_rect.topleft)
        except pygame.error:
            # Fallback nếu không tìm thấy file ảnh thì vẽ hình tròn tạm thời
            pygame.draw.circle(temp_surface, color + (alpha,), local_center, size)
        
    elif shape_type == "square":
        # Draw a centered square
        pygame.draw.rect(
            temp_surface, 
            color + (alpha,), 
            (local_center[0] - size, local_center[1] - size, size * 2, size * 2)
        )
        
    elif shape_type == "triangle":
        # Draw an upward-pointing triangle
        points = [
            (local_center[0], local_center[1] - size),
            (local_center[0] - size, local_center[1] + size),
            (local_center[0] + size, local_center[1] + size)
        ]
        pygame.draw.polygon(temp_surface, color + (alpha,), points)
        
    surface.blit(temp_surface, (center_x - size - 1, center_y - size - 1))


class turret:
    def __init__(self, x_position, y_position, shape_type="hexagon", cooldown=1.0, direction=0):
        self.x_position = x_position
        self.y_position = y_position
        self.shape_type = shape_type
        self.cooldown = cooldown
        self.direction = direction
        self.have_place = False
        self.original_image = None
        self.rect = None
        self.image = None # Chứa ảnh thực tế sau khi xoay

    def placing(self, size):
        self.have_place = True
        
        # Tạo bề mặt canvas lớn gấp đôi kích thước tháp để khi xoay góc không bị mất cạnh
        canvas_size = (size * 2 + 2) * 2
        self.original_image = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        
        # Vẽ tháp vào chính giữa canvas trống này
        canvas_center = (canvas_size // 2, canvas_size // 2)
        draw_shape(self.original_image, self.shape_type, (0, 255, 255), canvas_center, size)
        
        # Tạo khung rect cố định tâm tháp trên bản đồ game
        self.rect = self.original_image.get_rect(center=(self.x_position, self.y_position))
        self.image = self.original_image.copy()

    def draw(self, surface, size):
        # Nếu chưa đặt (đang ở chế độ preview di chuột) thì vẽ hình tĩnh bình thường
        if not self.have_place:
            draw_shape(surface, self.shape_type, (0, 255, 255), (self.x_position, self.y_position), size)
        else:
            # Phòng hờ trường hợp hàm placing chưa được kích hoạt ảnh gốc
            if self.original_image is None:
                self.placing(size)
            
            # Vẽ bức ảnh ĐÃ XOAY (self.image) ra màn hình chính
            surface.blit(self.image, self.rect.topleft)

    def construct_enemy_list(self, enemies):
        enemy_in_range = []
        for enemy in enemies:
            if abs(enemy.x_position - self.x_position) < 100 and abs(enemy.y_position - self.y_position) < 100:
                enemy_in_range.append(enemy)
        return enemy_in_range
        
    def point_toward(self, target_x, target_y):
        delta_x = target_x - self.x_position
        delta_y = target_y - self.y_position
        
        # Tính góc toán học bằng radian
        goc_radian = math.atan2(delta_y, delta_x)
        
        # Đổi sang độ và thêm dấu âm (-) để khớp với hệ tọa độ Pygame
        self.direction = -math.degrees(goc_radian)
        
        # Tiến hành xoay ảnh dựa trên hướng góc mới tính được
        if self.have_place and self.original_image is not None:
            current_center = self.rect.center
            self.image = pygame.transform.rotozoom(self.original_image, self.direction, 1)
            self.rect = self.image.get_rect(center=current_center)
       