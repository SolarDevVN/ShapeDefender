# src/turret_obj.py

import pygame
import math

from src.type import ShapeTurret, Settings
from src.enemy_obj import enemy

_image_cache = {}


def load_and_scale_asset(shape_type, size):
    """
    Translates turret shapes to their corresponding image assets,
    loading and caching them while preserving their original aspect ratio.
    """
    filename_map = {
        ShapeTurret.circle: "assets/Default.png",         # Image 1 (Single barrel)
        ShapeTurret.square: "assets/Double.png",          # Image 2 (Double barrel)
        ShapeTurret.hexagon: "assets/Eight Way.png",      # Image 3 (8-barrel Octo)
        ShapeTurret.triangle: "assets/Triple.png"         # Image 4 (3-barrel Triple)
    }
    
    path = filename_map.get(shape_type)
    if not path:
        return None
        
    cache_key = f"{shape_type}_{size}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]
        
    try:
        raw_img = pygame.image.load(path).convert_alpha()
        orig_w, orig_h = raw_img.get_size()
        
        # Scale modifier makes Eight Way (hexagon) 1.5x larger
        scale_modifier = 1.5 if shape_type == ShapeTurret.hexagon else 1.0
        
        new_h = int(size * 2 * scale_modifier)
        new_w = int(new_h * (orig_w / orig_h))
        
        scaled_img = pygame.transform.scale(raw_img, (new_w, new_h))
        _image_cache[cache_key] = scaled_img
        return scaled_img
    except pygame.error:
        # Returns None if the image file cannot be found
        return None


