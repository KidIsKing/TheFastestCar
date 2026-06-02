"""
TheFastestCar — бесконечная аркада на шоссе.
Экзаменационная работа по курсу «Программирование», 1 курс.
"""

import pygame
import random

try:
    from .constants import (
        WIDTH,
        HEIGHT,
        FPS,
        ASSETS,
        PLAYER_ROTATION,
        PLAYER_SCALE_W,
        PLAYER_SCALE_H,
        PLAYER_START_X_OFFSET,
        PLAYER_START_Y_MARGIN,
        PLAYER_MAX_HEALTH,
        PLAYER_HITBOX_W,
        PLAYER_HITBOX_H,
        PLAYER_MOVE_STEP,
        PLAYER_SIDE_MARGIN,
        ENEMY_IMAGE_SCALE_W,
        ENEMY_IMAGE_SCALE_H,
        ENEMY_SPEED_CHANGE_MIN,
        ENEMY_SPEED_CHANGE_MAX,
        ENEMY_DRIFT_CHANGE_MIN,
        ENEMY_DRIFT_CHANGE_MAX,
        ENEMY_DRIFT_MULT_MIN,
        ENEMY_DRIFT_MULT_MAX,
        ENEMY_HITBOX_W,
        ENEMY_HITBOX_H,
        ENEMY_BASE_DAMAGE_OFFSET,
        ENEMY_DAMAGE_STD_RATIO,
        ENEMY_DAMAGE_CLAMP_MULT,
        ENEMY_DEFAULT_SPEED,
        BONUS_SIZE,
        BONUS_COLOR,
        BONUS_OUTLINE_COLOR,
        BONUS_SCORE_BASE,
        BONUS_HEAL_MEAN,
        BONUS_HEAL_STD,
        BONUS_HEAL_MIN,
        BONUS_HEAL_MAX,
        FLOATING_TEXT_LIFESPAN,
        FLOATING_TEXT_RISE,
        FLOATING_TEXT_COLOR,
        ROAD_HALF_WIDTH_MARGIN,
        ROAD_SPEED,
        SPAWN_LEFT_SAFE_OFFSET,
        SPAWN_RIGHT_SAFE_OFFSET,
        LANE_COUNT,
        BASE_SPAWN_INTERVAL,
        MIN_SPAWN_INTERVAL,
        BASE_BONUS_INTERVAL,
        MIN_BONUS_INTERVAL,
        EVOLUTION_INTERVAL,
        GA_POPULATION_SIZE,
        GA_MUTATION_RATE,
        PLAYER_START_SPEED,
        PLAYER_MAX_SPEED,
        PLAYER_MIN_SPEED,
        SPEED_ACCELERATION,
        SPEED_COAST_DECELERATION,
        SPEED_BRAKE_DECELERATION,
        SPEED_SMOOTHING,
        THROTTLE_UP_RATE,
        THROTTLE_COAST_RATE,
        THROTTLE_BRAKE_RATE,
        MAX_LIFT,
        LIFT_SMOOTHING,
        COAST_SMOOTHING,
        BRAKE_SMOOTHING,
        UI_FONT_SIZE,
        UI_SCORE_POS,
        UI_BEST_SCORE_POS,
        UI_HEALTH_BAR,
        UI_HEALTH_BG_COLOR,
        UI_HEALTH_COLOR,
        UI_SPEED_POS,
        FIRE_SCALE,
        CRASH_DISPLAY_DELAY,
        ENEMY_MIN_GAP,
    )
    from .algorithms import (
        WeightedChoiceTable,
        ShuffleBag,
        EnemyGenome,
        GeneticAlgorithm,
    )
except Exception:
    # Fallback for running the script directly (not as package)
    from constants import WIDTH, HEIGHT, FPS, ASSETS
    from algorithms import (
        WeightedChoiceTable,
        ShuffleBag,
        EnemyGenome,
        GeneticAlgorithm,
    )


