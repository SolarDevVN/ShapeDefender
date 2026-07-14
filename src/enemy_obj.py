# src/enemy_obj.py
import pygame

class enemy(pygame.sprite.Sprite):
    # Added 'hp' with a default value of 100 to the initializer parameters
    def __init__(self, speed, damage, path_waypoints: list[pygame.math.Vector2], select_type, hp=100):
        super().__init__()
        self.speed = speed
        self.damage = damage
        self.path = path_waypoints
        self.waypoint_index = 0
        self.x_position = self.path[0].x
        self.y_position = self.path[0].y
        self.max_hp = hp
        self.hp = hp
        self.type = select_type
        
        # Setup pygame Sprite properties
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x_position), int(self.y_position)))
        self.draw_enemy_shape()

    def draw_enemy_shape(self):
        self.image.fill((0, 0, 0, 0))  # Clear transparent
        if self.type == "circle":
            pygame.draw.circle(self.image, (255, 0, 0), (15, 15), 15)
        elif self.type == "square":
            pygame.draw.rect(self.image, (255, 0, 0), (5, 5, 20, 20))
        elif self.type == "triangle":
            pygame.draw.polygon(self.image, (255, 0, 0), [(15, 0), (0, 30), (30, 30)])
        elif self.type == "pentagon":
            pygame.draw.polygon(self.image, (255, 0, 0), [(15, 0), (1, 10), (6, 27), (24, 27), (29, 10)])
        elif self.type == "hexagon":
            pygame.draw.polygon(self.image, (255, 0, 0), [(0, 15), (8, 2), (22, 2), (30, 15), (22, 28), (8, 28)])

    def move(self, dt):
        if self.waypoint_index >= len(self.path):
            return False

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