def draw_shape(surface, shape_type, color, center, size, alpha=255):
    """
    Draws the correct image asset centered on a position.
    Used for static rendering and placing previews.
    """
    center_x, center_y = center
    
    # Custom colored square previews for placing farms (Green represents money)
    if shape_type == ShapeTurret.farm_t1:
        temp_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, (0, 200, 0, alpha), (0, 0, size * 2, size * 2))
        pygame.draw.rect(temp_surf, (0, 100, 0, alpha), (0, 0, size * 2, size * 2), 2)
        surface.blit(temp_surf, (center_x - size, center_y - size))
        return
    elif shape_type == ShapeTurret.farm_t2:
        temp_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, (0, 130, 0, alpha), (0, 0, size * 2, size * 2))
        pygame.draw.rect(temp_surf, (0, 60, 0, alpha), (0, 0, size * 2, size * 2), 3)
        surface.blit(temp_surf, (center_x - size, center_y - size))
        return

    img = load_and_scale_asset(shape_type, size)
    
    if img is not None:
        if alpha < 255:
            img_to_draw = img.copy()
            img_to_draw.set_alpha(alpha)
        else:
            img_to_draw = img
            
        w, h = img_to_draw.get_size()
        surface.blit(img_to_draw, (center_x - w // 2, center_y - h // 2))
    else:
        # Simple vector fallback if image files are missing
        pygame.draw.circle(surface, (0, 255, 255), (center_x, center_y), size)


class turret:
    # Balanced default cooldown to 1/3 of a second (Requirement 2 updated)
    def __init__(self, x_position, y_position, shape_type="hexagon", cooldown=1.0 / 3.0, direction=0):
        self.x_position = x_position
        self.y_position = y_position
        self.shape_type = shape_type
        self.cooldown = cooldown
        self.direction = direction
        self.have_place = False
        self.original_image = None
        self.rect = None
        self.image = None  # Holds the rotated sprite
        self.cooldown_timer = 0.0
        self.fire_state = 0  # Tracks alternating barrel sequences

    def placing(self, size):
        self.have_place = True
        
        base_img = load_and_scale_asset(self.shape_type, size)
        
        if base_img is not None:
            self.original_image = base_img.copy()
            self.rect = self.original_image.get_rect(center=(self.x_position, self.y_position))
            self.image = self.original_image.copy()
        else:
            # Fallback canvas if files are missing or placing a vector-only farm
            canvas_size = size * 2
            self.original_image = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (0, 255, 255), (size, size), size)
            self.rect = self.original_image.get_rect(center=(self.x_position, self.y_position))
            self.image = self.original_image.copy()

    def draw(self, surface, size):
        if not self.have_place:
            draw_shape(surface, self.shape_type, (0, 255, 255), (self.x_position, self.y_position), size)
        else:
            if self.original_image is None:
                self.placing(size)
            surface.blit(self.image, self.rect.topleft)

    def construct_enemy_list(self, enemies: list[enemy]) -> list[enemy]:
        """
        Gathers targeted enemies inside range.
        Expanded search limit to Settings.tile_size * 5 (Requirement updated).
        """
        enemy_in_range = []
        for enemy in enemies:
            if abs(enemy.x_position - self.x_position) < Settings.tile_size * 5 and abs(enemy.y_position - self.y_position) < Settings.tile_size * 5:
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

        dist_to_enemy = math.hypot(target_enemy.x_position - self.x_position, target_enemy.y_position - self.y_position)
        
        lead_multiplier = 1.05
        travel_time = (dist_to_enemy / bullet_speed) * lead_multiplier if bullet_speed > 0 else 0

        predicted_x = target_enemy.x_position + enemy_vx * travel_time
        predicted_y = target_enemy.y_position + enemy_vy * travel_time

        dx = predicted_x - self.x_position
        dy = predicted_y - self.y_position
        angle_rad = math.atan2(dy, dx)
        
        return -math.degrees(angle_rad)

    def shoot(self, bullets_list, predicted_angle):
        """
        Spawns bullets with custom patterns based on the turret's shape type.
        Damage values are balanced to 1/3 of their original metrics.
        """
        from src.turret_attack_obj import bullet
        
        angle_rad = math.radians(-predicted_angle)
        perp_rad = angle_rad + math.pi / 2
        
        # Offset coordinates (8 pixels to the side of the center)
        dx = math.cos(perp_rad) * 8
        dy = math.sin(perp_rad) * 8
        
        if self.shape_type == ShapeTurret.circle:  # Single (Damage balanced: 25 -> 8)
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=400, damage=8)
            bullets_list.append(new_bullet)
            
        elif self.shape_type == ShapeTurret.square:  # Double (Damage balanced: 25 -> 8)
            if self.fire_state == 0:
                # Shoot left barrel offset
                new_bullet = bullet(self.x_position + dx, self.y_position + dy, predicted_angle, speed=400, damage=8)
                bullets_list.append(new_bullet)
                self.fire_state = 1
            else:
                # Shoot right barrel offset
                new_bullet = bullet(self.x_position - dx, self.y_position - dy, predicted_angle, speed=400, damage=8)
                bullets_list.append(new_bullet)
                self.fire_state = 0
                
        elif self.shape_type == ShapeTurret.triangle:  # Triple (Damage balanced: 15->5, 25->8)
            if self.fire_state == 0:
                # Shoot side barrels 1 and 2 together
                bullet1 = bullet(self.x_position + dx, self.y_position + dy, predicted_angle, speed=400, damage=5)
                bullet2 = bullet(self.x_position - dx, self.y_position - dy, predicted_angle, speed=400, damage=5)
                bullets_list.extend([bullet1, bullet2])
                self.fire_state = 1
            else:
                # Shoot center barrel 3
                bullet3 = bullet(self.x_position, self.y_position, predicted_angle, speed=400, damage=8)
                bullets_list.append(bullet3)
                self.fire_state = 0
                
        elif self.shape_type == ShapeTurret.hexagon:  # Eight Way (Damage balanced: 15 -> 5)
            for i in range(8):
                burst_angle = predicted_angle + (i * 45)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=400, damage=5)
                bullets_list.append(new_bullet)