class FloatingText:
    """Плавающий текст для визуальной обратной связи."""

    def __init__(self, text, pos, color=FLOATING_TEXT_COLOR, lifespan=FLOATING_TEXT_LIFESPAN, rise=FLOATING_TEXT_RISE):
        """Инициализировать текст."""
        self.text = str(text)
        self.start_x, self.start_y = int(pos[0]), int(pos[1])
        self.color = color
        self.lifespan = lifespan
        self.rise = rise
        self.start_time = pygame.time.get_ticks()
        self.dead = False

    def update(self):
        """Обновить прогресс анимации."""
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.lifespan:
            self.dead = True
            return
        self.progress = elapsed / float(self.lifespan)

    def draw(self, surface, font):
        """Отрисовать текст с плавным исчезновением."""
        if self.dead:
            return
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
    """Состояние и поведение игрока."""

    def __init__(self):
        """Загрузить спрайт, инициализировать позицию, здоровье, хитбокс."""
        image = pygame.image.load(ASSETS["player"])
        image = pygame.transform.rotate(image, PLAYER_ROTATION)
        image = pygame.transform.smoothscale(
            image, (int(image.get_width() * PLAYER_SCALE_W), int(image.get_width() * PLAYER_SCALE_H))
        )
        self.image = image
        self.rect = self.image.get_rect()
        self.start_x = WIDTH // 2 + PLAYER_START_X_OFFSET
        self.start_y = HEIGHT - self.rect.height - PLAYER_START_Y_MARGIN
        self.current_y = float(self.start_y)
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        # Хитбокс меньше спрайта — столкновения честнее, игрок не «умирает от касания краем»
        hb_w = int(self.rect.width * PLAYER_HITBOX_W)
        hb_h = int(self.rect.height * PLAYER_HITBOX_H)
        self.hitbox_offset_x = (self.rect.width - hb_w) // 2
        self.hitbox_offset_y = (self.rect.height - hb_h) // 2
        self.hitbox = pygame.Rect(
            self.rect.x + self.hitbox_offset_x,
            self.rect.y + self.hitbox_offset_y,
            hb_w,
            hb_h,
        )
        self.reset()

    def reset(self):
        """Сбросить состояние игрока."""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.current_y = float(self.start_y)
        self.health = self.max_health
        self._update_hitbox()

    def _update_hitbox(self):
        """Синхронизировать хитбокс со спрайтом — вызывается при любом изменении позиции."""
        self.hitbox.topleft = (
            self.rect.x + self.hitbox_offset_x,
            self.rect.y + self.hitbox_offset_y,
        )

    def update(self, keys):
        """Обработать ввод: горизонтальное движение с ограничением по дороге."""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_MOVE_STEP
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_MOVE_STEP
        # Ограничиваем движение в пределах дороги + небольшой отступ от края
        self.rect.left = max(self.rect.left, WIDTH // 2 - ROAD_HALF_WIDTH_MARGIN + PLAYER_SIDE_MARGIN)
        self.rect.right = min(self.rect.right, WIDTH // 2 + ROAD_HALF_WIDTH_MARGIN - PLAYER_SIDE_MARGIN)
        self._update_hitbox()

    def update_vertical_position(self, target_y, smoothing):
        """Плавное вертикальное смещение — визуальный эффект при ускорении."""
        self.current_y += (target_y - self.current_y) * smoothing
        self.rect.y = int(round(self.current_y))
        self._update_hitbox()

    def draw(self, surface):
        """Отрисовать спрайт."""
        surface.blit(self.image, self.rect)


class Enemy:
    """Враг с эволюционирующим поведением."""

    def __init__(self, image, x, y, speed, left_bound, right_bound, rng, genome=None):
        """Инициализировать врага."""
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.rng = rng
        self.genome = genome if genome else EnemyGenome()
        # Распаковываем гены в понятные переменные для использования в поведении
        self.aggressiveness = self.genome.genes[0]
        self.burst_rate = self.genome.genes[1]
        self.drift_intensity = self.genome.genes[2]
        self.float_x = float(self.rect.x)  # float-позиция для плавного дрифта
        self.base_speed = speed
        self.speed_variation = 0
        self.speed_target = 0
        self.next_speed_change = pygame.time.get_ticks() + self.rng.randint(ENEMY_SPEED_CHANGE_MIN, ENEMY_SPEED_CHANGE_MAX)
        # Инициализация дрифта: случайное направление и сила в пределах интенсивности
        self.drift_speed = self.rng.choice([-1, 1]) * self.rng.uniform(
            ENEMY_DRIFT_MULT_MIN * self.drift_intensity, ENEMY_DRIFT_MULT_MAX * self.drift_intensity
        )
        self.drift_target_speed = self.drift_speed
        self.next_drift_change = pygame.time.get_ticks() + self.rng.randint(ENEMY_DRIFT_CHANGE_MIN, ENEMY_DRIFT_CHANGE_MAX)
        self.scored = False
        # Хитбокс врага: чуть меньше спрайта, но больше, чем у игрока — баланс сложности
        hb_w = int(self.rect.width * ENEMY_HITBOX_W)
        hb_h = int(self.rect.height * ENEMY_HITBOX_H)
        self.hitbox_offset_x = (self.rect.width - hb_w) // 2
        self.hitbox_offset_y = (self.rect.height - hb_h) // 2
        self.hitbox = pygame.Rect(
            self.rect.x + self.hitbox_offset_x,
            self.rect.y + self.hitbox_offset_y,
            hb_w,
            hb_h,
        )
        # Базовый урон: зависит от скорости и агрессивности
        self.base_damage = int((ENEMY_BASE_DAMAGE_OFFSET + self.speed) * self.aggressiveness)

    def _update_hitbox(self):
        """Синхронизировать хитбокс."""
        self.hitbox.topleft = (
            self.rect.x + self.hitbox_offset_x,
            self.rect.y + self.hitbox_offset_y,
        )

    def update(self, world_speed=0):
        """Обновить позицию: вертикальное движение + боковой дрифт с плавными переходами."""
        now = pygame.time.get_ticks()
        # Случайное изменение скорости: имитация «нервного» вождения
        if now >= self.next_speed_change:
            self.next_speed_change = now + self.rng.randint(ENEMY_SPEED_CHANGE_MIN, ENEMY_SPEED_CHANGE_MAX)
            self.speed_target = (
                self.rng.uniform(ENEMY_SPEED_TARGET_MIN, ENEMY_SPEED_TARGET_MAX) * self.base_speed * self.aggressiveness
            )
        # Плавное приближение к целевому изменению скорости — без рывков
        self.speed_variation += (self.speed_target - self.speed_variation) * ENEMY_SPEED_VARIATION_SMOOTH
        actual_speed = self.base_speed + self.speed_variation
        self.rect.y += actual_speed + world_speed
        # Смена направления дрифта: частота зависит от burst_rate
        if now >= self.next_drift_change:
            self.next_drift_change = now + self.rng.randint(ENEMY_DRIFT_CHANGE_MIN, ENEMY_DRIFT_CHANGE_MAX)
            self.drift_target_speed = self.rng.choice([-1, 1]) * self.rng.uniform(
                ENEMY_DRIFT_MULT_MIN * self.drift_intensity, ENEMY_DRIFT_MULT_MAX * self.drift_intensity
            )
        # Плавный переход к новому направлению дрифта — естественное поведение
        self.drift_speed += (self.drift_target_speed - self.drift_speed) * ENEMY_DRIFT_SMOOTH
        self.float_x += self.drift_speed
        self.rect.x = int(round(self.float_x))
        # Отскок от границ дороги: меняем направление дрифта, чтобы не «застревать»
        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.float_x = float(self.rect.x)
            self.drift_target_speed = abs(self.drift_target_speed)
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.float_x = float(self.rect.x)
            self.drift_target_speed = -abs(self.drift_target_speed)
        self._update_hitbox()

    def draw(self, surface):
        """Отрисовать спрайт."""
        surface.blit(self.image, self.rect)

    def is_off_screen(self):
        """Проверить, ушёл ли враг за экран."""
        return self.rect.top > HEIGHT + self.rect.height

    def compute_damage(self):
        """Рассчитать урон: гауссов разброс + ограничение выбросов."""
        mean = float(self.base_damage)
        std = max(1.0, mean * ENEMY_DAMAGE_STD_RATIO)  # отклонение
        dmg = int(round(self.rng.gauss(mean, std)))
        # Clamp: защищаем от экстремальных значений
        return max(1, min(dmg, int(mean * ENEMY_DAMAGE_CLAMP_MULT)))


class Bonus:
    """Бонус на дороге."""

    def __init__(self, x, y, rng):
        """Инициализировать бонус."""
        self.rect = pygame.Rect(x, y, BONUS_SIZE, BONUS_SIZE)
        self.rng = rng
        self.color = BONUS_COLOR
        self.outline_color = BONUS_OUTLINE_COLOR
        self.scored = False

    def update(self, world_speed=0):
        """Сдвинуть бонус вниз."""
        self.rect.y += world_speed

    def draw(self, surface):
        """Отрисовать бонус."""
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.outline_color, self.rect, 2, border_radius=6)

    def is_off_screen(self):
        """Проверить, ушёл ли бонус за экран."""
        return self.rect.top > HEIGHT + self.rect.height


class Road:
    """Бесконечная дорога с параллакс-скроллингом."""

    def __init__(self):
        """Загрузить и масштабировать спрайт."""
        image = pygame.image.load(ASSETS["road"])
        self.image = pygame.transform.smoothscale(image, ((WIDTH // 2) + ROAD_HALF_WIDTH_MARGIN, HEIGHT))
        self.y1 = 0
        self.y2 = self.image.get_height()
        self.speed = ROAD_SPEED

    def update(self, world_speed=0):
        """Сдвинуть текстуры, реализовать зацикливание."""
        move = self.speed + world_speed
        self.y1 += move
        self.y2 += move
        if self.y1 >= HEIGHT:
            self.y1 = self.y2 - self.image.get_height()
        if self.y2 >= HEIGHT:
            self.y2 = self.y1 - self.image.get_height()

    def draw(self, surface):
        """Отрисовать две копии для бесконечного скролла."""
        x = WIDTH // 2 - self.image.get_width() // 2
        surface.blit(self.image, (x, self.y1))
        surface.blit(self.image, (x, self.y2))


class Game:
    """Координация игровой логики: ввод -> обновление -> отрисовка."""

    def __init__(self):
        """Инициализировать игру."""
        pygame.init()
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TheFastestCar")
        self.clock = pygame.time.Clock()
        # Независимые RNG для подсистем: спавн не зависит от поведения врагов, бонусы — от всего остального
        # Это даёт детерминированность при фиксированном seed и изолирует баги
        self.master_seed = random.randrange(2**32)
        self.master_rng = random.Random(self.master_seed)
        self.spawn_rng = random.Random(self.master_rng.randrange(2**32))
        self.enemy_rng = random.Random(self.master_rng.randrange(2**32))
        self.bonus_rng = random.Random(self.master_rng.randrange(2**32))
        self.ui_font = pygame.font.SysFont(None, UI_FONT_SIZE)
        self.floating_texts = []
        self.ga = GeneticAlgorithm(population_size=GA_POPULATION_SIZE, mutation_rate=GA_MUTATION_RATE)
        self.ga.evaluate_population()
        self.best_enemy_genome = self.ga.get_best_genome()
        fire_image = pygame.image.load(ASSETS["fire"])
        self.fire_image = pygame.transform.smoothscale(
            fire_image,
            (int(fire_image.get_width() * FIRE_SCALE), int(fire_image.get_width() * FIRE_SCALE)),
        )
        enemy_image = pygame.image.load(ASSETS["enemy"])
        self.enemy_image = pygame.transform.smoothscale(
            enemy_image,
            (int(enemy_image.get_width() * ENEMY_IMAGE_SCALE_W), int(enemy_image.get_width() * ENEMY_IMAGE_SCALE_H)),
        )
        self.player = Player()
        self.road = Road()
        self.enemies = []
        self.bonuses = []
        self.spawn_lanes = self.build_spawn_lanes()
        self.spawn_lane_bag = ShuffleBag(self.spawn_rng, self.spawn_lanes)
        self.bonus_lane_bag = ShuffleBag(self.bonus_rng, self.spawn_lanes)
        self.enemy_spawn_count = 0
        self.evolution_interval = EVOLUTION_INTERVAL
        self.running = True
        self.start_score = 0
        self.score = 0
        self.best_score = self.start_score
        self.last_spawn_time = pygame.time.get_ticks()
        self.last_bonus_spawn_time = pygame.time.get_ticks()
        self.base_spawn_interval = BASE_SPAWN_INTERVAL
        self.min_spawn_interval = MIN_SPAWN_INTERVAL
        self.base_bonus_interval = BASE_BONUS_INTERVAL
        self.min_bonus_interval = MIN_BONUS_INTERVAL
        self.player_speed = PLAYER_START_SPEED
        self.start_speed = self.player_speed
        self.max_speed = PLAYER_MAX_SPEED
        self.min_speed = PLAYER_MIN_SPEED
        self.speed_acceleration = SPEED_ACCELERATION
        self.speed_coast_deceleration = SPEED_COAST_DECELERATION
        self.speed_brake_deceleration = SPEED_BRAKE_DECELERATION
        # Коэффициент сглаживания скорости: меньше = плавнее, но с задержкой реакции
        self.speed_smoothing = SPEED_SMOOTHING
        self.throttle = 0.0
        self.throttle_up_rate = THROTTLE_UP_RATE
        self.throttle_coast_rate = THROTTLE_COAST_RATE
        self.throttle_brake_rate = THROTTLE_BRAKE_RATE
        self.max_lift = MAX_LIFT
        self.lift_smoothing = LIFT_SMOOTHING
        self.coast_smoothing = COAST_SMOOTHING
        self.brake_smoothing = BRAKE_SMOOTHING
        self.enemy_speed = ENEMY_DEFAULT_SPEED

    def build_spawn_lanes(self):
        """Рассчитать допустимые координаты спавна по горизонтали."""
        road_left = WIDTH // 2 - self.road.image.get_width() // 2
        road_right = WIDTH // 2 + self.road.image.get_width() // 2
        # Границы спавна: с отступом от игрока и краёв дороги, чтобы не появляться «в упор»
        self.spawn_left_bound = road_left + self.player.rect.width + SPAWN_LEFT_SAFE_OFFSET
        self.spawn_right_bound = road_right - self.player.rect.width - SPAWN_RIGHT_SAFE_OFFSET
        max_x = self.spawn_right_bound - self.enemy_image.get_width()
        lane_count = LANE_COUNT
        lane_step = (max_x - self.spawn_left_bound) / max(1, lane_count - 1)
        return [
            int(round(self.spawn_left_bound + lane_step * index))
            for index in range(lane_count)
        ]

    def spawn_enemy(self):
        """Создать врага, если позиция свободна; запустить эволюцию при необходимости."""
        x = self.spawn_lane_bag.draw()
        y = -self.enemy_image.get_height()
        # Проактивная проверка: не спавним врага поверх другого — предотвращает наложения «из коробки»
        if not self._can_spawn_at(x, y, margin=PLAYER_SIDE_MARGIN):
            return
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
        # Эволюция: каждые N врагов обновляем популяцию — поведение адаптируется к сессии
        if self.enemy_spawn_count % self.evolution_interval == 0:
            self.ga.evaluate_population()
            self.ga.evolve()
            self.best_enemy_genome = self.ga.get_best_genome()

    def spawn_floating_text(self, text, pos, color=FLOATING_TEXT_COLOR, lifespan=FLOATING_TEXT_LIFESPAN):
        """Добавить плавающий текст."""
        ft = FloatingText(text, pos, color=color, lifespan=lifespan)
        self.floating_texts.append(ft)

    def spawn_enemy_group(self):
        """Спавн группы врагов."""
        for _ in range(self.get_spawn_count()):
            self.spawn_enemy()

    def spawn_bonus(self):
        """Создать бонус."""
        x = self.bonus_lane_bag.draw()
        y = -BONUS_SIZE
        self.bonuses.append(Bonus(x, y, self.bonus_rng))

    def spawn_bonus_group(self):
        """Спавн группы бонусов."""
        for _ in range(self.get_bonus_count()):
            self.spawn_bonus()

    def get_spawn_interval(self):
        """Рассчитать интервал спавна: уменьшается с ростом скорости (квадратичное easing)."""
        speed_ratio = self.get_speed_ratio()
        speed_ratio = max(0.0, min(1.0, speed_ratio))
        easing = speed_ratio**2  # Квадратичное: медленный рост вначале, быстрый к концу
        interval = (
            self.base_spawn_interval
            - (self.base_spawn_interval - self.min_spawn_interval) * easing
        )
        return int(interval)

    def get_speed_ratio(self):
        """Нормализовать скорость в [0, 1]."""
        speed_range = self.max_speed - self.min_speed
        return (
            (self.player_speed - self.min_speed) / speed_range
            if speed_range != 0
            else 0.0
        )

    def get_spawn_count(self):
        """Взвешенный выбор количества врагов: вероятность группы растёт со скоростью."""
        speed_ratio = max(0.0, min(1.0, self.get_speed_ratio()))
        table = WeightedChoiceTable(self.spawn_rng)
        # Веса подобраны так, чтобы на низкой скорости чаще 1 враг, на высокой — группы
        table.add(1, max(10, int(90 - 45 * speed_ratio)))
        table.add(2, max(5, int(10 + 30 * speed_ratio)))
        table.add(3, max(1, int(2 + 20 * speed_ratio)))
        return table.roll()

    def get_bonus_interval(self):
        """Рассчитать интервал спавна бонусов."""
        speed_ratio = max(0.0, min(1.0, self.get_speed_ratio()))
        easing = speed_ratio**2
        interval = (
            self.base_bonus_interval
            - (self.base_bonus_interval - self.min_bonus_interval) * easing
        )
        return int(interval)

    def get_bonus_count(self):
        """Взвешенный выбор количества бонусов."""
        speed_ratio = max(0.0, min(1.0, self.get_speed_ratio()))
        table = WeightedChoiceTable(self.bonus_rng)
        table.add(1, max(10, int(85 - 40 * speed_ratio)))
        table.add(2, max(4, int(12 + 25 * speed_ratio)))
        table.add(3, max(1, int(3 + 12 * speed_ratio)))
        return table.roll()

    def handle_events(self):
        """Обработать события PyGame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        """Главный цикл обновления: физика, спавн, коллизии, логика."""
        keys = pygame.key.get_pressed()
        accelerating = keys[pygame.K_UP] or keys[pygame.K_w]
        braking = keys[pygame.K_DOWN] or keys[pygame.K_s]
        # Экспоненциальное сглаживание скорости: плавные переходы без рывков
        if accelerating:
            target_speed = self.max_speed
            self.throttle = min(1.0, self.throttle + self.throttle_up_rate)
        elif braking:
            target_speed = self.min_speed
            self.throttle = max(0.0, self.throttle - self.throttle_brake_rate)
        else:
            target_speed = self.player_speed
            self.throttle = max(0.0, self.throttle - self.throttle_coast_rate)
        # Плавное приближение к целевой скорости: коэффициент определяет «отзывчивость»
        self.player_speed += (target_speed - self.player_speed) * self.speed_smoothing
        self.player_speed = max(self.min_speed, min(self.max_speed, self.player_speed))
        # Вертикальное смещение: квадрат от throttle — мягкий старт, резкий пик
        lift_amount = self.max_lift * (self.throttle**2)
        target_y = self.player.start_y - lift_amount
        smoothing = (
            self.brake_smoothing
            if braking
            else self.lift_smoothing
            if accelerating
            else self.coast_smoothing
        )
        self.road.update(self.player_speed)
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
        # Разрешение перекрытий: предотвращает «слипание» врагов при активном дрифте
        self._resolve_enemy_overlaps()
        for bonus in list(self.bonuses):
            bonus.update(self.player_speed)
        # Коллизии: проверяем по хитбоксу, а не по полному спрайту — точнее и честнее
        collision_enemy = self.get_collision_enemy()
        if collision_enemy is not None:
            dmg = collision_enemy.compute_damage()
            self.player.health -= dmg
            if collision_enemy in self.enemies:
                self.enemies.remove(collision_enemy)
            self.spawn_floating_text(
                f"-{dmg} HP", (self.player.rect.centerx, self.player.rect.top - FLOATING_TEXT_OFFSET_HIT)
            )
            impact_x = (self.player.rect.centerx + collision_enemy.rect.centerx) // 2
            impact_y = (self.player.rect.centery + collision_enemy.rect.centery) // 2
            self.display.blit(
                self.fire_image, self.fire_image.get_rect(center=(impact_x, impact_y))
            )
            pygame.display.flip()
            pygame.time.delay(CRASH_DISPLAY_DELAY)  # Короткая пауза для визуального эффекта удара
            if self.player.health <= 0:
                self.show_crash_effect_and_pause(collision_enemy)
        collision_bonus = self.get_collision_bonus()
        if collision_bonus is not None:
            score_inc, heal = self.collect_bonus(collision_bonus)
            self.spawn_floating_text(
                f"+{heal} HP", (self.player.rect.centerx, self.player.rect.top - FLOATING_TEXT_OFFSET_HEAL)
            )
            self.spawn_floating_text(
                f"+{score_inc}", (self.player.rect.centerx, self.player.rect.top - FLOATING_TEXT_OFFSET_SCORE)
            )
        # Фильтрация ушедших за экран: используем list comprehension для чистоты
        self.enemies = [e for e in self.enemies if not e.is_off_screen()]
        self.bonuses = [b for b in self.bonuses if not b.is_off_screen()]
        # Обновление плавающих текстов: удаляем завершённые «на лету»
        for ft in list(self.floating_texts):
            ft.update()
            if ft.dead:
                self.floating_texts.remove(ft)

    def draw(self):
        """Отрисовать всё: фон -> объекты -> игрок -> UI -> плавающие тексты."""
        self.display.fill(BACKGROUND_COLOR)
        self.road.draw(self.display)
        for enemy in self.enemies:
            enemy.draw(self.display)
        for bonus in self.bonuses:
            bonus.draw(self.display)
        self.player.draw(self.display)
        self.show_score_and_speed()
        for ft in self.floating_texts:
            ft.draw(self.display, self.ui_font)
        pygame.display.flip()

    def get_collision_enemy(self):
        """Проверить столкновение с врагом по хитбоксу — точная проверка."""
        for enemy in self.enemies:
            if self.player.hitbox.colliderect(enemy.hitbox):
                return enemy
        return None

    def get_collision_bonus(self):
        """Проверить сбор бонуса: хитбокс игрока против прямоугольника бонуса."""
        for bonus in self.bonuses:
            if self.player.hitbox.colliderect(bonus.rect):
                return bonus
        return None

    def show_crash_effect_and_pause(self, crash_enemy):
        """Показать эффект аварии и ждать перезапуска."""
        impact_x = (self.player.rect.centerx + crash_enemy.rect.centerx) // 2
        impact_y = (self.player.rect.centery + crash_enemy.rect.centery) // 2
        self.display.blit(
            self.fire_image, self.fire_image.get_rect(center=(impact_x, impact_y))
        )
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
                        # Перезапуск: сбрасываем состояние, но сохраняем мастер-seed для детерминированности
                        pause = False
                        self.enemies.clear()
                        self.player.reset()
                        self.player_speed = self.start_speed
                        self.score = self.start_score
                        self.throttle = 0.0

    def check_points(self):
        """Начислить очки за обгон: когда игрок проехал выше врага."""
        for enemy in self.enemies:
            if not enemy.scored and self.player.rect.bottom < enemy.rect.top:
                self.score += 1 + self.player_speed // 10
                enemy.scored = True
        self.best_score = max(self.score, self.best_score)

    def collect_bonus(self, bonus):
        """Обработать сбор бонуса: очки + лечение с гауссовым разбросом."""
        if bonus in self.bonuses:
            self.bonuses.remove(bonus)
            score_gain = BONUS_SCORE_BASE + int(self.player_speed // 5)
            self.score += score_gain
            self.best_score = max(self.score, self.best_score)
            # Лечение: среднее, отклонение и границы берём из констант
            heal = int(round(self.bonus_rng.gauss(BONUS_HEAL_MEAN, BONUS_HEAL_STD)))
            heal = max(BONUS_HEAL_MIN, min(heal, BONUS_HEAL_MAX))
            self.player.health = min(self.player.max_health, self.player.health + heal)
            return score_gain, heal
        return 0, 0

    def _can_spawn_at(self, x, y, margin=PLAYER_SIDE_MARGIN):
        """Проверить, свободна ли зона спавна — проактивная защита от наложений."""
        spawn_rect = pygame.Rect(
            x, y, self.enemy_image.get_width(), self.enemy_image.get_height()
        )
        # Расширяем зону проверки на margin — запас безопасности для предотвращения «касаний краями»
        spawn_rect = spawn_rect.inflate(margin * 2, margin * 2)
        for enemy in self.enemies:
            # Пропускаем врагов, которые уже далеко внизу — оптимизация
            if enemy.rect.top > y + self.enemy_image.get_height() + margin:
                continue
            if spawn_rect.colliderect(enemy.rect):
                return False
        return True

    def _resolve_enemy_overlaps(self, min_gap=ENEMY_MIN_GAP):
        """
        Жёсткое разделение врагов: гарантирует минимальный зазор и убирает тряску.
        Алгоритм: если расстояние между центрами меньше допустимого — раздвигаем
        на нужную величину и обнуляем дрейф в сторону соседа (устраняет конфликт физики).
        """
        # Сортировка по Y: позволяет рано выходить из внутреннего цикла — оптимизация
        enemies_by_y = sorted(self.enemies, key=lambda e: e.rect.centery)

        for i in range(len(enemies_by_y)):
            a = enemies_by_y[i]
            for j in range(i + 1, len(enemies_by_y)):
                b = enemies_by_y[j]
                # Оптимизация: если b уже далеко ниже, пересечений не будет
                if b.rect.top > a.rect.bottom + 10:
                    break

                # Расстояние между центрами по горизонтали
                dist_x = abs(a.rect.centerx - b.rect.centerx)
                # Минимально допустимое расстояние: половина ширины обоих + зазор
                min_center_dist = (a.rect.width + b.rect.width) / 2 + min_gap

                if dist_x < min_center_dist:
                    # Сколько нужно раздвинуть
                    shift = (min_center_dist - dist_x) / 2.0

                    if a.rect.centerx < b.rect.centerx:
                        a.float_x -= shift
                        b.float_x += shift
                        # Отменяем дрейф в сторону друг друга — убираем «тряску»
                        if a.drift_target_speed > 0:
                            a.drift_target_speed = 0
                        if b.drift_target_speed < 0:
                            b.drift_target_speed = 0
                    else:
                        a.float_x += shift
                        b.float_x -= shift
                        if a.drift_target_speed < 0:
                            a.drift_target_speed = 0
                        if b.drift_target_speed > 0:
                            b.drift_target_speed = 0

                    # Привязка к границам дороги
                    a.rect.x = max(
                        self.spawn_left_bound,
                        min(
                            self.spawn_right_bound - a.rect.width, int(round(a.float_x))
                        ),
                    )
                    b.rect.x = max(
                        self.spawn_left_bound,
                        min(
                            self.spawn_right_bound - b.rect.width, int(round(b.float_x))
                        ),
                    )
                    # Синхронизируем координаты и хитбоксы
                    a.float_x = float(a.rect.x)
                    b.float_x = float(b.rect.x)
                    a._update_hitbox()
                    b._update_hitbox()

    def show_score_and_speed(self):
        """Отрисовать UI: счёт, рекорд, здоровье, скорость."""
        font = self.ui_font
        self.display.blit(font.render(f"Score: {self.score}", True, UI_TEXT_COLOR), UI_SCORE_POS)
        self.display.blit(
            font.render(f"Best score: {self.best_score}", True, UI_TEXT_COLOR),
            UI_BEST_SCORE_POS,
        )
        hb_x, hb_y, hb_w, hb_h = UI_HEALTH_BAR
        pygame.draw.rect(self.display, UI_HEALTH_BG_COLOR, (hb_x, hb_y, hb_w, hb_h))
        health_ratio = max(0.0, min(1.0, self.player.health / self.player.max_health))
        pygame.draw.rect(
            self.display,
            UI_HEALTH_COLOR,
            (hb_x + 2, hb_y + 2, int((hb_w - 4) * health_ratio), hb_h - 4),
        )
        self.display.blit(
            font.render(f"Speed: {self.player_speed * SPEED_DISPLAY_MULT:.2f}", True, UI_TEXT_COLOR),
            UI_SPEED_POS,
        )

    def run(self):
        """Запустить главный цикл: events -> update -> draw."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


def main():
    Game().run()


if __name__ == "__main__":
    main()
