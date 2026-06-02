"""
Алгоритмические классы: взвешенный выбор, мешок без возврата, геномы и генетический алгоритм.
"""

import bisect
import random


class WeightedChoiceTable:
    """Взвешенный случайный выбор с бинарным поиском."""

    def __init__(self, rng):
        self.rng = rng
        self.items = []
        self.cumulative_weights = []
        self.total_weight = 0

    def add(self, item, weight):
        if weight <= 0:
            return
        self.total_weight += weight
        self.items.append(item)
        self.cumulative_weights.append(self.total_weight)

    def roll(self):
        if not self.items:
            raise ValueError("WeightedChoiceTable is empty")
        ticket = self.rng.uniform(0, self.total_weight)
        index = bisect.bisect_left(self.cumulative_weights, ticket)
        return self.items[index]


class ShuffleBag:
    """Мешок без возврата: равномерное распределение без повторений."""

    def __init__(self, rng, items):
        self.rng = rng
        self.original_items = list(items)
        self.bag = []

    def draw(self):
        if not self.bag:
            self.bag = list(self.original_items)
            self.rng.shuffle(self.bag)
        return self.bag.pop()


class EnemyGenome:
    """Геном врага: параметры для генетической эволюции."""

    def __init__(self, genes=None):
        if genes:
            self.genes = list(genes)
        else:
            self.genes = [
                random.uniform(0.5, 1.3),
                random.uniform(0.3, 0.9),
                random.uniform(0.6, 1.8),
            ]
        self.fitness = 0.0

    def copy(self):
        return EnemyGenome(self.genes[:])


class GeneticAlgorithm:
    """Генетический алгоритм для эволюции параметров врагов."""

    def __init__(self, population_size=10, mutation_rate=0.35):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [EnemyGenome() for _ in range(population_size)]
        self.generation = 0
        self.best_genome = None
        self.best_fitness = -float("inf")

    def evaluate_population(self):
        for genome in self.population:
            aggressiveness, burst_rate, drift = genome.genes
            aggr_score = 100 - abs(aggressiveness - 0.8) * 60
            behavior_score = (burst_rate * 50) + (drift * 60)
            genome.fitness = max(0, aggr_score + behavior_score)
            if genome.fitness > self.best_fitness:
                self.best_fitness = genome.fitness
                self.best_genome = genome.copy()

    def tournament_selection(self, tournament_size=3):
        tournament = random.sample(
            self.population, min(tournament_size, len(self.population))
        )
        return max(tournament, key=lambda g: g.fitness)

    def crossover(self, parent_a, parent_b):
        point = random.randint(1, len(parent_a.genes) - 1)
        child_genes = parent_a.genes[:point] + parent_b.genes[point:]
        return EnemyGenome(child_genes)

    def mutate(self, genome, strength=0.15):
        mutated_genes = []
        for gene in genome.genes:
            if random.random() < self.mutation_rate:
                mutation = random.gauss(0, strength * gene)
                mutated_gene = max(0.0, min(2.0, gene + mutation))
                mutated_genes.append(mutated_gene)
            else:
                mutated_genes.append(gene)
        return EnemyGenome(mutated_genes)

    def evolve(self, elitism=1):
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        new_population = [g.copy() for g in sorted_pop[:elitism]]
        while len(new_population) < self.population_size:
            parent_a = self.tournament_selection()
            parent_b = self.tournament_selection()
            child = self.crossover(parent_a, parent_b)
            child = self.mutate(child)
            new_population.append(child)
        self.population = new_population
        self.generation += 1

    def get_best_genome(self):
        return self.best_genome
