import pygame

from config.constants import ASSETS, ROAD_SPEED, HEIGHT


class Road:
    """Дорога."""

    def __init__(self):
        self.image = pygame.image.load(ASSETS["road"])
        self.rect = self.image.get_rect()

        self.speed = ROAD_SPEED

        self.y1 = 0
        self.y2 = -self.image.get_height()  # вторая копия начинается сверху

    def draw(self, screen):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))

    def move(self, world_speed):
        self.y1 += world_speed
        self.y2 += world_speed

        # Перемещаем обе копии дороги наверх, когда они снизу вышли за экран
        if self.y1 >= HEIGHT:
            self.y1 = self.y2 - self.image.get_height()
        if self.y2 >= HEIGHT:
            self.y2 = self.y1 - self.image.get_height()
