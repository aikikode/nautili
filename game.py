#!/usr/bin/env python
import colors
import pygame
from menus import PauseMenu
from pytmx import tmxloader
from panels import RightTopPanel, TopPanel, MiniMap
from renderer import IsometricRenderer
from layers import LayersHandler
from settings import *

__author__ = 'aikikode'


class Game(object):
    def __init__(self, map_file):
        pygame.init()
        self.screen = pygame.display.set_mode(DISPLAY)
        pygame.display.set_caption("Nautili")
        try:
            self.layers_handler = lh = LayersHandler(tmxloader.load_pygame(map_file, pixelalpha=True))
        except:
            print "Unable to read map data. Possibly messed up layers."
            raise ValueError
            # Background
        self.bg_surface = pygame.Surface((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        # Panel
        self.right_top_panel = RightTopPanel(self,
                                             (MAIN_WIN_WIDTH - RIGHT_PANEL_WIDTH, MINIMAP_HEIGHT),
                                             (RIGHT_PANEL_WIDTH, RIGHT_PANEL_HEIGHT))
        self.top_panel = TopPanel(self, (0, 0), (TOP_PANEL_WIDTH, TOP_PANEL_HEIGHT))
        self.minimap = MiniMap(self, (MAIN_WIN_WIDTH - MINIMAP_WIDTH, 0), (MINIMAP_WIDTH, MINIMAP_HEIGHT))
        self.background = IsometricRenderer(self.layers_handler, self.bg_surface)
        # Helper variables from layers handler
        self.all_sprites = lh.get_all_sprites()
        self.clickable_objects_list = lh.get_clickable_objects()
        self.sea = lh.sea
        self.docks = lh.docks
        self.highlighted_sea = lh.highlighted_sea
        self.fire = lh.fire
        self.rocks = lh.rocks
        self.islands = lh.islands
        self.ships = lh.ships
        self.yellow_ships = lh.yellow_ships
        self.green_ships = lh.green_ships
        self.yellow_ports = lh.yellow_ports
        self.green_ports = lh.green_ports
        self.ports = lh.ports
        # Initial game variables state
        self.wind_type = None
        self.wind_direction = None
        self.player = PLAYER1
        self._paused = False
        # Prepare rendering
        self.background.fill(colors.BACKGROUND_COLOR)  # fill with water color
        self.background.add(self.sea + self.docks + self.rocks + self.islands)
        self.map_width, self.map_height = self.layers_handler.get_map_dimensions()
        self.move_camera(((MAIN_WIN_WIDTH - self.map_width) / 2, 0))
        self._cursor_default = pygame.mouse.get_cursor()
        self._cursor_close_hand = self._cursor_default
        self.selected_ship = None
        self.target_ships = []
        self.setup_cursors()

    def drop_selection(self):
        if self.selected_ship:
            self.selected_ship.unselect()
            self.selected_ship.aim_reset()
            self.selected_ship = None
        for ship in self.target_ships:
            ship.unselect()
        self.redraw()  # To remove move/aim tiled highlights

    def redraw(self, tiles_list=[]):
        self.background.update(self.sea + self.docks + tiles_list + self.rocks + self.islands)

    def setup_cursors(self):
        self._cursor_default = pygame.mouse.get_cursor()
        #the hand cursor
        _CLOSE_HAND_CURSOR = (
            "                ",
            "                ",
            "                ",
            "                ",
            "    XXXXXXXX    ",
            "    X..X..X.XX  ",
            " XXXX..X..X.X.X ",
            " X.XX.........X ",
            " X..X.........X ",
            " X.....X.X.X..X ",
            "  X....X.X.X..X ",
            "  X....X.X.X.X  ",
            "   X...X.X.X.X  ",
            "    X.......X   ",
            "     X....X.X   ",
            "     XXXXX XX   ")
        # _POINT_HAND_CURSOR = (
        #     "     XX         ",
        #     "    X..X        ",
        #     "    X..X        ",
        #     "    X..X        ",
        #     "    X..XXXXX    ",
        #     "    X..X..X.XX  ",
        #     " XX X..X..X.X.X ",
        #     "X..XX.........X ",
        #     "X...X.........X ",
        #     " X.....X.X.X..X ",
        #     "  X....X.X.X..X ",
        #     "  X....X.X.X.X  ",
        #     "   X...X.X.X.X  ",
        #     "    X.......X   ",
        #     "     X....X.X   ",
        #     "     XXXXX XX   ")
        _HCURS, _HMASK = pygame.cursors.compile(_CLOSE_HAND_CURSOR, ".", "X")
        self._cursor_close_hand = ((16, 16), (5, 1), _HCURS, _HMASK)

    def next_turn(self):
        self.drop_selection()
        if self.player == PLAYER1:
            self.player = PLAYER2
            self.top_panel.turn_label.set_text("Green player turn", colors.GREEN)
        else:
            self.player = PLAYER1
            self.top_panel.turn_label.set_text("Yellow player turn", colors.YELLOW)
        self.wind_type = None
        for model in self.ships + self.ports:
            model.reset()
        self.toggle_pause()

    def toggle_pause(self):
        self._paused = not self._paused

    def game_ended(self):
        if not self.yellow_ships:
            p = PauseMenu(self.screen, "Green won!", color=colors.GREEN)
            p.run()
            return True
        elif not self.green_ships:
            p = PauseMenu(self.screen, "Yellow won!", color=colors.YELLOW)
            p.run()
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
                if ship.coords() not in self.layers_handler.docks_coords:  # Do not move ships that are in ports
                    ship.calculate_moves(self.wind_type, self.wind_direction,
                                         obstacles=self.layers_handler.storm_move_obstacles +
                                                   map(lambda s: s.coords(), self.ships) +
                                                   map(lambda p: p.coords(), self.ports),
                                         step=1)
                    ship.move()
                    ship.check_crash(self.layers_handler.deadly_obstacles)
        self.remove_dead_ships()

    def remove_dead_ships(self):
        self.yellow_ships = filter(lambda s: s.is_alive(), self.yellow_ships)
        self.green_ships = filter(lambda s: s.is_alive(), self.green_ships)
        self.ships = self.yellow_ships + self.green_ships

    def get_camera_offset(self):
        return self.background.offset

    def move_camera(self, delta):
        offset_x, offset_y = self.get_camera_offset()
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
        self.background.fill(colors.BACKGROUND_COLOR)  # fill with water color
        self.background.increase_offset(delta)
        for obj in self.ships + self.ports + \
                [ship.health_bar for ship in self.ships] + \
                [ship.cannon_bar for ship in self.ships] + \
                [port.health_bar for port in self.ports] + \
                [port.cannon_bar for port in self.ports]:
            obj.offset = self.background.offset
            obj.rect = obj.rect.move(delta)
        self.background.draw()

    def start(self):
        background = self.background
        right_top_panel = self.right_top_panel
        background.draw()
        exit_game = False
        ctrl_mode = False
        drag_mode = False
        previous_mouse_pos = None
        pause = PauseMenu(self.screen)
        timer = pygame.time.Clock()
        while not self.game_ended() and not exit_game:
            timer.tick(60)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit("QUIT")
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_LCTRL or e.key == pygame.K_RCTRL):
                    ctrl_mode = True
                if e.type == pygame.KEYUP and (e.key == pygame.K_LCTRL or e.key == pygame.K_RCTRL):
                    ctrl_mode = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                    if ctrl_mode:
                        if self.player == PLAYER1:
                            p = PauseMenu(self.screen, "Green won!", color=colors.GREEN)
                        else:
                            p = PauseMenu(self.screen, "Yellow won!", color=colors.YELLOW)
                        p.run()
                        exit_game = True
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    right_top_panel.end_move()
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_LSHIFT or e.key == pygame.K_RSHIFT):
                    right_top_panel.shoot()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_TAB:
                    right_top_panel.get_wind()
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_UP or e.key == pygame.K_w):
                    self.move_camera((0, 300))
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_DOWN or e.key == pygame.K_s):
                    self.move_camera((0, -300))
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_LEFT or e.key == pygame.K_a):
                    self.move_camera((300, 0))
                if e.type == pygame.KEYDOWN and (e.key == pygame.K_RIGHT or e.key == pygame.K_d):
                    self.move_camera((-300, 0))
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 2:
                    drag_mode = True
                    pygame.mouse.set_cursor(*self._cursor_close_hand)
                    previous_mouse_pos = e.pos
                if e.type == pygame.MOUSEBUTTONUP and e.button == 2:
                    drag_mode = False
                    pygame.mouse.set_cursor(*self._cursor_default)
                    previous_mouse_pos = None
                if e.type == pygame.MOUSEBUTTONDOWN and (e.button == 1 or e.button == 3):
                    clicked = False
                    if not right_top_panel.check_click(e.pos) and not self.minimap.check_click(e.pos):
                        for obj in self.clickable_objects_list:
                            clicked = obj.check_click(e.pos)
                            if clicked:
                                break
                        else:
                            if self.selected_ship:
                                self.selected_ship.unselect()
                                self.selected_ship = None
                                self.redraw()
                    if clicked:
                        # Check whether there's an object
                        if e.button == 1:
                            try:
                                if self.player == PLAYER1:
                                    ships_to_select = self.yellow_ships + self.yellow_ports
                                else:
                                    ships_to_select = self.green_ships + self.green_ports
                                if self.selected_ship:
                                    self.selected_ship.unselect()
                                self.selected_ship = \
                                    filter(lambda obj: obj.coords() == (clicked.coords()), ships_to_select)[0]
                                self.selected_ship.select()
                                self.right_top_panel.shoot_label.set_text("")
                                #print "Object {} clicked".format(selected_ship)
                                if self.selected_ship.is_alive():
                                    shots = self.selected_ship.calculate_shots(
                                        obstacles=self.layers_handler.shoot_obstacles)
                                    highlighted = []
                                    try:
                                        # Highlight possible movements
                                        highlighted = self.\
                                            selected_ship.\
                                            calculate_moves(self.wind_type,
                                                            self.wind_direction,
                                                            obstacles=self.layers_handler.move_obstacles + map(
                                                                lambda x: x.coords(),
                                                                self.ships) + map(lambda x: x.coords(), self.ports),
                                                            docks=self.layers_handler.docks_coords)
                                    except AttributeError, ex:
                                        pass
                                else:
                                    shots = []
                                    highlighted = []
                                self.redraw(LayersHandler.filter_layer(self.highlighted_sea, highlighted) +
                                            LayersHandler.filter_layer(self.fire, shots))
                            except IndexError:
                                if self.selected_ship:
                                    try:
                                        # we clicked on empty sea - move object there
                                        self.selected_ship.move(clicked.coords())
                                    except AttributeError:
                                        pass
                                    self.all_sprites = self.layers_handler.get_all_sprites()
                                    self.redraw()
                                    self.selected_ship = None
                        else:
                            try:
                                targets = self.ships + self.ports
                                target_ship = filter(lambda obj: obj.coords() == (clicked.coords()), targets)[0]
                                if self.selected_ship and self.selected_ship != target_ship:
                                    if self.selected_ship.aim(target_ship):
                                        self.target_ships.append(target_ship)
                            except IndexError:
                                pass
                if drag_mode:
                    cur_mouse_pos = pygame.mouse.get_pos()
                    if cur_mouse_pos != previous_mouse_pos:
                        self.move_camera(map(lambda x, y: x - y, cur_mouse_pos, previous_mouse_pos))
                        previous_mouse_pos = cur_mouse_pos
                        # Process HUD mouse over
            right_top_panel.mouse_over(pygame.mouse.get_pos())
            # end event handing
            self.screen.blit(self.bg_surface, (0, 0))
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            right_top_panel.draw()
            self.top_panel.update()
            self.top_panel.draw()
            self.minimap.draw()
            if self._paused:
                pause.run()
                self.toggle_pause()
            pygame.display.update()
        return False