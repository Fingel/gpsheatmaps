from PIL import Image, ImageFilter
from numpy import arange
import math
from pudb import set_trace

WITH_ALPHA = False
WITH_TRANSPARENCY = True
MIN_RADIUS = 2  # in px
MAX_RADIUS = 50  # in px
MAX_IMAGE_SIZE = 10000  # in px


def create_image(data, image_width, image_height, spot_radius=20, dimming=75):
    """
    Create a heatmapped image from data.
    Parameters:
    data: Array of Array of tuples (lat, lng)
    """
    image_width = min(MAX_IMAGE_SIZE, max(0, int(image_width)))
    image_height = min(MAX_IMAGE_SIZE, max(0, int(image_height)))
    spot_radius = min(MAX_RADIUS, max(MIN_RADIUS, int(spot_radius)))
    dimming = min(255, max(0, int(dimming)))

    image = Image.new('RGBA', (image_width, image_height), "white")
    pixel_map = image.load()
    for datum in data:
        if len(datum) == 1:
            pixel_map = draw_circular_gradient(pixel_map, datum[0][0], datum[0][1], image_width, image_height, spot_radius, dimming)
        else:
            for i in xrange(0, len(datum) - 1):
                pixel_map = draw_bilinear_gradient(pixel_map, datum[i], datum[i + 1], image_width, image_height, spot_radius, dimming)

    gradient = create_gradient()
    gradient_size = len(gradient)

    # Traverse the image, get value of pixel and assign the the color
    # from the corresponding index in the gradient array
    for x in xrange(image_width):
        for y in xrange(image_height):
            value = pixel_map[x, y][0]  # greyscale so just get red
            if value == 255:
                pixel_map[x, y] = (255, 255, 255, 0) # make white transparent
            elif value < gradient_size:
                pixel_map[x, y] = gradient[value]

    if spot_radius >= 30:
        image = image.filter(ImageFilter.BLUR)

    return image


def draw_circular_gradient(pixel_map, center_x, center_y, image_width, image_height, spot_radius, dimming):
    dirty = {}
    ratio = (255 - dimming) / spot_radius
    for r in xrange(spot_radius, 0, -1):
        channel = dimming + r * ratio
        angle_step = 0.45 / r
        for angle in arange(0, math.pi * 2, angle_step):
            x = max(0, min(image_width - 1, int(math.floor(center_x + r * math.cos(angle)))))
            y = max(0, min(image_height - 1 , int(math.floor(center_y + r * math.sin(angle)))))
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


def draw_bilinear_gradient(pixel_map, point0, point1, image_width, image_height, spot_radius, dimming):
    if point0[0] < point1[0]:
        x0 = point0[0]
        y0 = point0[1]
        x1 = point1[0]
        y1 = point1[1]
    else:
        x0 = point1[0]
        y0 = point1[1]
        x1 = point0[0]
        y1 = point0[1]

    if x0 == x1 and y0 == y1:
        return False

    steep = True if abs(y1 - y0) > abs(x1 - x0) else False
    if steep:
        x0, y0 = y0, x0  # swap
        x1, y1, = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    deltax = x1 - x0
    deltay = abs(y1 - y0)
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
                pixel_map = draw_circular_gradient(pixel_map, y, x, image_width, image_height, spot_radius, dimming)
            else:
                pixel_map = draw_circular_gradient(pixel_map, x, y, image_width, image_height, spot_radius, dimming)
        error -= deltay
        if(error < 0):
            y = y + ystep
            error = error + deltax

    return pixel_map


def create_gradient(gradient_f="gradient.png"):
    """
    Open an image of a gradient and pick out
    its colors along the x axis. Return them as
    an array
    """
    image = Image.open(gradient_f)
    gradient = image.load()
    width_g, height_g = image.size
    grad_rgba = []
    for x in xrange(width_g - 1, 0, -1):
        r, g, b, a = gradient[x, 1]
        grad_rgba.append((r, g, b, a))
    return grad_rgba
