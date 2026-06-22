import pygame


class Car:
    """Базовый класс для всех машин игры."""

    def __init__(self, image_path, scale_x, scale_y, hitbox_decrease, offset_x):
        base_image = pygame.image.load(image_path)
        self.image_scaled = pygame.transform.smoothscale(
            base_image,
            (
                int(base_image.get_width() * scale_x),
                int(base_image.get_height() * scale_y),
            ),
        )
        # Повёрнутая версия
        self.image_rotated = pygame.transform.rotate(self.image_scaled, 180)
        self.image = self.image_scaled  # по умолчанию

        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(*hitbox_decrease)  # уменьшаем хитбокс

        self.offset_x = (
            offset_x  # смещение по оси OX для правки отображения в дебаг-режиме
        )

        self.speed = 0

    def draw(self, screen):
        draw_x = self.rect.x + self.offset_x  # учитываем смещение картинки
        screen.blit(self.image, (draw_x, self.rect.y))

    def sync_hitbox(self):
        self.hitbox.center = self.rect.center  # синхронизируем картинку и её хитбокс
