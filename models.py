#!/usr/bin/env python
import os
import pygame
import numpy as np
import math
import wind

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
        self.possible_moves = []
        self.possible_shots = []
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
        if (x, y) in self.possible_moves:
            self.x = x
            self.y = y
            self.rect.topleft = self.renderer.isometric_to_orthogonal(self.x, self.y)
            self.possible_moves = []
            self.__update_image()
            return True
        return False


    def calculate_shots(self, obstacles=[]):
        self.possible_shots = self.calculate_area(self.fire_range, obstacles)
        return self.possible_shots

    def calculate_moves(self, wind_type, wind_direction, obstacles=[]):
        def rotate(axis, obj):
            """
            Rotate object with obj coords around the axis, getting closer and closer to the axis with each step
            """
            res = [obj]
            arr = []
            for x in xrange(1, 8):
                arr.append((x, self.max_move - (8 - x if x > 4 else x) + 1))
            sector = (math.atan2(*map(lambda x, y: x - y, obj, axis)[::-1]) / math.pi * 4) % 8
            arr = map(lambda x: ((x[0] + sector) % 8, x[1] if x[1] > 0 else 1), arr)
            for el in arr:
                if el[0] == 0:
                    res.append((axis[0] + el[1], axis[1]))
                elif el[0] == 1:
                    res.append((axis[0] + el[1], axis[1] + el[1]))
                elif el[0] == 2:
                    res.append((axis[0], axis[1] + el[1]))
                elif el[0] == 3:
                    res.append((axis[0] - el[1], axis[1] + el[1]))
                elif el[0] == 4:
                    res.append((axis[0] - el[1], axis[1]))
                elif el[0] == 5:
                    res.append((axis[0] - el[1], axis[1] - el[1]))
                elif el[0] == 6:
                    res.append((axis[0], axis[1] - el[1]))
                elif el[0] == 7:
                    res.append((axis[0] + el[1], axis[1] - el[1]))
            return res
        # Handle wind as a number of obstacles
        max_move = self.max_move
        if wind_type == wind.STILLE:
            max_move = self.stille_move
        #elif wind_type == wind.WIND:
        else:
            delta = self.max_move + 1
            if wind_direction == wind.NORTH:
                obstacles += rotate(self.coords(), (self.x - delta, self.y - delta))
            if wind_direction == wind.EAST:
                obstacles += rotate(self.coords(), (self.x + delta, self.y - delta))
            if wind_direction == wind.SOUTH:
                obstacles += rotate(self.coords(), (self.x + delta, self.y + delta))
            if wind_direction == wind.WEST:
                obstacles += rotate(self.coords(), (self.x - delta, self.y + delta))
            if wind_direction == wind.NORTH_EAST:
                obstacles += rotate(self.coords(), (self.x, self.y - delta))
            if wind_direction == wind.NORTH_WEST:
                obstacles += rotate(self.coords(), (self.x - delta, self.y))
            if wind_direction == wind.SOUTH_EAST:
                obstacles += rotate(self.coords(), (self.x + delta, self.y))
            if wind_direction == wind.SOUTH_WEST:
                obstacles += rotate(self.coords(), (self.x, self.y + delta))
        self.possible_moves = self.calculate_area(max_move, obstacles)
        return self.possible_moves

    def calculate_area(self, limit, obstacles):
        moves = []
        for delta in xrange(1, limit + 1):
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
                        while abs(stepx) + abs(stepy) <= 2*(limit + 1):
                            moves.remove((movex + stepx, movey + stepy))
                            stepx += np.sign(stepx)
                            stepy += np.sign(stepy)
                    except:
                        pass
            except:
                pass
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
