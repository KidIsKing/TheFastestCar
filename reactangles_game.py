import pygame
import random


WIDTH, HEIGHT = 1280, 720
WIDTH_FOR_SPAWN = WIDTH - 50

PLAYER_WIDTH = 100
PLAYER_HEIGHT = 120
PLAYER_START_X = WIDTH // 2
PLAYER_START_Y = HEIGHT - PLAYER_HEIGHT

player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

enemies = []
last_spawn = pygame.time.get_ticks()
SPAWN_INTERVAL = 1000
ENEMY_SPEED = 5


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

    # Перемещение игрока на стрелочки и WASD
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_rect.x -= 10
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_rect.x += 10
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_rect.y -= 10
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_rect.y += 10

    # Ограничение игрока в пределах экрана
    if player_rect.x > WIDTH:
        player_rect.x = 0
    if player_rect.x < 0:
        player_rect.x = WIDTH - PLAYER_WIDTH
    if player_rect.y > HEIGHT:
        player_rect.y = 0
    if player_rect.y < 0:
        player_rect.y = HEIGHT - PLAYER_HEIGHT

    pygame.draw.rect(display, (0, 255, 0), player_rect)

    if now - last_spawn >= SPAWN_INTERVAL:
        # Появление нового врага в случайной позиции по x экрана,
        # на высоте равной высоте игрока сверху и с шириной и длиной игрока
        enemy = pygame.Rect(random.randint(50, WIDTH_FOR_SPAWN), -PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        enemies.append(enemy)
        last_spawn = now

    for enemy in enemies:
        enemy.y += ENEMY_SPEED
        pygame.draw.rect(display, (255, 0, 0), enemy)

    # Детекция столкновения
    collide_with = None
    for enemy in enemies:
        if player_rect.colliderect(enemy):
            collide_with = enemy
            break

    if collide_with:
        collision_x = (player_rect.centerx + collide_with.centerx) // 2
        collision_y = (player_rect.centery + collide_with.centery) // 2
        pygame.draw.circle(display, (255, 255, 0), (collision_x, collision_y), 18)
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
                    player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
