#!/usr/bin/env python
"""
Helper module holding wind types and directions
"""
import random

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


def get_random_with_probability(prob_distr):
    assert prob_distr
    r = random.uniform(0, 1)
    s = 0
    for item in prob_distr:
        s += item[1]
        if s >= r:
            return item[0]


def get_random_wind(prob_distr=None):
    if not prob_distr:
        prob_distr = [[STILLE, 0.1], [STORM, 0.1], [WIND, 0.8]]
    return get_random_with_probability(prob_distr)


def get_random_direction():
    return random.sample(WIND_DIRECTIONS, 1)[0]


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
