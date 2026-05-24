import pygame
import random


WIDTH, HEIGHT = 1280, 720

ASSETS_PATH = "assets/"
ASSETS = {
    "road": ASSETS_PATH + "road_background.png",
    "player": ASSETS_PATH + "car_player.png",
    "enemy": ASSETS_PATH + "enemy_player.png",
    "fire": ASSETS_PATH + "fire.png"
}

road_img = pygame.image.load(ASSETS["road"])
road_img = pygame.transform.smoothscale(road_img, ((WIDTH // 2) + 450, HEIGHT))

road_y1 = 0
road_y2 = road_img.get_height()
ROAD_SCROLL_SPEED = 5

player_img = pygame.image.load(ASSETS["player"])
player_img = pygame.transform.rotate(player_img, 90)
player_ratio = player_img.get_width() / player_img.get_height()
player_img = pygame.transform.smoothscale(player_img, (player_img.get_width() * 0.3, player_img.get_width() * 0.5))

PLAYER_START_X = WIDTH // 2 - 90
PLAYER_START_Y = HEIGHT - player_img.get_height() - 20

player_pos_x = PLAYER_START_X
player_pos_y = PLAYER_START_Y

player_rect = player_img.get_rect()

ENEMIES_SPAWN_INTERVAL = 1000
ENEMY_SPEED = 5
last_spawn_time = pygame.time.get_ticks()

enemy_img = pygame.image.load(ASSETS["enemy"])
enemy_img = pygame.transform.smoothscale(enemy_img, (enemy_img.get_width() * 0.15, enemy_img.get_width() * 0.25))

enemies = []

fire_img = pygame.image.load(ASSETS["fire"])
fire_img = pygame.transform.smoothscale(fire_img, (fire_img.get_width() * 0.5, fire_img.get_width() * 0.5))


pygame.init()

display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TheFastestCar")
clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if event.type == pygame.KEYDOWN:
        if event.type == pygame.K_ESCAPE:
            running = False

    now = pygame.time.get_ticks()

    display.fill((0, 0, 0))

    # Прокрутка дороги
    road_y1 += ROAD_SCROLL_SPEED
    road_y2 += ROAD_SCROLL_SPEED
    if road_y1 >= HEIGHT:
        road_y1 = road_y2 - road_img.get_height()
    if road_y2 >= HEIGHT:
        road_y2 = road_y1 - road_img.get_height()

    display.blit(road_img, (WIDTH // 2 - road_img.get_width() // 2, road_y1))
    display.blit(road_img, (WIDTH // 2 - road_img.get_width() // 2, road_y2))

    # Перемещение игрока на стрелочки и WASD
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_pos_x -= 10
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_pos_x += 10
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_pos_y -= 5
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_pos_y += 5

    player_rect = player_img.get_rect(x=player_pos_x, y=player_pos_y)
    pygame.draw.rect(display, (0, 255, 0), player_rect, 4)
    display.blit(player_img, (player_pos_x, player_pos_y))

    now = pygame.time.get_ticks()
    if now - last_spawn_time >= ENEMIES_SPAWN_INTERVAL:
        # Появление нового врага в случайной позиции по x экрана
        enemy_rect = enemy_img.get_rect(topleft=(WIDTH // 2, -enemy_img.get_height()))
        enemy_rect.x = random.randint(
            WIDTH // 2 - road_img.get_width() // 2 + player_img.get_width(),
            WIDTH // 2 + road_img.get_width() // 2 - player_img.get_width()
        )
        enemies.append(enemy_rect)
        last_spawn_time = now

    for enemy in enemies:
        enemy.y += ENEMY_SPEED
    enemies = [enemy for enemy in enemies if enemy.y < HEIGHT + enemy_img.get_height()]

    for enemy in enemies:
        pygame.draw.rect(display, (255, 0, 0), enemy, 4)
        display.blit(enemy_img, enemy)

    # Детекция столкновения
    crash_into = None
    for enemy in enemies:
        if player_rect.colliderect(enemy):
            crash_into = enemy
            break

    if crash_into:
        impact_x = (player_rect.centerx + crash_into.centerx) // 2
        impact_y = (player_rect.centery + crash_into.centery) // 2
        display.blit(fire_img, fire_img.get_rect(center=(impact_x, impact_y)))
        pygame.display.flip()

        pause = True
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pause = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pause = False

                    if event.key == pygame.K_SPACE:
                        pause = False

                    enemies = []
                    player_pos_x = PLAYER_START_X
                    player_pos_y = PLAYER_START_Y

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
