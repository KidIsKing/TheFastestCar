import pygame
from core.menu_manager import MenuManager
from config.constants import ASSETS, WIDTH, HEIGHT


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    icon = pygame.image.load(ASSETS["icon"])
    pygame.display.set_icon(icon)
    pygame.display.set_caption("TheFastestCar")

    app = MenuManager(screen)
    app.run()


if __name__ == "__main__":
    main()
