# src/farm_obj.py

import pygame
from src.type import ShapeTurret

class farm:
    def __init__(self, x_position, y_position, shape_type):
        self.x_position = x_position
        self.y_position = y_position
        self.shape_type = shape_type
        self.money_timer = 0.0
        
        # Determine income generation rate per second
        self.generation_rate = 1 if shape_type == ShapeTurret.farm_t1 else 2
        
        # Set farm visual boundaries
        self.size = 16  # Matches HEX_SIZE (0.4 * TILE_SIZE)
        self.rect = pygame.Rect(self.x_position - self.size, self.y_position - self.size, self.size * 2, self.size * 2)

    def update(self, dt):
        """
        Counts down 1 second. Returns generation income when ready, otherwise returns 0.
        """
        self.money_timer += dt
        if self.money_timer >= 1.0:
            self.money_timer -= 1.0
            return self.generation_rate
        return 0

    def draw(self, surface):
        # Draw styled green structure (Light Green for T1, Dark Green for T2)
        if self.shape_type == ShapeTurret.farm_t1:
            pygame.draw.rect(surface, (0, 200, 0), self.rect)
            pygame.draw.rect(surface, (0, 100, 0), self.rect, 2)
        else:
            pygame.draw.rect(surface, (0, 130, 0), self.rect)
            pygame.draw.rect(surface, (0, 60, 0), self.rect, 3)