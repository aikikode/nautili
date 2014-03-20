#!/usr/bin/env python
import pygame
from pytmx import tmxloader
from renderer import Renderer
from layers import LayersHandler

__author__ = 'aikikode'

WIN_WIDTH = 1600
WIN_HEIGHT = 768
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)

PLATFORM_WIDTH = 64
PLATFORM_HEIGHT = 64


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Armada")
    bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
    fg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
    layers_handler = LayersHandler(tmxloader.load_pygame("./maps/map1.tmx", pixelalpha=True))
    background = Renderer(layers_handler, bg)
    #foreground = Renderer(layers_handler, fg)
    allsprites = layers_handler.get_all_sprites()
    clickable_objects_list = layers_handler.get_clickable_objects()
    sea = layers_handler.sea
    highlighted_sea = layers_handler.highlighted_sea
    rocks = layers_handler.rocks
    islands = layers_handler.islands
    ships = layers_handler.ships
    background.add(sea + rocks + islands)
    #foreground.add(islands)
    background.draw()
    #foreground.draw()
    selected_ship = None
    highlighted = None
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
                        selected_ship = None
                        background.clear()
                        background.add(sea + rocks + islands)
                        background.draw()
            if clicked:
                # Check whether there's an object
                try:
                    selected_ship = filter(lambda obj: obj.coords() == (clicked.coords()), ships)[0]
                    #print "Object {} clicked".format(selected_ship)
                    # Highlight possible movements
                    highlighted = selected_ship.calculate_moves(obstacles=layers_handler.ground_obstacles + map(lambda x: x.coords(), ships))
                    background.clear()
                    background.add(sea + rocks + islands)
                    background.add(LayersHandler.filter_layer(highlighted_sea, highlighted))
                    background.draw()
                except IndexError:
                    if selected_ship:
                        # we clicked on empty sea - move object there
                        selected_ship.move(*clicked.coords())
                        allsprites = layers_handler.get_all_sprites()
                        background.clear()
                        background.add(sea + rocks + islands)
                        background.draw()
                        selected_ship = None

        screen.blit(bg, (0, 0))
        allsprites.update()
        allsprites.draw(screen)
        screen.blit(fg, (0, 0))
        pygame.display.update()


