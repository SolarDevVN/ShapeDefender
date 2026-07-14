# src/farm_obj.py

import pygame
from src.type import ShapeTurret

class farm(pygame.sprite.Sprite):
    def __init__(self, x_position, y_position, shape_type):
        super().__init__()
        self.x_position = x_position
        self.y_position = y_position
        self.shape_type = shape_type
        self.money_timer = 0.0
        
        self.generation_rate = 3 if shape_type == ShapeTurret.farm_t1 else 7
        self.size = 16
        
        # Setup pygame Sprite properties
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x_position), int(self.y_position)))
        self.draw_farm()

    def draw_farm(self):
        if self.shape_type == ShapeTurret.farm_t1:
            pygame.draw.rect(self.image, (0, 200, 0), (0, 0, self.size * 2, self.size * 2))
            pygame.draw.rect(self.image, (0, 100, 0), (0, 0, self.size * 2, self.size * 2), 2)
        else:
            pygame.draw.rect(self.image, (0, 130, 0), (0, 0, self.size * 2, self.size * 2))
            pygame.draw.rect(self.image, (0, 60, 0), (0, 0, self.size * 2, self.size * 2), 3)

    def update(self, dt):
        self.money_timer += dt
        if self.money_timer >= 1.0:
            self.money_timer -= 1.0
            return self.generation_rate
        return 0