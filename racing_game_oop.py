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
        self.reset()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.current_y = float(self.start_y)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= 10
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += 10

        self.rect.left = max(self.rect.left, WIDTH // 2 - 450 + 20)
        self.rect.right = min(self.rect.right, WIDTH // 2 + 450 - 20)

    def update_vertical_position(self, target_y, smoothing):
        self.current_y += (target_y - self.current_y) * smoothing
        self.rect.y = int(round(self.current_y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy:
    def __init__(self, image, x, y, speed, left_bound, right_bound, rng):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.rng = rng
        self.float_x = float(self.rect.x)
        self.drift_speed = self.rng.choice([-1, 1]) * self.rng.uniform(
            0.08,
            0.22,
        )
        self.drift_target_speed = self.drift_speed
        self.next_drift_change = (
            pygame.time.get_ticks() + self.rng.randint(1200, 2600)
        )
        self.scored = False

    def update(self, world_speed=0):
        self.rect.y += self.speed + world_speed

        now = pygame.time.get_ticks()
        if now >= self.next_drift_change:
            self.next_drift_change = now + self.rng.randint(1200, 2600)
            self.drift_target_speed = self.rng.choice([-1, 1]) * self.rng.uniform(
                0.08,
                0.28,
            )

        self.drift_speed += (self.drift_target_speed - self.drift_speed) * 0.6
        self.float_x += self.drift_speed
        self.rect.x = int(round(self.float_x))

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

    def is_off_screen(self):
        return self.rect.top > HEIGHT + self.rect.height


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
            )
        )

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

        for enemy in self.enemies:
            enemy.update(self.player_speed)

        for bonus in self.bonuses:
            bonus.update(self.player_speed)

        self.enemies = [enemy for enemy in self.enemies if not enemy.is_off_screen()]
        self.bonuses = [bonus for bonus in self.bonuses if not bonus.is_off_screen()]

    def draw(self):
        self.display.fill((0, 0, 0))
        self.road.draw(self.display)

        for enemy in self.enemies:
            enemy.draw(self.display)

        for bonus in self.bonuses:
            bonus.draw(self.display)

        self.player.draw(self.display)
        self.show_score_and_speed()
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
            self.score += 5 + int(self.player_speed // 5)
            self.best_score = max(self.score, self.best_score)

    def show_score_and_speed(self):
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        best_score_text = font.render(f"Best score: {self.best_score}", True, (255, 255, 255))
        self.display.blit(score_text, (10, 10))
        self.display.blit(best_score_text, (10, 35))

        speed_text = font.render(f"Speed: {self.player_speed * 7:.2f}", True, (255, 255, 255))
        self.display.blit(speed_text, (10, HEIGHT - 30))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            crash_enemy = self.get_collision_enemy()
            if crash_enemy is not None:
                self.show_crash_effect_and_pause(crash_enemy)

            bonus = self.get_collision_bonus()
            if bonus is not None:
                self.collect_bonus(bonus)

            self.clock.tick(FPS)

        pygame.quit()


def main():
    Game().run()


if __name__ == "__main__":
    main()
