#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pygame

try:
    infoObject = pygame.display.Info()
except pygame.error:  # pygame hadn't been initialized
    pygame.init()
    infoObject = pygame.display.Info()


MONITOR_WIDTH = infoObject.current_w
MONITOR_HEIGHT = infoObject.current_h
win_delta = 100
WIN_WIDTH = MONITOR_WIDTH - win_delta
WIN_HEIGHT = MONITOR_HEIGHT - win_delta
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)

MAIN_WIN_WIDTH = WIN_WIDTH
MAIN_WIN_HEIGHT = WIN_HEIGHT
RIGHT_PANEL_WIDTH = 200
RIGHT_PANEL_HEIGHT = 500
TOP_PANEL_WIDTH = MAIN_WIN_WIDTH
TOP_PANEL_HEIGHT = 50

MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150

PLAYER1 = "yellow"
PLAYER2 = "green"
NEUTRAL_PLAYER = "neutral"

TMP_DIR = ".tmp"
MODELS_DIR = os.path.join("data", "models")
HUD_DIR = os.path.join("data", "hud")
MISC_DIR = os.path.join("data", "misc")
MAP_DIR = "maps"
SAVED_GAMES_DIR = "saves"
