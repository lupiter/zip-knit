#!/usr/bin/env python

import sys
from PIL import Image
import pattern.file as brother

# import convenience functions
from pattern.maths import roundfour, bytes_for_memo

VERSION = "1.0"


class PatternInserter: # pylint: disable=too-few-public-methods
    def insert_pattern(self, oldbrotherfile, pattnum, imgfile, newbrotherfile):

        bf = brother.BrotherFile(oldbrotherfile)

        # ok got a bank, now lets figure out how big this thing we want to insert is
        the_image = Image.open(imgfile)
        the_image.load()

        im_size = the_image.size
        width = im_size[0]
        print("width:" + str(width))
        height = im_size[1]
        print("height:" + str(height))

        # find the program entry
        the_pattern = bf.get_pattern(pattnum)

        if height != the_pattern.rows or width != the_pattern.stitches:
            raise InserterException(
                "Pattern is the wrong size, the BMP is ",
                height,
                "x",
                width,
                "and the pattern is ",
                the_pattern.rows,
                "x",
                the_pattern.stitches,
            )

        # debugging stuff here
        x = 0
        y = 0

        x = width - 1
        for y in range(height):
            for x in range(width):
                value = the_image.getpixel((x, y))
                if value:
                    print("* ")
                else:
                    print("  ")
            print(" ")

        # debugging stuff done

        # now to make the actual, yknow memo+pattern data

        # the memo seems to be always blank. i have no idea really
        memoentry = []
        for i in range(bytes_for_memo(height)):
            memoentry.append(0x0)

        # now for actual real live pattern data!
        pattmemnibs = []
        for r in range(height):
            row = []  # we'll chunk in bits and then put em into nibbles
            for s in range(width):
                x = s
                value = the_image.getpixel((x, height - r - 1))
                is_black = value == 0
                if is_black:
                    row.append(1)
                else:
                    row.append(0)
            # print row
            # turn it into nibz
            for s in range(roundfour(width) / 4):
                n = 0
                for nibs in range(4):
                    # print "row size = ", len(row), "index = ",s*4+nibs

                    if len(row) == (s * 4 + nibs):
                        break  # padding!

                    if row[s * 4 + nibs]:
                        n |= 1 << nibs
                pattmemnibs.append(n)
                # print hex(n),

        if len(pattmemnibs) % 2:
            # odd nibbles, buffer to a byte
            pattmemnibs.append(0x0)

        # print len(pattmemnibs), "nibbles of data"

        # turn into bytes
        pattmem = []
        for i in range(len(pattmemnibs) / 2):
            pattmem.append(pattmemnibs[i * 2] | (pattmemnibs[i * 2 + 1] << 4))

        # print map(hex, pattmem)
        # whew.

        # now to insert this data into the file

        # now we have to figure out the -end- of the last pattern is
        endaddr = 0x6DF

        beginaddr = the_pattern.pattern_end_offset
        endaddr = beginaddr + bytes_for_memo(height) + len(pattmem)
        print(
            "beginning will be at "
            + str(hex(beginaddr))
            + ", end at "
            + str(hex(endaddr))
        )

        # Note - It's note certain that in all cases this collision test is needed. What's happening
        # when you write below this address (as the pattern grows downward in memory) in that you
        # begin to overwrite the pattern index data that starts at low memory. Since you overwrite
        # the info for highest memory numbers first, you may be able to get away with it as long as
        # you don't attempt to use higher memories.
        # Steve

        if beginaddr <= 0x2B8:
            print(
                "Sorry, this will collide with the pattern "
                + f"entry data since {hex(beginaddr)} is <= 0x2B8!"
            )
            # exit

        # write the memo and pattern entry from the -end- to the -beginning- (up!)
        for i in range(len(memoentry)):
            bf.set_indexed_byte(endaddr, 0)
            endaddr -= 1

        for i in enumerate(pattmem):
            bf.set_indexed_byte(endaddr, pattmem[i])
            endaddr -= 1

        # push the data to a file
        with open(newbrotherfile, "wb") as outfile:
            d = bf.get_full_data()
            outfile.write(d)
            outfile.close()


class InserterException(Exception):
    def get_message(self):
        msg = ""
        for arg in self.args:
            if msg != "":
                msg += " "
            msg += str(arg)

        return msg


class PatternNotFoundException(InserterException):
    def __init__(self, pattern_number: int):
        self.pattern_number = pattern_number


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} oldbrotherfile pattern# image.bmp newbrotherfile")
        sys.exit()
    inserter = PatternInserter()
    argv = sys.argv
    try:
        inserter.insert_pattern(argv[1], argv[2], argv[3], argv[4])
    except PatternNotFoundException as e:
        print(f"ERROR: Pattern {e.pattern_number} not found")
        sys.exit(1)
    except InserterException as e:
        print(("ERROR: ", e.get_message()))
        sys.exit(1)
