import pygame


class BaseManager:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

    def handle_event(self):
        for event in pygame.event.get():
            self.process_event(event)

    def process_event(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass
