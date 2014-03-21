#!/usr/bin/env python
import pygame
from models import Ship, Port
from textures import Sea, Island, Rock

__author__ = 'aikikode'


class LayersHandler(object):
    BACKGROUND_LAYER = 0
    HIGHLIGHT_LAYER = 1
    ISLANDS_LAYER = 2
    ROCKS_LAYER = 3

    def __init__(self, tiledmap):
        self.tiledmap = tiledmap
        self.sea = self.get_layer_tiles(LayersHandler.BACKGROUND_LAYER, Sea)
        self.rocks = self.get_layer_tiles(LayersHandler.ROCKS_LAYER, Rock)
        self.islands = self.get_layer_tiles(LayersHandler.ISLANDS_LAYER, Island)
        self.highlighted_sea = self.get_layer_tiles(LayersHandler.HIGHLIGHT_LAYER, Sea)
        self.visible_sea = LayersHandler.exclude_defined(
            LayersHandler.exclude_defined(
                self.sea,
                self.rocks),
            self.islands)
        self.ground_obstacles = map(lambda x: x.coords(),
                                    LayersHandler.filter_not_none(LayersHandler.flatten(self.rocks))) + \
                                map(lambda x: x.coords(),
                                    LayersHandler.filter_not_none(LayersHandler.flatten(self.islands)))
        self.ships = self.get_objects("ships_yellow", Ship)
        self.ports = self.get_objects("ports_yellow", Port)

    def get_layer_tiles(self, layer_num, classname):
        res = [[None for x in xrange(0, self.tiledmap.width)] for y in xrange(0, self.tiledmap.height)]
        for y in xrange(0, self.tiledmap.height):
            for x in xrange(0, self.tiledmap.width):
                tile = self.tiledmap.getTileImage(x, y, layer_num)
                if tile:
                    ort_x, ort_y = self.isometric_to_orthogonal(x, y)
                    res[x][y] = classname(tile, x, y, pygame.Rect((ort_x + 16, ort_y + 30), (32, 20)))
        return res

    def get_objects(self, object_name, classname):
        res = []
        objects = filter(lambda gr: gr.name == object_name, self.tiledmap.objectgroups)[0]
        for object in objects:
            # convert to global coords:
            res.append(classname(self, *self.tile_to_isometric(object.x, object.y), **object.__dict__))
        return res

    def get_all_sprites(self):
        return pygame.sprite.OrderedUpdates(sorted(self.ships + self.ports, key=lambda s: s.x + s.y))

    def get_clickable_objects(self):
        return LayersHandler.filter_not_none(LayersHandler.flatten(self.visible_sea))

    def isometric_to_orthogonal(self, x, y):
        return (self.tiledmap.height + x - y - 1) * (self.tiledmap.tilewidth / 2), \
               (x + y) * (self.tiledmap.tileheight / 2)

    #def orthogonal_to_isometric(self, x, y):
    #    tw = float(self.tiledmap.tilewidth)
    #    th = float(self.tiledmap.tileheight)
    #    return x/tw + y/th + (1 - th)/2, y/th - x/tw + (th - 1)/2

    def tile_to_isometric(self, x, y):
        tw = self.tiledmap.tilewidth
        return (x - 1)/(tw / 2), (y - 1)/(tw / 2)

    @staticmethod
    def filter_layer(layer_table, coords_list):
        res = []
        for coords in coords_list:
            try:
                res.append(layer_table[coords[0]][coords[1]])
            except IndexError:
                pass
        return res

    @staticmethod
    def exclude_defined(l1, l2):
        """
        Exclude all values from l1 that already exist in l2, e.g.
        exclude_defined([[1, 2], [3, 4]], [[None, 8], [19, None]]) -> [[1, None], [None, 4]]
        """
        return map(lambda x, y: map(lambda a, b: a if b is None else None, x, y), l1, l2)

    @staticmethod
    def filter_not_none(list):
        return filter(lambda x: x is not None, list)

    @staticmethod
    def flatten(list_of_lists):
        return sum(list_of_lists, [])