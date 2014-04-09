#!/usr/bin/env python
import os
import pygame
import shutil
from PIL import Image
from nautili import colors
from nautili.hud import Button, Label
from nautili.settings import DISPLAY, WIN_HEIGHT, WIN_WIDTH, MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, TMP_DIR, HUD_DIR, MISC_DIR, \
    MAP_DIR, SAVED_GAMES_DIR

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
        bg_image = pygame.image.load(os.path.join(HUD_DIR, "sea.jpg"))
        self.pygame_bg_image = pygame.transform.scale(bg_image, DISPLAY)
        self.objects = []

    def mouse_over(self, event_position):
        for obj in self.objects:
            obj.mouse_over(event_position)

    def check_click(self, event_position):
        for obj in self.objects:
            obj.check_click(event_position)

    def redraw(self):
        self.bg_surface.fill(colors.BACKGROUND_COLOR)
        self.bg_surface.blit(self.pygame_bg_image, (0, 0))
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
                raise SystemExit("QUIT")
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
        text = "New game"
        text_width = self.button_font.size(text)[0]
        self.new_game_button = Button(self.button_font, text,
                                      ((self.width - text_width) / 2, self.height / 2 - 130),
                                      colors=(colors.BLACK, colors.WHITE),
                                      on_click=self.new_game)
        text = "Load game"
        text_width = self.button_font.size(text)[0]
        self.load_game_button = Button(self.button_font, text,
                                       ((self.width - text_width) / 2, self.height / 2 - 60),
                                       colors=(colors.BLACK, colors.WHITE),
                                       on_click=self.load_game)
        text = "Exit"
        text_width = self.button_font.size(text)[0]
        self.exit_button = Button(self.button_font, text, ((self.width - text_width) / 2, self.height / 2),
                                  colors=(colors.BLACK, colors.WHITE),
                                  on_click=self.exit)
        self.objects.append(self.new_game_button)
        self.objects.append(self.load_game_button)
        self.objects.append(self.exit_button)

    def new_game(self):
        try:
            l = LoadMapMenu()
            l.run()
        except ExitToMainMenuException:
            pass

    def load_game(self):
        try:
            l = LoadGameMenu()
            l.run()
        except ExitToMainMenuException:
          pass

    def exit(self):
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        raise SystemExit("QUIT")

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit("QUIT")
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                return False
        self.mouse_over(pygame.mouse.get_pos())
        return True


class LoadMapMenu(BaseMainMenu):
    def __init__(self):
        BaseMainMenu.__init__(self)
        label_font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 30)
        text = "Choose the map"
        text_width = label_font.size(text)[0]
        label = Label(label_font, colors.BLACK, text,
                      (((self.width / 3) - text_width) / 2, 80))
        self.objects.append(label)
        self.read_map_dir()

    def read_map_dir(self):
        map_files = [os.path.splitext(f)[0] for f in os.listdir(MAP_DIR)
                     if os.path.isfile(os.path.join(MAP_DIR, f)) and os.path.splitext(f)[1] == ".tmx"]
        map_files.sort()
        for num, map_file in enumerate(map_files):
            text_width, text_height = self.button_font.size(map_file)
            button = Button(self.button_font, map_file, (((self.width / 3) - text_width)/2 + (1 if num % 2 == 0 else 2)*self.width/3, 40 + (text_height*1.2)*(num / 2)),
                            colors=(colors.BLACK, colors.WHITE),
                            on_click=self.load_map, args=[map_file])
            self.objects.append(button)

    def load_map(self, map_filename):
        try:
            from nautili import game
            g = game.Game(map_filename)
            g.start()
        except ValueError:
            pass

    def process_events(self):
        scroll_step = 30
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit("QUIT")
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return False
            if (e.type == pygame.KEYDOWN and (e.key == pygame.K_DOWN or e.key == pygame.K_s)) or\
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 5):
                # scroll down
                last_obj = self.objects[-1]
                if last_obj.pos[1] > self.height - 40:
                    for obj in self.objects:
                        obj.pos = map(lambda x, y: x + y, obj.pos, (0, -scroll_step))
            if (e.type == pygame.KEYDOWN and (e.key == pygame.K_UP or e.key == pygame.K_w)) or\
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 4):
                # scroll up
                first_obj = self.objects[1]
                if first_obj.pos[1] < 40:
                    for obj in self.objects:
                        obj.pos = map(lambda x, y: x + y, obj.pos, (0, scroll_step))
        self.mouse_over(pygame.mouse.get_pos())
        return True


