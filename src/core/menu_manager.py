import pygame
import sys

from core.base_manager import BaseManager
from core.game_manager import GameManager
from config.settings import settings
from ui.button import create_buttons
from config.constants import (
    WIDTH, HEIGHT, FPS, FADE_SPEED, WHITE, BLACK,
    ASSETS, Y_BUTTON, BUTTON_SPACING, MAX_FADE_ALPHA,
)


class MenuManager(BaseManager):
    def __init__(self, screen):
        super().__init__(screen)
        self.window = "menu"  # какое окно отображать
        self.game_manager = None  # GameManager создаётся при входе в игру

        self.main_background = pygame.image.load(ASSETS["main_background"])
        self.clock = pygame.time.Clock()
        self.first_font = pygame.font.SysFont(None, 72)
        self.second_font = pygame.font.SysFont(None, 40)

        # Переменные для затухания
        self.transition_state = None  # None, "fade_out", "fade_in"
        self.target_window = None  # целевое окно после затухания
        self.fade_alpha = 0  # уровень прозрачности для затухания
        self.fade_speed = FADE_SPEED  # скорость затухания

        # Создание кнопок
        self.start_button = create_buttons("Играть", Y_BUTTON, "green")
        self.settings_button = create_buttons(
            "Настройки", Y_BUTTON + BUTTON_SPACING, "green"
        )
        self.exit_button = create_buttons(
            "Выйти",
            Y_BUTTON + 2 * BUTTON_SPACING,
            "red"
        )
        self.oncoming_traffic_button = create_buttons(
            "Встречка",
            Y_BUTTON,
            "green"
        )
        self.back_button = create_buttons(
            "Назад",
            Y_BUTTON + BUTTON_SPACING,
            "green"
        )
        self.buttons_list = []

    def process_event(self, event):
        """Обработка события."""
        if event.type == pygame.QUIT:
            self.running = False

        if (
            self.window == "settings"
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            self.start_transition("menu")

        if self.window == "game" and self.game_manager is not None:
            self.game_manager.process_event(event)

        # Обработка событий для кнопок
        for button in self.buttons_list:
            button.handle_event(event)

        if event.type == pygame.USEREVENT:
            if event.button == self.start_button:
                self.start_transition("game")
            elif event.button == self.settings_button:
                self.start_transition("settings")
            elif event.button == self.back_button:
                self.start_transition("menu")
            elif event.button == self.exit_button:
                self.running = False
            elif event.button == self.oncoming_traffic_button:
                settings.oncoming_traffic_enabled = (
                    not settings.oncoming_traffic_enabled
                )

    def start_transition(self, target):
        """Старт анимации затухания и установка целевого окна."""
        if self.transition_state is None:
            self.target_window = target
            self.transition_state = "fade_out"
            self.fade_alpha = 0

    def apply_transition(self):
        """Управление логикой затухания."""
        # Логика затухания
        if self.transition_state == "fade_out":
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= MAX_FADE_ALPHA:
                self.fade_alpha = MAX_FADE_ALPHA
                # Переключение экрана пока окно чёрное
                self.window = self.target_window
                # Переключаем режим на осветление
                self.transition_state = "fade_in"

        # Логика осветления
        elif self.transition_state == "fade_in":
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.transition_state = None  # завершаем анимацию

        # Чёрный полупрозрачный слой для эффекта затухания поверх окна
        if self.transition_state is not None:
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

    def draw_background(self, background):
        """Базовая отрисовка фона"""
        self.screen.fill(BLACK)
        background = pygame.transform.smoothscale(
            background,
            (
                int(background.get_width() * 1.2),
                int(background.get_height() * 1.2),
            ),
        )
        self.screen.blit(background, (-50, 0))

    def draw_text(self, text, font, color, x_pos, y_pos, center=False):
        """Отрисовка текста."""
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(centerx=x_pos, y=y_pos)
        else:
            text_rect = text_surface.get_rect(topleft=(x_pos, y_pos))
        self.screen.blit(text_surface, text_rect)

    def draw_buttons(self):
        "Базовая отрисовка кнопок."
        for button in self.buttons_list:
            button.check_hover(pygame.mouse.get_pos())
            button.draw(self.screen)

    def draw_main_menu(self):
        """Отрисовка главного меню."""
        self.draw_background(self.main_background)
        self.draw_text(
            "TheFastestCar.",
            self.first_font,
            WHITE,
            WIDTH // 2,
            110,
            center=True
        )
        self.draw_text(
            "Игра для экзамена по программированию. by Яна Масалова",
            self.second_font,
            WHITE,
            WIDTH // 2,
            170,
            center=True
        )
        # Обработка и отрисовка кнопок
        self.draw_buttons()

    def draw_settings_menu(self):
        """Отрисовка меню настроек."""
        self.draw_background(self.main_background)
        self.draw_text(
            "Настройки",
            self.first_font,
            WHITE,
            WIDTH // 2,
            110,
            center=True
        )

        # Показываем текущее состояние встречки
        traffic_status = "ВКЛ" if settings.oncoming_traffic_enabled else "ВЫКЛ"
        self.draw_text(
            f"Встречка: {traffic_status}",
            self.second_font,
            WHITE,
            WIDTH // 2,
            230,
            center=True
        )

        # Обработка и отрисовка кнопок
        self.draw_buttons()

    def draw(self):
        """Отрисовка текущего окна."""
        if self.window == "menu":
            self.buttons_list = [
                self.start_button,
                self.settings_button,
                self.exit_button
            ]
            self.draw_main_menu()
        elif self.window == "settings":
            self.buttons_list = [
                self.oncoming_traffic_button,
                self.back_button
            ]
            self.draw_settings_menu()

    def run(self):
        """Бесконечный игровой цикл."""
        while self.running:
            self.handle_event()

            if self.window == "game":
                if self.game_manager is None:
                    self.game_manager = GameManager(self.screen)
                elif not self.game_manager.running:
                    if self.transition_state is None:
                        self.start_transition("menu")

            if self.window in ["menu", "settings"]:
                self.draw()
            elif self.window == "game" and self.game_manager is not None:
                self.buttons_list = []
                self.game_manager.run()

            self.apply_transition()

            if (
                self.window == "menu"
                and self.game_manager is not None
                and self.transition_state is None
            ):
                self.game_manager = None

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
