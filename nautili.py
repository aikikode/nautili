#!/usr/bin/env python

__author__ = 'aikikode'

import pygame
from pygame.locals import *
from pytmx import tmxloader
import numpy as np
from models import Ship
from renderer import Renderer
from textures import Island, Rock, Sea

WIN_WIDTH = 1600
WIN_HEIGHT = 768
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)

PLATFORM_WIDTH = 64
PLATFORM_HEIGHT = 64

BACKGROUND_LAYER = 0
HIGHLIGHT_LAYER = 1
ISLANDS_LAYER = 2
ROCKS_LAYER = 3


def exclude_defined(l1, l2):
    """
    Exclude all values from l1 that already exist in l2, e.g.
    exclude_defined([[1, 2], [3, 4]], [[None, 8], [19, None]]) -> [[1, None], [None, 4]]
    """
    return map(lambda x, y: map(lambda a, b: a if b is None else None, x, y), l1, l2)


def rerender_map(map_renderer, bg, highlighted_coords=None):
    map_renderer.render_layer(BACKGROUND_LAYER)
    if highlighted_coords:
        map_renderer.render_layer(HIGHLIGHT_LAYER, classname=None, coords_list=highlighted_coords)
    map_renderer.render_layer(ISLANDS_LAYER)
    map_renderer.render_layer(ROCKS_LAYER)


def filter_not_none(list):
    return filter(lambda x: x is not None, list)


def flatten(list_of_lists):
    return sum(list_of_lists, [])


def load_map(mapfile, bg):
    global map_renderer
    global clickable_objects_list
    global islands
    global rocks
    global ships
    global obstacles
    map_renderer = Renderer(tmxloader.load_pygame(mapfile, pixelalpha=True), bg)
    sea = map_renderer.render_layer(BACKGROUND_LAYER, Sea)
    islands = map_renderer.render_layer(ISLANDS_LAYER, Island)
    rocks = map_renderer.render_layer(ROCKS_LAYER, Rock)
    sea = exclude_defined(sea, rocks)
    sea = exclude_defined(sea, islands)
    obstacles = map(lambda x: x.coords(), filter_not_none(flatten(rocks)))
    obstacles += map(lambda x: x.coords(), filter_not_none(flatten(islands)))
    ships = map_renderer.get_objects("ships", Ship)
    clickable_objects_list = filter_not_none(flatten(sea))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Armada")
    bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    load_map("./maps/map1.tmx", bg)
    selected_ship = None
    highlighted = None
    allsprites = pygame.sprite.RenderPlain(ships)
    while True:
        for e in pygame.event.get():
            clicked = False
            if e.type == pygame.QUIT:
                raise SystemExit, "QUIT"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for object in clickable_objects_list:
                    clicked = object.check_click(e.pos)
                    if clicked: break
                else:
                    if selected_ship:
                        rerender_map(map_renderer, bg)
                        selected_ship = None
            if clicked:
                # Check whether there's an object
                try:
                    selected_ship = filter(lambda obj: obj.coords() == (clicked.coords()), ships)[0]
                    #print "Object {} clicked".format(selected_ship)
                    # Highlight possible movements
                    highlighted = selected_ship.calculate_moves(obstacles=obstacles)
                    rerender_map(map_renderer, bg, highlighted)
                except IndexError:
                    if selected_ship:
                        # we clicked on empty sea - move object there
                        selected_ship.move(*clicked.coords())
                        rerender_map(map_renderer, bg)
                        selected_ship = None

        screen.blit(bg, (0, 0))
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.update()


