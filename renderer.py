#!/usr/bin/env python
import pygame

__author__ = 'aikikode'


class Renderer(object):
    def __init__(self, layers_handler, screen):
        self.layers_handler = layers_handler
        self.screen = screen
        self.__textures = []

    def add(self, obj_list):
        l = obj_list
        while 1:
            try:
                l = sum(l, [])
            except TypeError:
                break
        for obj in l:
            if obj:
                self.__textures.append(obj)

    def clear(self):
        self.__textures = []

    def fill(self, color):
        self.screen.fill(color)

    def draw(self):
        for obj in self.__textures:
            self.screen.blit(obj.tile, self.layers_handler.isometric_to_orthogonal(obj.x, obj.y))
