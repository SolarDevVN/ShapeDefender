# src/enemy_obj.py
import pygame

class enemy:
    # Added 'hp' with a default value of 100 to the initializer parameters
    def __init__(self, speed, damage, path_waypoints: list[pygame.math.Vector2], select_type, hp=100):
        self.speed = speed
        self.damage = damage
        self.path = path_waypoints
        self.waypoint_index = 0
        self.x_position = self.path[0].x
        self.y_position = self.path[0].y
        self.max_hp = hp
        self.hp = hp
        self.type = select_type

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
        if self.type == "circle":
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x_position), int(self.y_position)), 15)
        elif self.type == "square":
            pygame.draw.rect(surface, (255, 0, 0), (int(self.x_position) - 10, int(self.y_position) - 10, 20, 20))
        elif self.type == "triangle":
            pygame.draw.polygon(surface, (255, 0, 0), [
                (int(self.x_position), int(self.y_position) - 15),
                (int(self.x_position) - 15, int(self.y_position) + 15),
                (int(self.x_position) + 15, int(self.y_position) + 15)
            ])
        elif self.type == "pentagon":
            pygame.draw.polygon(surface, (255, 0, 0), [
                (int(self.x_position), int(self.y_position) - 15),
                (int(self.x_position) - 14, int(self.y_position) - 5),
                (int(self.x_position) - 9, int(self.y_position) + 12),
                (int(self.x_position) + 9, int(self.y_position) + 12),
                (int(self.x_position) + 14, int(self.y_position) - 5)
            ])
        elif self.type == "hexagon":
            pygame.draw.polygon(surface, (255, 0, 0), [
                (int(self.x_position) - 15, int(self.y_position)),
                (int(self.x_position) - 7, int(self.y_position) - 13),
                (int(self.x_position) + 7, int(self.y_position) - 13),
                (int(self.x_position) + 15, int(self.y_position)),
                (int(self.x_position) + 7, int(self.y_position) + 13),
                (int(self.x_position) - 7, int(self.y_position) + 13)
            ])