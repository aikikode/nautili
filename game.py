#!/usr/bin/env python
import colors
from menus import PauseMenu
import pygame
from pytmx import tmxloader
from panels import RightTopPanel, LeftTopPanel
from renderer import IsometricRenderer
from layers import LayersHandler
from settings import *

__author__ = 'aikikode'


class Game(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(DISPLAY)
        pygame.display.set_caption("Nautili")
        # Background
        self.bg_surface = pygame.Surface((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        # Panel
        self.right_top_panel = RightTopPanel(self, (MAIN_WIN_WIDTH - RIGHT_PANEL_WIDTH, 0), (RIGHT_PANEL_WIDTH, RIGHT_PANEL_HEIGHT))
        self.left_top_panel = LeftTopPanel(self, (0, 0), (LEFT_PANEL_WIDTH, LEFT_PANEL_HEIGHT))
        self.layers_handler = lh = LayersHandler(tmxloader.load_pygame("./maps/map2.tmx", pixelalpha=True))
        self.background = IsometricRenderer(self.layers_handler, self.bg_surface)
        # Helper variables from layers handler
        self.allsprites = lh.get_all_sprites()
        self.clickable_objects_list = lh.get_clickable_objects()
        self.sea = lh.sea
        self.highlighted_sea = lh.highlighted_sea
        self.fire = lh.fire
        self.rocks = lh.rocks
        self.islands = lh.islands
        self.ships = lh.ships
        self.yellow_ships = lh.yellow_ships
        self.green_ships = lh.green_ships
        self.ports = lh.ports
        # Initial game variables state
        self.wind_type = None
        self.wind_direction = None
        self.player = PLAYER1
        self._paused = False
        # Prepare rendering
        self.background.fill(colors.BACKGROUND_COLOR) # fill with water color
        self.background.add(self.sea + self.rocks + self.islands)
        self.map_width, self.map_height = self.layers_handler.get_map_rect()
        self.move_camera(((MAIN_WIN_WIDTH - self.map_width) / 2, 0))

    def next_turn(self):
        if self.player == PLAYER1:
            self.player = PLAYER2
            self.left_top_panel.label.text = "Green player turn"
            self.left_top_panel.label.color = colors.GREEN
        else:
            self.player = PLAYER1
            self.left_top_panel.label.text = "Yellow player turn"
            self.left_top_panel.label.color = colors.YELLOW
        self.wind_type = None
        for ship in self.ships:
            ship.reset()
        self.toggle_pause()


    def toggle_pause(self, text=""):
        self._paused = not self._paused
        ##self.bg_surface.fill([21, 37, 45])
        #ypos = 0
        #while ypos <= MAIN_WIN_HEIGHT:
        #    xpos = 0
        #    while xpos <= MAIN_WIN_WIDTH:
        #        self.fg_surface.blit(self.pygame_shade_image, (xpos, ypos))
        #        xpos += self.shade_image.size[0]
        #    ypos += self.shade_image.size[1]
        #label_font = pygame.font.Font(None, 40)
        #self.pause_label = Label(self.fg_surface, label_font, WHITE, text, (MAIN_WIN_WIDTH / 2 - 80, MAIN_WIN_HEIGHT / 2 - 20))
        ##self.screen.blit(self.fg_surface, (0, 0))
        ##pygame.display.update()

    def game_ended(self):
        if not self.yellow_ships:
            print "Green won!"
            return True
        elif not self.green_ships:
            print "Yellow won!"
            return True
        return False

    def max_storm_move(self):
        return sorted(self.ships, key=lambda ship: ship.storm_move, reverse=True)[0].storm_move

    def force_ships_move(self):
        if self.player == PLAYER1:
            ships_to_move = self.yellow_ships
        else:
            ships_to_move = self.green_ships
        for x in xrange(0, self.max_storm_move()):
            for ship in ships_to_move:
                ship.calculate_moves(self.wind_type, self.wind_direction,
                                     obstacles=self.layers_handler.storm_move_obstacles +
                                               map(lambda x: x.coords(), self.ships) +
                                               map(lambda y: y.coords(), self.ports),
                                     max=1)
                ship.move()
                ship.check_crash(self.layers_handler.deadly_obstacles)
        self.remove_dead_ships()

    def remove_dead_ships(self):
        self.yellow_ships = filter(lambda s: s.is_alive(), self.yellow_ships)
        self.green_ships = filter(lambda s: s.is_alive(), self.green_ships)
        self.ships = self.yellow_ships + self.green_ships

    def move_camera(self, delta):
        offset_x, offset_y = self.background.offset
        delta_x, delta_y = delta
        if MAIN_WIN_WIDTH - offset_x - delta_x > self.map_width:
            delta_x = MAIN_WIN_WIDTH - offset_x - self.map_width
        elif offset_x + delta_x > 0:
            delta_x = -offset_x
        if MAIN_WIN_HEIGHT - offset_y - delta_y > self.map_height:
            delta_y = MAIN_WIN_HEIGHT - offset_y - self.map_height
        elif offset_y + delta_y > 0:
            delta_y = -offset_y
        delta = (delta_x, delta_y)
        self.background.fill(colors.BACKGROUND_COLOR) # fill with water color
        self.background.increase_offset(delta)
        for obj in self.ships + self.ports:
            obj.offset = self.background.offset
            obj.rect = obj.rect.move(delta)
        self.background.draw()

    def start(self):
        background = self.background
        right_top_panel = self.right_top_panel
        background.draw()
        #target_ship = None
        #highlighted = None
        selected_ship = None
        exit_game = False
        ctrl_mode = False
        p = PauseMenu(self.screen)
        while not self.game_ended() and not exit_game:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit, "QUIT"
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_LCTRL or e.key == pygame.K_RCTRL):
                    ctrl_mode = True
                if e.type == pygame.KEYUP and (e.key == pygame.K_LCTRL or e.key == pygame.K_RCTRL):
                    ctrl_mode = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                    if ctrl_mode:
                        exit_game = True
                if self._paused:
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                        self.toggle_pause()
                else:
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
                        self.move_camera((0, 300))
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_DOWN:
                        self.move_camera((0, -300))
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_LEFT:
                        self.move_camera((300, 0))
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RIGHT:
                        self.move_camera((-300, 0))
                    if e.type == pygame.MOUSEBUTTONDOWN and (e.button == 1 or e.button == 3):
                        clicked = False
                        if not right_top_panel.check_click(e.pos):
                            for obj in self.clickable_objects_list:
                                clicked = obj.check_click(e.pos)
                                if clicked:
                                    break
                            else:
                                if selected_ship:
                                    #selected_ship.aim_reset()
                                    selected_ship = None
                                    background.update(self.sea + self.rocks + self.islands)
                        if clicked:
                            # Check whether there's an object
                            if e.button == 1:
                                try:
                                    if self.player == PLAYER1:
                                        ships_to_select = self.yellow_ships
                                    else:
                                        ships_to_select = self.green_ships
                                    selected_ship = filter(lambda obj: obj.coords() == (clicked.coords()), ships_to_select)[0]
                                    #print "Object {} clicked".format(selected_ship)
                                    # Highlight possible movements
                                    highlighted = selected_ship.calculate_moves(self.wind_type, self.wind_direction,
                                                                                obstacles=self.layers_handler.move_obstacles + map(
                                                                                    lambda x: x.coords(), self.ships) + map(
                                                                                    lambda x: x.coords(), self.ports))
                                    shots = selected_ship.calculate_shots(obstacles=self.layers_handler.shoot_obstacles)
                                    background.update(self.sea + self.rocks + self.islands +
                                                      LayersHandler.filter_layer(self.highlighted_sea, highlighted) +
                                                      LayersHandler.filter_layer(self.fire, shots))
                                except IndexError:
                                    if selected_ship:
                                        # we clicked on empty sea - move object there
                                        selected_ship.move(clicked.coords())
                                        self.allsprites = self.layers_handler.get_all_sprites()
                                        background.update(self.sea + self.rocks + self.islands)
                                        selected_ship = None
                            else:
                                try:
                                    target_ship = filter(lambda obj: obj.coords() == (clicked.coords()), self.ships)[0]
                                    if selected_ship and selected_ship != target_ship:
                                        if selected_ship.aim(target_ship):
                                            pass
                                            #TODO: Draw curved arrow to the target
                                            #background.clear()
                                            #background.add(self.sea + self.rocks + self.islands +
                                            #               LayersHandler.filter_layer(self.highlighted_sea, highlighted) +
                                            #               LayersHandler.filter_layer(self.fire, shots))
                                            #(x0, y0) = self.layers_handler.isometric_to_orthogonal(selected_ship.x, selected_ship.y)
                                            #for target in selected_ship.get_targets():
                                            #    (x1, y1) = self.layers_handler.isometric_to_orthogonal(target.x, target.y)
                                            #    background.add_line((x0, y0), (x1, y1))
                                            #background.draw()
                                except IndexError:
                                    pass
            # Process HUD mouseover
            right_top_panel.mouseover(pygame.mouse.get_pos())
            # end event handing
            self.screen.blit(self.bg_surface, (0, 0))
            self.allsprites.update()
            self.allsprites.draw(self.screen)
            right_top_panel.draw()
            self.left_top_panel.draw()
            if self._paused:
                p.show()
            pygame.display.update()