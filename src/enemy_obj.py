# src/enemy_obj.py
import pygame
import math

class enemy(pygame.sprite.Sprite):
    # Added 'hp' with a default value of 100 to the initializer parameters
    def __init__(self, speed, damage, path_waypoints: list[pygame.math.Vector2], select_type, hp=100):
        super().__init__()
        self.speed = speed
        self.base_speed = speed # Store original speed to restore after slowing effects
        self.damage = damage
        self.path = path_waypoints
        self.waypoint_index = 0
        self.x_position = self.path[0].x
        self.y_position = self.path[0].y
        self.max_hp = hp
        self.hp = hp
        self.type = select_type
        
        # Temp slow timer applied by sniper darts (Requirement added)
        self.slow_timer = 0.0
        
        # Setup pygame Sprite properties
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x_position), int(self.y_position)))

    def get_rainbow_color(self):
        """
        Calculates rainbow colors based on wave-scaled max health metrics.
        Red represents the early game, shifting to Purple at the endgame.
        """
        if self.max_hp <= 120:
            return (220, 50, 50)       # Red
        elif self.max_hp <= 250:
            return (255, 127, 0)      # Orange
        elif self.max_hp <= 450:
            return (255, 215, 0)      # Yellow
        elif self.max_hp <= 800:
            return (50, 205, 50)       # Green
        elif self.max_hp <= 1500:
            return (30, 144, 255)      # Blue
        elif self.max_hp <= 3000:
            return (75, 0, 130)        # Indigo
        else:
            return (138, 43, 226)      # Purple

    def move(self, dt):
        if self.waypoint_index >= len(self.path):
            return False

        # Handles slow velocity scaling (Requirement added)
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * 0.5  # Reduce speed by 50%
            if self.slow_timer <= 0:
                self.speed = self.base_speed
        else:
            self.speed = self.base_speed

        target = self.path[self.waypoint_index]
        current_pos = pygame.math.Vector2(self.x_position, self.y_position)
        direction = target - current_pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()
            step = self.speed * dt

            if step >= distance:
                self.x_position = target.x
                self.y_position = target.y
                self.waypoint_index += 1
            else:
                new_pos = current_pos + direction * step
                self.x_position = new_pos.x
                self.y_position = new_pos.y
        else:
            self.waypoint_index += 1
            
        # Keep Sprite rect aligned with coordinates
        self.rect.center = (int(self.x_position), int(self.y_position))
        return True

    def draw(self, surface):
        self.image.fill((0, 0, 0, 0))  # Clear transparent
        color = self.get_rainbow_color()
        
        if self.type == "circle":
            pygame.draw.circle(self.image, color, (15, 15), 15)
        elif self.type == "square":
            pygame.draw.rect(self.image, color, (5, 5, 20, 20))
        elif self.type == "triangle":
            pygame.draw.polygon(self.image, color, [(15, 0), (0, 30), (30, 30)])
        elif self.type == "pentagon":
            pygame.draw.polygon(self.image, color, [(15, 0), (1, 10), (6, 27), (24, 27), (29, 10)])
        elif self.type == "hexagon":
            pygame.draw.polygon(self.image, color, [(0, 15), (8, 2), (22, 2), (30, 15), (22, 28), (8, 28)])
        elif self.type == "diamond":  # Faster diamond shape
            pygame.draw.polygon(self.image, color, [(15, 0), (5, 15), (15, 30), (25, 15)])
        elif self.type == "star":  # Projectile stunner Star
            points = []
            for i in range(10):
                r = 15 if i % 2 == 0 else 6
                angle = math.radians(i * 36 - 90)
                points.append((15 + r * math.cos(angle), 15 + r * math.sin(angle)))
            pygame.draw.polygon(self.image, color, points)
        elif self.type == "octagon":  # Mini-boss octagon
            points = []
            for i in range(8):
                angle = math.radians(i * 45 - 22.5)
                points.append((15 + 15 * math.cos(angle), 15 + 15 * math.sin(angle)))
            pygame.draw.polygon(self.image, color, points)
        elif self.type == "dodecagon":  # Boss dodecagon
            points = []
            for i in range(12):
                angle = math.radians(i * 30 - 15)
                points.append((15 + 15 * math.cos(angle), 15 + 15 * math.sin(angle)))
            pygame.draw.polygon(self.image, color, points)