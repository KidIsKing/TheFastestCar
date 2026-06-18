import pygame
import random
import sys

from button import ImageButton


# Constans
WIDTH = 1100
HEIGHT = 800

CENTER_X_FOR_BUTTONS = 370
START_Y_POS_PLAYER = 600

# Хитбоксы
PLAYER_HITBOX_DECREASE = (-110, 0)
ENEMY_HITBOX_DECREASE = (-180, 0)

# Ограничения дороги
ROAD_LEFT_BORDER = 120
ROAD_RIGHT_BORDER = WIDTH - 120

LANE_POSITIONS = [130, 320, 510, 700]  # X-координаты полос для спавна врагов

# Визуальные смещения
PLAYER_OFFSET_X = -1
ENEMY_OFFSET_X = -3

ENEMY_MIN_GAP = 5

ROAD_SPEED = 8

FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fade
FADE_SPEED = 10
MAX_FADE_ALPHA = 150

# Assets
ASSETS_PATH = "assets/"
ASSETS = {
    # Меню
    "main_background": ASSETS_PATH + "images/background_menu.png",
    "green_button": ASSETS_PATH + "images/buttons/green_button.png",
    "green_button_hover": ASSETS_PATH + "images/buttons/green_button_hover.png",
    "red_button": ASSETS_PATH + "images/buttons/red_button.png",
    "red_button_hover": ASSETS_PATH + "images/buttons/red_button_hover.png",
    "click_sound": ASSETS_PATH + "sounds/click.mp3",
    # Игра
    "player_car": ASSETS_PATH + "images/player_car.png",
    "enemy_car": ASSETS_PATH + "images/enemy_car.png",
    "road": ASSETS_PATH + "images/road.png",
}


# Алгоритм 1. Проверка столкновения двух AABB-прямоугольников (Axis-Aligned Bounding Box).
def aabb_collide(hitbox1, hitbox2):
    """
    Проверка столкновения двух AABB-прямоугольников (Axis-Aligned Bounding Box).

    Два прямоугольника НЕ пересекаются, если один полностью:
    - левее, правее, выше или ниже другого.
    Если ни одно из этих условий не выполняется — коллизия есть.

    Возвращает True, если прямоугольники пересекаются.
    """
    return (
        hitbox1.left <= hitbox2.right
        and hitbox1.right >= hitbox2.left
        and hitbox1.top <= hitbox2.bottom
        and hitbox1.bottom >= hitbox2.top
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

        self.sync_hitbox()

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
            settings.oncoming_traffic_enabled 
            and self.rect.x in LANE_POSITIONS[:2]
        )

        # Выбираем ориентацию картинки
        if self.is_oncoming:
            self.image = self.image_rotated
            self.base_speed = random.randint(5, 7)  # встречные быстрее
        else:
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


