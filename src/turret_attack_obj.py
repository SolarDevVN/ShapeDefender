# src/turret_attack_obj.py

import pygame
import math

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
        self.bullet_type = bullet_type  # "normal", "cluster", "omega", "fracture", "fracture_mini", "mini", "hyper"
        
        rad = math.radians(-angle)
        self.dx = math.cos(rad) * speed
        self.dy = math.sin(rad) * speed
        
        # Hyper energy balls are scaled massively
        size = 30 if bullet_type == "hyper" else (12 if bullet_type in ["cluster", "omega", "fracture"] else 6)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Color codes based on ammunition tier
        if bullet_type == "hyper":
            color = (0, 191, 255)  # Bright Cyan laser ball
        elif bullet_type != "normal":
            color = (255, 165, 0)
        else:
            color = (255, 255, 0)
            
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(int(self.x_position), int(self.y_position)))

    def move(self, dt, bullet_group):
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