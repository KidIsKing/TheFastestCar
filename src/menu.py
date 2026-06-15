import pygame
import sys

from button import ImageButton


# Constans
WIDTH = 1500
HEIGHT = 850

CENTER_X_FOR_BUTTONS = 590
FPS = 60
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Assets
ASSETS_PATH = "assets/"
ASSETS = {
    "main_background": ASSETS_PATH + "images/background_menu.png",
    "game_background": ASSETS_PATH + "images/road.png",
    "green_button": ASSETS_PATH + "images/buttons/green_button.png",
    "green_button_hover": ASSETS_PATH + "images/buttons/green_button_hover.png",
    "red_button": ASSETS_PATH + "images/buttons/red_button.png",
    "red_button_hover": ASSETS_PATH + "images/buttons/red_button_hover.png",
    "click_sound": ASSETS_PATH + "sounds/click.mp3",
}


class MenuManager:
    def __init__(self):
        self.running = True
        self.window = "menu"  # какое окно отображать
        self.fade_alpha = 0  # уровень прозрачности для анимации затухания

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TheFastestCar")
        self.main_background = pygame.image.load(ASSETS["main_background"])
        self.game_background = pygame.image.load(ASSETS["game_background"])
        self.clock = pygame.time.Clock()

        self.first_font = pygame.font.SysFont(None, 128)
        self.second_font = pygame.font.SysFont(None, 64)

        # Создание кнопок
        self.start_button = ImageButton(
            CENTER_X_FOR_BUTTONS,
            300,
            350,
            100,
            "Играть",
            ASSETS["green_button"],
            ASSETS["green_button_hover"],
            ASSETS["click_sound"],
        )
        self.settings_button = ImageButton(
            CENTER_X_FOR_BUTTONS,
            400,
            350,
            100,
            "Настройки",
            ASSETS["green_button"],
            ASSETS["green_button_hover"],
            ASSETS["click_sound"],
        )
        self.exit_button = ImageButton(
            CENTER_X_FOR_BUTTONS,
            500,
            350,
            100,
            "Выйти",
            ASSETS["red_button"],
            ASSETS["red_button_hover"],
            ASSETS["click_sound"],
        )
        self.move_on_direction_button = ImageButton(
            CENTER_X_FOR_BUTTONS,
            300,
            350,
            100,
            "Встречка",
            ASSETS["green_button"],
            ASSETS["green_button_hover"],
            ASSETS["click_sound"],
        )
        self.left_line_button = ImageButton(
            CENTER_X_FOR_BUTTONS,
            400,
            350,
            100,
            "Левосторонка",
            ASSETS["green_button"],
            ASSETS["green_button_hover"],
            ASSETS["click_sound"],
        )
        self.back_button = ImageButton(
            CENTER_X_FOR_BUTTONS,
            500,
            350,
            100,
            "Назад",
            ASSETS["green_button"],
            ASSETS["green_button_hover"],
            ASSETS["click_sound"],
        )
        self.buttons_list = []

    def handle_event(self):
        "Обработка событий."
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Обработка событий для кнопок
            for button in self.buttons_list:
                button.handle_event(event)

            if event.type == pygame.USEREVENT and event.button == self.start_button:
                self.fade()
                self.window = "game"

            if event.type == pygame.USEREVENT and event.button == self.settings_button:
                self.fade()
                self.window = "settings"

            if event.type == pygame.USEREVENT and event.button == self.back_button:
                self.fade()
                self.window = "menu"

            if event.type == pygame.USEREVENT and event.button == self.exit_button:
                self.running = False

    def draw_background(self, background):
        "Базовая отрисовка фона"
        self.screen.fill(BLACK)
        self.screen.blit(background, (0, 0))

    def draw_text(self, text, font, color, x_pos, y_pos):
        "Отрисовка текста."
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x_pos, y_pos))

    def draw_buttons(self):
        "Базовая отрисовка кнопок."
        for button in self.buttons_list:
            button.check_hover(pygame.mouse.get_pos())
            button.draw(self.screen)

    def draw_main_menu(self):
        "Отрисовка главного меню."
        self.draw_background(self.main_background)

        # Текст главного меню
        self.draw_text("TheFastestCar. Главное меню", self.first_font, WHITE, 100, 110)
        self.draw_text("by Яна Масалова. Игра для экзамена по программированию", self.second_font, WHITE, 100, 200)

        # Обработка и отрисовка кнопок
        self.draw_buttons()

        pygame.display.flip()

    def draw_settings_menu(self):
        "Отрисовка меню настроек."
        self.draw_background(self.main_background)

        # Текст меню настроек
        self.draw_text("Настройки", self.first_font, WHITE, 535, 110)

        # Обработка и отрисовка кнопок
        self.draw_buttons()

        pygame.display.flip()

    def draw_play_menu(self):
        "Отрисовка игры."
        self.draw_background(self.game_background)

        # Обработка и отрисовка кнопок
        self.draw_buttons()

        pygame.display.flip()

    def fade(self):
        "Анимация затухания между окнами."
        # Анимация затухания текущего экрана
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(self.fade_alpha)
        self.screen.blit(fade_surface, (0, 0))

        # Увеличения уровня прозрачности
        self.fade_alpha += 5
        if self.fade_alpha >= 105:
            self.fade_alpha = 255
            self.running = False

        pygame.display.flip()

    def run(self):
        "Бесконечный игровой цикл."
        while self.running:
            self.handle_event()

            if self.window == "menu":
                self.buttons_list = [
                    self.start_button,
                    self.settings_button,
                    self.exit_button
                ]
                self.draw_main_menu()
            elif self.window == "settings":
                self.buttons_list = [
                    self.move_on_direction_button,
                    self.left_line_button,
                    self.back_button
                ]
                self.draw_settings_menu()
            elif self.window == "game":
                self.buttons_list = []
                self.draw_play_menu()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    manager = MenuManager()

    manager.run()
