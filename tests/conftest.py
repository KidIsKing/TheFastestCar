"""Фикстуры pytest для тестов TheFastestCar."""

import pytest
import random
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def deterministic_rng():
    """Генератор с фиксированным seed для детерминированных тестов."""
    return random.Random(42)


@pytest.fixture
def weighted_table_cls():
    """Импортируем класс взвешенного выбора."""
    from src.main import WeightedChoiceTable

    return WeightedChoiceTable


@pytest.fixture
def shuffle_bag_cls():
    """Импортируем класс ShuffleBag."""
    from src.main import ShuffleBag

    return ShuffleBag


@pytest.fixture
def ga_cls():
    """Импортируем генетический алгоритм."""
    from src.main import GeneticAlgorithm

    return GeneticAlgorithm


@pytest.fixture
def enemy_genome_cls():
    """Импортируем геном врага."""
    from src.main import EnemyGenome

    return EnemyGenome
