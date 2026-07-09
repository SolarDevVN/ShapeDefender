# src/bullet_obj.py
import pygame
import math


class bullet:
    def __init__(self, x_position, y_position, angle, speed, damage):
        self.x_position = x_position
        self.y_position = y_position
        self.speed = speed
        self.damage = damage
        
        # Convert Pygame angle back to radians to calculate 2D direction vectors
        rad = math.radians(-angle)
        self.dx = math.cos(rad) * speed
        self.dy = math.sin(rad) * speed

    def move(self, dt):
        self.x_position += self.dx * dt
        self.y_position += self.dy * dt

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x_position), int(self.y_position)), 5)