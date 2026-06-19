import pygame
import random
import sys

from entities import Player, Enemy, Road, Bonus
from settings import settings
from button import create_buttons
from constants import (
    WIDTH,
    HEIGHT,
    ENEMY_MIN_GAP,
    FPS,
    PLAYER_MAX_HEALTH, PLAYER_INVULNERABLE_DURATION, BASE_DAMAGE,
    DAMAGE_SPREAD, DAMAGE_MIN, DAMAGE_MAX,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    HEALTH_BAR_X,
    HEALTH_BAR_Y,
    HEALTH_BAR_BORDER,
    WHITE,
    BLACK,
    GREEN,
    RED,
    YELLOW,
    FADE_SPEED,
    MAX_FADE_ALPHA,
    ASSETS,
)


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


class Overlay:
    """Окно поверх игры."""

    PANEL_WIDTH = 500
    PANEL_HEIGHT = 400
    OVERLAY_ALPHA = 150
    BUTTON_SPACING = 100  # расстояние между кнопками по Y
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
            y_pos = self.FIRST_BUTTON_Y + i * self.BUTTON_SPACING
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


class GameManager:
    def __init__(self, screen):
        self.screen = screen

        self.road = Road()
        self.player = Player()
        self.enemies = [Enemy() for _ in range(3)]
        self.health_bar = HealthBar(PLAYER_MAX_HEALTH)
        self.hp = Bonus(ASSETS["hp"])
        self.ex = Bonus(ASSETS["ex"])

        self.current_world_speed = settings.base_world_speed
        self.player_visual_offset_y = 0

        self.collided_enemy = None  # враг, с которым столкнулся игрок

        self.running = True
        self.game_over = False  # Флаг окончания игры
        self.game_pause = False  # Флаг паузы
        self.debug_mode = False

        # Создаём оверлеи
        self.game_over_overlay = Overlay(
            "Игра окончена", [("Начать заново", "restart"), ("Выйти в меню", "to_menu")]
        )
        self.pause_overlay = Overlay(
            "Пауза", [("Продолжить", "continue"), ("Выйти в меню", "to_menu")]
        )

    def handle_events(self, event):
        """Обработка нажатий клавиш."""
        # Обработка экранчика проигрыша
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                return

            action = self.game_over_overlay.handle_event(event)
            if action == "restart":
                self.restart_game()
            elif action == "to_menu":
                self.running = False
            return

        # Обработка экранчика паузы
        if self.game_pause:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_pause = False
                return

            action = self.pause_overlay.handle_event(event)
            if action == "continue":
                self.game_pause = False
            elif action == "to_menu":
                self.running = False
            return

        # Запуск окошка паузы при нажатии ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_pause = True

        # Включение/выключение дебаг-режима
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.debug_mode = (
                not self.debug_mode
            )  # переключаем режим на обратное значение

    def restart_game(self):
        self.player = Player()
        self.enemies = [Enemy() for _ in range(3)]
        self.road = Road()
        self.hp = Bonus(ASSETS["hp"], "hp")
        self.ex = Bonus(ASSETS["ex"], "ex")
        self.health_bar.update(PLAYER_MAX_HEALTH)
        self.collided_enemy = None
        self.current_world_speed = settings.base_world_speed
        self.player_visual_offset_y = 0
        self.game_over = False

    def calculate_damage(self):
        """Расчёт урона с гауссовым распределением."""
        damage = random.gauss(BASE_DAMAGE, DAMAGE_SPREAD)
        damage = max(DAMAGE_MIN, max(DAMAGE_MAX, int(damage)))
        return damage

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

    def check_health(self, enemy):
        if self.player.invulnerable:
            return

        damage = self.calculate_damage()

        self.player.health -= damage

        self.health_bar.update(self.player.health)

        self.player.invulnerable = True
        self.player.invulnerable_timer = PLAYER_INVULNERABLE_DURATION

        if self.player.health <= 0:
            self.game_over = True
            self.collided_enemy = enemy

    def check_player_enemy_collision(self):
        """Проверка столкновений игрока с врагами через AABB."""
        if self.game_over:
            return

        for enemy in self.enemies:
            if aabb_collide(self.player.hitbox, enemy.hitbox):
                self.check_health(enemy)
                return

    def give_effects(self):
        pass

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
        self.current_world_speed += (
            target_speed - self.current_world_speed
        ) * smoothing

        # Ограничения
        self.current_world_speed = max(
            settings.min_world_speed,
            min(settings.max_world_speed, self.current_world_speed),
        )

    def _update_player_visual_offset(self):
        """Визуальное смещение игрока при разгоне и замедлении."""
        speed_range = settings.max_world_speed - settings.base_world_speed

        if speed_range == 0:
            speed_ratio = 0
        else:
            speed_ratio = (
                self.current_world_speed - settings.base_world_speed
            ) / speed_range

        offset_ratio = speed_ratio**2

        target_offset = settings.max_player_offset_y * offset_ratio

        self.player_visual_offset_y += (
            target_offset - self.player_visual_offset_y
        ) * 0.1

    def update(self):
        """Обновление состояния игры."""
        if self.game_over:
            for enemy in self.enemies:
                if enemy is not self.collided_enemy:
                    enemy.move(
                        self.current_world_speed * 0.02
                    )  # нетронутые враги продолжают двигаться
            return

        self.player.update_invulnerable()

        # Обновляем скорость и смещение
        self._update_world_speed()
        self._update_player_visual_offset()

        self.road.move(self.current_world_speed)
        for enemy in self.enemies:
            enemy.move(self.current_world_speed)
        self.player.move()
        self.hp.move(self.current_world_speed)
        self.ex.move(self.current_world_speed)

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

    def draw_healh_bar(self):
        """Отрисовка полоски здоровья."""
        bar_x = 10
        bar_y = 10
        bar_width = 149
        bar_height = 45
        border_thickness = 3

        # Фон полоски
        pygame.draw.rect(
            self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height)
        )

        # Динамическое заполнение
        health_ratio = self.player.health / self.player.max_health
        fill_width = bar_width * health_ratio

        if health_ratio > 0.5:
            color = GREEN
        elif health_ratio > 0.25:
            color = YELLOW
        else:
            color = RED

        pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))
        # Рамка
        pygame.draw.rect(
            self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), border_thickness
        )

        font = pygame.font.SysFont(None, 30)
        text = font.render(
            f"{self.player.health}/{self.player.max_health}", True, WHITE
        )
        text_rect = text.get_rect(
            center=(bar_x + bar_width // 2, bar_y + bar_height // 2)
        )
        self.screen.blit(text, text_rect)

    def draw(self):
        """Отрисовка игрового экрана."""
        self.road.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.player.draw(self.screen)
        self.hp.draw(self.screen)
        self.ex.draw(self.screen)

        self.health_bar.draw(self.screen)

        self.draw_debug()

        if self.game_over:
            self.game_over_overlay.draw(self.screen)
        elif self.game_pause:
            self.pause_overlay.draw(self.screen)

    def run(self):
        """Главный процесс игры."""
        if (
            self.game_pause or not self.running
        ):  # если игра заморожена, то не обновляем её
            self.draw()
            return

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
        self.start_button = create_buttons("Играть", 300, "green")
        self.settings_button = create_buttons("Настройки", 400, "green")
        self.exit_button = create_buttons("Выйти", 500, "red")
        self.oncoming_traffic_button = create_buttons("Встречка", 300, "green")
        self.back_button = create_buttons("Назад", 400, "green")

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

            if (
                self.window == "settings"
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                self.start_transition("menu")

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
        self.draw_text(f"Встречка: {traffic_status}", self.second_font, WHITE, 440, 230)

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
                    if self.transition_state is None:
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


def main():
    manager = MenuManager()
    manager.run()


if __name__ == "__main__":
    main()
