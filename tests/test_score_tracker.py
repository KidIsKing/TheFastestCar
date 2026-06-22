import pytest
from systems.score_tracker import ScoreTracker


class TestScoreTracker:
    """Тесты ScoreTracker."""

    def setup_method(self):
        """Свежий трекер перед каждым тестом."""
        self.tracker = ScoreTracker()

    def test_initial_score_is_zero(self):
        """Начальный счёт = 0."""
        assert self.tracker.score == 0

    def test_add_score(self):
        """Добавление очков увеличивает счёт."""
        self.tracker.add_score(50)
        assert self.tracker.score == 50

    def test_add_multiple_scores(self):
        """Несколько добавлений суммируются."""
        self.tracker.add_score(10)
        self.tracker.add_score(20)
        self.tracker.add_score(30)
        assert self.tracker.score == 60

    def test_score_cannot_be_negative(self):
        """Счёт не может стать отрицательным."""
        self.tracker.score = -100
        assert self.tracker.score == 0

    def test_reset_clears_score(self):
        """reset() обнуляет счёт."""
        self.tracker.add_score(100)
        self.tracker.reset()
        assert self.tracker.score == 0

    def test_best_score_updated(self):
        """Рекорд обновляется при превышении."""
        initial_best = self.tracker.best_score
        self.tracker.add_score(initial_best + 1000)
        assert self.tracker.best_score == initial_best + 1000

    def test_best_score_not_decreased(self):
        """Рекорд не уменьшается при малом счёте."""
        self.tracker.add_score(1000)
        best = self.tracker.best_score
        self.tracker.reset()
        self.tracker.add_score(10)
        assert self.tracker.best_score == best

    def test_get_best_score_returns_int(self):
        """get_best_score() возвращает число."""
        result = self.tracker.get_best_score()
        assert isinstance(result, int)
