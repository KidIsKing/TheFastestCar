import pygame
import sys
from button import ImageButton

pygame.init()

WIDTH, HEIGHT = 600, 550

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Button test")


green_button = ImageButton(
    WIDTH/2-(500/2),
    -150,
    500,
    740,
    "",
    "assets/green_button.png",
    "assets/green_button_hover.png",
    "assets/click.mp3")


def main_menu():
    running = True
    while running:
        screen.fill((0, 0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("BUTTON TEST", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(300, 50))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT and event.button == green_button:
                print("Кнопка была нажата")

            green_button.handle_event(event)

        # Для реагирования кнопки на наведение мыши
        green_button.check_hover(pygame.mouse.get_pos())
        green_button.draw(screen)
        pygame.display.flip()


main_menu()
