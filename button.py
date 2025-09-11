import pygame
from config import *

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = WHITE
        self.text_color = WHITE
        self.clicked = False

    def draw_start(self, screen):
        # mouse hover detection
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.color, self.rect, border_radius= 5)
            self.text_color = BLACK
        else:
            pygame.draw.rect(screen, self.color, self.rect, 3, border_radius= 5 )
            self.text_color = WHITE

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))
