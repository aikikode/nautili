#!/usr/bin/env python
"""
Ships, ports, etc.
"""
from collections import Counter
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
        self._update_image()
        self.storm_move = int(storm_move)
        self._storm_moves_left = self.storm_move
        self._has_moved = False
        self.base_armor = int(base_armor)
        self.armor = self.base_armor
        self.fire_range = int(fire_range)
        self.max_move = int(max_move)
        self.shots_count = int(shots_count)
        self.stille_move = int(stille_move)
        self._shots_left = self.shots_count
        self._targets = []
        self._is_alive = True

    def _update_image(self):
        self.image = pygame.image.load(
            os.path.join(MODELS_DIR, "{}_{}_{}.png".format(self.model, self.player, self.direction))).convert_alpha()

    def reset(self):
        self._storm_moves_left = self.storm_move
        self._has_moved = False
        self._shots_left = self.shots_count
        self._targets = []

    def move(self, (x, y)=(None, None)):
        if self._has_moved:
            return False
        if (x, y) in self.possible_moves:
            self.x = x
            self.y = y
            self._has_moved = True
        elif (x, y) == (None, None) and len(self.possible_moves) == 1: # storm step
            coords = self.possible_moves[0]
            if coords:
                self.x, self.y = coords
            else:
                return False
        else:
            return False
        self.rect.topleft = self.renderer.isometric_to_orthogonal(self.x, self.y)
        self.possible_moves = []
        self._update_image()
        self.aim_reset()
        return True

    def calculate_shots(self, obstacles=[]):
        self.possible_shots = self.calculate_area(self.fire_range, obstacles)
        return self.possible_shots

    def calculate_moves(self, wind_type, wind_direction, obstacles=[], max=None):
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
        if self._has_moved or wind_type not in [wind.STILLE, wind.WIND, wind.STORM]:
            return []
        # Handle wind as a number of obstacles
        max_move = self.max_move
        if wind_type == wind.STORM:
            if max:
                max_move = max if max else self.storm_move
            cur = []
            for delta in xrange(1, max_move + 1):
                if wind_direction == wind.NORTH:
                    next = (self.x - delta, self.y - delta)
                if wind_direction == wind.EAST:
                    next = (self.x + delta, self.y - delta)
                if wind_direction == wind.SOUTH:
                    next = (self.x + delta, self.y + delta)
                if wind_direction == wind.WEST:
                    next = (self.x - delta, self.y + delta)
                if wind_direction == wind.NORTH_EAST:
                    next = (self.x, self.y - delta)
                if wind_direction == wind.NORTH_WEST:
                    next = (self.x - delta, self.y)
                if wind_direction == wind.SOUTH_EAST:
                    next = (self.x + delta, self.y)
                if wind_direction == wind.SOUTH_WEST:
                    next = (self.x, self.y + delta)
                if next in obstacles:
                    break
                else:
                    self._storm_moves_left -= delta
                    if self._storm_moves_left >= 0:
                        cur = [next]
            self.possible_moves = cur
        else:
            if wind_type == wind.STILLE:
                max_move = self.stille_move
            elif wind_type == wind.WIND:
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

    def aim_reset(self):
        for target in self._targets:
            self._shots_left += 1
        self._targets = []

    def aim(self, target):
        if self._shots_left < 0 or target.coords() not in self.possible_shots:
            return False
        if self._shots_left == 0:
            if self._targets:
                self._targets.pop(0)
                self._shots_left += 1
            else:
                return False
        self._targets.append(target)
        self._shots_left -= 1
        #print "{} aimed at {}".format(self, target)
        return True

    def shoot(self, hit=True):
        if hit:
            c = Counter(self._targets)
            for target, shot_count in c.items():
                print "{} shot at {} {} time(s)".format(self, target, shot_count)
                target.take_damage(shot_count)
        elif self._targets:
            print "{} missed".format(self)
        self._targets = []

    def get_targets(self):
        return self._targets

    def take_damage(self, damage):
        self.armor -= damage
        if self.armor <= 0:
            #print "{} is down".format(self)
            self._is_alive = False

    def is_alive(self):
        return self._is_alive


class Port(Model):
    def __init__(self, renderer, isom_x, isom_y, model='port_1', player='yellow', base_armor=1, fire_range=1, shots_count=1, **kwargs):
        Model.__init__(self, renderer, isom_x, isom_y, model, player)
        self._update_image()
        self.base_armor = int(base_armor)
        self.fire_range = int(fire_range)
        self.shots_count = int(shots_count)

    def _update_image(self):
        self.image = pygame.image.load(
            os.path.join(MODELS_DIR, "{}_{}.png".format(self.model, self.player))).convert_alpha()
