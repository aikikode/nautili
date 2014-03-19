#!/usr/bin/env python
__author__ = 'aikikode'


class BaseTexture(object):
    def __init__(self, x, y, rect):
        self.x = x
        self.y = y
        self.rect = rect

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.x, self.y)

    def coords(self):
        return self.x, self.y

    def check_click(self, event_position):
        return None


class Sea(BaseTexture):
    def check_click(self, event_position):
        if self.rect.collidepoint(event_position):
            #print "Clicked on " + repr(self)
            return self
        return None


class Island(BaseTexture):
    pass


class Rock(Island):
    pass
