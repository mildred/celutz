# -*- coding: utf-8 -*-

"""
Given an image, generate a set of tiles at various zoom levels.
The format of the filename of times is:

  00<zoom>-00<x>-00<y>.jpg

where zoom is 0 for the original size, 1 when the image is downscaled 2
times, 2 when the image is downscaled 4 times, etc.
"""

from __future__ import unicode_literals, division, print_function

import sys
import os
import tempfile

import PIL.Image


def gen_tiles(image, output_path, min_scale=0, max_scale=8, crop_x=256, crop_y=256):
    orig_im = PIL.Image.open(image)
    for scale in range(min_scale, max_scale + 1):
        if scale == 0:
            im = orig_im
        else:
            scaled_size = (orig_im.size[0] >> scale, orig_im.size[1] >> scale)
            im = orig_im.resize(scaled_size)
        for x in range(0, im.size[0], crop_x):
            for y in range(0, im.size[1], crop_y):
                geom = (x, y, min(im.size[0], x + crop_x),
                        min(im.size[1], y + crop_y))
                dest = os.path.join(output_path,
                                    "{:03}-{:03}-{:03}.jpg".format(scale,
                                                                   x // crop_x,
                                                                   y // crop_y))
                im.crop(geom).save(dest)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <image>".format(sys.argv[0]))
        print("Generate tiles of the given image.")
        exit(1)
    origin = sys.argv[1]
    out = tempfile.mkdtemp(prefix="demo-pano-")
    print("Generating tiles in {} ...".format(out))
    gen_tiles(origin, out)
