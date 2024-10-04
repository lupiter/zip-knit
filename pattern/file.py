import array  # type: ignore
from pattern.maths import (
    nibbles,
    bytes_for_memo,
    bytes_per_pattern_and_memo,
    hto,
)
from pattern.pattern import PatternMetadata

__version__ = "1.0"


# Some file location constants
INIT_PATTERN_OFFSET = 0x06DF  # programmed patterns start here, grow down
CURRENT_PATTERN_ADDR = 0x07EA  # stored in MSN and following byte
CURRENT_ROW_ADDR = 0x06FF
NEXT_ROW_ADDR = 0x072F
CURRENT_ROW_NUMBER_ADDR = 0x0702
CARRIAGE_STATUS_ADDR = 0x070F
SELECT_ADDR = 0x07EA


# various unknowns which are probably something we care about
unknownList = {
    "0700": 0x0700,
    "0701": 0x0701,
    "0704": 0x0704,
    "0705": 0x0705,
    "0706": 0x0706,
    "0707": 0x0707,
    "0708": 0x0708,
    "0709": 0x0709,
    "070A": 0x070A,
    "070B": 0x070B,
    "070C": 0x070C,
    "070D": 0x070D,
    "070E": 0x070E,
    "0710": 0x0710,
    "0711": 0x0711,
    "0712": 0x0712,
    "0713": 0x0713,
    "0714": 0x0714,
    "0715": 0x0715,
}


class BrotherFile(): # pylint: disable=too-many-public-methods
    """Reading a brother "file" representing a floppy disk track"""

    def __init__(self, fn):
        self.dfn: str
        self.data: bytes
        self.verbose = False
        try:
            with open(fn, "rb+") as df:
                try:
                    self.data = df.read(-1)
                    if len(self.data) == 0:
                        raise FileNotFoundError("The file has no data")
                except:
                    print(f"Unable to read 2048 bytes from file <{fn}>")
                    raise
        except:
            print(f"Unable to open brother file <{fn}>")
            raise
        self.dfn = fn

    def get_indexed_byte(self, index: int) -> int:
        return self.data[index]

    def set_indexed_byte(self, index: int, b: int):
        # python strings are mutable so we
        # will convert the string to a char array, poke
        # and convert back
        dataarray = array.array("c")
        dataarray.frombytes(self.data)

        if self.verbose:
            print(("* writing ", hex(b), "to", hex(index)))
        # print dataarray

        # this is the actual edit
        dataarray[index] = chr(b)

        # save the new string. sure its not very memory-efficient
        # but who cares?
        self.data = dataarray.tobytes()

    # handy for debugging
    def get_full_data(self) -> bytes:
        return self.data

    def get_indexed_nibble(self, offset: int, nibble: int) -> int:
        # nibbles is zero based
        byte_data = int(nibble / 2)
        m, l = nibbles(self.data[offset - byte_data])
        if nibble % 2:
            return m
        return l

    def get_pattern(self, pattern_number: int) -> PatternMetadata | None:
        """
        Get information for a single pattern.
        Pattern information is stored at the beginning
        of the file, with seven bytes per pattern and
        99 possible patterns, numbered 901-999.
        Returns: A tuple:
          patternNumber
          stitches
          rows
          patternOffset
          memoOffset
        """
        patterns = self.get_patterns()
        for pattern in patterns:
            if pattern.number == pattern_number:
                return pattern
        return None

    def get_patterns(self) -> list[PatternMetadata]: # pylint: disable=too-many-locals
        """
        Get a list of custom patterns stored in the file, or
        information for a single pattern.
        Pattern information is stored at the beginning
        of the file, with seven bytes per pattern and
        99 possible patterns, numbered 901-999.
        Returns: A list of tuples:
          patternNumber
          stitches
          rows
          patternOffset
          memoOffset
        """
        patlist: list[PatternMetadata] = []
        idx = 0
        pptr = INIT_PATTERN_OFFSET
        for pi in range(1, 100):
            flag = self.data[idx]
            if self.verbose:
                print(f"Entry {pi}, flag is 0x{flag}X")
            idx = idx + 1
            unknown = self.data[
                idx
            ]  # is this the mode? or track? mode 1 disk has two tracks, mode 2 disk has 40 tracks
            idx = idx + 1
            rh, rt = nibbles(self.data[idx])
            idx = idx + 1
            ro, sh = nibbles(self.data[idx])
            idx = idx + 1
            st, so = nibbles(self.data[idx])
            idx = idx + 1
            _, ph = nibbles(self.data[idx])  # is unk here page number?
            idx = idx + 1
            pt, po = nibbles(self.data[idx])
            idx = idx + 1
            rows = hto(rh, rt, ro)
            stitches = hto(sh, st, so)
            patno = hto(ph, pt, po)
            # we have this entry
            if self.verbose:
                print(f"   Pattern {patno}: {rows} Rows, {stitches} Stitches - ")
            if flag != 0:
                # valid entry
                pptr = len(self.data) - 1 - ((flag << 8) + unknown)
                memoff = pptr
                if self.verbose:
                    print(("Memo #", patno, "offset ", memoff))
                patoff = pptr - bytes_for_memo(rows)
                if self.verbose:
                    print(("Pattern #", patno, "offset ", patoff))
                pptr = pptr - bytes_per_pattern_and_memo(stitches, rows)
                if self.verbose:
                    print(("Ending offset ", hex(pptr)))
                patlist.append(
                    PatternMetadata(patno, stitches, rows, memoff, patoff, pptr)
                )
            else:
                break
        return patlist

    def get_pattern_data(self, pattern_number: int) -> bytearray:
        """
        Return an array containing the pattern
        information for a pattern.
        """
        return self.get_pattern(pattern_number).get_data(self.data)

    # def motif_data(self) -> list[dict]:
    #     motiflist = []
    #     addr = 0x07FB
    #     for _ in range(6):
    #         mph, mpt = nibbles(self.data[addr])
    #         if mph & 8:
    #             mph = mph - 8
    #             side = "right"
    #         else:
    #             side = "left"
    #         mpo, _ = nibbles(self.data[addr + 1])
    #         mch, mct = nibbles(self.data[addr + 2])
    #         mco, _ = nibbles(self.data[addr + 3])
    #         pos = hto(mph, mpt, mpo)
    #         cnt = hto(mch, mct, mco)
    #         motiflist.append({"position": pos, "copies": cnt, "side": side})
    #         addr = addr - 3
    #     return motiflist

    # def pattern_position(self) -> dict:
    #     addr = 0x07FE
    #     _, ph = nibbles(self.data[addr])
    #     if ph & 8:
    #         ph = ph - 8
    #         side = "right"
    #     else:
    #         side = "left"
    #     pt, po = nibbles(self.data[addr + 1])
    #     pos = hto(ph, pt, po)

    #     return {"position": pos, "side": side}

    # these are hardcoded for now
    # def unknown_one(self):
    #     info = array.array("B")
    #     for i in range(0x06E0, 0x06E5):
    #         info.append(self.data[i])
    #     return info

    # def unknown_memo_range(self):
    #     info = array.array("B")
    #     for i in range(0x0731, 0x0787):
    #         info.append(self.data[i])
    #     return info

    # def unknown_end_range(self):
    #     info = array.array("B")
    #     for i in range(0x07D0, 0x07E9):
    #         info.append(self.data[i])
    #     return info

    # def unknown_addrs(self):
    #     return list(unknownList.items())