class GameManager:
    def __init__(self, screen):
        self.screen = screen

        self.road = Road()
        self.player = Player()
        self.enemies = [Enemy() for _ in range(3)]

        self.running = True
        self.game_over = False  # Флаг окончания игры
        self.debug_mode = False

        self.current_world_speed = settings.base_world_speed
        self.player_visual_offset_y = 0

    def handle_events(self, event):
        # Возврат в главное меню из игры по нажатию ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.debug_mode = (
                not self.debug_mode
            )  # переключаем режим на обратное значение

    def check_enemies_collision(self):
        """Проверка столкновений врагов друг с другом через AABB."""
        for i, enemy in enumerate(self.enemies):
            for other in self.enemies[i + 1 :]:
                if not aabb_collide(enemy.hitbox, other.hitbox):
                    continue  # столкновения нет - идём дальше

                # Определяем, кто из врагов выше, а кто ниже
                top_enemy, bottom_enemy = (
                    (enemy, other)
                    if enemy.hitbox.top < other.hitbox.top
                    else (other, enemy)
                )

                self.resolve_enemies_collision(
                    top_enemy, bottom_enemy
                )  # разрешаем столкновение

    def resolve_enemies_collision(self, top_enemy, bottom_enemy):
        """Разрешение столкновения врагов."""
        top_enemy.speed = min(
            top_enemy.speed, bottom_enemy.speed
        )  # верхний враг замедляется до скорости нижнего

        # Устанавливаем минимальный зазор между врагами, чтобы они не слипались
        min_gap = ENEMY_MIN_GAP
        if top_enemy.rect.bottom > bottom_enemy.rect.top - min_gap:
            top_enemy.rect.bottom = bottom_enemy.rect.top - min_gap

    def check_player_enemy_collision(self):
        """Проверка столкновений игрока с врагами через AABB."""
        if self.game_over:
            return

        for enemy in self.enemies:
            if aabb_collide(self.player.hitbox, enemy.hitbox):
                self.game_over = True
                self.running = False
                return

    def _update_world_speed(self):
        """Изменение скорости всех объектов по нажатию клавиш вверх и вниз."""
        keys = pygame.key.get_pressed()

        # Определяем целевую скорость и плавность
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            target_speed = settings.max_world_speed
            smoothing = settings.acceleration_smoothing
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            target_speed = settings.min_world_speed
            smoothing = settings.deceleration_smoothing
        else:
            target_speed = settings.base_world_speed
            smoothing = settings.deceleration_smoothing

        # Плавное изменение скорости
        self.current_world_speed += (target_speed - self.current_world_speed) * smoothing

        # Ограничения
        self.current_world_speed = max(
            settings.min_world_speed,
            min(settings.max_world_speed, self.current_world_speed)
        )

    def _update_player_visual_offset(self):
        """Визуальное смещение игрока при разгоне и замедлении."""
        speed_range = settings.max_world_speed - settings.base_world_speed

        if speed_range == 0:
            speed_ratio = 0
        else:
            speed_ratio = (self.current_world_speed - settings.base_world_speed) / speed_range

        offset_ratio = speed_ratio ** 2

        target_offset = settings.max_player_offset_y * offset_ratio

        self.player_visual_offset_y += (target_offset - self.player_visual_offset_y) * 0.1

    def update(self):
        """Обновление состояния игры."""
        if self.game_over:
            return

        # Обновляем скорость и смещение
        self._update_world_speed()
        self._update_player_visual_offset()

        self.road.move(self.current_world_speed)
        for enemy in self.enemies:
            enemy.move(self.current_world_speed)
        self.player.move()

        # Смещение игрока
        self.player.rect.y = self.player.base_y - self.player_visual_offset_y
        self.player.sync_hitbox()

        # Проверки коллизий через AABB
        self.check_enemies_collision()
        self.check_player_enemy_collision()

    def draw_debug(self):
        """Отрисовка хитбоксов в дебаг-режиме."""
        if not self.debug_mode:
            return  # ничего не делаем

        pygame.draw.rect(self.screen, GREEN, self.player.hitbox, 2)

        for enemy in self.enemies:
            pygame.draw.rect(self.screen, RED, enemy.hitbox, 2)

    def draw(self):
        """Отрисовка игрового экрана."""
        self.road.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.player.draw(self.screen)

        self.draw_debug()

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

        self.first_font = pygame.font.SysFont(None, 72)
        self.second_font = pygame.font.SysFont(None, 40)

        # Создание кнопок
        self.start_button = self._create_button("Играть", 300, "green")
        self.settings_button = self._create_button("Настройки", 400, "green")
        self.exit_button = self._create_button("Выйти", 500, "red")
        self.oncoming_traffic_button = self._create_button("Встречка", 300, "green")
        self.back_button = self._create_button("Назад", 400, "green")

        self.buttons_list = []

    def _create_button(self, text, y_pos, color):
        """Инкапсулированный метод для создания кнопок."""
        return ImageButton(
            CENTER_X_FOR_BUTTONS,
            y_pos,
            350,
            100,
            text,
            ASSETS[f"{color}_button"],
            ASSETS[f"{color}_button_hover"],
            ASSETS["click_sound"],
        )

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
                elif event.button == self.oncoming_traffic_button:
                    settings.oncoming_traffic_enabled = (
                        not settings.oncoming_traffic_enabled
                    )

    def draw_background(self, background):
        """Базовая отрисовка фона"""
        self.screen.fill(BLACK)
        self.screen.blit(background, (-350, -100))

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
        self.draw_text("TheFastestCar. Главное меню", self.first_font, WHITE, 168, 110)
        self.draw_text(
            "Игра для экзамена по программированию. by Яна Масалова",
            self.second_font,
            WHITE,
            130,
            170,
        )
        # Обработка и отрисовка кнопок
        self.draw_buttons()

    def draw_settings_menu(self):
        """Отрисовка меню настроек."""
        self.draw_background(self.main_background)
        self.draw_text("Настройки", self.first_font, WHITE, 415, 110)

        # Показываем текущее состояние встречки
        traffic_status = "ВКЛ" if settings.oncoming_traffic_enabled else "ВЫКЛ"
        self.draw_text(f"Встречка: {traffic_status}", self.second_font, WHITE, 440, 290)

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
                    self.oncoming_traffic_button,
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


class Settings:
    """Настройки и переменные, влияющие на игру."""

    def __init__(self):
        self.oncoming_traffic_enabled = False

        # Параметры логики скорости
        self.base_world_speed = 8
        self.max_world_speed = 18
        self.min_world_speed = 3

        self.acceleration_smoothing = 0.03  # плавность разгона
        self.deceleration_smoothing = 0.05  # плавность торможения

        self.max_player_offset_y = 100  # смещение по OY при разгоне


settings = Settings()


def main():
    manager = MenuManager()
    manager.run()


if __name__ == "__main__":
    main()
