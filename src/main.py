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
# Fade
FADE_SPEED = 10
MAX_FADE_ALPHA = 150
# Assets
ASSETS_PATH = "assets/"
ASSETS = {
    # Меню
    "main_background": ASSETS_PATH + "images/background_menu.png",
    "game_background": ASSETS_PATH + "images/road.png",
    "green_button": ASSETS_PATH + "images/buttons/green_button.png",
    "green_button_hover": ASSETS_PATH + "images/buttons/green_button_hover.png",
    "red_button": ASSETS_PATH + "images/buttons/red_button.png",
    "red_button_hover": ASSETS_PATH + "images/buttons/red_button_hover.png",
    "click_sound": ASSETS_PATH + "sounds/click.mp3",
    # Игра
    "player_car": ASSETS_PATH + "images/player_car.png",
}


class Player:
    def __init__(self):
        self.image = pygame.image.load(ASSETS["player_car"])
        # self.image.
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player()
        self.running = True

        self.game_background = pygame.image.load(ASSETS["game_background"])

    def handle_events(self, event):
        # Возврат в главное меню из игры по нажатию ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False

    def update(self):
        """Обновление состояния игры."""
        self.player.move()

    def draw(self):
        """Отрисовка игрового экрана."""
        self.screen.blit(self.game_background, (0, 0))
        self.player.draw(self.screen)

    def run(self):
        """Главный процесс игры."""
        self.update()
        self.draw()


class MenuManager:
    def __init__(self):
        self.running = True
        self.window = "menu"  # какое окно отображать

        # Переменные для затухания
        self.transition_state = None  # None, "fade_out", "fade_in"
        self.target_window = None  # целевое окно после затухания
        self.fade_alpha = 0  # уровень прозрачности для затухания
        self.fade_speed = FADE_SPEED  # скорость затухания

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TheFastestCar")
        self.main_background = pygame.image.load(ASSETS["main_background"])
        self.clock = pygame.time.Clock()

        # Режимы
        self.game_manager = None  # объект GameManager будет создан при входе в игру

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

    def start_transition(self, target):
        """Старт анимации затухания и установка целевого окна."""
        if self.transition_state is None:
            self.target_window = target
            self.transition_state = "fade_out"
            self.fade_alpha = 0

    def handle_event(self):
        """Обработка событий."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.window == "game" and self.game_manager is not None:
                self.game_manager.handle_events(event)

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

    def draw_background(self, background):
        """Базовая отрисовка фона"""
        self.screen.fill(BLACK)
        self.screen.blit(background, (0, 0))

    def draw_text(self, text, font, color, x_pos, y_pos):
        """Отрисовка текста."""
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x_pos, y_pos))

    def draw_buttons(self):
        "Базовая отрисовка кнопок."
        for button in self.buttons_list:
            button.check_hover(pygame.mouse.get_pos())
            button.draw(self.screen)

    def draw_main_menu(self):
        """Отрисовка главного меню."""
        self.draw_background(self.main_background)
        self.draw_text("TheFastestCar. Главное меню", self.first_font, WHITE, 100, 110)
        self.draw_text(
            "by Яна Масалова. Игра для экзамена по программированию",
            self.second_font,
            WHITE,
            100,
            200,
        )
        # Обработка и отрисовка кнопок
        self.draw_buttons()

    def draw_settings_menu(self):
        """Отрисовка меню настроек."""
        self.draw_background(self.main_background)
        self.draw_text("Настройки", self.first_font, WHITE, 535, 110)
        # Обработка и отрисовка кнопок
        self.draw_buttons()

    def apply_transition(self):
        """Управление логикой затухания."""
        # Логика затухания
        if self.transition_state == "fade_out":
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= MAX_FADE_ALPHA:
                self.fade_alpha = MAX_FADE_ALPHA
                self.window = self.target_window  # переключение экрана пока окно чёрное
                self.transition_state = "fade_in"  # переключаем режим на осветление

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

    def run(self):
        """Бесконечный игровой цикл."""
        while self.running:
            self.handle_event()

            if self.window == "game":
                if self.game_manager is None:
                    self.game_manager = GameManager(self.screen)
                elif not self.game_manager.running:
                    self.game_manager = None
                    self.start_transition("menu")

            if self.window == "menu":
                self.buttons_list = [
                    self.start_button,
                    self.settings_button,
                    self.exit_button,
                ]
                self.draw_main_menu()
            elif self.window == "settings":
                self.buttons_list = [
                    self.move_on_direction_button,
                    self.left_line_button,
                    self.back_button,
                ]
                self.draw_settings_menu()
            elif self.window == "game" and self.game_manager is not None:
                self.buttons_list = []
                self.game_manager.run()

            self.apply_transition()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    manager = MenuManager()
    manager.run()


if __name__ == "__main__":
    main()
