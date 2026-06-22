import pygame

from ui.button import create_buttons
from config.constants import (
    WIDTH, HEIGHT, BUTTON_SPACING, HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT, HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_BORDER,
    WHITE, BLACK, GREEN, YELLOW, RED
)


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
            screen,
            color,
            (HEALTH_BAR_X, HEALTH_BAR_Y, fill_width, HEALTH_BAR_HEIGHT)
        )
        # Рамка
        pygame.draw.rect(
            screen,
            WHITE,
            (HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT),
            HEALTH_BAR_BORDER,
        )

        text = self.font.render(
            f"{self.current_health}/{self.max_health}", True, WHITE
        )
        text_rect = text.get_rect(
            center=(
                HEALTH_BAR_X + HEALTH_BAR_WIDTH // 2,
                HEALTH_BAR_Y + HEALTH_BAR_HEIGHT // 2,
            )
        )
        screen.blit(text, text_rect)
