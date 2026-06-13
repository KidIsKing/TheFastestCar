import pygame
import sys
from button import ImageButton

pygame.init()

WIDTH, HEIGHT = 1664, 928
MAX_FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Button test 2")
main_background = pygame.image.load("assets/background_menu.png")
clock = pygame.time.Clock()

# # Загрузка и установка курсора
# cursor = pygame.image.load("assets/cursor.png")
# pygame.mouse.set_visible(False)  # скрываем стандартный курсор


def main_menu():
    # Создание кнопок
    start_button = ImageButton(
        WIDTH / 2 - 350/2,
        300,
        350,
        100,
        "Играть",
        "assets/green_button.png",
        "assets/green_button_hover.png",
        "assets/click.mp3",
    )
    settings_button = ImageButton(
        WIDTH / 2 - 350/2,
        400,
        350,
        100,
        "Настройки",
        "assets/green_button.png",
        "assets/green_button_hover.png",
        "assets/click.mp3",
    )
    exit_button = ImageButton(
        WIDTH / 2 - 350/2,
        500,
        350,
        100,
        "Выйти",
        "assets/red_button.png",
        "assets/red_button_hover.png",
        "assets/click.mp3",
    )

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(main_background, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("TheFastestCar. Главное меню", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 100))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT and event.button == start_button:
                fade()
                start_game()

            if event.type == pygame.USEREVENT and event.button == settings_button:
                # print("Кнопка \"Настройки\" была нажата")
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == exit_button:
                running = False
                pygame.quit()
                sys.exit()

            for btn in [start_button, settings_button, exit_button]:
                btn.handle_event(event)

        for btn in [start_button, settings_button, exit_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)

        # draw_cursor()
        pygame.display.flip()


def settings_menu():
    is_oncoming_button = ImageButton(
        WIDTH / 2 - 350/2,
        200,
        350,
        100,
        "Встречка",
        "assets/green_button.png",
        "assets/green_button_hover.png",
        "assets/click.mp3",
    )
    change_line_button = ImageButton(
        WIDTH / 2 - 350/2,
        300,
        350,
        100,
        "Левосторонка",
        "assets/green_button.png",
        "assets/green_button_hover.png",
        "assets/click.mp3",
    )
    back_button = ImageButton(
        WIDTH / 2 - 350/2,
        400,
        350,
        100,
        "Назад",
        "assets/green_button.png",
        "assets/green_button_hover.png",
        "assets/click.mp3",
    )

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(main_background, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Настройки. Выбор режимов игры", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 100))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Возврат в главное меню
                if event.key == pygame.K_ESCAPE:
                    fade()
                    running = False

            if event.type == pygame.USEREVENT and event.button == back_button:
                # print("Кнопка \"Назад\" была нажата")
                fade()
                main_menu()

            for btn in [is_oncoming_button, change_line_button, back_button]:
                btn.handle_event(event)

        for btn in [is_oncoming_button, change_line_button, back_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)

        # draw_cursor()
        pygame.display.flip()


def start_game():
    back_button = ImageButton(
        WIDTH / 2 - 350/2,
        400,
        350,
        100,
        "Назад",
        "assets/green_button.png",
        "assets/green_button_hover.png",
        "assets/click.mp3",
    )

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(main_background, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Запускаем игру...", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 100))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Возврат в главное меню
                if event.key == pygame.K_ESCAPE:
                    fade()
                    running = False

            if event.type == pygame.USEREVENT and event.button == back_button:
                fade()
                main_menu()

            for btn in [back_button]:
                btn.handle_event(event)

        for btn in [back_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)

        # draw_cursor()
        pygame.display.flip()


def fade():
    running = True
    fade_alpha = 0  # Уровень прозрачности для анимации

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Анимация затухания текущего экрана
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

        # Увеличения уровня прозрачности
        fade_alpha += 5
        if fade_alpha >= 105:
            fade_alpha = 255
            running = False

        pygame.display.flip()
        clock.tick(MAX_FPS)


# def draw_cursor():
#     # Отображение курсора в текущей позиции мыши
#     x, y = pygame.mouse.get_pos()
#     screen.blit(cursor, (x, y))


main_menu()
