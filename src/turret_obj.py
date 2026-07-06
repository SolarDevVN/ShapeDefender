# src/turret_obj.py

import pygame
import math

def draw_shape(surface, shape_type, color, center, size, alpha=255):
    """
    Draws a colored shape (hexagon, circle, square, or triangle).
    Supports transparency via the alpha parameter (0-255).
    """
    center_x, center_y = center
    
    # Create temporary surface with transparency support
    temp_surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
    local_center = (size + 1, size + 1)
    
    if shape_type == "hexagon":
        points = []
        for vertex_index in range(6):
            angle_rad = math.radians(60 * vertex_index)
            vertex_x = local_center[0] + size * math.cos(angle_rad)
            vertex_y = local_center[1] + size * math.sin(angle_rad)
            points.append((vertex_x, vertex_y))
        pygame.draw.polygon(temp_surface, color + (alpha,), points)
        
    elif shape_type == "circle":
        pygame.draw.circle(temp_surface, color + (alpha,), local_center, size)
        
    elif shape_type == "square":
        # Draw a centered square
        pygame.draw.rect(
            temp_surface, 
            color + (alpha,), 
            (local_center[0] - size, local_center[1] - size, size * 2, size * 2)
        )
        
    elif shape_type == "triangle":
        # Draw an upward-pointing triangle
        points = [
            (local_center[0], local_center[1] - size),
            (local_center[0] - size, local_center[1] + size),
            (local_center[0] + size, local_center[1] + size)
        ]
        pygame.draw.polygon(temp_surface, color + (alpha,), points)
        
    surface.blit(temp_surface, (center_x - size - 1, center_y - size - 1))


class turret:
    def __init__(self, x_position, y_position, shape_type="hexagon", cooldown=1.0, direction=0):
        self.x_position = x_position
        self.y_position = y_position
        self.shape_type = shape_type
        self.cooldown = cooldown
        self.direction = direction
        self.have_place = False

    def placing(self):
        self.have_place = True

    def draw(self, surface, size):
        # Draw the solid version of whatever shape this turret is
        draw_shape(surface, self.shape_type, (0, 255, 255), (self.x_position, self.y_position), size)