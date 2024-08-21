import array
from array import * # type: ignore
import typing
from pattern.maths import nibbles, nibblesPerRow, bytesForMemo, bytesPerPatternAndMemo, roundeven, hto

__version__ = '1.0'


# Some file location constants
initPatternOffset = 0x06DF # programmed patterns start here, grow down
currentPatternAddr = 0x07EA # stored in MSN and following byte
currentRowAddr = 0x06FF
nextRowAddr = 0x072F
currentRowNumberAddr = 0x0702
carriageStatusAddr = 0x070F
selectAddr = 0x07EA



# various unknowns which are probably something we care about
unknownList = {'0700':0x0700, '0701':0x0701,
               '0704':0x0704, '0705':0x0705, '0706':0x0706, '0707':0x0707,
               '0708':0x0708, '0709':0x0709, '070A':0x070A, '070B':0x070B,
               '070C':0x070C, '070D':0x070D, '070E':0x070E, '0710':0x0710,
               '0711':0x0711, '0712':0x0712, '0713':0x0713, '0714':0x0714,
               '0715':0x0715}


class brotherFile(object):

    def __init__(self, fn):
        self.dfn: str
        self.data: bytes
        self.verbose = False
        try:
            try:
                self.df = open(fn, 'rb+')     # YOU MUST HAVE BINARY FORMAT!!!
            except IOError:
                # for now, read only
                raise
                #self.df = open(fn, 'w')
        except:
            print(('Unable to open brother file <%s>' % fn))
            raise
        try:
            self.data = self.df.read(-1)
            self.df.close()
            if len(self.data) == 0:
                raise Exception()
        except:
            print(('Unable to read 2048 bytes from file <%s>' % fn))
            raise
        self.dfn = fn
        return

    def __del__(self):
        return

    def getIndexedByte(self, index: int) -> int:
        return self.data[index]

    def setIndexedByte(self, index: int, b: int):
        # python strings are mutable so we
        # will convert the string to a char array, poke
        # and convert back
        dataarray = array('c')
        dataarray.frombytes(self.data)

        if self.verbose:
            print(("* writing ", hex(b), "to", hex(index)))
        #print dataarray

        # this is the actual edit
        dataarray[index] = chr(b)

        # save the new string. sure its not very memory-efficient
        # but who cares?
        self.data = dataarray.tobytes()
        
    # handy for debugging
    def getFullData(self) -> bytes:
        return self.data

    def getIndexedNibble(self, offset: int, nibble: int) -> int:
        # nibbles is zero based
        bytes = int(nibble/2)
        m, l = nibbles(self.data[offset-bytes])
        if nibble % 2:
            return m
        else:
            return l

    def getRowData(self, pattOffset: int, stitches: int, rownumber: int) -> bytes:
        row=array('B')
        nibspr = nibblesPerRow(stitches)
        startnib = int(nibspr * rownumber)
        endnib = int(startnib + nibspr)

        for i in range(startnib, endnib, 1):
            nib = self.getIndexedNibble(pattOffset, i)
            row.append(nib & 0x01)
            stitches = stitches - 1
            if stitches:
                row.append((nib & 0x02) >> 1)
                stitches = stitches - 1
            if stitches:
                row.append((nib & 0x04) >> 2)
                stitches = stitches - 1
            if stitches:
                row.append((nib & 0x08) >> 3)
                stitches = stitches - 1
        return row

    def getPatterns(self, patternNumber: typing.Optional[int] = None) -> list[dict]:
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
        patlist: list[dict] = []
        idx = 0
        pptr = initPatternOffset
        for pi in range(1, 100):
            flag = self.data[idx]
            if self.verbose:
                print(('Entry %d, flag is 0x%02X' % (pi, flag)))
            idx = idx + 1
            unknown = self.data[idx] # is this the mode? or track? mode 1 disk has two tracks, mode 2 disk has 40 tracks
            idx = idx + 1
            rh, rt = nibbles(self.data[idx])
            idx = idx + 1
            ro, sh = nibbles(self.data[idx])
            idx = idx + 1
            st, so = nibbles(self.data[idx])
            idx = idx + 1
            unk, ph = nibbles(self.data[idx]) # is unk here page number?
            idx = idx + 1
            pt, po = nibbles(self.data[idx])
            idx = idx + 1
            rows = hto(rh,rt,ro)
            stitches = hto(sh,st,so)
            patno = hto(ph,pt,po)
            # we have this entry
            if self.verbose:
                print(('   Pattern %3d: %3d Rows, %3d Stitches - ' % (patno, rows, stitches)))
            if flag != 0:
                # valid entry
                pptr =  len(self.data) -1 - ((flag << 8) + unknown) 
                memoff = pptr
                if self.verbose:
                    print(("Memo #",patno, "offset ", memoff))
                patoff = pptr - bytesForMemo(rows)
                if self.verbose:
                     print(("Pattern #",patno, "offset ", patoff))
                pptr = pptr - bytesPerPatternAndMemo(stitches, rows)
                if self.verbose:
                     print(("Ending offset ", hex(pptr)))
                if patternNumber:
                    if patternNumber == patno:
                        patlist.append({'number':patno, 'stitches':stitches, 'rows':rows, 'memo':memoff, 'pattern':patoff, 'pattend':pptr})
                else:
                    patlist.append({'number':patno, 'stitches':stitches, 'rows':rows, 'memo':memoff, 'pattern':patoff, 'pattend':pptr})
            else:
                break
        return patlist

    def getMemo(self) -> bytes:
        """
        Return an array containing the memo
        information for the pattern currently in memory
        """
        patt = self.patternNumber()
        if patt > 900:
            return self.getPatternMemo(patt)
        else:
            rows = 0 # TODO XXXXXXXXX
        return [0]

    def patternNumber(self) -> int:
        sn, pnh = nibbles(self.data[currentPatternAddr])
        pnt, pno = nibbles(self.data[currentPatternAddr+1])
        pattern = hto(pnh,pnt,pno)
        return(pattern)

    def getPatternMemo(self, patternNumber: int) -> bytes:
        """
        Return an array containing the memo
        information for a custom pattern. The array
        is the same length as the number of rows
        in the pattern.
        """
        list = self.getPatterns(patternNumber)
        if len(list) == 0:
            return None
        memos = array('B')
        memoOff = list[0]['memo']
        rows = list[0]['rows']
        memlen = roundeven(rows)/2
        # memo is padded to en even byte
        for i in range(memoOff, memoOff-memlen, -1):
            msn, lsn = nibbles(self.data[i])
            memos.append(lsn)
            rows = rows - 1
            if (rows):
                memos.append(msn)
                rows = rows - 1
        return memos

    def getPattern(self, patternNumber: int) -> list[bytes]:
        """
        Return an array containing the pattern
        information for a pattern.
        """
        list = self.getPatterns(patternNumber)
        if len(list) == 0:
            return None
        pattern = []

        patoff = int(list[0]['pattern'])
        rows = list[0]['rows']
        stitches = list[0]['stitches']

        #print 'patoff = 0x%04X' % patoff
        #print 'rows = ', rows
        #print 'stitches = ', stitches
        for i in range(0, rows):
            arow = self.getRowData(patoff, stitches, i)
            #print arow
            pattern.append(arow)
        return pattern

    def displayPattern(self, patternNumber: int) -> None:
        """
        Display a user pattern stored in file saved 
        from the brother knitting machine. Patterns
        in memory are stored with the beginning of the
        pattern at the highest memory address.
        """

        return

    def rowNumber(self) -> int:
        sn, rnh = nibbles(self.data[currentRowNumberAddr])
        rnt, rno = nibbles(self.data[currentRowNumberAddr+1])
        rowno = hto(rnh,rnt,rno)
        return(rowno)

    def nextRow(self) -> bytes:
        return self.getRowData(nextRowAddr, 200, 0)
        
    def selectorValue(self) -> int:
        return self.data[selectAddr]

    def carriageStatus(self) -> int:
        return self.data[carriageStatusAddr]

    def motifData(self) -> list[dict]:
        motiflist = []
        addr = 0x07FB
        for i in range(6):
            mph, mpt = nibbles(self.data[addr])
            if mph & 8:
                mph = mph - 8
                side = 'right'
            else:
                side = 'left'
            mpo, foo = nibbles(self.data[addr+1])
            mch, mct = nibbles(self.data[addr+2])
            mco, bar = nibbles(self.data[addr+3])
            pos = hto(mph,mpt,mpo)
            cnt = hto(mch,mct,mco)
            motiflist.append({'position':pos, 'copies':cnt, 'side':side})
            addr = addr - 3
        return motiflist

    def patternPosition(self) -> dict:
        addr = 0x07FE
        foo, ph = nibbles(self.data[addr])
        if ph & 8:
            ph = ph - 8
            side = 'right'
        else:
            side = 'left'
        pt, po = nibbles(self.data[addr+1])
        pos = hto(ph,pt,po)

        return {'position':pos, 'side':side}

    # these are hardcoded for now
    def unknownOne(self):
        info = array('B')
        for i in range(0x06E0, 0x06E5):
            info.append(self.data[i])
        return info

    def unknownMemoRange(self):
        info = array('B')
        for i in range(0x0731, 0x0787):
            info.append(self.data[i])
        return info

    def unknownEndRange(self):
        info = array('B')
        for i in range(0x07D0, 0x07E9):
            info.append(self.data[i])
        return info

    def unknownAddrs(self):
        return list(unknownList.items())
            
