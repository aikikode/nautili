#!/usr/bin/env python

__author__ = 'aikikode'

import pygame


class Ship(pygame.sprite.Sprite):
    def __init__(self, renderer, x, y, type=None, player=None):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.type = type
        self.player = player
        self.renderer = renderer
        self.image = pygame.image.load("./tilesets/test_player.png").convert_alpha()
        self.rect = pygame.Rect(*(renderer.isometric_to_orthogonal(x, y) + (64, 64)))

    def coords(self):
        return self.x, self.y

    def __repr__(self):
        return "{}({}, {}): {}, {}".format(self.__class__.__name__, self.x, self.y, self.type, self.player)

    def draw(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))

    def move(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        self.rect.topleft = self.renderer.isometric_to_orthogonal(self.x, self.y)
