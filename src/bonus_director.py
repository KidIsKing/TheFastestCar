import random
import time

from constants import BASE_WORLD_SPEED, MAX_WORLD_SPEED


class BonusDirector:
    """Режиссёр для бонусов."""

    BASE_CHANCE_HP = 0.003
    BASE_CHANCE_EX = 0.005

    BONUS_COUNT_MEAN = 1.2
    BONUS_COUNT_STD = 0.3

    BASE_EXPERIENCE = 10
    EXPERIENCE_SPREAD = 3

    def __init__(self):
        # PRD-накопители шансов
        self.current_chance_hp = self.BASE_CHANCE_HP
        self.current_chance_ex = self.BASE_CHANCE_EX

        self.start_time = time.time()

    def get_time_alive(self):
        """Время жизни игрока в секундах."""
        return time.time() - self.start_time

    def get_time_multiplier(self):
        """Множитель очков от времени: +10% каждую минуту."""
        return 1.0 + (self.get_time_alive() / 60) * 0.1

    def get_speed_multiplier(self, current_world_speed):
        """Квадратичный множитель от скорости."""
        speed_range = MAX_WORLD_SPEED - BASE_WORLD_SPEED
        if speed_range == 0:
            return 1
        speed_ratio = (current_world_speed - BASE_WORLD_SPEED) / speed_range
        speed_ratio = max(0, min(1, speed_ratio))
        return 1.0 + speed_ratio ** 2

    def get_bonus_weights(self, player):
        """Динамические веса для выбора типа бонуса."""
        health_ratio = player.health / player.max_health

        # Линейная интерполяция
        if health_ratio >= 1.0:
            weight_hp = 5
        elif health_ratio <= 0.3:
            weight_hp = 80
        else:
            weight_hp = 5 + (80 - 5) * (1 - health_ratio) / 0.7

        weight_ex = 90 - weight_hp
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

        base_chance_hp = self.BASE_CHANCE_HP
        if health_ratio < 0.5:
            base_chance_hp *= 2
        if health_ratio < 0.3:
            base_chance_hp *= 2  # двойное удвоение при критическом здоровье

        base_chance_ex = self.BASE_CHANCE_EX
        speed_multiplier = self.get_speed_multiplier(current_world_speed)
        base_chance_ex *= speed_multiplier

        self.current_chance_hp += base_chance_hp
        self.current_chance_ex += base_chance_ex

        if random.random() < self.current_chance_hp:
            self.current_chance_hp = self.BASE_CHANCE_HP  # сброс
            return self.choose_bonus_type(player)

        if random.random() < self.current_chance_ex:
            self.current_chance_ex = self.BASE_CHANCE_EX  # сброс
            return "ex"

        return None

    def get_bonus_count(self):
        """Количество бонусов за спавн (нормальное распределение)."""
        count = random.gauss(self.BONUS_COUNT_MEAN, self.BONUS_COUNT_STD)
        return int(max(1, min(2, round(count))))

    def calculate_experience(self, current_world_speed):
        """Расчёт очков опыта с учётом множителей."""
        base_exp = random.gauss(self.BASE_EXPERIENCE, self.EXPERIENCE_SPREAD)
        base_exp = max(5, min(15, int(base_exp)))

        time_mult = self.get_time_multiplier()
        speed_mult = self.get_speed_multiplier(current_world_speed)

        return int(base_exp * time_mult * speed_mult)

    def calculate_health_bonus(self):
        """Расчёт HP от бонуса здоровья (гауссово распределение)."""
        health = random.gauss(7, 2)
        return int(max(5, min(10, health)))
