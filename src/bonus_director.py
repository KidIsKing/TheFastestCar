import random
import time

from constants import (
    BASE_WORLD_SPEED, MAX_WORLD_SPEED, BASE_CHANCE_HP, BASE_CHANCE_EX,
    TIME_MULTIPLIER_PER_MINUTE, WEIGHT_HP_MAX, WEIGHT_HP_MIN, TOTAL_WEIGHT,
    HEALTH_RANGE_FOR_INTERPOLATION, BONUS_COUNT_MEAN, BONUS_COUNT_STD,
    BASE_EXPERIENCE, EXPERIENCE_SPREAD, EXPERIENCE_MAX, EXPERIENCE_MIN,
    HEALTH_BONUS_MEAN, HEALTH_BONUS_STD, HEALTH_BONUS_MAX, HEALTH_BONUS_MIN,
    HEALTH_MULTIPLIER_LOW, HEALTH_MULTIPLIER_CRITICAL, HEALTH_THRESHOLD_LOW,
    HEALTH_THRESHOLD_CRITICAL, SPEED_MULTIPLIER_POWER, WEIGHT_THRESHOLD_LOW,
    WEIGHT_THRESHOLD_CRITICAL, MAX_BONUSES_ON_SCREEN
)


class BonusDirector:
    """Режиссёр для бонусов."""

    def __init__(self):
        # PRD-накопители шансов
        self.current_chance_hp = BASE_CHANCE_HP
        self.current_chance_ex = BASE_CHANCE_EX

        self.start_time = time.time()

    def get_time_alive(self):
        """Время жизни игрока в секундах."""
        return time.time() - self.start_time

    def get_time_multiplier(self):
        """Множитель очков от времени: +10% каждую минуту."""
        return 1.0 + (self.get_time_alive() / 60) * TIME_MULTIPLIER_PER_MINUTE

    def get_speed_multiplier(self, current_world_speed):
        """Квадратичный множитель от скорости."""
        speed_range = MAX_WORLD_SPEED - BASE_WORLD_SPEED
        if speed_range == 0:
            return 1
        speed_ratio = (current_world_speed - BASE_WORLD_SPEED) / speed_range
        speed_ratio = max(0, min(1, speed_ratio))
        return 1.0 + speed_ratio ** SPEED_MULTIPLIER_POWER

    def get_bonus_weights(self, player):
        """Динамические веса для выбора типа бонуса."""
        health_ratio = player.health / player.max_health

        # Линейная интерполяция
        if health_ratio >= WEIGHT_THRESHOLD_LOW:
            weight_hp = WEIGHT_HP_MIN
        elif health_ratio <= WEIGHT_THRESHOLD_CRITICAL:
            weight_hp = WEIGHT_HP_MAX
        else:
            weight_hp = (
                WEIGHT_HP_MIN +
                (WEIGHT_HP_MAX - WEIGHT_HP_MIN) *
                (1 - health_ratio) / HEALTH_RANGE_FOR_INTERPOLATION
            )

        weight_ex = TOTAL_WEIGHT - weight_hp
        return weight_hp, weight_ex

    def choose_bonus_type(self, player):
        """Взвешенный случайный выбор типа бонуса."""
        weight_hp, weight_ex = self.get_bonus_weights(player)
        total = weight_hp + weight_ex
        roll = random.random() * total

        if roll < weight_hp:
            return "hp"
        else:
            return "ex"

    def should_spawn_bonus(self, player, current_world_speed):
        """
        PRD-проверка: должен ли появиться бонус в этом кадре.
        Возвращает тип бонуса или None.
        """
        health_ratio = player.health / player.max_health

        if current_world_speed <= BASE_WORLD_SPEED:
            return None

        base_chance_hp = BASE_CHANCE_HP
        if health_ratio < HEALTH_THRESHOLD_LOW:
            base_chance_hp *= HEALTH_MULTIPLIER_LOW
        if health_ratio < HEALTH_THRESHOLD_CRITICAL:
            base_chance_hp *= HEALTH_MULTIPLIER_CRITICAL  # двойное удвоение

        base_chance_ex = BASE_CHANCE_EX
        speed_multiplier = self.get_speed_multiplier(current_world_speed)
        base_chance_ex *= speed_multiplier

        self.current_chance_hp += base_chance_hp
        self.current_chance_ex += base_chance_ex

        if random.random() < self.current_chance_hp:
            self.current_chance_hp = BASE_CHANCE_HP  # сброс
            return self.choose_bonus_type(player)

        if random.random() < self.current_chance_ex:
            self.current_chance_ex = BASE_CHANCE_EX  # сброс
            return "ex"

        return None

    def get_bonus_count(self):
        """Количество бонусов за спавн (нормальное распределение)."""
        count = random.gauss(BONUS_COUNT_MEAN, BONUS_COUNT_STD)
        return int(max(1, min(MAX_BONUSES_ON_SCREEN, round(count))))

    def calculate_experience(self, current_world_speed):
        """Расчёт очков опыта с учётом множителей."""
        base_exp = random.gauss(BASE_EXPERIENCE, EXPERIENCE_SPREAD)
        base_exp = max(EXPERIENCE_MIN, min(EXPERIENCE_MAX, int(base_exp)))

        time_mult = self.get_time_multiplier()
        speed_mult = self.get_speed_multiplier(current_world_speed)

        return int(base_exp * time_mult * speed_mult)

    def calculate_health_bonus(self):
        """Расчёт HP от бонуса здоровья (гауссово распределение)."""
        health = random.gauss(HEALTH_BONUS_MEAN, HEALTH_BONUS_STD)
        return int(max(HEALTH_BONUS_MIN, min(HEALTH_BONUS_MAX, health)))
