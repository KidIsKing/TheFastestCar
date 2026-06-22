import pygame

from config.constants import WHITE, ASSETS, WIDTH, BUTTON_WIDTH, BUTTON_HEIGHT


class ImageButton:
    """Интерактивная кнопка."""

    SCALE = 0.65
    FONT_SIZE = 36
    TEXT_COLOR = WHITE

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        image_path,
        hover_image_path=None,
        sound_path=None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

        self.image = self._load_and_scale_image(image_path)

        if hover_image_path:
            self.hover_image = self._load_and_scale_image(hover_image_path)
        else:
            self.hover_image = self.image  # если нет ассета для нажатой кнопки

        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

        self.font = pygame.font.Font(None, self.FONT_SIZE)

    def _load_and_scale_image(self, image_path):
        image = pygame.image.load(image_path)
        image = pygame.transform.smoothscale(
            image,
            (
                int(image.get_width() * self.SCALE),
                int(image.get_height() * self.SCALE),
            ),
        )
        return image

    def draw(self, screen):
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

        text_surface = self.font.render(self.text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.is_hovered
        ):
            if self.sound:
                self.sound.play()
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, button=self)
            )


def create_buttons(
    text, y_pos, color="green", width=BUTTON_WIDTH, height=BUTTON_HEIGHT
):
    return ImageButton(
        WIDTH // 2 - width // 2,
        y_pos,
        width,
        height,
        text,
        ASSETS[f"{color}_button"],
        ASSETS[f"{color}_button_hover"],
        ASSETS["click_sound"],
    )
