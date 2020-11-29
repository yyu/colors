#!/usr/bin/env python3

import re
import fileinput
import time

shades = (0, 95, 135, 175, 215, 255)

def closest_shade(x):
    """Find the closest shade to a given x.
    This is not optimal, nor is it very pythonic, but it's ok when shade array is small.
    """
    delta_min = 256
    closest_shade = 0
    for shade in shades:
        if abs(shade - x) < delta_min:
            delta_min = abs(shade -x)
            closest_shade = shade
    return closest_shade

class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __hash__(self):
        return self.r << 16 | self.g << 8 | self.b

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __repr__(self):
        return '(%3d, %3d, %3d)' % (self.r, self.g, self.b)

    def to_html(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)

    @staticmethod
    def from_html(rrggbb):
        if rrggbb[0] == '#':
            rrggbb = rrggbb[1:]
        if not re.match(r'[0-9a-fA-F]{6}', rrggbb):
            raise RuntimeError('bad html color code: %s' % rrggbb)
        r = int(rrggbb[:2], 16)
        g = int(rrggbb[2:4], 16)
        b = int(rrggbb[4:], 16)
        if r == g and g == b:
            x = r // 10 * 10 + 8
            if x > 238: x = 255
            return RGB(x, x, x)
        else:
            return RGB(closest_shade(r), closest_shade(g), closest_shade(b))

def get_xterm256():
    """Returns a list of RGB objects. This index of each RGB is the xterm color value.

    For example, xterm256[209] is (255, 135, 95), which means if we do `echo -e "\033[48;5;209m  \033[0m"` we get an orange block.
    """
    xterm256 = [-1] * 256

    xterm256[ 0] = RGB(  0,   0,   0)
    xterm256[ 1] = RGB(128,   0,   0)
    xterm256[ 2] = RGB(  0, 128,   0)
    xterm256[ 3] = RGB(128, 128,   0)
    xterm256[ 4] = RGB(  0,   0, 128)
    xterm256[ 5] = RGB(128,   0, 128)
    xterm256[ 6] = RGB(  0, 128, 128)
    xterm256[ 7] = RGB(192, 192, 192)
    xterm256[ 8] = RGB(128, 128, 128)
    xterm256[ 9] = RGB(255,   0,   0)
    xterm256[10] = RGB(  0, 255,   0)
    xterm256[11] = RGB(255, 255,   0)
    xterm256[12] = RGB(  0,   0, 255)
    xterm256[13] = RGB(255,   0, 255)
    xterm256[14] = RGB(  0, 255, 255)
    xterm256[15] = RGB(255, 255, 255)

    i = 16

    for r in shades:
        for g in shades:
            for b in shades:
                xterm256[i] = RGB(r, g, b)
                i += 1

    for x in range(8, 240, 10):
        xterm256[i] = RGB(x, x, x)
        i += 1

    return xterm256


if __name__ == '__main__':
    xterm256_reverse_map = {}

    xterm256 = get_xterm256()

    for i, c in enumerate(xterm256):
        xterm256_reverse_map[c] = i
        print('\033[38;5;%dm%d\033[0m %s %s' % (i, i, c.to_html(), c), end='\n')

    # print(xterm256_reverse_map)
    # print(xterm256_reverse_map[RGB(255, 175, 215)])

    # some tests
    for html_color in ('eeeeee', '#eeeeee', '#121212', '#801cee', 'ff87d7'):
        rgb = RGB.from_html(html_color)
        print(html_color, ' => ', rgb, rgb.to_html(), xterm256_reverse_map[rgb])

    print('-' * 80)
    # print('\033[48;5;232m' + '-' * 80)
    # print('\033[48;5;232m' + '.' * 80)
    # print('\033[?25l')  # hide the cursor

    nr_leds = 25

    line_no = 0
    for line in fileinput.input():
        line_no += 1
        line = line.strip()
        try:
            rgb = RGB.from_html(line)
            xterm256_color = xterm256_reverse_map[rgb]
            if line_no % nr_leds == 0:
                print('\033[%dA' % nr_leds, end='')
            print('\033[48;5;%dm  \033[0m ' % xterm256_color, end='')
            print(line, ' => ', rgb, rgb.to_html(), xterm256_color)
        except:
            # ignoring exceptions, simply print the unhandled line
            print(line)
        time.sleep(0.02)

    print('\033[0m')
