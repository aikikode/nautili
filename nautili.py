#!/usr/bin/env python

__author__ = 'aikikode'

import pygame
from pygame.locals import *
from pytmx import tmxloader
from models import Ship
from renderer import Renderer
from textures import Island, Rock, Sea

WIN_WIDTH = 1600
WIN_HEIGHT = 768
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)

PLATFORM_WIDTH = 64
PLATFORM_HEIGHT = 64

BACKGROUND_LAYER = 0
ISLANDS_LAYER = 1
ROCKS_LAYER = 2


def exclude_defined(l1, l2):
    """
    Exclude all values from l1 that already exist in l2, e.g.
    exclude_defined([[1, 2], [3, 4]], [[None, 8], [19, None]]) -> [[1, None], [None, 4]]
    """
    return map(lambda x, y: map(lambda a, b: a if b is None else None, x, y), l1, l2)


def load_map(mapfile, bg):
    global map_renderer
    global clickable_objects_list
    global ships
    map_renderer = Renderer(tmxloader.load_pygame(mapfile, pixelalpha=True), bg)
    sea = map_renderer.render_layer(BACKGROUND_LAYER, Sea)
    islands = map_renderer.render_layer(ISLANDS_LAYER, Island)
    rocks = map_renderer.render_layer(ROCKS_LAYER, Rock)
    sea = exclude_defined(sea, rocks)
    sea = exclude_defined(sea, islands)
    ships = map_renderer.get_objects("ships", Ship)
    clickable_objects_list = filter(lambda x: x is not None, sum(sea, []))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Armada")
    bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    load_map("./maps/map1.tmx", bg)
    selected = False
    allsprites = pygame.sprite.RenderPlain(ships)
    while 1:
        for e in pygame.event.get():
            clicked = False
            if e.type == pygame.QUIT:
                raise SystemExit, "QUIT"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for object in clickable_objects_list:
                    clicked = object.check_click(e.pos)
                    if clicked: break
            if clicked:
                # Check whether there's an object
                try:
                    obj = filter(lambda obj: obj.coords() == (clicked.coords()), ships)[0]
                    print "Object {} clicked".format(obj)
                    selected = obj
                except IndexError:
                    if selected:
                        # we clicked on empty sea - move object there
                        selected.move(*clicked.coords())
                        #selected.update(*clicked.coords())
                        selected = False
        screen.blit(bg, (0, 0))
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.update()


