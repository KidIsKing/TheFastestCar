import json
from pathlib import Path


class SaveManager:
    """Сохранение прогресса в JSON-файл."""

    SAVE_FILE = Path("save_data/save_data.json")

    KEY_BEST_SCORE = "best_score"

    @classmethod
    def load(cls):
        """Загрузка данных."""
        if not cls.SAVE_FILE.exists():
            return {}

        try:
            with open(cls.SAVE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки сохранений: {e}.")
            return {}

    @classmethod
    def save(cls, data):
        try:
            with open(cls.SAVE_FILE, "w", encoding="utf-8") as file:
                return json.dump(data, file, indent=2)
        except (IOError) as e:
            print(f"Ошибка сохранения: {e}.")

    @classmethod
    def get_best_score(cls):
        """Выгрузка рекорда из файла."""
        data = cls.load()
        return data.get(cls.KEY_BEST_SCORE, 0)

    @classmethod
    def set_best_score(cls, score):
        """Загрузка файла в игру."""
        data = cls.load()
        data[cls.KEY_BEST_SCORE] = score
        cls.save(data)
