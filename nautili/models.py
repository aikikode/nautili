#!/usr/bin/env python
"""
Ships, ports, etc.
"""
from collections import Counter
import os
import pygame
import numpy as np
import math
from PIL import Image
from nautili import wind, settings

__author__ = 'aikikode'


def clear_image(image):
    p = image.load()
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            p[x, y] = (0, 0, 0, 0)


class Model(pygame.sprite.Sprite):
    def __init__(self, layers_handler, x, y, model=None, player=None, base_armor=1, fire_range=1, shots_count=1,
                 **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.model = model
        self.player = player
        self.layers_handler = layers_handler
        self.image = None
        self.rect = pygame.Rect(*(layers_handler.isometric_to_orthogonal(x, y) + (64, 64)))
        self.possible_shots = []
        self._update_image()
        self.base_armor = int(base_armor)
        self.armor = self.base_armor
        self.fire_range = int(fire_range)
        self.shots_count = int(shots_count)
        self.shots_left = self.shots_count
        self.aimed_count = 0  # number of cannons aimed at this ship
        self._targets = []
        self._is_alive = True
        self._has_shot = False
        self.offset = (0, 0)
        self.health_bar = HealthBar(self)
        self.cannon_bar = CannonBar(self)
        self.target_bar = TargetBar(self)

    def get_data(self):
        return self.model, self.player, self.x, self.y, \
               self.base_armor, self.fire_range, self.shots_count, \
               self.armor, self._has_shot, self.shots_left

    @classmethod
    def from_data(cls, layers_handler, data):
        model, player, x, y, base_armor, fire_range, shots_count, armor, has_shot, shots_left = data
        model = cls(layers_handler, x, y, model=model, player=player,
                    base_armor=base_armor, fire_range=fire_range, shots_count=shots_count)
        model.armor = armor
        model._has_shot = has_shot
        model.shots_left = shots_left
        model.health_bar = HealthBar(model)
        model.cannon_bar = CannonBar(model)
        return model

    def coords(self):
        return self.x, self.y

    def __repr__(self):
        return "{}({}, {}): {}, {}".format(self.__class__.__name__, self.x, self.y, self.model, self.player)

    def select(self):
        self._update_image("selected")

    def unselect(self):
        self._update_image()

    def set_aimed(self):
        self.aimed_count += 1
        self.target_bar.draw()
        self._update_image("aimed")

    def unset_aimed(self, count=1):
        self.aimed_count -= count
        self.target_bar.draw()
        if self.aimed_count <= 0:
            self.aimed_count = 0
            self._update_image()

    def _update_image(self, img_type=""):
        if img_type:
            img_type = "_{}".format(img_type)
        self.image = pygame.image.load(
            os.path.join(settings.MODELS_DIR, "{}_{}{}.png".format(self.model, self.player, img_type))).convert_alpha()

    def reset(self):
        self.aimed_count = 0
        self.shots_left = self.shots_count
        self._targets = []
        self.health_bar.draw()
        self.cannon_bar.draw()
        self.target_bar.draw()
        self._has_shot = False

    def calculate_shots(self, obstacles=[]):
        self.possible_shots = self.calculate_area(self.fire_range, obstacles)
        return self.possible_shots

    def calculate_area(self, limit, obstacles):
        moves = []  # moves are just example, we use it to calculate all types of actions: moves, shots, etc.
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
                        while abs(stepx) + abs(stepy) <= 2 * (limit + 1):
                            moves.remove((movex + stepx, movey + stepy))
                            stepx += np.sign(stepx)
                            stepy += np.sign(stepy)
                    except:
                        pass
            except:
                pass
        return moves

    def has_targets(self):
        return self._targets != []

    def aim_reset(self):
        for target in self._targets:
            target.unset_aimed()
            self.shots_left += 1
        self._targets = []
        self.cannon_bar.draw()
        self.target_bar.draw()

    def aim(self, target):
        if not self.is_alive() or self.shots_left < 0 or target.coords() not in self.possible_shots:
            return False
        if self.shots_left == 0:
            if self._targets and target in self._targets:
                c = Counter(self._targets)
                self.shots_left += c[target]
                self._targets = filter(lambda t: t != target, self._targets)
                target.unset_aimed(c[target])
                self.cannon_bar.draw()
            return False
        target.set_aimed()
        self._targets.append(target)
        self.shots_left -= 1
        self.cannon_bar.draw()
        return True

    def shoot(self, hit=True):
        if self._targets:
            c = Counter(self._targets)
            for target, shot_count in c.items():
                if hit:
                    target.take_damage(shot_count)
                target.unset_aimed(shot_count)
        self._targets = []
        self.cannon_bar.draw()
        self._has_shot = True

    def get_targets(self):
        return self._targets

    def take_damage(self, damage):
        self.armor -= damage
        if self.armor <= 0:
            self.armor = 0
            self._is_alive = False
        self.health_bar.draw()
        self.cannon_bar.draw()

    def is_alive(self):
        return self._is_alive

    def repair(self, amount=1):
        if self.armor < self.base_armor:
            self.armor += amount
        if self.armor >= self.base_armor:
            self.armor = self.base_armor
            self._is_alive = True


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, model):
        pygame.sprite.Sprite.__init__(self)
        self.model = model
        self.damage_image = Image.open(os.path.join(settings.MODELS_DIR, "health_bar_cell_red.png"))
        if self.model.player == settings.PLAYER1:
            self.health_image = Image.open(os.path.join(settings.MODELS_DIR, "health_bar_cell_yellow.png"))
        elif self.model.player == settings.PLAYER2:
            self.health_image = Image.open(os.path.join(settings.MODELS_DIR, "health_bar_cell_green.png"))
        else:
            self.health_image = Image.open(os.path.join(settings.MODELS_DIR, "health_bar_cell_neutral.png"))
        self._cell_width, self._cell_height = self.damage_image.size
        self.image = None
        self.bar_width = 0
        self._delta = 0
        if not os.path.exists(settings.TMP_DIR):
            os.makedirs(settings.TMP_DIR)
        self.rect = None
        self.draw()

    def draw(self):
        out_fname = os.path.join(settings.TMP_DIR,
                                 "{}_health_{}_damage_{}.png".format(self.model.player,
                                                                     self.model.armor,
                                                                     self.model.base_armor - self.model.armor))
        if not os.path.exists(out_fname):
            blank_image = Image.new("RGBA", (64, self._cell_height), None)
            clear_image(blank_image)
            for x in xrange(self.model.armor):
                blank_image.paste(self.health_image, (self._cell_width * x, 0), self.health_image)
            for x in xrange(self.model.armor, self.model.base_armor):
                blank_image.paste(self.damage_image, (self._cell_width * x, 0), self.damage_image)
            blank_image.save(out_fname)
        self.image = pygame.image.load(out_fname).convert_alpha()
        tile_width = 64  # TODO: remove hardcode value
        self.bar_width = self._cell_width * self.model.base_armor
        self._delta = (tile_width - self.bar_width) / 2
        self.move()

    def move(self):
        x, y = self.model.rect.topleft
        x, y = x + self._delta, y - 5
        self.rect = pygame.Rect(x, y, self.bar_width, self._cell_height)


