#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base HUD elements: buttons, labels, etc.
"""

import pygame

from nautili import colors


class HudElement(pygame.sprite.Sprite):
    def __init__(self, pos, offset):
        pygame.sprite.Sprite.__init__(self)
        self.pos = map(lambda x, y: x + y, pos, offset)

    def draw(self):
        pass

    def mouse_over(self, mouse_position):
        pass

    def check_click(self, mouse_position):
        pass


class Button(HudElement):
    def __init__(self, font, text, pos, colors=(colors.GREY, colors.WHITE), offset=(0, 0), on_click=None, args=[]):
        HudElement.__init__(self, pos, offset)
        self.hovered = False
        self.font = font
        self.text = text
        self.rect = None
        self.image = None
        self.__enabled = True
        self.on_click = on_click
        self.args = args
        self.color = colors[0]
        self.hovered_color = colors[1]
        self.set_text(text)

    def update(self):
        self.set_text(self.text)

    def set_text(self, text):
        self.text = text
        image = self.font.render(text, True, self.get_color())
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def get_color(self):
        if self.hovered:
            return self.hovered_color
        else:
            return self.color

    def mouse_over(self, mouse_position):
        if self.__enabled:
            self.hovered = self.rect.collidepoint(mouse_position)

    def check_click(self, mouse_position):
        if self.__enabled and self.on_click and self.rect.collidepoint(mouse_position):
            self.on_click(*self.args)

    def disable(self):
        self.__enabled = False
        self.hovered = False

    def enable(self):
        self.__enabled = True
        self.hovered = True

    def enabled(self):
        return self.__enabled


class Label(HudElement):
    def __init__(self, font, color, text, pos, offset=(0, 0)):
        HudElement.__init__(self, pos, offset)
        self.color = color
        self.font = font
        self.text = text
        self.rect = None
        self.image = None
        self.set_text(text)

    def set_text(self, text, color=None):
        self.text = text
        if color:
            self.color = color
        image = self.font.render(text, True, self.color)
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def center(self, width):
        """
        Center the label inside the width panel
        """
        text_width = self.font.size(self.text)[0]
        self.rect.topleft = (self.pos[0] + (width - text_width) / 2, self.pos[1])
