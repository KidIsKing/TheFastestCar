import pygame
from constants import WIDTH, HEIGHT
from menu_manager import MenuManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TheFastestCar")

    app = MenuManager(screen)
    app.run()


if __name__ == "__main__":
    main()
