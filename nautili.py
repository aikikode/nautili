#!/usr/bin/env python
import pygame
import random
import math
from pytmx import tmxloader
from hud import Button
from renderer import Renderer, IsometricRenderer
from layers import LayersHandler
import wind

__author__ = 'aikikode'

WIN_WIDTH = 1280
WIN_HEIGHT = 900
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
HUD_WIDTH = WIN_WIDTH
HUD_HEIGHT = 200
MAIN_WIN_WIDTH = WIN_WIDTH
MAIN_WIN_HEIGHT = WIN_HEIGHT - HUD_HEIGHT

WIND_TYPE = None
WIND_DIRECTION = None

PLAYER1 = "yellow"
PLAYER2 = "green"


def game_ended():
    if not yellow_ships:
        print "Green won!"
        return True
    elif not green_ships:
        print "Yellow won!"
        return True
    return False


class Panel(object):
    def __init__(self, offset, size):
        self.width, self.height = size
        self.offset = offset
        self.hud_surface = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        self.hud = Renderer(self.hud_surface)
        self.objects = []
        self.button_font = pygame.font.Font(None, 40)
        self.get_wind_button = Button(self.hud_surface, self.button_font, "Wind:", (self.width / 2 - 80, 10),
                                      on_click=self.get_wind)
        self.shoot_button = Button(self.hud_surface, self.button_font, "Shoot", (self.width / 2 - 80, 60),
                                   on_click=self.shoot)
        self.end_move_button = Button(self.hud_surface, self.button_font, "End move", (self.width / 2 - 80, 90),
                                      on_click=self.end_move)
        self.objects.append(self.get_wind_button)
        self.objects.append(self.shoot_button)
        self.objects.append(self.end_move_button)

    def get_wind(self):
        global WIND_TYPE
        global WIND_DIRECTION
        self.get_wind_button.disable()
        WIND_TYPE = random.sample(wind.WIND_TYPES, 1)[0]
        if WIND_TYPE != wind.STILLE:
            WIND_DIRECTION = random.sample(wind.WIND_DIRECTIONS, 1)[0]
            self.get_wind_button.text = "Wind: {}, {}".format(wind.wind_type_to_str(WIND_TYPE),
                                                              wind.wind_direction_to_str(WIND_DIRECTION))
        else:
            self.get_wind_button.text = "Wind: {}".format(wind.wind_type_to_str(WIND_TYPE))
        if WIND_TYPE == wind.STORM:
            force_ships_move(player)

    def shoot(self):
        miss = random.randint(0, 2)
        if player == PLAYER1:
            ships_to_shoot = yellow_ships
        else:
            ships_to_shoot = green_ships
        for ship in ships_to_shoot:
            ship.shoot(not miss)
        global allsprites
        global ships
        global yellow_ships
        global green_ships
        allsprites = layers_handler.get_all_sprites()
        yellow_ships = filter(lambda s: s.is_alive(), yellow_ships)
        green_ships = filter(lambda s: s.is_alive(), green_ships)
        ships = yellow_ships + green_ships

    def end_move(self):
        global player
        if player == PLAYER1:
            player = PLAYER2
        else:
            player = PLAYER1
        self.get_wind_button.enable()
        self.get_wind_button.text = "Wind:"
        global WIND_TYPE
        WIND_TYPE = None
        for ship in ships:
            ship.reset()

    def draw(self, screen):
        self.hud.fill([21, 37, 45]) # fill with water color
        self.hud.draw()
        pygame.draw.line(self.hud_surface, (44, 92, 118), [0, 0], [self.width, 0], 2)
        for obj in self.objects:
            obj.draw()
        screen.blit(self.hud_surface, self.offset)

    def mouseover(self, event_position):
        for obj in self.objects:
            obj.mouseover(map(lambda x, y: x - y, event_position, self.offset))

    def check_click(self, event_position):
        for obj in self.objects:
            obj.check_click(map(lambda x, y: x - y, event_position, self.offset))


def max_storm_move():
    return sorted(ships, key=lambda ship: ship.storm_move, reverse=True)[0].storm_move