class CannonBar(pygame.sprite.Sprite):
    def __init__(self, model):
        pygame.sprite.Sprite.__init__(self)
        self.model = model
        self.empty_image = Image.open(os.path.join(settings.MODELS_DIR, "cannon_bar_cell_empty.png"))
        self.cannon_image = Image.open(os.path.join(settings.MODELS_DIR, "cannon_bar_cell.png"))
        self._cell_width, self._cell_height = self.empty_image.size
        self.image = None
        self.bar_width = 0
        self._delta = 0
        if not os.path.exists(settings.TMP_DIR):
            os.makedirs(settings.TMP_DIR)
        self.rect = None
        self.draw()

    def draw(self):
        out_fname = os.path.join(settings.TMP_DIR,
                                 "cannons_{}_empty_{}.png".format(self.model.shots_left,
                                                                  self.model.shots_count - self.model.shots_left))
        if not os.path.exists(out_fname):
            blank_image = Image.new("RGBA", (64, self._cell_height), None)
            clear_image(blank_image)
            for x in xrange(self.model.shots_left):
                blank_image.paste(self.cannon_image, (self._cell_width * x, 0), self.cannon_image)
            for x in xrange(self.model.shots_left, self.model.shots_count):
                blank_image.paste(self.empty_image, (self._cell_width * x, 0), self.empty_image)
            blank_image.save(out_fname)
        self.image = pygame.image.load(out_fname).convert_alpha()
        tile_width = 64  # TODO: remove hardcode value
        self.bar_width = self._cell_width * self.model.shots_count
        self._delta = math.floor((tile_width - self.bar_width) / 2.0 + 0.5)
        self.move()

    def move(self):
        x, y = self.model.rect.topleft
        x, y = x + self._delta, y - 20
        self.rect = pygame.Rect(x, y, self.bar_width, self._cell_height)


