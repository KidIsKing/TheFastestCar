import pytest
from systems.bonus_director import BonusDirector
from config.constants import BASE_WORLD_SPEED, MAX_WORLD_SPEED


class FakePlayer:
    """Заглушка игрока для тестов."""

    def __init__(self, health=100, max_health=100):
        self.health = health
        self.max_health = max_health


class TestBonusDirector:
    """Тесты BonusDirector."""

    def setup_method(self):
        """Создаём свежий экземпляр перед каждым тестом."""
        self.director = BonusDirector()

    def test_speed_multiplier_at_base_speed(self):
        """При базовой скорости множитель = 1.0."""
        mult = self.director.get_speed_multiplier(BASE_WORLD_SPEED)
        assert mult == pytest.approx(1.0, abs=0.01)

    def test_speed_multiplier_at_max_speed(self):
        """При максимальной скорости множитель = 2.0 (квадратичный)."""
        mult = self.director.get_speed_multiplier(MAX_WORLD_SPEED)
        assert mult == pytest.approx(2.0, abs=0.01)

    def test_speed_multiplier_at_mid_speed(self):
        """При средней скорости множитель ≈ 1.25."""
        mid_speed = (BASE_WORLD_SPEED + MAX_WORLD_SPEED) / 2
        mult = self.director.get_speed_multiplier(mid_speed)
        assert mult == pytest.approx(1.25, abs=0.01)

    def test_speed_multiplier_below_base(self):
        """Ниже базовой скорости — множитель не падает ниже 1.0."""
        mult = self.director.get_speed_multiplier(BASE_WORLD_SPEED - 5)
        assert mult == pytest.approx(1.0, abs=0.01)

    def test_bonus_weights_full_health(self):
        """При полном здоровье вес HP минимальный."""
        player = FakePlayer(health=100, max_health=100)
        weight_hp, weight_ex = self.director.get_bonus_weights(player)
        assert weight_hp == 5  # WEIGHT_HP_MIN
        assert weight_ex == 85  # TOTAL_WEIGHT - 5

    def test_bonus_weights_critical_health(self):
        """При критическом здоровье вес HP максимальный."""
        player = FakePlayer(health=20, max_health=100)  # 20% HP
        weight_hp, weight_ex = self.director.get_bonus_weights(player)
        assert weight_hp == 80  # WEIGHT_HP_MAX
        assert weight_ex == 10

    def test_bonus_weights_half_health(self):
        """При 50% HP — промежуточные веса (зона интерполяции)."""
        player = FakePlayer(health=50, max_health=100)
        weight_hp, weight_ex = self.director.get_bonus_weights(player)

        # health_ratio = 0.5, формула: 5 + 75 * 0.5 / 0.7 ≈ 58.57
        assert weight_hp == pytest.approx(58.57, abs=0.01)
        assert weight_ex == pytest.approx(31.43, abs=0.01)

    def test_choose_bonus_type_returns_valid(self):
        """Выбор типа бонуса всегда возвращает 'hp' или 'ex'."""
        player = FakePlayer(health=70, max_health=100)
        for _ in range(20):
            result = self.director.choose_bonus_type(player)
            assert result in ("hp", "ex")

    def test_calculate_health_bonus_within_range(self):
        """Бонус здоровья всегда в допустимом диапазоне."""
        for _ in range(50):
            hp = self.director.calculate_health_bonus()
            assert 5 <= hp <= 10  # HEALTH_BONUS_MIN..MAX

    def test_calculate_experience_positive(self):
        """Опыт всегда положительный."""
        for _ in range(50):
            exp = self.director.calculate_experience(BASE_WORLD_SPEED + 5)
            assert exp > 0
