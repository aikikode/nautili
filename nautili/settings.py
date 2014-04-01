#!/usr/bin/env python
import os

__author__ = 'aikikode'

WIN_WIDTH = 1440
WIN_HEIGHT = 1080
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
