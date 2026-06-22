import pygame
import random

from button import create_buttons
from settings import settings
from constants import (
    ASSETS, WIDTH, HEIGHT, ROAD_SPEED, PLAYER_HITBOX_DECREASE, PLAYER_OFFSET_X,
    BUTTON_SPACING, START_Y_POS_PLAYER, ROAD_LEFT_BORDER, ROAD_RIGHT_BORDER,
    ENEMY_HITBOX_DECREASE, ENEMY_OFFSET_X, LANE_POSITIONS, HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT, HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_BORDER,
    WHITE, BLACK, GREEN, YELLOW, RED
)


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
        # Повёрнутая версия (на 180°)
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


class Player(Car):
    """Машина игрока."""

    def __init__(self):
        super().__init__(
            ASSETS["player_car"], 0.35, 0.35, PLAYER_HITBOX_DECREASE, PLAYER_OFFSET_X
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


class Enemy(Car):
    """Машина врага."""

    def __init__(self):
        super().__init__(
            ASSETS["enemy_car"], 0.45, 0.35, ENEMY_HITBOX_DECREASE, ENEMY_OFFSET_X
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

        # Выбираем ориентацию картинки
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
        self.hitbox = self.rect.inflate(-10, -10)
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


class FloatingText:
    """Всплывающий текст с эффектом подъёма и затухания."""

    LIFE_TIME = 90
    RISE_SPEED = 1.5
    FADE_START = 60

    def __init__(self, text, x, y, color=WHITE):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life_time = self.LIFE_TIME

        self.font = pygame.font.SysFont(None, 36)
        self.surface = self.font.render(self.text, True, self.color)
        self.alpha = 255  # полная непрозрачность

    def update(self):
        """Обновление позиции и прозрачности."""
        self.y -= self.RISE_SPEED  # подъём вверх
        self.life_time -= 1

        # Затухание в последние кадры
        if self.life_time < self.FADE_START:
            fade_ratio = self.life_time / self.FADE_START
            self.alpha = int(255 * fade_ratio)

    def draw(self, screen):
        """Отрисовка текста с текущей прозрачностью."""
        # Создаём копию поверхности с альфа-каналом
        text_surface = self.surface.copy()
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, (self.x, self.y))

    def is_expired(self):
        """Проверка, истёк ли срок жизни."""
        return self.life_time <= 0


class Overlay:
    """Окно поверх игры."""

    PANEL_WIDTH = 500
    PANEL_HEIGHT = 400
    OVERLAY_ALPHA = 150
    FIRST_BUTTON_Y = 330

    def __init__(self, title, button_configs):
        """
        title — текст заголовка (например, "Game Over")
        button_configs — список кортежей (text, action_name)
        """
        self.title = title
        self.buttons = []
        self.button_actions = {}  # {кнопка: имя действия}

        self.panel_rect = pygame.Rect(
            WIDTH // 2 - self.PANEL_WIDTH // 2,
            HEIGHT // 2 - self.PANEL_HEIGHT // 2,
            self.PANEL_WIDTH,
            self.PANEL_HEIGHT,
        )

        self.title_font = pygame.font.SysFont(None, 96)

        self._create_button(button_configs)

    def _create_button(self, button_configs):
        for i, (text, action_name) in enumerate(button_configs):
            y_pos = self.FIRST_BUTTON_Y + i * BUTTON_SPACING
            button = create_buttons(text, y_pos, "green")
            self.buttons.append(button)
            self.button_actions[button] = action_name

    def draw(self, screen):
        # Полупрозрачный тёмный фон поверх всей игры
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(self.OVERLAY_ALPHA)
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, WHITE, self.panel_rect)
        pygame.draw.rect(screen, BLACK, self.panel_rect, 3)  # рамка

        text_surface = self.title_font.render(self.title, True, BLACK)
        text_x = self.panel_rect.centerx - text_surface.get_width() // 2
        text_y = self.panel_rect.top + 40
        screen.blit(text_surface, (text_x, text_y))

        for button in self.buttons:
            button.check_hover(pygame.mouse.get_pos())
            button.draw(screen)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

        if event.type == pygame.USEREVENT:
            for button in self.buttons:
                if event.button == button:
                    return self.button_actions[button]

        return None


class HealthBar:
    """Полоска здоровья."""

    def __init__(self, max_health):
        self.max_health = max_health
        self.current_health = max_health

        self.font = pygame.font.SysFont(None, 30)

    def update(self, health):
        self.current_health = max(0, health)  # не ниже 0

    def draw(self, screen):
        # Фон полоски
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT),
        )

        # Динамическое заполнение
        health_ratio = self.current_health / self.max_health
        fill_width = int(HEALTH_BAR_WIDTH * health_ratio)

        if health_ratio > 0.5:
            color = GREEN
        elif health_ratio > 0.25:
            color = YELLOW
        else:
            color = RED

        pygame.draw.rect(
            screen, color, (HEALTH_BAR_X, HEALTH_BAR_Y, fill_width, HEALTH_BAR_HEIGHT)
        )
        # Рамка
        pygame.draw.rect(
            screen,
            WHITE,
            (HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT),
            HEALTH_BAR_BORDER,
        )

        text = self.font.render(f"{self.current_health}/{self.max_health}", True, WHITE)
        text_rect = text.get_rect(
            center=(
                HEALTH_BAR_X + HEALTH_BAR_WIDTH // 2,
                HEALTH_BAR_Y + HEALTH_BAR_HEIGHT // 2,
            )
        )
        screen.blit(text, text_rect)
