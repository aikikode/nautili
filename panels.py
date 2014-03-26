#!/usr/bin/env python
import pygame
import pygame.gfxdraw
import random
import colors
from hud import Button, Label
from layers import LayersHandler
from renderer import Renderer
import settings
import wind

__author__ = 'aikikode'


class Panel(object):
    def __init__(self, game, offset, size):
        self.game = game
        self.width, self.height = size
        self.offset = offset
        self.hud_surface = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        self.rect = pygame.Rect(self.offset, size)
        self.hud = Renderer(self.hud_surface)
        self.objects = []

    def get_sprites(self):
        return pygame.sprite.OrderedUpdates(self.objects)

    def draw_sprites(self):
        allsprites = self.get_sprites()
        allsprites.update()
        allsprites.draw(self.game.screen)

    def draw(self):
        self.hud.draw()
        self.draw_sprites()
        self.game.screen.blit(self.hud_surface, self.offset)

    def mouseover(self, event_position):
        for obj in self.objects:
            obj.mouseover(event_position)

    def check_click(self, event_position):
        if self.rect.collidepoint(event_position):
            for obj in self.objects:
                obj.check_click(event_position)
            return True


class RightTopPanel(Panel):
    def __init__(self, game, offset, size):
        Panel.__init__(self, game, offset, size)
        button_font = pygame.font.Font(None, 40)
        self.get_wind_button = Button(button_font, "Wind:", (0, 10),
                                      offset=offset,
                                      on_click=self.get_wind)
        label_font = pygame.font.Font(None, 40)
        self.wind_label = Label(label_font, colors.WHITE, "", (0, 40), offset=offset)
        self.shoot_button = Button(button_font, "Shoot", (0, 80),
                                   offset=offset,
                                   on_click=self.shoot)
        self.shoot_label = Label(label_font, colors.WHITE, "", (0, 110), offset=offset)
        self.end_move_button = Button(button_font, "End move", (0, 170),
                                      offset=offset,
                                      on_click=self.end_move)
        self.objects.append(self.get_wind_button)
        self.objects.append(self.wind_label)
        self.objects.append(self.shoot_button)
        self.objects.append(self.shoot_label)
        self.objects.append(self.end_move_button)

    def get_wind(self):
        self.game.drop_selection()
        self.get_wind_button.disable()
        self.shoot_label.set_text("")
        self.game.wind_type = random.sample(wind.WIND_TYPES, 1)[0]
        self.game.wind_direction = random.sample(wind.WIND_DIRECTIONS, 1)[0]
        if self.game.wind_type == wind.WIND:
            self.wind_label.set_text("{}".format(wind.wind_direction_to_str(self.game.wind_direction)))
        else:
            self.wind_label.set_text("{}".format(wind.wind_type_to_str(self.game.wind_type)))
        if self.game.wind_type == wind.STORM:
            self.game.force_ships_move()

    def shoot(self):
        miss = random.randint(0, 2)
        if self.game.player == settings.PLAYER1:
            ships_to_shoot = self.game.yellow_ships
        else:
            ships_to_shoot = self.game.green_ships
        ships_to_shoot = filter(lambda s: s.has_targets(), ships_to_shoot)
        for ship in ships_to_shoot:
            ship.shoot(not miss)
        if ships_to_shoot:
            if miss:
                self.shoot_label.set_text("missed")
            else:
                self.shoot_label.set_text("hit!")
        self.game.allsprites = self.game.layers_handler.get_all_sprites()
        self.game.remove_dead_ships()
        self.game.drop_selection()

    def end_move(self):
        self.game.next_turn()
        self.get_wind_button.enable()
        self.wind_label.set_text("")
        self.shoot_label.set_text("")


