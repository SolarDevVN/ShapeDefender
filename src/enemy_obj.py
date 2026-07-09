# src/enemy_obj.py
import pygame

class enemy:
    # Added 'hp' with a default value of 100 to the initializer parameters
    def __init__(self, speed, damage, path_waypoints: list[pygame.math.Vector2], hp=100):
        self.speed = speed
        self.damage = damage
        self.path = path_waypoints
        self.waypoint_index = 0
        
        self.x_position = self.path[0].x
        self.y_position = self.path[0].y
        
        # Requirement 3: Add hp and max_hp
        self.max_hp = hp
        self.hp = hp

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
            
        return True

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x_position), int(self.y_position)), 15)