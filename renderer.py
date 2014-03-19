#!/usr/bin/env python
import pygame

__author__ = 'aikikode'


class Renderer(object):
    def __init__(self, tiledmap, screen):
        self.screen = screen
        self.tiledmap = tiledmap

    def render_layer(self, layer_num, classname=None, coords_list=None):
        def render_tile_helper(x, y):
            if x < 0 or y < 0:
                return
            tile = self.tiledmap.getTileImage(x, y, layer_num)
            if tile:
                if classname:
                    ort_x, ort_y = self.isometric_to_orthogonal(x, y)
                    res[x][y] = classname(x, y, pygame.Rect((ort_x + 16, ort_y + 30), (32, 20)))
                self.screen.blit(tile, self.isometric_to_orthogonal(x, y))
        res = [[None for x in xrange(0, self.tiledmap.width)] for y in xrange(0, self.tiledmap.height)]
        if coords_list:
            for coords in coords_list:
                try:
                    render_tile_helper(coords[0], coords[1])
                except Exception, ex:
                    print ex
        else:
            for y in xrange(0, self.tiledmap.height):
                for x in xrange(0, self.tiledmap.width):
                    render_tile_helper(x, y)
        return res

    def render_tile(self, x, y, layer_num):
        tile = self.tiledmap.getTileImage(x, y, layer_num)
        if tile:
            self.screen.blit(tile, self.isometric_to_orthogonal(x, y))

    def get_objects(self, object_name, classname):
        res = []
        objects = filter(lambda gr: gr.name == object_name, self.tiledmap.objectgroups)[0]
        for object in objects:
            # convert to global coords:
            res.append(classname(self, *self.tile_to_isometric(object.x, object.y)))
        return res

    def isometric_to_orthogonal(self, x, y):
        return (self.tiledmap.height + x - y - 1) * (self.tiledmap.tilewidth / 2),\
               (x + y) * (self.tiledmap.tileheight / 2)

    def orthogonal_to_isometric(self, x, y):
        tw = float(self.tiledmap.tilewidth)
        th = float(self.tiledmap.tileheight)
        return x/tw + y/th + (1 - th)/2, y/th - x/tw + (th - 1)/2

    def tile_to_isometric(self, x, y):
        tw = self.tiledmap.tilewidth
        return x / (tw / 2), y / (tw / 2)
