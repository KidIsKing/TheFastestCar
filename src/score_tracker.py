class ScoreTracker:
    """Очки и рекорды."""

    best_score = 0

    def __init__(self):
        self._score = 0

    @property
    def score(self):
        """Текущий счёт."""
        return self._score

    @score.setter
    def score(self, value):
        """Установка счёта с проверкой рекорда."""
        self._score = max(0, value)  # счёт не может быть отрицательным
        self._check_best_score()

    def _check_best_score(self):
        """Проверка и обновление рекорда."""
        if self._score > ScoreTracker.best_score:
            ScoreTracker.best_score = self._score

    def add_score(self, points):
        """Добавление очков."""
        self.score += points

    def reset(self):
        """Сброс текущего счёта."""
        self._score = 0

    @classmethod
    def get_best_score(cls):
        """Получение рекорда."""
        return cls.best_score
