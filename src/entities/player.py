import pygame

from entities.car import Car
from config.constants import (
    ASSETS, PLAYER_HITBOX_DECREASE, PLAYER_OFFSET_X,
    WIDTH, START_Y_POS_PLAYER, ROAD_LEFT_BORDER, ROAD_RIGHT_BORDER
)


class Player(Car):
    """Машина игрока."""

    def __init__(self):
        super().__init__(
            ASSETS["player_car"],
            0.35,
            0.35,
            PLAYER_HITBOX_DECREASE,
            PLAYER_OFFSET_X
        )
        self.image = self.image_rotated  # игрок всегда повернутая картинка
        self.rect = self.image.get_rect()  # пересоздаём rect после поворота

        self.base_x = WIDTH // 2 - self.rect.width // 2
        self.base_y = START_Y_POS_PLAYER
        self.rect.topleft = (self.base_x, self.base_y)

        self.speed = 5

        self.max_health = 100
        self.health = self.max_health

        # Неуязвимость после получения урона
        self.invulnerable = False
        self.invulnerable_timer = 0  # таймер, который будет обновляться
        self.invulnerable_duration = 60  # время неуязвимости

        self.sync_hitbox()

    def update_invulnerable(self):
        """Обновление таймера неуязвимости."""
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def draw(self, screen):
        # Если неуязвим - пропускаем некоторые кадры
        if self.invulnerable and self.invulnerable_timer % 13 < 5:
            return

        draw_x = self.rect.x + self.offset_x  # учитываем смещение картинки
        screen.blit(self.image, (draw_x, self.rect.y))

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Ограничения движения игрока в пределах дороги
        self.rect.left = max(self.rect.left, ROAD_LEFT_BORDER)
        self.rect.right = min(self.rect.right, ROAD_RIGHT_BORDER)

        self.rect.y = self.base_y  # управление через GameManager

        self.sync_hitbox()
