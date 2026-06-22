import pygame
import random

from config.constants import HEIGHT


class Bonus:
    """Бонус."""

    scale_x = 0.3
    scale_y = 0.3

    def __init__(self, image_path, effects_type):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.smoothscale(
            self.image,
            (
                int(self.image.get_width() * self.scale_x),
                int(self.image.get_height() * self.scale_y),
            ),
        )

        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(0, 0)
        self.speed = 0

        self.effects_type = effects_type

        # Начальная позиция
        self.rect.y = -100
        self.rect.x = random.randint(150, 850)

        self.sync_hitbox()

    def move(self, world_speed):
        self.rect.y += world_speed
        self.sync_hitbox()

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def sync_hitbox(self):
        self.hitbox.center = self.rect.center

    def is_off_screen(self):
        return self.rect.top > HEIGHT
