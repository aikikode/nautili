#!/usr/bin/env python
import pygame
import random
import colors
from hud import Button, Label
from renderer import Renderer
from settings import PLAYER1, PLAYER2
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
        self.get_wind_button = Button(button_font, "Wind:", (self.width / 2 - 80, 10),
                                      offset=offset,
                                      on_click=self.get_wind)
        label_font = pygame.font.Font(None, 40)
        self.wind_label = Label(label_font, colors.WHITE, "", (self.width / 2 - 80, 40), offset=offset)
        self.shoot_button = Button(button_font, "Shoot", (self.width / 2 - 80, 80),
                                   offset=offset,
                                   on_click=self.shoot)
        self.end_move_button = Button(button_font, "End move", (self.width / 2 - 80, 140),
                                      offset=offset,
                                      on_click=self.end_move)
        self.objects.append(self.get_wind_button)
        self.objects.append(self.wind_label)
        self.objects.append(self.shoot_button)
        self.objects.append(self.end_move_button)

    def get_wind(self):
        self.get_wind_button.disable()
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
        if self.game.player == PLAYER1:
            ships_to_shoot = self.game.yellow_ships
        else:
            ships_to_shoot = self.game.green_ships
        for ship in ships_to_shoot:
            ship.shoot(not miss)
        self.game.allsprites = self.game.layers_handler.get_all_sprites()
        self.game.remove_dead_ships()

    def end_move(self):
        self.game.next_turn()
        self.get_wind_button.enable()
        self.wind_label.set_text("")

    def draw(self):
        self.hud.draw()
        pygame.draw.line(self.hud_surface, (44, 92, 118), [0, 0], [self.width, 0], 2)
        self.draw_sprites()
        self.game.screen.blit(self.hud_surface, self.offset)


class LeftTopPanel(Panel):
    def __init__(self, game, offset, size):
        Panel.__init__(self, game, offset, size)
        label_font = pygame.font.Font(None, 40)
        self.label = Label(label_font, colors.YELLOW, "Yellow player turn", (10, 10))
        self.objects.append(self.label)
