#!/usr/bin/env python

import sys
from pattern.file import BrotherFile

# import convenience functions from brother module
from pattern.maths import nibbles_per_row, bytes_per_pattern, bytes_for_memo
from pattern.pattern import PatternMetadata

DEBUG = True

VERSION = "1.0"


class PatternDumper:  # pylint: disable=too-few-public-methods
    """Extractor for patterns"""

    def dump_pattern(self, filename, pattern_number=None, debug=DEBUG) -> list[PatternMetadata]:
        """Extract patterns from file"""
        if len(filename) < 1:
            raise ArgumentsException()

        bf = BrotherFile(filename)

        if pattern_number is None:
            if debug:
                self.__pattern_print(bf)
            return bf.get_patterns()
        print(f"Searching for pattern number {pattern_number}")
        pats = bf.get_pattern(pattern_number)
        if pats is None:
            raise PatternNotFoundException(pattern_number)
        print(f"{pats.stitches} Stitches, {pats.rows} Rows")
        return [bf.get_pattern_data(pattern_number)]

    def __pattern_print(
        self, bf: BrotherFile
    ):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        print("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        print("Data file")
        print("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

        # first dump the 99 'pattern id' blocks
        for i in range(99):
            print(f"program entry {i}")
            # each block is 7 bytes
            bytenum = i * 7

            pattused = bf.get_indexed_byte(bytenum)
            print("\t", hex(bytenum), ": ", hex(pattused), end=" ")
            if pattused == 1:
                print("\t(used)")
            else:
                print("\t(unused)")
                # print "\t-skipped-"
                # continue
            bytenum += 1

            unk1 = bf.get_indexed_byte(bytenum)
            print(f"\t{hex(bytenum)}: {hex(unk1)},\t(unknown)")
            bytenum += 1

            rows100 = bf.get_indexed_byte(bytenum)
            print(
                f"\t{hex(bytenum)}: {hex(rows100)}\t"
                + f"(rows = {(rows100 >> 4)*100} + {(rows100 & 0xF)*10}"
            )
            bytenum += 1

            rows1 = bf.get_indexed_byte(bytenum)
            print(
                f"\t{hex(bytenum)}: {hex(rows1)}\t"
                + f"\t+ {(rows1 >> 4)} stiches = {(rows1 & 0xF)*100}+"
            )
            bytenum += 1

            stitches10 = bf.get_indexed_byte(bytenum)
            print(
                f"\t{hex(bytenum)}: {hex(stitches10)}\t"
                + f"\t+ {(stitches10 >> 4)*10} + {(stitches10 & 0xF)})"
            )
            bytenum += 1

            prog100 = bf.get_indexed_byte(bytenum)
            print(
                f"\t{hex(bytenum)}: {hex(prog100)}\t(unknown , prog# = {(prog100&0xF) * 100}+"
            )
            bytenum += 1

            prog10 = bf.get_indexed_byte(bytenum)
            print(
                f"\t{hex(bytenum)}: {hex(prog10)}\t\t + {(prog10>>4) * 10} + {(prog10&0xF)})"
            )
            bytenum += 1

        print("============================================")
        print("Program memory grows -up-")
        # now we're onto data data

        # dump the first program
        pointer = 0x6DF  # this is the 'bottom' of the memory
        for i in range(99):
            # of course, not all patterns will get dumped
            pattused = bf.get_indexed_byte(i * 7)
            if pattused != 1:
                # :(
                break
            # otherwise its a valid pattern
            print("pattern bank #", i)
            # calc pattern size
            rows100 = bf.get_indexed_byte(i * 7 + 2)
            rows1 = bf.get_indexed_byte(i * 7 + 3)
            stitches10 = bf.get_indexed_byte(i * 7 + 4)

            rows = (rows100 >> 4) * 100 + (rows100 & 0xF) * 10 + (rows1 >> 4)
            stitches = (rows1 & 0xF) * 100 + (stitches10 >> 4) * 10 + (stitches10 & 0xF)
            print("rows = ", rows, "stitches = ", stitches)
            #        print "total nibs per row = ", nibblesPerRow(stitches)

            # dump the memo data
            print("memo length =", bytes_for_memo(rows))
            for i in range(bytes_for_memo(rows)):
                b = pointer - i
                print("\t", hex(b), ": ", hex(bf.get_indexed_byte(b)))
            pointer -= bytes_for_memo(rows)

            print("pattern length = ", bytes_per_pattern(stitches, rows))
            for i in range(bytes_per_pattern(stitches, rows)):
                b = pointer - i
                print("\t", hex(b), ": ", hex(bf.get_indexed_byte(b)), end=" ")
                for j in range(8):
                    if bf.get_indexed_byte(b) & (1 << j):
                        print("*", end=" ")
                    else:
                        print(" ", end=" ")
                print("")

            # print it out in nibbles per row?
            for row in range(rows):
                for nibs in range(nibbles_per_row(stitches)):
                    n = bf.get_indexed_nibble(
                        pointer, nibbles_per_row(stitches) * row + nibs
                    )
                    print(hex(n), end=" ")
                    for j in range(8):
                        if n & (1 << j):
                            print("*", end=" ")
                        else:
                            print(" ", end=" ")
                print("")
            pointer -= bytes_per_pattern(stitches, rows)

        # for i in range (0x06DF, 99*7, -1):
        #    print "\t",hex(i),": ",hex(bf.getIndexedByte(i))


class ArgumentsException(Exception):
    pass


class PatternNotFoundException(Exception):
    def __init__(self, pattern_number):
        self.pattern_number = pattern_number


def main():
    try:
        # print sys.argv
        dumper = PatternDumper()
        out = dumper.dump_pattern(sys.argv[1:])
        if len(out) > 1:
            print("Pattern   Stitches   Rows")
            for pat in out:
                print(f'  {pat["number"]}       {pat["stitches"]}      {pat["rows"]}')
        elif len(out) > 0:
            for row, _ in enumerate(out):
                for stitch, _ in enumerate(out[row]):
                    if (out[row][stitch]) == 0:
                        print(" ", end=" ")
                    else:
                        print("*", end=" ")
                print()

    except ArgumentsException:
        print(f"Usage: {sys.argv[0]} file [patternnum]")
        print("Dumps user programs (901-999) from brother data files")
        sys.exit(1)
    except IOError as e:
        print(e)
        print("Could not open file ", sys.argv[1])
        sys.exit(1)
    except PatternNotFoundException as e:
        print(f"Pattern {e.pattern_number} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
