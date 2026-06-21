from save_manager import SaveManager

class ScoreTracker:
    """Очки и рекорды."""
    def __init__(self):
        self._score = 0

        self.best_score = SaveManager.get_best_score()

    @property
    def score(self):
        """Текущий счёт."""
        return self._score

    @score.setter
    def score(self, value):
        """Установка счёта."""
        self._score = max(0, value)  # счёт не может быть отрицательным
        self._check_best_score()

    def _check_best_score(self):
        """Обновление рекорда."""
        if self._score > self.best_score:
            self.best_score = self._score
            SaveManager.set_best_score(self._score)

    def add_score(self, points):
        """Добавление очков."""
        self.score += points

    def reset(self):
        """Сброс текущего счёта."""
        self._score = 0

    def get_best_score(cls):
        """Получение рекорда."""
        return cls.best_score
