#!/usr/bin/env python
import os
import pygame
import shutil
from PIL import Image
from nautili import colors
from nautili.hud import Button, Label
from nautili.settings import DISPLAY, WIN_HEIGHT, WIN_WIDTH, MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, TMP_DIR, HUD_DIR, MODELS_DIR, MISC_DIR

__author__ = 'aikikode'


class Menu(object):
    def __init__(self):
        self.screen = None
        self.objects = []

    def get_sprites(self):
        return pygame.sprite.OrderedUpdates(self.objects)

    def draw_sprites(self):
        all_sprites = self.get_sprites()
        all_sprites.update()
        all_sprites.draw(self.screen)


class BaseMainMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        pygame.init()
        self.width, self.height = DISPLAY
        self.screen = pygame.display.set_mode(DISPLAY)
        pygame.display.set_icon(pygame.image.load(os.path.join(MISC_DIR, "icon.png")).convert_alpha())
        pygame.display.set_caption("Nautili")
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        image = os.path.join(HUD_DIR, "bg.png")
        self.bg_image = Image.open(image)
        self.pygame_bg_image = pygame.image.load(image)
        self.objects = []

    def mouse_over(self, event_position):
        for obj in self.objects:
            obj.mouse_over(event_position)

    def check_click(self, event_position):
        for obj in self.objects:
            obj.check_click(event_position)

    def redraw(self):
        self.bg_surface.fill(colors.BACKGROUND_COLOR)
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
            if not self.process_events():
                break
            self.redraw()

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit, "QUIT"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return False
        self.mouse_over(pygame.mouse.get_pos())
        return True


class MainMenu(BaseMainMenu):
    def __init__(self):
        BaseMainMenu.__init__(self)
        self.button_font = pygame.font.Font(None, 60)
        self.new_game_button = Button(self.button_font, "New game",
                                      (self.width / 2 - 110, self.height / 2 - 60),
                                      on_click=self.new_game)
        self.exit_button = Button(self.button_font, "Exit", (self.width / 2 - 45, self.height / 2),
                                  on_click=self.exit)
        self.objects.append(self.new_game_button)
        self.objects.append(self.exit_button)

    def new_game(self):
        l = LoadMapMenu()
        l.run()

    def exit(self):
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        raise SystemExit, "QUIT"

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit, "QUIT"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                return False
        self.mouse_over(pygame.mouse.get_pos())
        return True


class LoadMapMenu(BaseMainMenu):
    MAP_DIR = "maps"

    def __init__(self):
        BaseMainMenu.__init__(self)
        label_font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 30)
        label = Label(label_font, colors.WHITE, "Select a map from the list below",
                            (self.width / 2 - 250, 80))
        self.objects.append(label)
        self.read_map_dir()

    def read_map_dir(self):
        map_files = [os.path.splitext(f)[0] for f in os.listdir(LoadMapMenu.MAP_DIR)
                     if os.path.isfile(os.path.join(LoadMapMenu.MAP_DIR, f)) and os.path.splitext(f)[1] == ".tmx"]
        map_files.sort()
        for num, map_file in enumerate(map_files):
            button = Button(self.button_font, map_file, (self.width / 2 - 50, 140 + num * 30),
                            on_click=self.load_map, args=[map_file])
            self.objects.append(button)

    def load_map(self, map_file):
        map = os.path.join(LoadMapMenu.MAP_DIR, map_file + ".tmx")
        try:
            from nautili import game
            g = game.Game(map)
            g.start()
        except ValueError:
            pass


class PauseMenu(Menu):
    def __init__(self, screen, text="Other player turn", color=colors.WHITE):
        Menu.__init__(self)
        self.width, self.height = DISPLAY
        self.screen = screen
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        image = os.path.join("./data/hud", "shade.png")
        self.bg_image = Image.open(image)
        self.pygame_bg_image = pygame.image.load(image)
        label_font = pygame.font.Font(None, 50)
        prompt_font = pygame.font.Font(None, 30)
        delta = 135/17. * len(text) # x delta based on font size
        self.pause_label = Label(label_font, color, text,
                                  (MAIN_WIN_WIDTH / 2 - delta, MAIN_WIN_HEIGHT / 2 - 90))
        prompt_label = Label(prompt_font, colors.WHITE, "Press Spacebar to continue",
                                 (MAIN_WIN_WIDTH / 2 - 130, MAIN_WIN_HEIGHT / 2 - 40))
        self.objects = []
        self.objects.append(prompt_label)
        self.objects.append(self.pause_label)

    def mouse_over(self, event_position):
        for obj in self.objects:
            obj.mouse_over(event_position)

    def check_click(self, event_position):
        for obj in self.objects:
            obj.check_click(event_position)

    def draw(self):
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ypos = 0
        while ypos <= self.height:
            xpos = 0
            while xpos <= self.width:
                self.bg_surface.blit(self.pygame_bg_image, (xpos, ypos))
                xpos += self.bg_image.size[0]
            ypos += self.bg_image.size[1]
        self.screen.blit(self.bg_surface, (0, 0))
        self.draw_sprites()

    def run(self):
        self.draw()
        while 1:
            if not self.process_events():
                break
            pygame.display.update()

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit, "QUIT"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return False
        self.mouse_over(pygame.mouse.get_pos())
        return True


class OptionsMenu(Menu):
    pass