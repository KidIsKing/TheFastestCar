import pygame
import random
import sys

from entities import (
    Player, Enemy, Road, Bonus, FloatingText, Overlay, HealthBar
)
from bonus_director import BonusDirector
from score_tracker import ScoreTracker
from music_manager import MusicManager
from settings import settings
from button import create_buttons
from constants import (
    WIDTH, HEIGHT, ENEMY_MIN_GAP, FPS, FADE_SPEED,
    PLAYER_MAX_HEALTH, PLAYER_INVULNERABLE_DURATION, BASE_DAMAGE,
    DAMAGE_SPREAD, DAMAGE_MIN, DAMAGE_MAX, WHITE, BLACK, GREEN, RED, YELLOW,
    MAX_FADE_ALPHA, ASSETS, SPAWN_CHECK_INTERVAL, MAX_BONUSES_ON_SCREEN,
    OFFSET_X_FLOATING_TEXT, OFFSET_Y_FLOATING_TEXT,
    POSITION_X_FOR_STAT, POSITION_Y_FOR_STAT, DEBAG_BORDER,
    Y_BUTTON, BUTTON_SPACING
)


class MenuManager:
    def __init__(self):
        pygame.init()

        self.running = True
        self.window = "menu"  # какое окно отображать
        self.game_manager = None  # GameManager создаётся при входе в игру

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TheFastestCar")
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
            "Настройки",
            Y_BUTTON + BUTTON_SPACING,
            "green"
        )
        self.exit_button = create_buttons(
            "Выйти",
            Y_BUTTON + 2*BUTTON_SPACING,
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
        self.draw_text(
            "TheFastestCar. Главное меню",
            self.first_font,
            WHITE,
            168,
            110)
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
        self.draw_text(
            f"Встречка: {traffic_status}",
            self.second_font,
            WHITE,
            440,
            230
        )

        # Обработка и отрисовка кнопок
        self.draw_buttons()

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


class GameManager:
    """Менеджер игры."""
    def __init__(self, screen):
        self.screen = screen
        self.music_manager = MusicManager()
        self.music_manager.start_music()

        self.road = Road()
        self.player = Player()
        self.enemies = [Enemy() for _ in range(3)]

        self.health_bar = HealthBar(PLAYER_MAX_HEALTH)

        self.bonus_director = BonusDirector()
        self.bonuses = []
        self.bonus_handlers = {
            "hp": self.give_health,
            "ex": self.give_experience
        }

        # Таймер проверки спавна (проверка раз в 10 кадров)
        self.spawn_check_counter = 0
        self.spawn_check_interval = SPAWN_CHECK_INTERVAL

        self.score_tracker = ScoreTracker()

        self.floating_texts = []  # список активных всплывающих текстов

        self.current_world_speed = settings.base_world_speed
        self.player_visual_offset_y = 0

        self.collided_enemy = None  # враг, с которым столкнулся игрок

        self.running = True
        self.game_over = False  # Флаг окончания игры
        self.game_pause = False  # Флаг паузы
        self.debug_mode = False

        self.font = pygame.font.SysFont(None, 36)

        # Создаём оверлеи
        self.game_over_overlay = Overlay(
            "Игра окончена",
            [("Начать заново", "restart"), ("Выйти в меню", "to_menu")]
        )
        self.pause_overlay = Overlay(
            "Пауза",
            [("Продолжить", "continue"), ("Выйти в меню", "to_menu")]
        )

        self.last_update_time = pygame.time.get_ticks()
        self.time_alive_ms = 0

    def handle_events(self, event):
        """Обработка нажатий клавиш."""
        # Обработка экранчика проигрыша
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.music_manager.stop_all()
                self.running = False
                return

            action = self.game_over_overlay.handle_event(event)
            if action == "restart":
                self.restart_game()
            elif action == "to_menu":
                self.music_manager.stop_all()
                self.running = False
            return

        # Обработка экранчика паузы
        if self.game_pause:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_pause = False
                self.update_time()
                self.music_manager.toggle_pause_all()
                return

            action = self.pause_overlay.handle_event(event)
            if action == "continue":
                self.game_pause = False
                self.update_time()
                self.music_manager.toggle_pause_all()
            elif action == "to_menu":
                self.running = False
                self.music_manager.stop_all()
            return

        # Запуск окошка паузы при нажатии ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_pause = True
            self.update_time()
            self.music_manager.toggle_pause_all()
            return

        # Включение/выключение дебаг-режима
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.debug_mode = not self.debug_mode

    def restart_game(self):
        self.music_manager.stop_all()

        self.player = Player()
        self.enemies = [Enemy() for _ in range(3)]
        self.road = Road()

        self.health_bar.update(PLAYER_MAX_HEALTH)

        self.bonus_director = BonusDirector()
        self.bonuses = []

        self.floating_texts = []

        self.spawn_check_counter = 0

        self.score_tracker.reset()

        self.collided_enemy = None
        self.current_world_speed = settings.base_world_speed
        self.player_visual_offset_y = 0
        self.game_over = False

        self.music_manager.start_music()
        self.time_alive_ms = 0
        self.update_time()

    def calculate_damage(self):
        """Расчёт урона с гауссовым распределением."""
        damage = random.gauss(BASE_DAMAGE, DAMAGE_SPREAD)
        damage = max(DAMAGE_MIN, min(DAMAGE_MAX, int(damage)))
        return damage

    def take_health(self, enemy):
        """Отнимаем здоровье игрока."""
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
            self.music_manager.stop_music()
            self.music_manager.stop_engine()
            self.music_manager.play_crash()
        else:
            self.music_manager.play_damage()

        self._create_floating_text(f"-{damage} HP", RED)

    def apply_bonus(self, bonus):
        """Применение эффекта бонуса в зависимости от типа."""
        handler = self.bonus_handlers.get(bonus.effects_type)
        if handler:
            handler()
        self.music_manager.play_bonus()

    def give_experience(self):
        """Начисление опыта."""
        experience = self.bonus_director.calculate_experience(
            self.current_world_speed
        )
        self.score_tracker.add_score(experience)

        self._create_floating_text(f"+{experience} EXP", YELLOW)

    def give_health(self):
        """Начисление здоровья."""
        health_from_bonus = self.bonus_director.calculate_health_bonus()
        self.player.health = min(
            self.player.max_health,
            self.player.health + health_from_bonus
        )
        self.health_bar.update(self.player.health)

        self._create_floating_text(f"+{health_from_bonus} HP", GREEN)

    def check_enemies_collision(self):
        """Проверка столкновений врагов друг с другом через AABB."""
        for i, enemy in enumerate(self.enemies):
            for other in self.enemies[i+1:]:
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
        # Верхний враг замедляется до скорости нижнего
        top_enemy.speed = min(top_enemy.speed, bottom_enemy.speed)

        # Устанавливаем минимальный зазор между врагами, чтобы они не слипались
        min_gap = ENEMY_MIN_GAP
        if top_enemy.rect.bottom > bottom_enemy.rect.top - min_gap:
            top_enemy.rect.bottom = bottom_enemy.rect.top - min_gap

    def check_player_bonuses_collision(self):
        if self.game_over:
            return

        for bonus in self.bonuses:
            if aabb_collide(self.player.hitbox, bonus.hitbox):
                self.apply_bonus(bonus)
                self.bonuses.remove(bonus)  # удаляем бонус
                return

    def check_player_enemy_collision(self):
        """Проверка столкновений игрока с врагами через AABB."""
        if self.game_over:
            return

        for enemy in self.enemies:
            if aabb_collide(self.player.hitbox, enemy.hitbox):
                self.take_health(enemy)
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

    def _check_bonus_spawn(self):
        """Проверка необходимости спавна бонуса через режиссёра."""
        if len(self.bonuses) >= MAX_BONUSES_ON_SCREEN:
            return

        bonus_type = self.bonus_director.should_spawn_bonus(
            self.player,
            self.current_world_speed
            )

        if bonus_type is not None:
            count = self.bonus_director.get_bonus_count()

            count = min(count, MAX_BONUSES_ON_SCREEN - len(self.bonuses))

            for _ in range(count):
                self.bonuses.append(Bonus(ASSETS[bonus_type], bonus_type))

    def update_time(self):
        self.last_update_time = pygame.time.get_ticks()

    def update(self):
        """Обновление состояния игры."""
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        if self.game_over:
            for enemy in self.enemies:
                if enemy is not self.collided_enemy:
                    enemy.move(self.current_world_speed * 0.02)
            return

        self.time_alive_ms += dt

        self.player.update_invulnerable()

        self._update_world_speed()
        self._update_player_visual_offset()

        keys = pygame.key.get_pressed()
        is_accelerating = keys[pygame.K_UP] or keys[pygame.K_w]

        speed_range = settings.max_world_speed - settings.base_world_speed
        if speed_range > 0:
            speed_ratio = (self.current_world_speed - settings.base_world_speed) / speed_range
        else:
            speed_ratio = 0

        self.music_manager.update_engine(is_accelerating, speed_ratio)

        self.spawn_check_counter += 1
        if self.spawn_check_counter >= self.spawn_check_interval:
            self.spawn_check_counter = 0
            self._check_bonus_spawn()

        self.bonuses = [b for b in self.bonuses if not b.is_off_screen()]

        self.road.move(self.current_world_speed)
        for enemy in self.enemies:
            enemy.move(self.current_world_speed)
        for bonus in self.bonuses:
            bonus.move(self.current_world_speed)
        self.player.move()
        for text in self.floating_texts:
            text.update()

        self.floating_texts = [
            t for t in self.floating_texts if not t.is_expired()
        ]

        self.player.rect.y = self.player.base_y - self.player_visual_offset_y
        self.player.sync_hitbox()

        self.check_enemies_collision()
        self.check_player_enemy_collision()
        self.check_player_bonuses_collision()

    def _create_floating_text(self, text, color=WHITE):
        """Всплывающий текст над игроком."""
        # Позиция по OX со случайным смещением
        x = (self.player.rect.centerx -
             random.randint(-OFFSET_X_FLOATING_TEXT, OFFSET_X_FLOATING_TEXT))
        y = self.player.rect.top - OFFSET_Y_FLOATING_TEXT
        self.floating_texts.append(FloatingText(text, x, y, color))

    def draw_score(self):
        text = self.font.render(
            (f"Счёт: {self.score_tracker.score}. "
             f"Рекорд: {self.score_tracker.get_best_score()}"),
            True,
            WHITE
        )
        text_rect = text.get_rect(
            topright=(POSITION_X_FOR_STAT, POSITION_Y_FOR_STAT)
        )
        self.screen.blit(text, text_rect)

    def draw_time_alive(self):
        seconds = self.time_alive_ms / 1000
        text = self.font.render(
            f"Время жизни: {seconds:.2f}",
            True,
            WHITE
        )
        text_rect = text.get_rect(
            # 4 - смещение по OY
            topright=(POSITION_X_FOR_STAT, POSITION_Y_FOR_STAT*4)
        )
        self.screen.blit(text, text_rect)

    def draw_debug(self):
        """Отрисовка хитбоксов в дебаг-режиме."""
        if not self.debug_mode:
            return  # ничего не делаем

        pygame.draw.rect(self.screen, GREEN, self.player.hitbox, DEBAG_BORDER)

        for enemy in self.enemies:
            pygame.draw.rect(self.screen, RED, enemy.hitbox, DEBAG_BORDER)

    def draw(self):
        """Отрисовка игрового экрана."""
        self.road.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.player.draw(self.screen)
        for bonus in self.bonuses:
            bonus.draw(self.screen)

        for text in self.floating_texts:
            text.draw(self.screen)
        self.health_bar.draw(self.screen)

        self.draw_score()
        self.draw_time_alive()

        self.draw_debug()

        if self.game_over:
            self.game_over_overlay.draw(self.screen)
        elif self.game_pause:
            self.pause_overlay.draw(self.screen)

    def run(self):
        """Главный процесс игры."""
        if self.game_pause or not self.running:
            self.draw()
            return

        self.update()
        self.draw()


def aabb_collide(hitbox1, hitbox2):
    """Проверка столкновения двух AABB-прямоугольников."""
    return (
        hitbox1.left <= hitbox2.right
        and hitbox1.right >= hitbox2.left
        and hitbox1.top <= hitbox2.bottom
        and hitbox1.bottom >= hitbox2.top
    )


def main():
    manager = MenuManager()
    manager.run()


if __name__ == "__main__":
    main()