class TopPanel(Panel):
    def __init__(self, game, offset, size):
        Panel.__init__(self, game, offset, size)
        label_header_font = pygame.font.Font(None, 40)
        label_font = pygame.font.Font(None, 25)
        self.turn_label = Label(label_header_font, colors.YELLOW, "Yellow player turn", (10, 10))
        self.yellow_label = Label(label_font, colors.YELLOW, "Yellow", (self.width / 2 - 300, 15))
        self.yellow_counts = Label(label_font, colors.YELLOW, "ships: 0  ports: 0", (self.width / 2 - 240, 15))
        self.green_label = Label(label_font, colors.GREEN, "Green", (self.width / 2 + 90, 15))
        self.green_counts = Label(label_font, colors.GREEN, "ships: 0  ports: 0", (self.width / 2 + 150, 15))
        self.objects.append(self.turn_label)
        self.objects.append(self.yellow_label)
        self.objects.append(self.yellow_counts)
        self.objects.append(self.green_label)
        self.objects.append(self.green_counts)

    def update(self):
        self.yellow_counts.set_text("ships: {}  ports: {}".format(len(self.game.yellow_ships), 0))
        self.green_counts.set_text("ships: {}  ports: {}".format(len(self.game.green_ships), 0))


class MiniMap(Panel):
    def __init__(self, game, offset, size):
        Panel.__init__(self, game, offset, size)
        self.border = pygame.Rect((0, 0), (self.width, self.height))
        orig_map_width, orig_map_height = self.game.layers_handler.get_map_dimensions()
        orig_map_polygon = self.game.layers_handler.get_map_polygon()
        self.scale = max(orig_map_width / float(self.width), orig_map_height / float(self.height))
        self.map_offset = ((self.width - orig_map_width / self.scale) / 2,
                           (self.height - orig_map_height / self.scale) / 2)
        self.sea_polygon = map(lambda p: (p[0] / self.scale + self.map_offset[0],
                                          p[1] / self.scale + self.map_offset[1]),
                               orig_map_polygon)
        self.cam_width = settings.MAIN_WIN_WIDTH / self.scale
        self.cam_height = settings.MAIN_WIN_HEIGHT / self.scale

    def draw_layer(self, layer, color):
        for tile in LayersHandler.filter_not_none(LayersHandler.flatten(layer)):
            pygame.draw.circle(self.hud_surface, color,
                               map(lambda x, offs: int(x/self.scale + offs),
                                   self.game.layers_handler.isometric_to_orthogonal(*tile.coords()), self.map_offset), 1)

    def draw(self):
        self.hud.fill(colors.BLACK)
        self.hud.draw()
        # Draw sea
        pygame.gfxdraw.filled_polygon(self.hud_surface, self.sea_polygon, colors.LIGHT_BLUE)
        # Draw islands, rocks and etc.
        self.draw_layer(self.game.islands, colors.DARK_GREEN)
        self.draw_layer(self.game.rocks, colors.RED)
        self.draw_layer(self.game.yellow_ships, colors.YELLOW)
        self.draw_layer(self.game.green_ships, colors.GREEN)
        # Draw camera rectangle
        camera_offset = map(lambda p, offs: p / -self.scale + offs, self.game.get_camera_offset(), self.map_offset)
        cam_rect = pygame.Rect(camera_offset, (self.cam_width, self.cam_height))
        pygame.draw.rect(self.hud_surface, colors.WHITE, cam_rect, 1)
        pygame.draw.rect(self.hud_surface, colors.WHITE, self.border, 1)
        # Draw additional stuff
        self.draw_sprites()
        self.game.screen.blit(self.hud_surface, self.offset)

    def check_click(self, event_position):
        if self.rect.collidepoint(event_position):
            current_camera_offset = map(lambda p, offs: p / -self.scale + offs, self.game.get_camera_offset(), self.map_offset)
            mouse_minimap_coords = map(lambda x, y: x - y, event_position, self.offset)
            new_camera_offset = (mouse_minimap_coords[0] - self.cam_width / 2, mouse_minimap_coords[1] - self.cam_height / 2)
            self.game.move_camera(map(lambda x, y: (x - y) * self.scale, current_camera_offset, new_camera_offset))
            return True
