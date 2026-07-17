# src/turret_obj.py

import pygame
import math
import random

from src.type import ShapeTurret, Settings
from src.enemy_obj import enemy

_image_cache = {}


def load_and_scale_asset(shape_type, size):
    """
    Translates turret shapes to their corresponding image assets,
    loading and caching them while preserving their original aspect ratio.
    """
    filename_map = {
        # Eater Branch
        ShapeTurret.eater: "assets/Eater.png",
        ShapeTurret.devourer: "assets/Devourer.png",
        ShapeTurret.cluster: "assets/Cluster.png",
        ShapeTurret.omega: "assets/Omega.png",
        ShapeTurret.fracture: "assets/Fracture.png",
        ShapeTurret.triple_cluster: "assets/Triple Cluster.png",
        
        # Double Branch
        ShapeTurret.double: "assets/Double.png",
        ShapeTurret.triple: "assets/Triple.png",
        ShapeTurret.tri_way: "assets/Tri-Way.png",
        ShapeTurret.orchestra: "assets/Orchestra.png",
        ShapeTurret.super_t: "assets/Super.png",
        ShapeTurret.five_way: "assets/Five-Way.png",
        ShapeTurret.six_way: "assets/Six-Way.png",
        ShapeTurret.scatter: "assets/Scatter.png",
        ShapeTurret.eight_way: "assets/Eight-Way.png",
        ShapeTurret.ultra: "assets/Ultra.png",
        ShapeTurret.hyper: "assets/Hyper.png",
        
        # Scout Branch
        ShapeTurret.scout: "assets/Scout.png",
        ShapeTurret.hitman: "assets/Hitman.png",
        ShapeTurret.scoper: "assets/Scoper.png",
        ShapeTurret.watcher: "assets/Watcher.png",
        ShapeTurret.agent: "assets/Agent.png",
        ShapeTurret.railgun: "assets/Railgun.png",
        ShapeTurret.double_railgun: "assets/Double Railgun.png",
        ShapeTurret.triple_railgun: "assets/Triple Railgun.png",

        # Chaser Branch (Requirement added)
        ShapeTurret.chaser: "assets/Chaser.png",
        ShapeTurret.banana_chaser: "assets/Big Mega Enormous Giangantic Banana Chaser.png",
        ShapeTurret.mega_chaser: "assets/Mega Chaser.png",
        ShapeTurret.gladiator: "assets/Gladiator.png",
        ShapeTurret.fortress: "assets/Fortress.png",
        ShapeTurret.triple_chaser: "assets/Triple Chaser.png",
        ShapeTurret.ultra_chaser: "assets/Ultra Chaser.png",
        ShapeTurret.espresso: "assets/Espresso.png",
        ShapeTurret.emperor: "assets/Emperor.png"
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
        
        # Scale modifier makes late-game superstructures visually larger
        scale_modifier = 1.0
        if shape_type in [ShapeTurret.omega, ShapeTurret.devourer, ShapeTurret.super_t, ShapeTurret.ultra, ShapeTurret.hyper, ShapeTurret.double_railgun, ShapeTurret.triple_railgun, ShapeTurret.emperor, ShapeTurret.fortress]:
            scale_modifier = 1.4
            
        new_h = int(size * 2 * scale_modifier)
        new_w = int(new_h * (orig_w / orig_h))
        
        scaled_img = pygame.transform.scale(raw_img, (new_w, new_h))
        _image_cache[cache_key] = scaled_img
        return scaled_img
    except pygame.error:
        return None


def draw_shape(surface, shape_type, color, center, size, alpha=255):
    """
    Draws the correct image asset centered on a position.
    Used for static rendering and placing previews.
    """
    center_x, center_y = center
    
    # Custom colored square previews for placing farms
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


class turret(pygame.sprite.Sprite):
    def __init__(self, x_position, y_position, shape_type=ShapeTurret.eater, cooldown=1.0 / 3.0, direction=0):
        super().__init__()
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
        self.stun_timer = 0.0
        
        # Configure dynamic range factors
        self.range_factor = 5
        if shape_type == ShapeTurret.scout:
            self.range_factor = 6
            self.cooldown = 0.25
        elif shape_type == ShapeTurret.hitman:
            self.range_factor = 7
            self.cooldown = 0.2
        elif shape_type == ShapeTurret.scoper:
            self.range_factor = 9
            self.cooldown = 2.0
        elif shape_type == ShapeTurret.watcher:
            self.range_factor = 10
            self.cooldown = 1.0
        elif shape_type == ShapeTurret.agent:
            self.range_factor = 16  # Half map
            self.cooldown = 0.3
        elif shape_type in [ShapeTurret.railgun, ShapeTurret.double_railgun, ShapeTurret.triple_railgun]:
            self.range_factor = 5
            self.cooldown = 5.0  

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

    def construct_enemy_list(self, enemies) -> list[enemy]:
        enemy_in_range = []
        for enemy_sprite in enemies:
            if abs(enemy_sprite.x_position - self.x_position) < Settings.tile_size * self.range_factor and abs(enemy_sprite.y_position - self.y_position) < Settings.tile_size * self.range_factor:
                enemy_in_range.append(enemy_sprite)
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

    def shoot(self, bullet_group, predicted_angle):
        """
        Custom bullet configurations spanning all 4 unique trees (Requirement updated).
        """
        from src.turret_attack_obj import bullet
        
        angle_rad = math.radians(-predicted_angle)
        perp_rad = angle_rad + math.pi / 2
        
        # Offset coordinates (8 pixels to the side of the center)
        dx = math.cos(perp_rad) * 8
        dy = math.sin(perp_rad) * 8
        
        # --- EATER EVOLUTION LINE ---
        if self.shape_type == ShapeTurret.eater:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=350, damage=12, bullet_type="normal")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.devourer:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=300, damage=35, bullet_type="normal")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.cluster:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=250, damage=15, bullet_type="cluster")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.omega:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=250, damage=45, bullet_type="omega")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.fracture:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=250, damage=15, bullet_type="fracture")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.triple_cluster:
            for i in range(3):
                burst_angle = predicted_angle + (i * 120)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=250, damage=15, bullet_type="cluster")
                bullet_group.add(new_bullet)

        # --- DOUBLE EVOLUTION LINE ---
        elif self.shape_type == ShapeTurret.double:
            if self.fire_state == 0:
                new_bullet = bullet(self.x_position + dx, self.y_position + dy, predicted_angle, speed=380, damage=10, bullet_type="normal")
                bullet_group.add(new_bullet)
                self.fire_state = 1
            else:
                new_bullet = bullet(self.x_position - dx, self.y_position - dy, predicted_angle, speed=380, damage=10, bullet_type="normal")
                bullet_group.add(new_bullet)
                self.fire_state = 0

        elif self.shape_type == ShapeTurret.triple:
            if self.fire_state == 0:
                bullet1 = bullet(self.x_position + dx, self.y_position + dy, predicted_angle, speed=380, damage=10, bullet_type="normal")
                bullet2 = bullet(self.x_position - dx, self.y_position - dy, predicted_angle, speed=380, damage=10, bullet_type="normal")
                bullet_group.add(bullet1, bullet2)
                self.fire_state = 1
            else:
                bullet3 = bullet(self.x_position, self.y_position, predicted_angle, speed=380, damage=15, bullet_type="normal")
                bullet_group.add(bullet3)
                self.fire_state = 0

        elif self.shape_type == ShapeTurret.tri_way:
            for offset in [-45, 0, 45]:
                new_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=350, damage=10, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.orchestra:
            for offset_idx in range(-2, 3):
                offset_dx = dx * offset_idx * 0.4
                offset_dy = dy * offset_idx * 0.4
                new_bullet = bullet(self.x_position + offset_dx, self.y_position + offset_dy, predicted_angle, speed=400, damage=6, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.super_t:
            for offset_idx in range(-3, 4):
                offset_dx = dx * offset_idx * 0.35
                offset_dy = dy * offset_idx * 0.35
                new_bullet = bullet(self.x_position + offset_dx, self.y_position + offset_dy, predicted_angle, speed=300, damage=12, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.five_way:
            for i in range(-2, 3):
                offset = i * 22.5
                new_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=320, damage=10, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.six_way:
            for offset in [-45, 0, 45]:
                b_front = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=320, damage=12, bullet_type="normal")
                b_back = bullet(self.x_position, self.y_position, predicted_angle + 180 + offset, speed=320, damage=12, bullet_type="normal")
                bullet_group.add(b_front, b_back)

        elif self.shape_type == ShapeTurret.scatter:
            for i in range(-3, 4):
                offset = i * 22.5
                new_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=350, damage=10, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.eight_way:
            for i in range(8):
                burst_angle = predicted_angle + (i * 45)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=320, damage=15, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.ultra:
            for i in range(12):
                burst_angle = predicted_angle + (i * 30)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=350, damage=15, bullet_type="normal")
                bullet_group.add(new_bullet)

        elif self.shape_type == ShapeTurret.hyper:
            angles = random.sample(range(0, 360, 5), 14)
            for angle in angles:
                new_bullet = bullet(self.x_position, self.y_position, angle, speed=300, damage=50, bullet_type="hyper")
                bullet_group.add(new_bullet)

        # --- SCOUT EVOLUTION LINE ---
        elif self.shape_type == ShapeTurret.scout:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=600, damage=15, bullet_type="normal")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.hitman:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=700, damage=35, bullet_type="normal")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.scoper:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=800, damage=120, bullet_type="normal")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.watcher:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=500, damage=40, bullet_type="slow")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.agent:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=600, damage=30, bullet_type="slow")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.railgun:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=500, damage=600, bullet_type="laser")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.double_railgun:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=500, damage=1200, bullet_type="laser")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.triple_railgun:
            for offset in [-10, 0, 10]:
                new_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=500, damage=600, bullet_type="laser")
                bullet_group.add(new_bullet)

        # --- CHASER EVOLUTION LINE (Requirement added) ---
        elif self.shape_type == ShapeTurret.chaser:
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=300, damage=15, bullet_type="homing")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.banana_chaser:
            # Giant homing missile with double damage (Requirement updated)
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=300, damage=30, bullet_type="homing_large")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.mega_chaser:
            # Massive homing missile with even more damage (Requirement updated)
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=280, damage=60, bullet_type="homing_mega")
            bullet_group.add(new_bullet)
            
        elif self.shape_type == ShapeTurret.gladiator:
            # 1 massive center beam, 2 smaller side-angled normal cannons (Requirement updated)
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=280, damage=60, bullet_type="homing_mega")
            bullet_group.add(new_bullet)
            for offset in [-30, 30]:
                side_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(side_bullet)
                
        elif self.shape_type == ShapeTurret.fortress:
            # Gladiator setup on both front and back (Requirement updated)
            # Front
            new_bullet = bullet(self.x_position, self.y_position, predicted_angle, speed=280, damage=60, bullet_type="homing_mega")
            bullet_group.add(new_bullet)
            for offset in [-30, 30]:
                side_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(side_bullet)
            # Back
            new_bullet_b = bullet(self.x_position, self.y_position, predicted_angle + 180, speed=280, damage=60, bullet_type="homing_mega")
            bullet_group.add(new_bullet_b)
            for offset in [-30, 30]:
                side_bullet_b = bullet(self.x_position, self.y_position, predicted_angle + 180 + offset, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(side_bullet_b)
                
        elif self.shape_type == ShapeTurret.triple_chaser:
            # 3 homing triangles spaced 60 degrees apart (Requirement updated)
            for offset in [-60, 0, 60]:
                new_bullet = bullet(self.x_position, self.y_position, predicted_angle + offset, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(new_bullet)
                
        elif self.shape_type == ShapeTurret.ultra_chaser:
            # 6 radial homing triangles spaced 60 degrees apart in a full circle (Requirement updated)
            for i in range(6):
                burst_angle = predicted_angle + (i * 60)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(new_bullet)
                
        elif self.shape_type == ShapeTurret.espresso:
            # Hybrid: 6 radial homing triangles + 1 giant anti-boss cannonball straight forward (Requirement updated)
            for i in range(6):
                burst_angle = predicted_angle + (i * 60)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(new_bullet)
            # Giant nuke cannonball
            nuke = bullet(self.x_position, self.y_position, predicted_angle, speed=320, damage=500, bullet_type="normal")
            bullet_group.add(nuke)
            
        elif self.shape_type == ShapeTurret.emperor:
            # Hybrid: 6 radial homing triangles + 2 giant parallel anti-boss cannonballs (Requirement updated)
            for i in range(6):
                burst_angle = predicted_angle + (i * 60)
                new_bullet = bullet(self.x_position, self.y_position, burst_angle, speed=300, damage=15, bullet_type="homing")
                bullet_group.add(new_bullet)
            # Double parallel nukes
            nuke1 = bullet(self.x_position + dx, self.y_position + dy, predicted_angle, speed=320, damage=500, bullet_type="normal")
            nuke2 = bullet(self.x_position - dx, self.y_position - dy, predicted_angle, speed=320, damage=500, bullet_type="normal")
            bullet_group.add(nuke1, nuke2)