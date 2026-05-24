import pygame
import random


WIDTH, HEIGHT = 1280, 720
FPS = 60

ASSETS_PATH = "assets/"
ASSETS = {
    "road": ASSETS_PATH + "road_background.png",
    "player": ASSETS_PATH + "car_player.png",
    "enemy": ASSETS_PATH + "enemy_player.png",
    "fire": ASSETS_PATH + "fire.png",
}


class Player:
    def __init__(self):
        image = pygame.image.load(ASSETS["player"])
        image = pygame.transform.rotate(image, 90)
        image = pygame.transform.smoothscale(image, (int(image.get_width() * 0.3), int(image.get_width() * 0.5)))

        self.image = image
        self.rect = self.image.get_rect()
        self.start_x = WIDTH // 2 - 90
        self.start_y = HEIGHT - self.rect.height - 20
        self.reset()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= 10
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += 10

        self.rect.left = max(self.rect.left, WIDTH // 2 - 450 + 20)
        self.rect.right = min(self.rect.right, WIDTH // 2 + 450 - 20)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, HEIGHT)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy:
    def __init__(self, image, x, y, speed):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def update(self, world_speed=0):
        self.rect.y += self.speed + world_speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

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
        self.running = True
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = 2000
        self.player_speed = 2
        self.start_speed = self.player_speed
        self.max_speed = 30
        self.min_speed = 2
        self.acceleration = 0.01  # нажатие W прибавляет это значение
        self.deceleration = 1  # нажатие S убирает это значение
        self.enemy_speed = 5

    def spawn_enemy(self):
        min_x = WIDTH // 2 - self.road.image.get_width() // 2 + self.player.rect.width + 140
        max_x = WIDTH // 2 + self.road.image.get_width() // 2 - self.player.rect.width - 220
        x = random.randint(min_x, max_x)
        y = -self.enemy_image.get_height()
        self.enemies.append(Enemy(self.enemy_image, x, y, self.enemy_speed))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_speed = min(self.player_speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_speed = max(self.player_speed - self.deceleration, self.min_speed)

        self.road.update(self.player_speed)

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval:
            self.spawn_enemy()
            self.last_spawn_time = now

        for enemy in self.enemies:
            enemy.update(self.player_speed)

        self.enemies = [enemy for enemy in self.enemies if not enemy.is_off_screen()]

    def draw(self):
        self.display.fill((0, 0, 0))
        self.road.draw(self.display)

        for enemy in self.enemies:
            enemy.draw(self.display)

        self.player.draw(self.display)
        pygame.display.flip()

    def get_collision_enemy(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                return enemy
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

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            crash_enemy = self.get_collision_enemy()
            if crash_enemy is not None:
                self.show_crash_effect_and_pause(crash_enemy)

            self.clock.tick(FPS)

        pygame.quit()


def main():
    Game().run()


if __name__ == "__main__":
    main()