class TargetBar(pygame.sprite.Sprite):
    def __init__(self, model):
        pygame.sprite.Sprite.__init__(self)
        self.model = model
        self.target_image = Image.open(os.path.join(settings.MODELS_DIR, "target_bar_cell.png"))
        self._cell_width, self._cell_height = self.target_image.size
        self.image = None
        self.bar_width = 0
        self._delta = 0
        if not os.path.exists(settings.TMP_DIR):
            os.makedirs(settings.TMP_DIR)
        self.rect = None
        self.draw()

    def draw(self):
        if self.model.aimed_count > 0:
            out_fname = os.path.join(settings.TMP_DIR, "targets_{}.png".format(self.model.aimed_count))
            if not os.path.exists(out_fname):
                blank_image = Image.new("RGBA", (self._cell_width * 8, self._cell_height), None)
                clear_image(blank_image)
                for x in xrange(self.model.aimed_count):
                    blank_image.paste(self.target_image, (self._cell_width * x, 0), self.target_image)
                blank_image.save(out_fname)
            self.image = pygame.image.load(out_fname).convert_alpha()
            tile_width = 64  # TODO: remove hardcode value
            self.bar_width = self._cell_width * self.model.aimed_count
            self._delta = math.floor((tile_width - self.bar_width) / 2.0 + 0.5)
            self.move()
        else:
            self.image = pygame.Surface((0, 0))
            self.rect = pygame.Rect(0, 0, 0, 0)

    def move(self):
        x, y = self.model.rect.topleft
        x, y = x + self._delta, y - 30
        self.rect = pygame.Rect(x, y, self.bar_width, self._cell_height)


