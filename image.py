# coding=utf8

#
# python-aosd -- python bindings for libaosd
#
# Copyright (C) 2010 Armin Häberling <armin.aha@gmail.com>
#
# Based on the image example from libaosd.
#

import sys
import pygame
pygame.display.init()
import cairo

import aosd

MARGIN = 10
RADIUS = 20
WIDTH = 185
HEIGHT = 220

def round_rect(context, x, y, w, h, r):
    context.new_path()
    context.move_to(x+r, y)
    context.line_to(x+w-r, y) # top edge
    context.curve_to(x+w, y, x+w, y, x+w, y+r)
    context.line_to(x+w, y+h-r) # right edge
    context.curve_to(x+w, y+h, x+w, y+h, x+w-r, y+h)
    context.line_to(x+r, y+h) # bottom edge
    context.curve_to(x, y+h, x, y+h, x, y+h-r)
    context.line_to(x, y+r) # left edge
    context.curve_to(x, y, x, y, x+r, y)
    context.close_path()


def render(context, data):
    image = data['image']
    width = image.get_width()
    height = image.get_height()

    context.set_source_rgba(0, 0, 0, 1)
#    round_rect(context, 0, 0, width + (2 * MARGIN),
#        height + (2 * MARGIN), RADIUS)
    context.fill()

    context.save()
    context.set_source_surface(image, MARGIN, MARGIN)
    context.paint_with_alpha(50 / 100.0)
    context.restore()

def main(argv):
#    image = cairo.ImageSurface.create_from_png(options.filename)
    image = pygame.image.load(argv[1]).convert(32)
    width  = image.get_width()
    height = image.get_height()
    image = cairo.ImageSurface.create_for_data(pygame.surfarray.pixels2d(image).data, cairo.FORMAT_RGB24, width, height)
    osd = aosd.Aosd()
    osd.set_transparency(aosd.TRANSPARENCY_COMPOSITE)
    osd.set_position(4, width + 2 * MARGIN, height + 2 * MARGIN)
#    osd.set_position_offset(250, 500)
    osd.set_renderer(render, {'image': image})
    osd.flash(300, 3000, 300)
    osd.show()
    print dir(osd)
    from time import sleep
    print '.',
    sleep(1)
    print '.',
    sleep(1)
    print '.',
    sleep(1)
    print '.',
    osd.hide()


if __name__ == "__main__":
    main(sys.argv)

