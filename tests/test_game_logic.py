"""Тесты высокоуровневой логики игры."""

import pytest
import sys
from pathlib import Path

# Добавляем корень проекта (если conftest.py не подхватился)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSpawnLogic:
    """Тесты спавна врагов и бонусов."""

    def test_spawn_interval_decreases_with_speed(self):
        """Интервал спавна уменьшается при росте скорости."""
        from src.main import Game  # ← обновлённый импорт
        import pygame

        pygame.init()

        game = Game()
        game.player_speed = game.min_speed
        interval_low = game.get_spawn_interval()
        game.player_speed = game.max_speed
        interval_high = game.get_spawn_interval()

        assert interval_low > interval_high, "Интервал должен уменьшаться"
        pygame.quit()

    def test_spawn_count_increases_with_speed(self):
        """Количество врагов в группе растёт со скоростью."""
        from src.main import Game  # ← обновлённый импорт
        import pygame

        pygame.init()

        game = Game()
        game.player_speed = game.min_speed
        low_counts = [game.get_spawn_count() for _ in range(50)]
        game.player_speed = game.max_speed
        high_counts = [game.get_spawn_count() for _ in range(50)]

        avg_low = sum(low_counts) / len(low_counts)
        avg_high = sum(high_counts) / len(high_counts)
        assert avg_high >= avg_low, (
            f"Среднее: низкая={avg_low:.2f}, высокая={avg_high:.2f}"
        )
        pygame.quit()


class TestPlayerMovement:
    """Тесты движения игрока."""

    def test_player_stays_within_road(self):
        """Игрок не может выйти за границы дороги."""
        from src.main import Player, WIDTH  # ← обновлённый импорт
        import pygame

        pygame.init()

        player = Player()
        for _ in range(100):
            player.update(
                {
                    pygame.K_LEFT: True,
                    pygame.K_a: False,
                    pygame.K_RIGHT: False,
                    pygame.K_d: False,
                }
            )

        road_left = WIDTH // 2 - 450 + 20
        assert player.rect.left >= road_left
        pygame.quit()
