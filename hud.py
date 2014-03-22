#!/usr/bin/env python
"""
Base HUD elements: buttons, labels, etc.
"""
__author__ = 'aikikode'


class Button(object):
    def __init__(self, screen, font, text, pos, on_click=None):
        self.hovered = False
        self.screen = screen
        self.font = font
        self.text = text
        self.pos = pos
        self.rect = None
        self.set_rect()
        self.on_click = on_click
        self.__enabled = True

    def draw(self):
        self.set_rend()
        self.screen.blit(self.rend, self.rect)

    def set_rend(self):
        self.rend = self.font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 100, 100)

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos

    def mouseover(self, mouse_position):
        if self.__enabled:
            self.hovered = self.rect.collidepoint(mouse_position)

    def check_click(self, mouse_position):
        if self.__enabled and self.on_click and self.rect.collidepoint(mouse_position):
            self.on_click()

    def disable(self):
        self.__enabled = False
        self.hovered = False

    def enable(self):
        self.__enabled = True
        self.hovered = True
