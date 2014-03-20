#!/usr/bin/env python
import os
import pygame
import numpy as np

__author__ = 'aikikode'

MODELS_DIR = os.path.join("tilesets", "models")


class Model(pygame.sprite.Sprite):
    def __init__(self, renderer, x, y, model=None, player=None, *args):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.model = model
        self.player = player
        self.renderer = renderer
        self.image = pygame.image.load("./tilesets/test_player.png").convert_alpha()
        self.rect = pygame.Rect(*(renderer.isometric_to_orthogonal(x, y) + (64, 64)))

    def coords(self):
        return self.x, self.y

    def __repr__(self):
        return "{}({}, {}): {}, {}".format(self.__class__.__name__, self.x, self.y, self.model, self.player)

    def draw(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))


class Ship(Model):
    def __init__(self, renderer, isom_x, isom_y, model='steam_corvette', player='yellow', **kwargs):
        Model.__init__(self, renderer, isom_x, isom_y, model, player)
        self.max_move = 3
        self.accepted_moves = []
        self.direction = 'se'
        self.__set_image()

    def __set_image(self):
        self.image = pygame.image.load(
            os.path.join(MODELS_DIR, "{}_{}_{}.png".format(self.model, self.player, self.direction))).convert_alpha()

    def move(self, x, y):
        if (x, y) in self.accepted_moves:
            self.x = x
            self.y = y
            self.rect.topleft = self.renderer.isometric_to_orthogonal(self.x, self.y)
            self.accepted_moves = []
            return True
        return False

    def calculate_moves(self, obstacles=[]):
        moves = []
        for delta in xrange(1, self.max_move):
            moves.append((self.x, self.y + delta))
            moves.append((self.x, self.y - delta))
            moves.append((self.x + delta, self.y))
            moves.append((self.x + delta, self.y + delta))
            moves.append((self.x + delta, self.y - delta))
            moves.append((self.x - delta, self.y))
            moves.append((self.x - delta, self.y + delta))
            moves.append((self.x - delta, self.y - delta))
        for move in moves[:]:
            movex, movey = move
            try:
                if movex < 0 or \
                                movey < 0 or \
                                move in obstacles:
                    deltax = movex - self.x
                    stepx = deltax / abs(deltax) if deltax else 0
                    deltay = movey - self.y
                    stepy = deltay / abs(deltay) if deltay else 0
                    if (movex, movey) in moves: moves.remove((movex, movey))
                    try:
                        while abs(stepx) + abs(stepy) <= 2 * self.max_move:
                            moves.remove((movex + stepx, movey + stepy))
                            stepx += np.sign(stepx)
                            stepy += np.sign(stepy)
                    except:
                        pass
            except:
                pass
        self.accepted_moves = moves
        return moves


class Port(Model):
    def __init__(self, renderer, isom_x, isom_y, model=None, player=None):
        Model.__init__(self, renderer, isom_x, isom_y, model, player)