class LoadGameMenu(BaseMainMenu):
    def __init__(self):
        BaseMainMenu.__init__(self)
        label_font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 30)
        text = "Choose the savegame"
        text_width = label_font.size(text)[0]
        label = Label(label_font, colors.BLACK, text,
                      (((self.width / 3) - text_width) / 2, 80))
        self.objects.append(label)
        self.read_savegame_dir()

    def read_savegame_dir(self):
        saved_games = [os.path.splitext(f)[0] for f in os.listdir(SAVED_GAMES_DIR)
                     if os.path.isfile(os.path.join(SAVED_GAMES_DIR, f)) and os.path.splitext(f)[1] == ".sav"]
        saved_games.sort()
        for num, saved_game in enumerate(saved_games):
            text_width, text_height = self.button_font.size(saved_game)
            button = Button(self.button_font, saved_game, (((self.width / 3) - text_width)/2 + (1 if num % 2 == 0 else 2)*self.width/3, 40 + (text_height*1.2)*(num / 2)),
                            colors=(colors.BLACK, colors.WHITE),
                            on_click=self.load_game, args=[saved_game])
            self.objects.append(button)

    def load_game(self, saved_game_file):
        saved_game = os.path.join(SAVED_GAMES_DIR, saved_game_file + ".sav")
        try:
            from nautili import game
            g = game.Game.load(saved_game)
            g.start()
        except ValueError:
            pass

    def process_events(self):
        scroll_step = 30
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit("QUIT")
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return False
            if (e.type == pygame.KEYDOWN and (e.key == pygame.K_DOWN or e.key == pygame.K_s)) or\
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 5):
                # scroll down
                last_obj = self.objects[-1]
                if last_obj.pos[1] > self.height - 40:
                    for obj in self.objects:
                        obj.pos = map(lambda x, y: x + y, obj.pos, (0, -scroll_step))
            if (e.type == pygame.KEYDOWN and (e.key == pygame.K_UP or e.key == pygame.K_w)) or\
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 4):
                # scroll up
                first_obj = self.objects[1]
                if first_obj.pos[1] < 40:
                    for obj in self.objects:
                        obj.pos = map(lambda x, y: x + y, obj.pos, (0, scroll_step))
        self.mouse_over(pygame.mouse.get_pos())
        return True


class PauseMenu(Menu):
    def __init__(self, screen, text="Other player turn", color=colors.WHITE):
        Menu.__init__(self)
        self.width, self.height = DISPLAY
        self.screen = screen
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        image = os.path.join("./data/hud", "shade.png")
        self.bg_image = Image.open(image)
        self.pygame_bg_image = pygame.image.load(image)
        self.objects = []
        if text:
            label_font = pygame.font.Font(None, 50)
            text_width = label_font.size(text)[0]
            self.pause_label = Label(label_font, color, text,
                                     ((MAIN_WIN_WIDTH - text_width) / 2, MAIN_WIN_HEIGHT / 2 - 90))
            self.objects.append(self.pause_label)
        prompt_text = "Press Spacebar to continue"
        prompt_font = pygame.font.Font(None, 30)
        text_width = prompt_font.size(prompt_text)[0]
        prompt_label = Label(prompt_font, colors.WHITE, prompt_text,
                             ((MAIN_WIN_WIDTH - text_width) / 2, MAIN_WIN_HEIGHT / 2 - 40))
        self.objects.append(prompt_label)

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
                raise SystemExit("QUIT")
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.check_click(e.pos)
            if e.type == pygame.KEYDOWN and (e.key == pygame.K_SPACE or e.key == pygame.K_ESCAPE):
                return False
        self.mouse_over(pygame.mouse.get_pos())
        return True


class ExitToMainMenuException(Exception):
    pass


class GameMenu(PauseMenu):
    def __init__(self, game, screen, text="", color=colors.WHITE):
        PauseMenu.__init__(self, screen, text, color)
        self.game = game
        self.button_font = pygame.font.Font(None, 50)
        text = "Save and exit"
        text_width = self.button_font.size(text)[0]
        self.save_game_button = Button(self.button_font, text,
                                       ((self.width - text_width) / 2, self.height / 2 - 150),
                                       on_click=self.save_game)
        self.objects.append(self.save_game_button)
        text = "Exit without saving"
        text_width = self.button_font.size(text)[0]
        self.exit_game_button = Button(self.button_font, text,
                                       ((self.width - text_width) / 2, self.height / 2 - 100),
                                       on_click=self.exit_game)
        self.objects.append(self.exit_game_button)
        step = 20
        top = min(self.save_game_button.rect.top, self.exit_game_button.rect.top)
        left = min(self.save_game_button.rect.left, self.exit_game_button.rect.left)
        right = max(self.save_game_button.rect.right, self.exit_game_button.rect.right)
        bottom = max(self.save_game_button.rect.bottom, self.exit_game_button.rect.bottom) + 40
        self.menu_border = pygame.Rect((left - step, top - step), (right - left + 2*step, bottom - top + 2*step))

    def save_game(self):
        self.game.save_game()
        self.exit_game()

    def exit_game(self):
        raise ExitToMainMenuException()

    def draw(self):
        self.bg_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        ypos = 0
        while ypos <= self.height:
            xpos = 0
            while xpos <= self.width:
                self.bg_surface.blit(self.pygame_bg_image, (xpos, ypos))
                xpos += self.bg_image.size[0]
            ypos += self.bg_image.size[1]
        pygame.draw.rect(self.bg_surface, colors.WHITE, self.menu_border, 1)
        self.screen.blit(self.bg_surface, (0, 0))
        self.draw_sprites()
