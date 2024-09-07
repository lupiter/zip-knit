#!/usr/bin/python
import sys
from PIL import Image

FILE_NAME = "./qr_test.bmp"


def getprops():
    """Convert an image into an ascii representation"""
    x = 0
    y = 0
    im_file = Image.open(FILE_NAME)
    im_file.load()
    im_size = im_file.size
    width = im_size[0]
    print(("width:", width))
    height = im_size[1]
    print(("height:", height))
    x = width - 1
    while x > 0:
        value = im_file.getpixel((x, y))
        if value:
            sys.stdout.write("* ")
        else:
            sys.stdout.write("  ")
        # sys.stdout.write(str(value))
        x = x - 1
        if x == 0:  # did we hit the end of the line?
            y = y + 1
            x = width - 1
            print(" ")
            if y == height:
                return


if __name__ == "__main__":
    getprops()
