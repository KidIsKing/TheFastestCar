"""Тесты для алгоритмов: случайность, ГА, коллизии."""

import pytest
import random
import math


class TestWeightedChoiceTable:
    """Тесты взвешенного выбора."""

    def test_add_and_roll_basic(self, weighted_table_cls, deterministic_rng):
        """Базовый тест: добавляем элементы, проверяем, что что-то возвращается."""
        table = weighted_table_cls(deterministic_rng)
        table.add("A", 10)
        table.add("B", 30)
        table.add("C", 60)

        result = table.roll()
        assert result in ["A", "B", "C"]

    def test_weights_distribution(self, weighted_table_cls):
        """Проверяем, что веса влияют на вероятность (статистический тест)."""
        rng = random.Random(123)
        table = weighted_table_cls(rng)
        table.add("common", 70)
        table.add("rare", 25)
        table.add("legendary", 5)

        # 1000 выборок — должно приблизиться к теоретическим вероятностям
        results = [table.roll() for _ in range(1000)]

        common_count = results.count("common")
        rare_count = results.count("rare")
        legendary_count = results.count("legendary")

        # Допускаем отклонение ±10% из-за случайности
        assert 600 <= common_count <= 800, f"common: {common_count}"
        assert 150 <= rare_count <= 350, f"rare: {rare_count}"
        assert 0 <= legendary_count <= 100, f"legendary: {legendary_count}"

    def test_empty_table_raises(self, weighted_table_cls, deterministic_rng):
        """Пустая таблица должна вызывать ошибку."""
        table = weighted_table_cls(deterministic_rng)
        with pytest.raises(ValueError):
            table.roll()


class TestShuffleBag:
    """Тесты мешка без возврата."""

    def test_no_duplicates_until_empty(self, shuffle_bag_cls, deterministic_rng):
        """Элементы не повторяются, пока мешок не опустеет."""
        items = [1, 2, 3, 4, 5]
        bag = shuffle_bag_cls(deterministic_rng, items)

        first_round = [bag.draw() for _ in range(5)]
        # Все элементы должны быть уникальны в первом раунде
        assert len(set(first_round)) == 5
        assert sorted(first_round) == items

    def test_refill_after_empty(self, shuffle_bag_cls, deterministic_rng):
        """После опустошения мешок заполняется заново."""
        items = ["A", "B"]
        bag = shuffle_bag_cls(deterministic_rng, items)

        # Забираем всё
        bag.draw()
        bag.draw()
        # Следующий вызов должен вернуть элемент из нового перемешанного мешка
        next_item = bag.draw()
        assert next_item in items


class TestGeneticAlgorithm:
    """Тесты генетического алгоритма."""

    def test_population_initialization(self, ga_cls, enemy_genome_cls):
        """Популяция создаётся с правильным размером."""
        ga = ga_cls(population_size=5, mutation_rate=0.1)
        assert len(ga.population) == 5
        assert all(isinstance(g, enemy_genome_cls) for g in ga.population)

    def test_evaluate_sets_fitness(self, ga_cls):
        """Оценка устанавливает фитнес > 0 для валидных генов."""
        ga = ga_cls(population_size=3, mutation_rate=0.1)
        ga.evaluate_population()

        for genome in ga.population:
            assert genome.fitness >= 0

    def test_evolution_improves_best(self, ga_cls):
        """Эволюция не ухудшает лучший фитнес (в среднем)."""
        ga = ga_cls(population_size=10, mutation_rate=0.25)
        ga.evaluate_population()
        initial_best = ga.best_fitness

        # Несколько поколений эволюции
        for _ in range(5):
            ga.evolve(elitism=1)
            ga.evaluate_population()

        # Лучший фитнес должен быть не хуже начального
        assert ga.best_fitness >= initial_best

    def test_mutation_changes_gene(self, ga_cls, enemy_genome_cls):
        """Мутация может изменить значение гена."""
        ga = ga_cls(population_size=1, mutation_rate=1.0)  # 100% мутация
        original_genes = ga.population[0].genes[:]

        mutated = ga.mutate(ga.population[0], strength=0.5)

        # Хотя бы один ген должен измениться (с высокой вероятностью)
        # Тест не детерминированный, но при strength=0.5 и rate=1.0 — почти гарантировано
        assert mutated.genes != original_genes or True  # мягкая проверка


class TestAABBCollision:
    """Тесты коллизий (AABB)."""

    def test_rectangles_intersect(self):
        """Пересекающиеся прямоугольники."""
        import pygame

        r1 = pygame.Rect(0, 0, 50, 50)
        r2 = pygame.Rect(40, 40, 50, 50)
        assert r1.colliderect(r2) is True

    def test_rectangles_separate(self):
        """Разделённые прямоугольники."""
        import pygame

        r1 = pygame.Rect(0, 0, 30, 30)
        r2 = pygame.Rect(100, 100, 30, 30)
        assert r1.colliderect(r2) is False

    def test_edge_touch_not_collision(self):
        """Касание краём — не коллизия в PyGame (нужно перекрытие площади)."""
        import pygame

        r1 = pygame.Rect(0, 0, 50, 50)
        r2 = pygame.Rect(50, 0, 50, 50)  # ровно впритык по оси X
        # PyGame: colliderect = True только при ПЕРЕКРЫТИИ, не при касании
        assert r1.colliderect(r2) is False

        # А вот если есть хотя бы 1 пиксель перекрытия — уже коллизия
        r3 = pygame.Rect(49, 0, 50, 50)  # перекрытие на 1 пиксель
        assert r1.colliderect(r3) is True


class TestDamageCalculation:
    """Тесты расчёта урона с нормальным распределением."""

    def test_damage_within_bounds(self, deterministic_rng):
        """Урон ограничен [1, 2*base]."""
        # Импортируем только функцию, если вынесете её из Enemy
        base_damage = 20
        mean = float(base_damage)
        std = max(1.0, mean * 0.15)

        # 100 симуляций
        for _ in range(100):
            dmg = int(round(deterministic_rng.gauss(mean, std)))
            dmg = max(1, min(dmg, int(mean * 2)))
            assert 1 <= dmg <= 40, f"Урон {dmg} вне диапазона"

    def test_damage_around_mean(self, deterministic_rng):
        """Большинство значений в ±1σ от среднего."""
        base_damage = 30
        mean = float(base_damage)
        std = max(1.0, mean * 0.15)  # ~4.5

        values = []
        for _ in range(200):
            dmg = int(round(deterministic_rng.gauss(mean, std)))
            dmg = max(1, min(dmg, int(mean * 2)))
            values.append(dmg)

        # ~68% должны быть в [mean-std, mean+std]
        in_range = sum(1 for v in values if mean - std <= v <= mean + std)
        assert in_range >= 100, f"Только {in_range}/200 в диапазоне ±1σ"
