#!/usr/bin/env python
import pygame
import random
from layers import LayersHandler

__author__ = 'aikikode'

RED = (255, 0, 0)

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        self._textures = []

    def add(self, obj_list):
        for obj in LayersHandler.flatten(obj_list):
            if obj:
                self._textures.append(obj)

    def clear(self):
        self._textures = []

    def update(self, obj_list=[]):
        self.clear()
        if obj_list:
            self.add(obj_list)
        self.draw()

    def fill(self, color):
        self.screen.fill(color)

    def draw(self):
        for obj in self._textures:
            self.screen.blit(obj.tile, (obj.x, obj.y))


class IsometricRenderer(Renderer):
    def __init__(self, layers_handler, screen):
        Renderer.__init__(self, screen)
        self.layers_handler = layers_handler
        self._lines = []

    def clear(self):
        Renderer.clear(self)
        self._lines = []

    def add_line(self, (x0, y0), (x1, y1)):
        (x0, y0) = (x0 + 32, y0 + 32)
        (x1, y1) = (x1 + 32, y1 + 32)
        noise = 20 * random.random() - 10
        self._lines.append(((x0 + noise, y0 + noise), (x1, y1)))

    def draw_lines(self):
        for line in self._lines:
            pygame.draw.line(self.screen, RED, [line[0][0], line[0][1]], [line[1][0], line[1][1]], 2)

    def draw(self):
        for obj in self._textures:
            self.screen.blit(obj.tile, self.layers_handler.isometric_to_orthogonal(obj.x, obj.y))
        self.draw_lines()
