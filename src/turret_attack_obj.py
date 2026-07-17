# src/turret_attack_obj.py

import pygame
import math
import random

class bullet(pygame.sprite.Sprite):
    def __init__(self, x_position, y_position, angle, speed, damage, bullet_type="normal", range_limit=200):
        super().__init__()
        self.x_position = x_position
        self.y_position = y_position
        
        # Track origin coordinates to measure travel distance
        self.origin_x = x_position
        self.origin_y = y_position
        self.range_limit = range_limit
        
        self.speed = speed
        self.damage = damage
        self.bullet_type = bullet_type  # "normal", "cluster", "omega", "fracture", "fracture_mini", "mini", "hyper", "stun", "slow", "laser", "homing", "homing_large", "homing_mega"
        
        # Infinite pierce for laser beams, 5 pierce limit for Hyper
        self.pierce_limit = 5 if bullet_type == "hyper" else (999999 if bullet_type == "laser" else 1)
        
        # Dedicated persistent target slot to prevent frame-by-frame target switching (Requirement updated)
        self.target = None
        
        rad = math.radians(-angle)
        self.dx = math.cos(rad) * speed
        self.dy = math.sin(rad) * speed
        
        # Dimensions based on projectile classification
        if bullet_type == "homing_mega":
            size = 28
        elif bullet_type == "homing_large":
            size = 20
        elif bullet_type in ["hyper", "laser"]:
            size = 30
        elif bullet_type in ["cluster", "omega", "fracture", "stun", "homing"]:
            size = 14
        else:
            size = 6
            
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x_position), int(self.y_position)))
        self.size = size
        
        # Setup specific coloring parameters
        if bullet_type == "hyper":
            self.color = (0, 191, 255)
        elif bullet_type == "laser":
            self.color = (0, 255, 255)  
        elif bullet_type == "slow":
            self.color = (124, 252, 0)  
        elif bullet_type == "stun":
            self.color = (30, 144, 255)  
        elif bullet_type in ["homing", "homing_large", "homing_mega"]:
            self.color = (255, 165, 0) if bullet_type == "homing" else (0, 191, 255)
        elif bullet_type != "normal":
            self.color = (255, 165, 0)
        else:
            self.color = (255, 255, 0)
            
        self.redraw_projectile()

    def redraw_projectile(self):
        self.image.fill((0, 0, 0, 0))
        center_x, center_y = self.size, self.size
        
        # Renders projectiles of this class as sharp, vector-rotating triangles
        if self.bullet_type in ["homing", "homing_large", "homing_mega"]:
            angle = math.atan2(self.dy, self.dx)
            length = self.size * 1.4
            width = self.size * 0.7
            
            p1 = (center_x + length * math.cos(angle), center_y + length * math.sin(angle))
            p2 = (center_x + width * math.cos(angle + math.radians(135)), center_y + width * math.sin(angle + math.radians(135)))
            p3 = (center_x + width * math.cos(angle - math.radians(135)), center_y + width * math.sin(angle - math.radians(135)))
            pygame.draw.polygon(self.image, self.color, [p1, p2, p3])
        else:
            pygame.draw.circle(self.image, self.color, (center_x, center_y), self.size // 2)

    def move(self, dt, bullet_group, enemies_group=None):
        """
        Modified move handles persistent lock-on targeting (Requirement updated).
        """
        # Homing targeting logic
        if self.bullet_type in ["homing", "homing_large", "homing_mega"] and enemies_group is not None:
            # Only scan and pick a new target if our current target is dead or missing
            if self.target is None or not self.target.alive() or self.target not in enemies_group:
                max_hp = -1
                candidates = []
                for enemy_sprite in enemies_group:
                    if enemy_sprite.alive():
                        if enemy_sprite.hp > max_hp:
                            max_hp = enemy_sprite.hp
                            candidates = [enemy_sprite]
                        elif enemy_sprite.hp == max_hp:
                            candidates.append(enemy_sprite)
                
                # Lock onto a single target from the highest-health candidates
                self.target = random.choice(candidates) if candidates else None
                
            # Steer smoothly and aggressively toward our locked target
            if self.target:
                dx = self.target.x_position - self.x_position
                dy = self.target.y_position - self.y_position
                dist = math.hypot(dx, dy)
                if dist > 0:
                    desired_dx = (dx / dist) * self.speed
                    desired_dy = (dy / dist) * self.speed
                    # Snappy 0.35 blending prevents orbit overshoot and guarantees hits
                    self.dx += (desired_dx - self.dx) * 0.35
                    self.dy += (desired_dy - self.dy) * 0.35
                    cur_speed = math.hypot(self.dx, self.dy)
                    if cur_speed > 0:
                        self.dx = (self.dx / cur_speed) * self.speed
                        self.dy = (self.dy / cur_speed) * self.speed
                        
            self.redraw_projectile()

        self.x_position += self.dx * dt
        self.y_position += self.dy * dt
        self.rect.center = (int(self.x_position), int(self.y_position))
        
        # Detonate automatically upon reaching maximum turret range
        if self.bullet_type in ["cluster", "omega", "fracture", "fracture_mini"]:
            distance_traveled = math.hypot(self.x_position - self.origin_x, self.y_position - self.origin_y)
            if distance_traveled >= self.range_limit:
                self.trigger_explosion(bullet_group)
                self.kill()

    def trigger_explosion(self, bullet_group):
        """
        Handles unique splinter and cluster logic depending on the bullet type.
        """
        if self.bullet_type == "cluster":
            for i in range(12):
                angle = i * 30
                new_bullet = bullet(self.x_position, self.y_position, angle, speed=200, damage=5, bullet_type="mini")
                bullet_group.add(new_bullet)
                
        elif self.bullet_type == "omega":
            for i in range(24):
                angle = i * 15
                new_bullet = bullet(self.x_position, self.y_position, angle, speed=200, damage=10, bullet_type="mini")
                bullet_group.add(new_bullet)
                
        elif self.bullet_type == "fracture":
            for i in range(5):
                angle = i * 72
                new_bullet = bullet(self.x_position, self.y_position, angle, speed=200, damage=8, bullet_type="fracture_mini")
                bullet_group.add(new_bullet)
                
        elif self.bullet_type == "fracture_mini":
            for i in range(5):
                angle = i * 72
                new_bullet = bullet(self.x_position, self.y_position, angle, speed=200, damage=5, bullet_type="mini")
                bullet_group.add(new_bullet)