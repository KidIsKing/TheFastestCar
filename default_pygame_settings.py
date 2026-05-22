import pygame


pygame.init()

WIDTH, HEIGHT = 1280, 720

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
