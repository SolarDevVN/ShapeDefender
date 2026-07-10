# src/turret_obj.py

import pygame
import math

from src.type import ShapeTurret, Settings
from src.enemy_obj import enemy

_image_cache = {}


def draw_shape(surface, shape_type, color, center, size, alpha=255):
    """
    Draws a colored shape (hexagon, circle, square, or triangle).
    Supports transparency via the alpha parameter (0-255).
    """
    center_x, center_y = center
    
    if shape_type == ShapeTurret.circle:
        img_key = f"circle_{size}"
        if img_key in _image_cache:
            img, circle_center_x, circle_center_y = _image_cache[img_key]
        else:
            try:
                if "raw_circle" not in _image_cache:
                    _image_cache["raw_circle"] = pygame.image.load("assets/Default.png").convert_alpha()
                
                raw_img = _image_cache["raw_circle"]
                orig_w, orig_h = raw_img.get_size()
                
                # Find the exact circle center using get_bounding_rects()
                mask = pygame.mask.from_surface(raw_img)
                rects = mask.get_bounding_rects()
                bbox = rects[0] if rects else pygame.Rect(0, 0, orig_w, orig_h)
                orig_circle_diameter = bbox.height
                orig_center_x = bbox.x + orig_circle_diameter / 2
                orig_center_y = bbox.y + orig_circle_diameter / 2
                
                # Scale keeping the original aspect ratio
                scale_factor = (size * 2) / orig_circle_diameter
                new_w = int(orig_w * scale_factor)
                new_h = int(orig_h * scale_factor)
                
                img = pygame.transform.scale(raw_img, (new_w, new_h))
                
                circle_center_x = int(orig_center_x * scale_factor)
                circle_center_y = int(orig_center_y * scale_factor)
                
                _image_cache[img_key] = (img, circle_center_x, circle_center_y)
            except pygame.error:
                img = None
        
        if img is not None:
            if alpha < 255:
                img_to_draw = img.copy()
                img_to_draw.set_alpha(alpha)
            else:
                img_to_draw = img
                
            surface.blit(img_to_draw, (center_x - circle_center_x, center_y - circle_center_y))
        else:
            # Fallback nếu không tìm thấy file ảnh thì vẽ hình tròn tạm thời
            temp_surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            local_center = (size + 1, size + 1)
            pygame.draw.circle(temp_surface, color + (alpha,), local_center, size)
            surface.blit(temp_surface, (center_x - size - 1, center_y - size - 1))
        
    else:
        # Create temporary surface with transparency support
        temp_surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        local_center = (size + 1, size + 1)
        
        if shape_type == ShapeTurret.hexagon:
            points = []
            for vertex_index in range(6):
                angle_rad = math.radians(60 * vertex_index)
                vertex_x = local_center[0] + size * math.cos(angle_rad)
                vertex_y = local_center[1] + size * math.sin(angle_rad)
                points.append((vertex_x, vertex_y))
            pygame.draw.polygon(temp_surface, color + (alpha,), points)
            
        elif shape_type == ShapeTurret.square:
            # Draw a centered square
            pygame.draw.rect(
                temp_surface, 
                color + (alpha,), 
                (local_center[0] - size, local_center[1] - size, size * 2, size * 2)
            )
            
        elif shape_type == ShapeTurret.triangle:
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
        self.cooldown_timer = 0.0

    def placing(self, size):
        self.have_place = True
        
        # Tạo bề mặt canvas lớn gấp đôi kích thước tháp để khi xoay góc không bị mất cạnh
        if self.shape_type == ShapeTurret.circle:
            try:
                if "raw_circle" not in _image_cache:
                    _image_cache["raw_circle"] = pygame.image.load("assets/Circle Tank.png").convert_alpha()
                
                raw_img = _image_cache["raw_circle"]
                orig_w, orig_h = raw_img.get_size()
                
                # Find exact boundaries of the circle within the original canvas
                mask = pygame.mask.from_surface(raw_img)
                rects = mask.get_bounding_rects()
                bbox = rects[0] if rects else pygame.Rect(0, 0, orig_w, orig_h)
                orig_circle_diameter = bbox.height
                orig_center_x = bbox.x + orig_circle_diameter / 2
                
                scale_factor = (size * 2) / orig_circle_diameter
                new_w = int(orig_w * scale_factor)
                
                scaled_center_x = int(orig_center_x * scale_factor)
                dx = new_w - scaled_center_x
                dy = size
                max_dist = math.hypot(dx, dy)
                canvas_size = int(max_dist * 2) + 4
            except pygame.error:
                canvas_size = (size * 2 + 2) * 2
        else:
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
            
            # Vẽ bức ảnh Đã XOAY (self.image) ra màn hình chính
            surface.blit(self.image, self.rect.topleft)

    def construct_enemy_list(self, enemies: list[enemy]) -> list[enemy]:
        enemy_in_range = []
        for enemy in enemies:
            if abs(enemy.x_position - self.x_position) < Settings.tile_size * 3 and abs(enemy.y_position - self.y_position) < Settings.tile_size * 3:
                enemy_in_range.append(enemy)
        return enemy_in_range
        
    def point_toward(self, target_x, target_y):
        delta_x = target_x - self.x_position
        delta_y = target_y - self.y_position
        
        radian_value = math.atan2(delta_y, delta_x)
        
        self.direction = -math.degrees(radian_value)
        
        if self.have_place and self.original_image is not None:
            current_center = self.rect.center
            self.image = pygame.transform.rotozoom(self.original_image, self.direction, 1)
            self.rect = self.image.get_rect(center=current_center)

    def predict_target_position(self, target_enemy, bullet_speed):
        current_pos = pygame.math.Vector2(target_enemy.x_position, target_enemy.y_position)
        
        if target_enemy.waypoint_index >= len(target_enemy.path):
            dx = target_enemy.x_position - self.x_position
            dy = target_enemy.y_position - self.y_position
            return -math.degrees(math.atan2(dy, dx))
            
        target_wp = target_enemy.path[target_enemy.waypoint_index]
        direction = target_wp - current_pos
        
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.math.Vector2(0, 0)
            
        enemy_vx = direction.x * target_enemy.speed
        enemy_vy = direction.y * target_enemy.speed

        # Calculate standard distance
        dist_to_enemy = math.hypot(target_enemy.x_position - self.x_position, target_enemy.y_position - self.y_position)
        
        # Multiply travel time by 1.25 to overshoot slightly and hit "in the face"
        lead_multiplier = 1.05
        travel_time = (dist_to_enemy / bullet_speed) * lead_multiplier if bullet_speed > 0 else 0

        # Predict future position with extra lead
        predicted_x = target_enemy.x_position + enemy_vx * travel_time
        predicted_y = target_enemy.y_position + enemy_vy * travel_time

        dx = predicted_x - self.x_position
        dy = predicted_y - self.y_position
        angle_rad = math.atan2(dy, dx)
        
        return -math.degrees(angle_rad)