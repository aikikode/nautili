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


class Ship(Model):
    def __init__(self, renderer, isom_x, isom_y, model='steam_corvette', player='yellow', base_armor=1, fire_range=1, max_move=1, shots_count=1, stille_move=1, storm_move=1, **kwargs):
        Model.__init__(self, renderer, isom_x, isom_y, model, player)
        self.accepted_moves = []
        self.direction = 'se'
        self.__update_image()
        self.storm_move = int(storm_move)
        self.base_armor = int(base_armor)
        self.fire_range = int(fire_range)
        self.max_move = int(max_move)
        self.shots_count = int(shots_count)
        self.stille_move = int(stille_move)

    def __update_image(self):
        self.image = pygame.image.load(
            os.path.join(MODELS_DIR, "{}_{}_{}.png".format(self.model, self.player, self.direction))).convert_alpha()

    def move(self, x, y):
        if (x, y) in self.accepted_moves:
            self.x = x
            self.y = y
            self.rect.topleft = self.renderer.isometric_to_orthogonal(self.x, self.y)
            self.accepted_moves = []
            self.__update_image()
            return True
        return False

    def calculate_shots(self, obstacles=[]):
        return self.calculate_moves(obstacles)

    def calculate_moves(self, obstacles=[]):
        moves = []
        for delta in xrange(1, self.max_move + 1):
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
    def __init__(self, renderer, isom_x, isom_y, model='port_1', player='yellow', base_armor=1, fire_range=1, shots_count=1, **kwargs):
        Model.__init__(self, renderer, isom_x, isom_y, model, player)
        self.__update_image()
        self.base_armor = int(base_armor)
        self.fire_range = int(fire_range)
        self.shots_count = int(shots_count)

    def __update_image(self):
        self.image = pygame.image.load(
            os.path.join(MODELS_DIR, "{}_{}.png".format(self.model, self.player))).convert_alpha()
