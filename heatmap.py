from PIL import Image, ImageFilter
from numpy import arange
import math
from pudb import set_trace

WITH_ALPHA = False
WITH_TRANSPARENCY = True
MIN_RADIUS = 2  # in px
MAX_RADIUS = 50  # in px
MAX_IMAGE_SIZE = 10000  # in px


class HeatMapPoint:

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return 'HeatMapPoint(x=%s, y=%s)' % (self.x, self.y)


def create_image(data, image_width, image_height, alpha_mode=False, spot_radius=30, dimming=75):
    image_width = min(MAX_IMAGE_SIZE, max(0, int(image_width)))
    image_height = min(MAX_IMAGE_SIZE, max(0, int(image_height)))
    spot_radius = min(MAX_RADIUS, max(MIN_RADIUS, int(spot_radius)))
    dimming = min(255, max(0, int(dimming)))

    image = Image.new('RGBA', (image_width, image_height), "white")
    pixel_map = image.load()
    for datum in data:
        if len(datum) == 1:
            pixel_map = draw_circular_gradient(pixel_map, datum[0].x, datum[0].y, spot_radius, dimming)
        else:
            for i in xrange(len(datum)):
                pixel_map = draw_bilinear_gradient(pixel_map, datum[i], datum[i + 1], spot_radius, dimming)

    if spot_radius >= 30:
        image = image.filter(ImageFilter.BLUR)

    gradient = create_gradient(image, alpha_mode)
    gradient_size = len(gradient)

    for x in xrange(image_width):
        for y in xrange(image_height):
            level = pixel_map[x, y][3]  # & 0xFF
            if level >= 0 and level < gradient_size:
                pixel_map[x, y][3] = gradient[level]

    # might need to make some stuff transparent here
    image.save('/home/austin/heat.png')
    return image


def draw_circular_gradient(pixel_map, center_x, center_y, spot_radius, dimming):
    # set_trace()
    dirty = {}
    ratio = (255 - dimming) / spot_radius
    for r in xrange(spot_radius, 0, -1):
        channel = dimming + r * ratio
        angle_step = 0.45 / r
        for angle in arange(0, math.pi * 2, angle_step):
            x = int(math.floor(center_x + r * math.cos(angle)))
            y = int(math.floor(center_y + r * math.sin(angle)))
            try:
                _ = dirty[(x, y)]
            except KeyError:
                dirty[(x, y)] = False
            if not dirty[(x, y)]:
                previous_channel = pixel_map[x, y][0]  # greyscale image so just get red
                new_channel = max(0, min(255, (previous_channel * channel) / 255))
                pixel_map[x, y] = (new_channel, new_channel, new_channel)
                dirty[(x, y)] = True
    return pixel_map


def draw_bilinear_gradient(pixel_map, point0, point1, spot_radius, dimming):
    if point0.x < point1.x:
        x0 = point0.x
        y0 = point0.y
        x1 = point1.x
        y1 = point1.y
    else:
        x0 = point1.x
        y0 = point1.y
        x1 = point0.x
        y1 = point0.y

    if x0 == x1 and y0 == y1:
        return False

    steep = True if math.abs(y1 - y0) > math.abs(x1 - x0) else False
    if steep:
        x0, y0 = y0, x0  # swap
        x1, y1, = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    deltax = x1 = x0
    deltay = math.abs(y1 - y0)
    error = deltax / 2
    y = y0
    if y0 < y1:
        ystep = 1
    else:
        ystep = -1
    step = max(1, math.floor(spot_radius / 3))
    for x in xrange(x0, x1, 1):
        if ((x - x0) % step) == 0:
            if(steep):
                pixel_map = draw_circular_gradient(pixel_map, y, x, spot_radius, dimming)
            else:
                pixel_map = draw_circular_gradient(pixel_map, x, y, spot_radius, dimming)
        error -= deltay
        if(error < 0):
            y = y + ystep
            error = error + deltax

    return pixel_map


def create_gradient(pixel_map, mode):
    image = Image.open("gradient.png")
    gradient = image.load()
    width_g, height_g = image.size
    grad_rgba = []
    for y in reversed(xrange(height_g - 1)):
        r, g, b, a = gradient[1, y]
        alpha = min(127, max(0, math.floor(127 - y / 2)))
        if mode == WITH_ALPHA:
            grad_rgba.append((r, g, b, alpha))
        else:
            grad_rgba.append((r, g, b))

    return grad_rgba