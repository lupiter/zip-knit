import os
from PDDemulate.disk_sector import DiskSector


class Disk:
    """
    Fields:
        self.lastDatFilePath : string
    """

    def __init__(self, basename: str):
        self.num_sectors = 80
        self.sectors: list[DiskSector] = []
        self.filespath = ""
        self.last_dat_file_path = None
        # Set up disk Files and internal buffers

        # if absolute path, just accept it
        if os.path.isabs(basename):
            dirpath = basename
        else:
            dirpath = os.path.abspath(basename)

        if os.path.exists(dirpath):
            if not os.access(dirpath, os.R_OK | os.W_OK):
                print(
                    f"Directory <{dirpath}> exists but cannot be accessed, check permissions"
                )
                raise IOError
            if not os.path.isdir(dirpath):
                print(f"Specified path <{dirpath}> exists but is not a directory")
                raise IOError
        else:
            try:
                os.mkdir(dirpath)
            except Exception as e:
                print(f"Unable to create directory <{dirpath}>")
                raise IOError from e

        self.filespath = dirpath
        # we have a directory now - set up disk sectors
        for i in range(self.num_sectors):
            fname = os.path.join(dirpath, i)
            ds = DiskSector(fname)
            self.sectors.append(ds)

    def __del__(self):
        return

    def format(self) -> None:
        for i in range(self.num_sectors):
            self.sectors[i].format()

    def find_sector_id(self, psn: int, sector_id: bytes) -> bytes:
        for i in range(psn, self.num_sectors):
            sid = self.sectors[i].get_sector_id()
            if sector_id == sid:
                return b"00" + b"%02X" % i + b"0000"
        return b"40000000"

    def get_sector_id(self, psn: int) -> bytes:
        return self.sectors[psn].get_sector_id()

    def set_sector_id(self, psn: int, sector_id: bytes) -> None:
        self.sectors[psn].set_sector_id(sector_id)

    def write_sector(self, psn: int, lsn: int, indata: bytes) -> None:
        self.sectors[psn].write(indata)
        if psn % 2:
            filenum = ((psn - 1) / 2) + 1
            filename = f"file-{filenum}.dat" % filenum
            # we wrote an odd sector, so create the
            # associated file
            fn1 = os.path.join(self.filespath, f"{psn - 1}.dat")
            fn2 = os.path.join(self.filespath, f"{psn}.dat")
            outfn = os.path.join(self.filespath, filename)
            cmd = f"cat {fn1} {fn2} > {outfn}"
            os.system(cmd)
            self.last_dat_file_path = outfn

    def read_sector(self, psn: int, lsn: int) -> bytes:
        return self.sectors[psn].read(1024)
