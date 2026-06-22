import random

from entities.car import Car
from config.settings import settings
from config.constants import (
    ASSETS, ENEMY_HITBOX_DECREASE, ENEMY_OFFSET_X, LANE_POSITIONS, HEIGHT
)


class Enemy(Car):
    """Машина врага."""

    def __init__(self):
        super().__init__(
            ASSETS["enemy_car"],
            0.45,
            0.35,
            ENEMY_HITBOX_DECREASE,
            ENEMY_OFFSET_X
        )

        self.base_speed = 0
        self.is_oncoming = False  # встречка

        self.spawn()

    def spawn(self):
        """Генерация случайных параметров для появления нового врага."""
        self.rect.y = -200
        self.rect.x = random.choice(LANE_POSITIONS)

        # Переменная, определяющая встречный ли это враг
        self.is_oncoming = (
            settings.oncoming_traffic_enabled and self.rect.x in LANE_POSITIONS[:2]
        )

        # Выбираем скорость и ориентацию картинки
        if self.is_oncoming:
            self.offset_x = ENEMY_OFFSET_X
            self.image = self.image_rotated
            self.base_speed = random.randint(5, 7)  # встречные быстрее
        else:
            self.offset_x = 4
            self.image = self.image_scaled
            self.base_speed = random.randint(3, 5)  # попутные медленнее

        # Пересоздаём rect
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))

        self.sync_hitbox()

    def move(self, world_speed):
        if self.is_oncoming:
            visual_speed = self.base_speed + world_speed
        else:
            visual_speed = world_speed - self.base_speed

        self.rect.y += visual_speed

        # Если враг ушёл за нижнюю границу — создаём нового
        if self.rect.top > HEIGHT:
            self.spawn()

        self.sync_hitbox()
