import pygame
import random
import bisect


WIDTH, HEIGHT = 1280, 720
FPS = 60

ASSETS_PATH = "assets/"
ASSETS = {
    "road": ASSETS_PATH + "road_background.png",
    "player": ASSETS_PATH + "car_player.png",
    "enemy": ASSETS_PATH + "enemy_player.png",
    "fire": ASSETS_PATH + "fire.png",
}


class WeightedChoiceTable:
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
    """Геном врага: параметры, которые эволюционируют"""
    def __init__(self, genes=None):
        if genes:
            # гены = [агрессивность, вероятность рывка, интенсивность дрифта]
            self.genes = list(genes)
        else:
            # случайная инициализация в разумных диапазонах
            self.genes = [
                random.uniform(0.5, 1.3),   # агрессивность
                random.uniform(0.3, 0.9),   # вероятность рывка
                random.uniform(0.6, 1.8),   # интенсивность дрифта (большая амплитуда)
            ]
        self.fitness = 0.0

    def copy(self):
        """Создать копию генома"""
        return EnemyGenome(self.genes[:])


class GeneticAlgorithm:
    """Генетический алгоритм для эволюции врагов"""
    def __init__(self, population_size=10, mutation_rate=0.35):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [EnemyGenome() for _ in range(population_size)]
        self.generation = 0
        self.best_genome = None
        self.best_fitness = -float('inf')

    def evaluate_population(self):
        """Оценить приспособленность каждого генома в популяции"""
        for genome in self.population:
            # Приблизительная оценка на основе параметров
            aggressiveness, burst_rate, drift = genome.genes
            
            # Агрессивность: оптимально около 0.8
            aggr_score = 100 - abs(aggressiveness - 0.8) * 60
            
            # Рывок и дрифт - высокие значения поощряются (активное поведение)
            behavior_score = (burst_rate * 50) + (drift * 60)
            
            # Комбинированный фитнес с приоритетом на поведение
            genome.fitness = max(0, aggr_score + behavior_score)
            
            # Обновляем лучший результат
            if genome.fitness > self.best_fitness:
                self.best_fitness = genome.fitness
                self.best_genome = genome.copy()

    def tournament_selection(self, tournament_size=3):
        """Турнирный отбор: выбираем K случайных, побеждает лучший"""
        tournament = random.sample(
            self.population,
            min(tournament_size, len(self.population))
        )
        return max(tournament, key=lambda g: g.fitness)

    def crossover(self, parent_a, parent_b):
        """Одноточечное скрещивание"""
        point = random.randint(1, len(parent_a.genes) - 1)
        child_genes = parent_a.genes[:point] + parent_b.genes[point:]
        return EnemyGenome(child_genes)

    def mutate(self, genome, strength=0.15):
        """Мутация: случайно отклоняем гены"""
        mutated_genes = []
        for gene in genome.genes:
            if random.random() < self.mutation_rate:
                mutation = random.gauss(0, strength * gene)
                mutated_gene = gene + mutation
                mutated_gene = max(0.0, min(2.0, mutated_gene))
                mutated_genes.append(mutated_gene)
            else:
                mutated_genes.append(gene)
        return EnemyGenome(mutated_genes)

    def evolve(self, elitism=1):
        """Выполнить один цикл эволюции"""
        sorted_pop = sorted(
            self.population,
            key=lambda g: g.fitness,
            reverse=True
        )
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
        """Вернуть лучший геном из истории"""
        return self.best_genome


