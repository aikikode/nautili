#!/usr/bin/env python
"""
Helper module holding wind types and directions
"""
__author__ = 'aikikode'

STILLE = 0
WIND = 1
STORM = 2
WIND_TYPES = [STILLE, WIND, STORM]

NORTH = 3
SOUTH = 4
EAST = 5
WEST = 6
NORTH_EAST = 7
NORTH_WEST = 8
SOUTH_EAST = 9
SOUTH_WEST = 10
WIND_DIRECTIONS = [NORTH, SOUTH, EAST, WEST, NORTH_EAST, NORTH_WEST, SOUTH_EAST, SOUTH_WEST]


def wind_type_to_str(w):
    if w == STILLE:
        return "stille"
    elif w == WIND:
        return "wind"
    elif w == STORM:
        return "storm"
    else:
        return "Unknown wind type: {}".format(w)


def wind_direction_to_str(wd):
    if wd == NORTH:
        return "north"
    elif wd == SOUTH:
        return "south"
    elif wd == EAST:
        return "east"
    elif wd == WEST:
        return "west"
    elif wd == NORTH_EAST:
        return "north_east"
    elif wd == NORTH_WEST:
        return "north_west"
    elif wd == SOUTH_EAST:
        return "south_east"
    elif wd == SOUTH_WEST:
        return "south_west"
    else:
        return "Unknown wind direction: {}".format(wd)
