import pygame
import random

from base_manager import BaseManager
from entities import Player, Enemy, Road, Bonus, FloatingText, Overlay, HealthBar
from bonus_director import BonusDirector
from score_tracker import ScoreTracker
from music_manager import MusicManager
from settings import settings
from collision import check_enemies_collision, aabb_collide
from spawn_system import check_bonus_spawn
from constants import (
    WIDTH, HEIGHT, FPS, PLAYER_MAX_HEALTH, PLAYER_INVULNERABLE_DURATION,
    BASE_DAMAGE, DAMAGE_SPREAD, DAMAGE_MIN, DAMAGE_MAX, WHITE, BLACK, GREEN,
    RED, YELLOW, ASSETS, SPAWN_CHECK_INTERVAL, OFFSET_X_FLOATING_TEXT,
    OFFSET_Y_FLOATING_TEXT, POSITION_X_FOR_STAT, POSITION_Y_FOR_STAT, DEBAG_BORDER
)


class GameManager(BaseManager):
    def __init__(self, screen):
        super().__init__(screen)
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

        self.game_over = False
        self.game_pause = False
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

    def process_event(self, event):
        """Обработка события."""
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

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.music_manager.stop_decel()
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.music_manager.play_decel()

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.music_manager.play_decel()
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.music_manager.stop_decel()

        # Запуск окошка паузы при нажатии ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_pause = True
            self.music_manager.stop_decel()
            self.update_time()
            self.music_manager.toggle_pause_all()
            return

        # Включение/выключение дебаг-режима
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.debug_mode = not self.debug_mode

    def restart_game(self):
        """Перезапуск игры."""
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
            self.music_manager.stop_decel()
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

        # Ускорение для музыки
        keys = pygame.key.get_pressed()
        is_accelerating = keys[pygame.K_UP] or keys[pygame.K_w]
        speed_range = settings.max_world_speed - settings.base_world_speed
        if speed_range > 0:
            speed_ratio = (self.current_world_speed - settings.base_world_speed) / speed_range
        else:
            speed_ratio = 0
        self.music_manager.update_engine(is_accelerating, speed_ratio)

        # Спавн бонусов
        self.spawn_check_counter += 1
        if self.spawn_check_counter >= self.spawn_check_interval:
            self.spawn_check_counter = 0
            check_bonus_spawn(
                self.bonus_director,
                self.player,
                self.current_world_speed,
                self.bonuses
            )
        self.bonuses = [b for b in self.bonuses if not b.is_off_screen()]

        # Движение объектов
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

        # Колизии
        check_enemies_collision(self.enemies)
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
        """Отрисовка счёта."""
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
        """Отрисовка времени жизни."""
        total_seconds = self.time_alive_ms / 1000
        minutes = int(total_seconds) // 60
        seconds = int(total_seconds) % 60

        # Заголовок
        title_surface = self.font.render("Время жизни:", True, WHITE)
        title_rect = title_surface.get_rect(
            topright=(POSITION_X_FOR_STAT, POSITION_Y_FOR_STAT * 4)
        )
        self.screen.blit(title_surface, title_rect)

        # Значение (минуты:секунды)
        time_text = f"{minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, WHITE)
        time_rect = time_surface.get_rect(
            topright=(POSITION_X_FOR_STAT, title_rect.bottom + 5)
        )
        self.screen.blit(time_surface, time_rect)

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