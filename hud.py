#!/usr/bin/env python
"""
Base HUD elements: buttons, labels, etc.
"""
__author__ = 'aikikode'


class HudElement(object):
    def __init__(self, screen, pos):
        self.screen = screen
        self.pos = pos

    def draw(self):
        pass

    def mouseover(self, mouse_position):
        pass

    def check_click(self, mouse_position):
        pass


class Button(HudElement):
    def __init__(self, screen, font, text, pos, on_click=None):
        HudElement.__init__(self, screen, pos)
        self.hovered = False
        self.font = font
        self.text = text
        self.rect = None
        self.rend = None
        self.__enabled = True
        self.on_click = on_click
        self.set_rect()

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


class Label(HudElement):
    def __init__(self, screen, font, color, text, pos):
        HudElement.__init__(self, screen, pos)
        self.color = color
        self.font = font
        self.text = text
        self.rect = None
        self.rend = None
        self.set_rect()

    def draw(self):
        self.set_rend()
        self.screen.blit(self.rend, self.rect)

    def set_rend(self):
        self.rend = self.font.render(self.text, True, self.color)

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos
