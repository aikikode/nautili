#!/usr/bin/env python
import pygame

__author__ = 'aikikode'


class BaseTexture(object):
    def __init__(self, tile, x, y, rect):
        self.tile = tile
        self.x = x
        self.y = y
        self.rect = rect

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.x, self.y)

    def coords(self):
        return self.x, self.y

    def check_click(self, event_position):
        return None


class SpriteTexture(pygame.sprite.Sprite):
    def __init__(self, tile, x, y, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = tile
        self.x = x
        self.y = y
        self.rect = rect
        self.rect.topleft = (rect.x - 16, rect.y - 30)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.x, self.y)

    def coords(self):
        return self.x, self.y


class Sea(BaseTexture):
    def check_click(self, event_position):
        if self.rect.collidepoint(event_position):
            #print "Clicked on " + repr(self)
            return self
        return None


class Rock(BaseTexture):
    pass


class Island(BaseTexture):
    pass
