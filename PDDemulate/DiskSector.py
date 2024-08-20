#
# Note that this code makes a fundamental assumption which
# is only true for the disk format used by the brother knitting
# machine, which is that there is only one logical sector (LS) per
# physical sector (PS). The PS size is fixed at 1280 bytes, and
# the brother uses a LS size of 1024 bytes, so only one can fit.
#

import os


class DiskSector:
    def __init__(self, fn):
        self.sectorSz = 1024
        self.idSz = 12
        self.data: bytes = b""
        self.id: bytes = b""
        # self.id = array('c')

        dfn = fn + ".dat"
        idfn = fn + ".id"

        try:
            try:
                self.df = open(dfn, "rb+")
            except IOError:
                self.df = open(dfn, "wb")

            try:
                self.idf = open(idfn, "rb+")
            except IOError:
                self.idf = open(idfn, "wb")

            dfs = os.path.getsize(dfn)
            idfs = os.path.getsize(idfn)

        except:
            print("Unable to open files using base name <%s>" % fn)
            raise

        try:
            if dfs == 0:
                # New or empty file
                self.data = bytearray(self.sectorSz)
                self.writeDFile()
            elif dfs == self.sectorSz:
                # Existing file
                self.data = self.df.read(self.sectorSz)
            else:
                print("Found a data file <%s> with the wrong size" % dfn)
                raise IOError
        except:
            print("Unable to handle data file <%s>" % fn)
            raise

        try:
            if idfs == 0:
                # New or empty file
                self.id = bytearray(self.idSz)
                self.writeIdFile()
            elif idfs == self.idSz:
                # Existing file
                self.id = self.idf.read(self.idSz)
            else:
                print(
                    "Found an ID file <%s> with the wrong size, is %d should be %d"
                    % (idfn, idfs, self.idSz)
                )
                raise IOError
        except:
            print("Unable to handle id file <%s>" % fn)
            raise

        return

    def __del__(self):
        return

    def format(self):
        self.data = bytearray(self.sectorSz)
        self.writeDFile()
        self.id = bytearray(self.idSz)
        self.writeIdFile()

    def writeDFile(self) -> None:
        self.df.seek(0)
        self.df.write(self.data)
        self.df.flush()
        return

    def writeIdFile(self) -> None:
        self.idf.seek(0)
        self.idf.write(self.id)
        self.idf.flush()
        return

    def read(self, length: int) -> bytes:
        if length != self.sectorSz:
            print("Error, read of %d bytes when expecting %d" % (length, self.sectorSz))
            raise IOError
        return self.data

    def write(self, indata: bytes) -> None:
        if len(indata) != self.sectorSz:
            print(
                "Error, write of %d bytes when expecting %d"
                % (len(indata), self.sectorSz)
            )
            raise IOError
        self.data = indata
        self.writeDFile()
        return

    def getSectorId(self) -> bytes:
        return self.id

    def setSectorId(self, newid: bytes) -> None:
        if len(newid) == 0:
            self.id = b"".join([bytes([0]) for num in range(self.idSz)])
        elif len(newid) != self.idSz:
            print(
                f"Error, bad id {newid} length of {len(newid)} bytes when expecting {self.id}"
            )
            raise IOError
        else:
            self.id = newid
        self.writeIdFile()
        print("Wrote New ID: ", end=" ")
        self.dumpId()
        return

    def dumpId(self) -> None:
        print(f"{self.id}")