class FloatingText:
    def __init__(self, text, pos, color=(255, 255, 255), lifespan=900, rise=36):
        self.text = str(text)
        self.start_x, self.start_y = int(pos[0]), int(pos[1])
        self.color = color
        self.lifespan = lifespan
        self.rise = rise
        self.start_time = pygame.time.get_ticks()
        self.dead = False

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.lifespan:
            self.dead = True
            return
        self.progress = elapsed / float(self.lifespan)

    def draw(self, surface, font):
        if self.dead:
            return
        # позиция поднимается, альфа плавно уменьшается
        y = int(self.start_y - self.rise * self.progress)
        alpha = int(255 * (1.0 - self.progress))
        text_surf = font.render(self.text, True, self.color)
        try:
            text_surf.set_alpha(alpha)
        except Exception:
            pass
        x = int(self.start_x - text_surf.get_width() // 2)
        surface.blit(text_surf, (x, y))


class Player:
    def __init__(self):
        image = pygame.image.load(ASSETS["player"])
        image = pygame.transform.rotate(image, 90)
        image = pygame.transform.smoothscale(image, (int(image.get_width() * 0.3), int(image.get_width() * 0.5)))

        self.image = image
        self.rect = self.image.get_rect()
        self.start_x = WIDTH // 2 - 90
        self.start_y = HEIGHT - self.rect.height - 20
        self.current_y = float(self.start_y)
        # здоровье и хитбокс
        self.max_health = 100
        self.health = self.max_health
        # хитбокс меньше спрайта для более честных столкновений
        hb_w = int(self.rect.width * 0.7)
        hb_h = int(self.rect.height * 0.6)
        self.hitbox_offset_x = (self.rect.width - hb_w) // 2
        self.hitbox_offset_y = (self.rect.height - hb_h) // 2
        self.hitbox = pygame.Rect(self.rect.x + self.hitbox_offset_x,
                      self.rect.y + self.hitbox_offset_y,
                      hb_w, hb_h)
        self.reset()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.current_y = float(self.start_y)
        self.health = self.max_health
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x,
                                self.rect.y + self.hitbox_offset_y)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= 10
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += 10

        self.rect.left = max(self.rect.left, WIDTH // 2 - 450 + 20)
        self.rect.right = min(self.rect.right, WIDTH // 2 + 450 - 20)
        # обновить позицию хитбокса
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x,
                    self.rect.y + self.hitbox_offset_y)

    def update_vertical_position(self, target_y, smoothing):
        self.current_y += (target_y - self.current_y) * smoothing
        self.rect.y = int(round(self.current_y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # отладка: рисовать хитбокс (закомментировать в финале)
        # pygame.draw.rect(surface, (0,255,0), self.hitbox, 1)  # пример рисования хитбокса

class Enemy:
    def __init__(self, image, x, y, speed, left_bound, right_bound, rng, genome=None):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.rng = rng
        self.genome = genome if genome else EnemyGenome()
        
        # достаем гены для поведения
        self.aggressiveness = self.genome.genes[0]
        self.burst_rate = self.genome.genes[1]
        self.drift_intensity = self.genome.genes[2]
        
        self.float_x = float(self.rect.x)
        # система ускорения/замедления вперед
        self.base_speed = speed
        self.speed_variation = 0
        self.speed_target = 0
        self.next_speed_change = pygame.time.get_ticks() + self.rng.randint(600, 1500)
        
        # система боковых перестроений с большой амплитудой
        self.drift_speed = self.rng.choice([-1, 1]) * self.rng.uniform(
            0.4 * self.drift_intensity,
            1.0 * self.drift_intensity,
        )
        self.drift_target_speed = self.drift_speed
        self.next_drift_change = (
            pygame.time.get_ticks() + self.rng.randint(250, 700)
        )
        self.scored = False
        # хитбокс меньше спрайта для более честных столкновений
        hb_w = int(self.rect.width * 0.8)
        hb_h = int(self.rect.height * 0.85)
        self.hitbox_offset_x = (self.rect.width - hb_w) // 2
        self.hitbox_offset_y = (self.rect.height - hb_h) // 2
        self.hitbox = pygame.Rect(self.rect.x + self.hitbox_offset_x,
                      self.rect.y + self.hitbox_offset_y,
                      hb_w, hb_h)
        # базовый урон (зависит от агрессивности)
        self.base_damage = int((8 + self.speed) * self.aggressiveness)

    def update(self, world_speed=0):
        now = pygame.time.get_ticks()
        
        # случайное ускорение/замедление враги
        if now >= self.next_speed_change:
            self.next_speed_change = now + self.rng.randint(600, 1500)
            self.speed_target = self.rng.uniform(-0.3, 0.3) * self.base_speed * self.aggressiveness
        
        # плавный переход к целевому ускорению
        self.speed_variation += (self.speed_target - self.speed_variation) * 0.12
        
        # применяем ускорение/замедление
        actual_speed = self.base_speed + self.speed_variation
        self.rect.y += actual_speed + world_speed
        
        # быстрые перестроения между полосами
        if now >= self.next_drift_change:
            self.next_drift_change = now + self.rng.randint(250, 700)
            self.drift_target_speed = self.rng.choice([-1, 1]) * self.rng.uniform(
                0.4 * self.drift_intensity,
                1.0 * self.drift_intensity,
            )
        
        # быстрое реагирование на смену направления дрифта
        self.drift_speed += (self.drift_target_speed - self.drift_speed) * 0.25
        self.float_x += self.drift_speed
        self.rect.x = int(round(self.float_x))
        # обновить позицию хитбокса
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x,
                       self.rect.y + self.hitbox_offset_y)

        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.float_x = float(self.rect.x)
            self.drift_target_speed = abs(self.drift_target_speed)
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.float_x = float(self.rect.x)
            self.drift_target_speed = -abs(self.drift_target_speed)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # отладка: хитбокс врага
        # pygame.draw.rect(surface, (255,0,0), self.hitbox, 1)  # пример рисования хитбокса врага
    def is_off_screen(self):
        return self.rect.top > HEIGHT + self.rect.height

    def compute_damage(self):
        # гауссов урон вокруг base_damage, с ограничением
        mean = float(self.base_damage)
        std = max(1.0, mean * 0.15)
        dmg = int(round(self.rng.gauss(mean, std)))
        dmg = max(1, min(dmg, int(mean * 2)))
        return dmg


class Bonus:
    def __init__(self, x, y, rng):
        self.rect = pygame.Rect(x, y, 34, 34)
        self.rng = rng
        self.color = (255, 215, 0)
        self.outline_color = (255, 245, 180)
        self.scored = False

    def update(self, world_speed=0):
        self.rect.y += world_speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.outline_color, self.rect, 2, border_radius=6)

    def is_off_screen(self):
        return self.rect.top > HEIGHT + self.rect.height


class Road:
    def __init__(self):
        image = pygame.image.load(ASSETS["road"])
        self.image = pygame.transform.smoothscale(image, ((WIDTH // 2) + 450, HEIGHT))
        self.y1 = 0
        self.y2 = self.image.get_height()
        self.speed = 5

    def update(self, world_speed=0):
        move = self.speed + world_speed
        self.y1 += move
        self.y2 += move

        if self.y1 >= HEIGHT:
            self.y1 = self.y2 - self.image.get_height()
        if self.y2 >= HEIGHT:
            self.y2 = self.y1 - self.image.get_height()

    def draw(self, surface):
        x = WIDTH // 2 - self.image.get_width() // 2
        surface.blit(self.image, (x, self.y1))
        surface.blit(self.image, (x, self.y2))


class Game:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TheFastestCar")
        self.clock = pygame.time.Clock()

        self.master_seed = random.randrange(2**32)
        self.master_rng = random.Random(self.master_seed)
        self.spawn_rng = random.Random(self.master_rng.randrange(2**32))
        self.enemy_rng = random.Random(self.master_rng.randrange(2**32))
        self.bonus_rng = random.Random(self.master_rng.randrange(2**32))
        # шрифт UI и временные плавающие надписи
        self.ui_font = pygame.font.SysFont(None, 36)
        self.floating_texts = []

        # Генетический алгоритм для эволюции врагов
        self.ga = GeneticAlgorithm(population_size=8, mutation_rate=0.35)
        self.ga.evaluate_population()
        self.best_enemy_genome = self.ga.get_best_genome()

        fire_image = pygame.image.load(ASSETS["fire"])
        self.fire_image = pygame.transform.smoothscale(
            fire_image,
            (int(fire_image.get_width() * 0.5), int(fire_image.get_width() * 0.5)),
        )

        enemy_image = pygame.image.load(ASSETS["enemy"])
        self.enemy_image = pygame.transform.smoothscale(
            enemy_image,
            (int(enemy_image.get_width() * 0.15), int(enemy_image.get_width() * 0.25)),
        )

        self.player = Player()
        self.road = Road()
        self.enemies = []
        self.bonuses = []
        self.spawn_lanes = self.build_spawn_lanes()
        self.spawn_lane_bag = ShuffleBag(self.spawn_rng, self.spawn_lanes)
        self.bonus_lane_bag = ShuffleBag(self.bonus_rng, self.spawn_lanes)
        
        # счетчик спавненных врагов для эволюции
        self.enemy_spawn_count = 0
        self.evolution_interval = 10  # эволюция после каждых 10 врагов
        self.running = True
        self.start_score = 0
        self.score = 0
        self.best_score = self.start_score
        self.last_spawn_time = pygame.time.get_ticks()
        self.last_bonus_spawn_time = pygame.time.get_ticks()
        self.base_spawn_interval = 2200
        self.min_spawn_interval = 700
        self.base_bonus_interval = 3600
        self.min_bonus_interval = 1400
        self.player_speed = 2
        self.start_speed = self.player_speed
        self.max_speed = 15
        self.min_speed = 2
        self.speed_acceleration = 0.07
        self.speed_coast_deceleration = 0.03
        self.speed_brake_deceleration = 0.3
        self.throttle = 0.0
        self.throttle_up_rate = 0.02
        self.throttle_coast_rate = 0.008
        self.throttle_brake_rate = 0.05
        self.max_lift = 36
        self.lift_smoothing = 0.08
        self.coast_smoothing = 0.035
        self.brake_smoothing = 0.18
        self.enemy_speed = 5

    def build_spawn_lanes(self):
        road_left = WIDTH // 2 - self.road.image.get_width() // 2
        road_right = WIDTH // 2 + self.road.image.get_width() // 2
        self.spawn_left_bound = road_left + self.player.rect.width + 140
        self.spawn_right_bound = road_right - self.player.rect.width - 220
        max_x = self.spawn_right_bound - self.enemy_image.get_width()
        lane_count = 5
        lane_step = (max_x - self.spawn_left_bound) / max(1, lane_count - 1)
        return [
            int(round(self.spawn_left_bound + lane_step * index))
            for index in range(lane_count)
        ]

    def spawn_enemy(self):
        x = self.spawn_lane_bag.draw()
        y = -self.enemy_image.get_height()
        self.enemies.append(
            Enemy(
                self.enemy_image,
                x,
                y,
                self.enemy_speed,
                self.spawn_left_bound,
                self.spawn_right_bound,
                self.enemy_rng,
                genome=self.best_enemy_genome,
            )
        )
        self.enemy_spawn_count += 1
        
        # периодическая эволюция генов врагов
        if self.enemy_spawn_count % self.evolution_interval == 0:
            self.ga.evaluate_population()
            self.ga.evolve()
            self.best_enemy_genome = self.ga.get_best_genome()

    def spawn_floating_text(self, text, pos, color=(255, 255, 255), lifespan=900):
        ft = FloatingText(text, pos, color=color, lifespan=lifespan)
        self.floating_texts.append(ft)

    def spawn_enemy_group(self):
        spawn_count = self.get_spawn_count()
        for _ in range(spawn_count):
            self.spawn_enemy()

    def spawn_bonus(self):
        x = self.bonus_lane_bag.draw()
        y = -34
        self.bonuses.append(Bonus(x, y, self.bonus_rng))

    def spawn_bonus_group(self):
        bonus_count = self.get_bonus_count()
        for _ in range(bonus_count):
            self.spawn_bonus()

    def get_spawn_interval(self):
        speed_ratio = self.get_speed_ratio()
        speed_ratio = max(0.0, min(1.0, speed_ratio))
        easing = speed_ratio ** 2
        interval = self.base_spawn_interval - (
            self.base_spawn_interval - self.min_spawn_interval
        ) * easing
        return int(interval)

    def get_speed_ratio(self):
        speed_range = self.max_speed - self.min_speed
        if speed_range == 0:
            return 0.0
        return (self.player_speed - self.min_speed) / speed_range

    def get_spawn_count(self):
        speed_ratio = max(0.0, min(1.0, self.get_speed_ratio()))
        table = WeightedChoiceTable(self.spawn_rng)
        table.add(1, max(10, int(90 - 45 * speed_ratio)))
        table.add(2, max(5, int(10 + 30 * speed_ratio)))
        table.add(3, max(1, int(2 + 20 * speed_ratio)))
        return table.roll()

    def get_bonus_interval(self):
        speed_ratio = max(0.0, min(1.0, self.get_speed_ratio()))
        easing = speed_ratio ** 2
        interval = self.base_bonus_interval - (
            self.base_bonus_interval - self.min_bonus_interval
        ) * easing
        return int(interval)

    def get_bonus_count(self):
        speed_ratio = max(0.0, min(1.0, self.get_speed_ratio()))
        table = WeightedChoiceTable(self.bonus_rng)
        table.add(1, max(10, int(85 - 40 * speed_ratio)))
        table.add(2, max(4, int(12 + 25 * speed_ratio)))
        table.add(3, max(1, int(3 + 12 * speed_ratio)))
        return table.roll()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        accelerating = keys[pygame.K_UP] or keys[pygame.K_w]
        braking = keys[pygame.K_DOWN] or keys[pygame.K_s]

        if accelerating:
            self.player_speed = min(self.player_speed + self.speed_acceleration, self.max_speed)
            self.throttle = min(1.0, self.throttle + self.throttle_up_rate)
        elif braking:
            self.player_speed = max(self.player_speed - self.speed_brake_deceleration, self.min_speed)
            self.throttle = max(0.0, self.throttle - self.throttle_brake_rate)
        else:
            self.player_speed = max(self.player_speed - self.speed_coast_deceleration, self.min_speed)
            self.throttle = max(0.0, self.throttle - self.throttle_coast_rate)

        lift_amount = self.max_lift * (self.throttle ** 2)
        target_y = self.player.start_y - lift_amount
        smoothing = self.brake_smoothing if braking else self.lift_smoothing if accelerating else self.coast_smoothing

        self.road.update(self.player_speed)

        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.player.update_vertical_position(target_y, smoothing)

        self.check_points()

        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.get_spawn_interval():
            self.spawn_enemy_group()
            self.last_spawn_time = now

        if now - self.last_bonus_spawn_time >= self.get_bonus_interval():
            self.spawn_bonus_group()
            self.last_bonus_spawn_time = now

        for enemy in list(self.enemies):
            enemy.update(self.player_speed)

        for bonus in list(self.bonuses):
            bonus.update(self.player_speed)

        # обработка столкновений с врагами -> нанести урон; удалить врага при попадании
        collision_enemy = self.get_collision_enemy()
        if collision_enemy is not None:
            dmg = collision_enemy.compute_damage()
            self.player.health -= dmg
            # удалить врага, который врезался в игрока
            if collision_enemy in self.enemies:
                self.enemies.remove(collision_enemy)
            # плавающий текст для урона (спавн на 50px выше капота, чтобы было видно)
            self.spawn_floating_text(
                f"-{dmg} HP",
                (self.player.rect.centerx, self.player.rect.top - 56),
                (255, 255, 255),
            )
            # показать небольшой эффект попадания
            impact_x = (self.player.rect.centerx + collision_enemy.rect.centerx) // 2
            impact_y = (self.player.rect.centery + collision_enemy.rect.centery) // 2
            self.display.blit(self.fire_image, self.fire_image.get_rect(center=(impact_x, impact_y)))
            pygame.display.flip()
            pygame.time.delay(120)
            if self.player.health <= 0:
                # фатально - пауза и сброс
                self.show_crash_effect_and_pause(collision_enemy)

        # собрать бонусы
        collision_bonus = self.get_collision_bonus()
        if collision_bonus is not None:
            score_inc, heal = self.collect_bonus(collision_bonus)
            self.spawn_floating_text(
                f"+{heal} HP",
                (self.player.rect.centerx, self.player.rect.top - 72),
                (255, 255, 255),
            )
            self.spawn_floating_text(
                f"+{score_inc}",
                (self.player.rect.centerx, self.player.rect.top - 44),
                (255, 255, 255),
            )

        self.enemies = [enemy for enemy in self.enemies if not enemy.is_off_screen()]
        self.bonuses = [bonus for bonus in self.bonuses if not bonus.is_off_screen()]

        # обновить плавающие надписи и удалить устаревшие
        for ft in list(self.floating_texts):
            ft.update()
            if ft.dead:
                self.floating_texts.remove(ft)

    def draw(self):
        self.display.fill((0, 0, 0))
        self.road.draw(self.display)

        for enemy in self.enemies:
            enemy.draw(self.display)

        for bonus in self.bonuses:
            bonus.draw(self.display)

        self.player.draw(self.display)
        self.show_score_and_speed()

        # рисовать плавающие надписи последними (поверх всех сущностей)
        for ft in self.floating_texts:
            ft.draw(self.display, self.ui_font)

        pygame.display.flip()

    def get_collision_enemy(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                return enemy
        return None

    def get_collision_bonus(self):
        for bonus in self.bonuses:
            if self.player.rect.colliderect(bonus.rect):
                return bonus
        return None

    def show_crash_effect_and_pause(self, crash_enemy):
        impact_x = (self.player.rect.centerx + crash_enemy.rect.centerx) // 2
        impact_y = (self.player.rect.centery + crash_enemy.rect.centery) // 2
        self.display.blit(self.fire_image, self.fire_image.get_rect(center=(impact_x, impact_y)))
        pygame.display.flip()

        pause = True
        while pause and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pause = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        pause = False
                    elif event.key == pygame.K_SPACE:
                        pause = False
                        self.enemies.clear()
                        self.player.reset()
                        self.player_speed = self.start_speed
                        self.score = self.start_score
                        self.throttle = 0.0

    def check_points(self):
        for enemy in self.enemies:
            if not enemy.scored and self.player.rect.bottom < enemy.rect.top:
                self.score += 1 + self.player_speed // 10
                enemy.scored = True
        self.best_score = max(self.score, self.best_score)

    def collect_bonus(self, bonus):
        if bonus in self.bonuses:
            self.bonuses.remove(bonus)
            # очки + лечение
            score_gain = 5 + int(self.player_speed // 5)
            self.score += score_gain
            self.best_score = max(self.score, self.best_score)
            # лечение с небольшим гауссовским разбросом
            heal = int(round(self.bonus_rng.gauss(20.0, 5.0)))
            heal = max(5, min(heal, 40))
            self.player.health = min(self.player.max_health, self.player.health + heal)
            return score_gain, heal

        return 0, 0

    def show_score_and_speed(self):
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        best_score_text = font.render(f"Best score: {self.best_score}", True, (255, 255, 255))
        self.display.blit(score_text, (10, 10))
        self.display.blit(best_score_text, (10, 35))

        # полоса здоровья
        hb_x = 10
        hb_y = 70
        hb_w = 220
        hb_h = 14
        pygame.draw.rect(self.display, (60, 60, 60), (hb_x, hb_y, hb_w, hb_h))
        health_ratio = max(0.0, min(1.0, self.player.health / self.player.max_health))
        pygame.draw.rect(self.display, (50, 205, 50), (hb_x + 2, hb_y + 2, int((hb_w - 4) * health_ratio), hb_h - 4))

        speed_text = font.render(f"Speed: {self.player_speed * 7:.2f}", True, (255, 255, 255))
        self.display.blit(speed_text, (10, HEIGHT - 30))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            # коллизии обрабатываются внутри update(): урон, смерть и сбор бонусов

            self.clock.tick(FPS)

        pygame.quit()


def main():
    Game().run()


if __name__ == "__main__":
    main()
