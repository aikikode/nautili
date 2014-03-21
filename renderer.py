#!/usr/bin/env python
from layers import LayersHandler

__author__ = 'aikikode'


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

    def draw(self):
        for obj in self._textures:
            self.screen.blit(obj.tile, self.layers_handler.isometric_to_orthogonal(obj.x, obj.y))
