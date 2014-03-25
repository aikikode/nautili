#!/usr/bin/env python
import os
import pygame
from PIL import Image
from colors import WHITE
import game
from hud import Button, Label
from settings import DISPLAY, WIN_HEIGHT, WIN_WIDTH, MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT

__author__ = 'aikikode'


class Menu(object):
    def __init__(self):
        self.screen = None
        self.objects = []

    def get_sprites(self):
        return pygame.sprite.OrderedUpdates(self.objects)

    def draw_sprites(self):
        allsprites = self.get_sprites()
        allsprites.update()
        allsprites.draw(self.screen)


class MainMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        pygame.init()
        self.width, self.height = DISPLAY
        self.screen = pygame.display.set_mode(DISPLAY)
        pygame.display.set_caption("Nautili")
        self.button_font = pygame.font.Font(None, 60)
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        image = os.path.join("tilesets", "bg.png")
        self.bg_image = Image.open(image)
        self.pygame_bg_image = pygame.image.load(image)
        self.new_game_button = Button(self.button_font, "New game",
                                      (self.width / 2 - 110, self.height / 2 - 60),
                                      on_click=self.new_game)
        self.exit_button = Button(self.button_font, "Exit", (self.width / 2 - 45, self.height / 2),
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
        self.screen.blit(self.bg_surface, (0, 0))
        self.draw_sprites()
        pygame.display.update()

    def run(self):
        while 1:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit, "QUIT"
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.check_click(e.pos)
            self.mouseover(pygame.mouse.get_pos())
            self.redraw()


class PauseMenu(Menu):
    def __init__(self, screen, text="Other player turn"):
        Menu.__init__(self)
        self.width, self.height = DISPLAY
        self.screen = screen
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        image = os.path.join("tilesets", "shade.png")
        self.bg_image = Image.open(image)
        self.pygame_bg_image = pygame.image.load(image)
        label_font = pygame.font.Font(None, 50)
        prompt_font = pygame.font.Font(None, 30)
        pause_label = Label(label_font, WHITE, text,
                                  (MAIN_WIN_WIDTH / 2 - 135, MAIN_WIN_HEIGHT / 2 - 90))
        prompt_label = Label(prompt_font, WHITE, "Press Spacebar to continue",
                                 (MAIN_WIN_WIDTH / 2 - 130, MAIN_WIN_HEIGHT / 2 - 40))
        self.objects = []
        self.objects.append(prompt_label)
        self.objects.append(pause_label)
        self.draw()

    def draw(self):
        ypos = 0
        while ypos <= self.height:
            xpos = 0
            while xpos <= self.width:
                self.bg_surface.blit(self.pygame_bg_image, (xpos, ypos))
                xpos += self.bg_image.size[0]
            ypos += self.bg_image.size[1]

    def show(self):
        self.screen.blit(self.bg_surface, (0, 0))
        self.draw_sprites()


class OptionsMenu(Menu):
    pass
