#!/usr/bin/env python
import os
import pygame
from PIL import Image
import game
from hud import Button
from renderer import Renderer
from settings import DISPLAY, WIN_HEIGHT, WIN_WIDTH

__author__ = 'aikikode'


class MainMenu(object):
    def __init__(self):
        pygame.init()
        self.width, self.height = DISPLAY
        self.screen = pygame.display.set_mode(DISPLAY)
        pygame.display.set_caption("Nautili")
        self.button_font = pygame.font.Font(None, 60)
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        image = os.path.join("tilesets", "bg.png")
        self.bg_image = Image.open(image)
        self.pygame_bg_image = pygame.image.load(image)
        self.renderer = Renderer(self.bg_surface)
        self.new_game_button = Button(self.bg_surface, self.button_font, "New game",
                                      (self.width / 2 - 110, self.height / 2 - 60),
                                      on_click=self.new_game)
        self.exit_button = Button(self.bg_surface, self.button_font, "Exit", (self.width / 2 - 45, self.height / 2),
                                  on_click=self.exit)
        self.objects = []
        self.objects.append(self.new_game_button)
        self.objects.append(self.exit_button)

    def mouseover(self, event_position):
        for obj in self.objects:
            obj.mouseover(event_position)

    def check_click(self, event_position):
        for obj in self.objects:
            obj.check_click(event_position)

    def new_game(self):
        g = game.Game()
        g.start()

    def exit(self):
        raise SystemExit, "QUIT"

    def redraw(self):
        self.bg_surface.fill([21, 37, 45])
        ypos = 0
        while ypos <= self.height:
            xpos = 0
            while xpos <= self.width:
                self.bg_surface.blit(self.pygame_bg_image, (xpos, ypos))
                xpos += self.bg_image.size[0]
            ypos += self.bg_image.size[1]
        for obj in self.objects:
            obj.draw()
        self.screen.blit(self.bg_surface, (0, 0))
        pygame.display.update()

    def run(self):
        while 1:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit, "QUIT"
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.check_click(e.pos)
            for obj in self.objects:
                obj.draw()
            self.mouseover(pygame.mouse.get_pos())
            self.redraw()


class OptionsMenu(object):
    pass