class Ship(Model):
    def __init__(self, layers_handler, isom_x, isom_y, model='steam_corvette', player=settings.PLAYER1, base_armor=1,
                 fire_range=1, max_move=1, shots_count=1, stille_move=1, storm_move=1, **kwargs):
        self.direction = 'se'
        Model.__init__(self, layers_handler, isom_x, isom_y, model, player, base_armor, fire_range, shots_count)
        self.possible_moves = []
        self.storm_move = int(storm_move)
        self._storm_moves_left = self.storm_move
        self._has_moved = False
        self.max_move = int(max_move)
        self.stille_move = int(stille_move)

    def get_data(self):
        return self.model, self.player, self.x, self.y, \
               self.base_armor, self.fire_range, self.shots_count, \
               self.stille_move, self.storm_move, \
               self.armor, self._has_moved, self._has_shot, \
               self.shots_left

    @classmethod
    def from_data(cls, layers_handler, data):
        model, player, x, y, base_armor, fire_range, shots_count, stille_move, storm_move, armor, has_moved, has_shot, shots_left = data
        ship = cls(layers_handler, x, y, model=model, player=player,
                   base_armor=base_armor, fire_range=fire_range, shots_count=shots_count,
                   stille_move=stille_move, storm_move=storm_move)
        ship.armor = armor
        ship._has_moved = has_moved
        ship._has_shot = has_shot
        ship.shots_left = shots_left
        ship.health_bar = HealthBar(ship)
        ship.cannon_bar = CannonBar(ship)
        return ship

    def _update_image(self, img_type=""):
        if img_type:
            img_type = "_{}".format(img_type)
        self.image = pygame.image.load(
            os.path.join(settings.MODELS_DIR,
                         "{}_{}_{}{}.png".format(self.model, self.player, self.direction, img_type))).convert_alpha()

    def reset(self):
        Model.reset(self)
        self._storm_moves_left = self.storm_move
        self._has_moved = False

    def move(self, (x, y)=(None, None)):
        if self._has_moved:
            return False
        if (x, y) in self.possible_moves:
            self.x = x
            self.y = y
            self._has_moved = True
        elif (x, y) == (None, None) and len(self.possible_moves) == 1:  # storm step
            coords = self.possible_moves[0]
            if coords:
                self.x, self.y = coords
            else:
                return False
        else:
            return False
        self.rect.topleft = map(lambda offset, self_coord: offset + self_coord,
                                self.offset,
                                self.layers_handler.isometric_to_orthogonal(self.x, self.y))
        self.health_bar.move()
        self.cannon_bar.move()
        self.target_bar.move()
        self.possible_moves = []
        self._update_image()
        self.aim_reset()
        return True

    def calculate_moves(self, wind_type, wind_direction, obstacles=[], step=None, docks=[]):
        def rotate(axis, obj):
            """
            Rotate object with obj coords around the axis, getting closer and closer to the axis with each step till pi
            angle
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

        def is_in_port():
            return self.coords() in docks

        def get_dock_moves():
            if is_in_port():
                return filter(lambda dock: max(abs(self.x - dock[0]), abs(self.y - dock[1])) == 1, docks)
            return []

        if self._has_moved or wind_type not in [wind.STILLE, wind.WIND, wind.STORM]:
            return []
            # Handle wind as a number of obstacles
        max_move = self.max_move
        if wind_type == wind.STORM:
            cur = get_dock_moves()
            if not is_in_port():
                obstacles += docks
                max_move = step if step else self.storm_move
                for delta in xrange(1, max_move + 1):
                    if wind_direction == wind.NORTH:
                        next_move = (self.x - delta, self.y - delta)
                    if wind_direction == wind.EAST:
                        next_move = (self.x + delta, self.y - delta)
                    if wind_direction == wind.SOUTH:
                        next_move = (self.x + delta, self.y + delta)
                    if wind_direction == wind.WEST:
                        next_move = (self.x - delta, self.y + delta)
                    if wind_direction == wind.NORTH_EAST:
                        next_move = (self.x, self.y - delta)
                    if wind_direction == wind.NORTH_WEST:
                        next_move = (self.x - delta, self.y)
                    if wind_direction == wind.SOUTH_EAST:
                        next_move = (self.x + delta, self.y)
                    if wind_direction == wind.SOUTH_WEST:
                        next_move = (self.x, self.y + delta)
                    if next_move in obstacles or next_move[0] < 0 or next_move[1] < 0 or \
                                    next_move[0] >= self.layers_handler.tiledmap.width or \
                                    next_move[1] >= self.layers_handler.tiledmap.height:
                        break
                    else:
                        self._storm_moves_left -= delta
                        if self._storm_moves_left >= 0:
                            cur = [next_move]
            self.possible_moves = cur
        else:
            self.possible_moves = get_dock_moves()
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
            self.possible_moves += self.calculate_area(max_move, obstacles)
        return self.possible_moves

    def check_crash(self, obstacles):
        if self.coords() in obstacles:
            self._is_alive = False

    def skipped_turn(self):
        return not self._has_moved and not self._has_shot


class Port(Model):
    def __init__(self, layers_handler, isom_x, isom_y, model='port_1', player=settings.PLAYER1, base_armor=1,
                 fire_range=1, shots_count=1, **kwargs):
        Model.__init__(self, layers_handler, isom_x, isom_y, model, player, base_armor, fire_range, shots_count)

    def get_dock(self):
        return [(self.x + delta_x, self.y + delta_y) for delta_x in xrange(-1, 2) for delta_y in xrange(-1, 2) if
                abs(delta_x) + abs(delta_y) != 0]

    def set_player(self, player):
        self.player = player
        self.health_bar = HealthBar(self)
        self._update_image()

    def take_damage(self, damage):
        Model.take_damage(self, damage)
        if not self.is_alive():
            self.player = settings.NEUTRAL_PLAYER
            self._update_image()
            self.health_bar = HealthBar(self)


class RoyalPort(Port):
    def __init__(self, layers_handler, isom_x, isom_y, model='royal_port', player=settings.PLAYER1, base_armor=1,
                 **kwargs):
        Port.__init__(self, layers_handler, isom_x, isom_y, model, player, base_armor, fire_range=0, shots_count=0)

    def take_damage(self, damage):
        Model.take_damage(self, damage)
