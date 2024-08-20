import os
from PDDemulate.DiskSector import DiskSector


class Disk:
    """
    Fields:
        self.lastDatFilePath : string
    """

    def __init__(self, basename: str):
        self.numSectors = 80
        self.Sectors: list[DiskSector] = []
        self.filespath = ""
        self.lastDatFilePath = None
        # Set up disk Files and internal buffers

        # if absolute path, just accept it
        if os.path.isabs(basename):
            dirpath = basename
        else:
            dirpath = os.path.abspath(basename)

        if os.path.exists(dirpath):
            if not os.access(dirpath, os.R_OK | os.W_OK):
                print(
                    "Directory <%s> exists but cannot be accessed, check permissions"
                    % dirpath
                )
                raise IOError
            elif not os.path.isdir(dirpath):
                print("Specified path <%s> exists but is not a directory" % dirpath)
                raise IOError
        else:
            try:
                os.mkdir(dirpath)
            except:
                print("Unable to create directory <%s>" % dirpath)
                raise IOError

        self.filespath = dirpath
        # we have a directory now - set up disk sectors
        for i in range(self.numSectors):
            fname = os.path.join(dirpath, "%02d" % i)
            ds = DiskSector(fname)
            self.Sectors.append(ds)
        return

    def __del__(self):
        return

    def format(self) -> None:
        for i in range(self.numSectors):
            self.Sectors[i].format()
        return

    def findSectorID(self, psn: int, id: bytes) -> bytes:
        for i in range(psn, self.numSectors):
            sid = self.Sectors[i].getSectorId()
            if id == sid:
                return b"00" + b"%02X" % i + b"0000"
        return b"40000000"

    def getSectorID(self, psn: int) -> bytes:
        return self.Sectors[psn].getSectorId()

    def setSectorID(self, psn: int, id: bytes) -> None:
        self.Sectors[psn].setSectorId(id)
        return

    def writeSector(self, psn: int, lsn: int, indata: bytes) -> None:
        self.Sectors[psn].write(indata)
        if psn % 2:
            filenum = ((psn - 1) / 2) + 1
            filename = "file-%02d.dat" % filenum
            # we wrote an odd sector, so create the
            # associated file
            fn1 = os.path.join(self.filespath, "%02d.dat" % (psn - 1))
            fn2 = os.path.join(self.filespath, "%02d.dat" % psn)
            outfn = os.path.join(self.filespath, filename)
            cmd = "cat %s %s > %s" % (fn1, fn2, outfn)
            os.system(cmd)
            self.lastDatFilePath = outfn
        return

    def readSector(self, psn: int, lsn: int) -> bytes:
        return self.Sectors[psn].read(1024)