def force_ships_move(player):
    # TODO: range to max ship storm move
    if player == PLAYER1:
        ships_to_move = yellow_ships
    else:
        ships_to_move = green_ships
    for x in xrange(0, max_storm_move()):
        for ship in ships_to_move:
            ship.calculate_moves(WIND_TYPE, WIND_DIRECTION,
                                 obstacles=layers_handler.move_obstacles +
                                           map(lambda x: x.coords(), ships) +
                                           map(lambda y: y.coords(), ports),
                                 max=1)
            ship.move()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Armada")
    bg_surface = pygame.Surface((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
    panel = Panel((0, MAIN_WIN_HEIGHT), (HUD_WIDTH, HUD_HEIGHT))
    #fg = pygame.Surface((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
    layers_handler = LayersHandler(tmxloader.load_pygame("./maps/map1.tmx", pixelalpha=True))
    background = IsometricRenderer(layers_handler, bg_surface)
    #foreground = Renderer(layers_handler, fg)
    allsprites = layers_handler.get_all_sprites()
    clickable_objects_list = layers_handler.get_clickable_objects()
    sea = layers_handler.sea
    highlighted_sea = layers_handler.highlighted_sea
    fire = layers_handler.fire
    rocks = layers_handler.rocks
    islands = layers_handler.islands
    ships = layers_handler.ships
    yellow_ships = layers_handler.yellow_ships
    green_ships = layers_handler.green_ships
    ports = layers_handler.ports
    #background.fill([51, 88, 20]) # fill with grass color
    background.fill([21, 37, 45]) # fill with water color
    background.add(sea + rocks + islands)
    #foreground.add(islands)
    background.draw()
    #foreground.draw()
    selected_ship = None
    target_ship = None
    highlighted = None
    player = PLAYER1
    while not game_ended():
        for e in pygame.event.get():
            clicked = False
            if e.type == pygame.QUIT:
                raise SystemExit, "QUIT"
            if e.type == pygame.MOUSEBUTTONDOWN and (e.button == 1 or e.button == 3):
                for object in clickable_objects_list:
                    clicked = object.check_click(e.pos)
                    if clicked: break
                else:
                    if not panel.check_click(e.pos) and selected_ship:
                        #selected_ship.aim_reset()
                        selected_ship = None
                        background.update(sea + rocks + islands)
                if clicked:
                    # Check whether there's an object
                    if e.button == 1:
                        try:
                            if player == PLAYER1:
                                ships_to_select = yellow_ships
                            else:
                                ships_to_select = green_ships
                            selected_ship = filter(lambda obj: obj.coords() == (clicked.coords()), ships_to_select)[0]
                            #print "Object {} clicked".format(selected_ship)
                            # Highlight possible movements
                            highlighted = selected_ship.calculate_moves(WIND_TYPE, WIND_DIRECTION,
                                                                        obstacles=layers_handler.move_obstacles + map(
                                                                            lambda x: x.coords(), ships) + map(
                                                                            lambda x: x.coords(), ports))
                            shots = selected_ship.calculate_shots(obstacles=layers_handler.shoot_obstacles)
                            background.update(sea + rocks + islands + LayersHandler.filter_layer(highlighted_sea,
                                                                                                 highlighted) + LayersHandler.filter_layer(
                                fire, shots))
                        except IndexError:
                            if selected_ship:
                                # we clicked on empty sea - move object there
                                selected_ship.move(clicked.coords())
                                allsprites = layers_handler.get_all_sprites()
                                background.update(sea + rocks + islands)
                                selected_ship = None
                    else:
                        try:
                            target_ship = filter(lambda obj: obj.coords() == (clicked.coords()), ships)[0]
                            if selected_ship and selected_ship != target_ship:
                                if selected_ship.aim(target_ship):
                                    # Draw curved arrow to the target
                                    background.clear()
                                    background.add(sea + rocks + islands +
                                                   LayersHandler.filter_layer(highlighted_sea, highlighted) +
                                                   LayersHandler.filter_layer(fire, shots))
                                    (x0, y0) = layers_handler.isometric_to_orthogonal(selected_ship.x, selected_ship.y)
                                    for target in selected_ship.get_targets():
                                        (x1, y1) = layers_handler.isometric_to_orthogonal(target.x, target.y)
                                        background.add_line((x0, y0), (x1, y1))
                                    background.draw()
                        except IndexError:
                            pass

                            # Process HUD mouseover
        panel.mouseover(pygame.mouse.get_pos())
        # end event handing
        screen.blit(bg_surface, (0, 0))
        panel.draw(screen)
        allsprites.update()
        allsprites.draw(screen)
        #screen.blit(fg, (0, 0))
        pygame.display.update()
