"""
Note that this code makes a fundamental assumption which
 is only true for the disk format used by the brother knitting
 machine, which is that there is only one logical sector (LS) per
 physical sector (PS). The PS size is fixed at 1280 bytes, and
 the brother uses a LS size of 1024 bytes, so only one can fit.
"""

import os


class DiskSector:
    def __init__(self, fn):
        self.sector_size = 1024
        self.id_size = 12
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
            print(f"Unable to open files using base name <{fn}>")
            raise

        try:
            if dfs == 0:
                # New or empty file
                self.data = bytearray(self.sector_size)
                self.write_d_file()
            elif dfs == self.sector_size:
                # Existing file
                self.data = self.df.read(self.sector_size)
            else:
                print(f"Found a data file <{dfn}> with the wrong size")
                raise IOError
        except:
            print(f"Unable to handle data file <{fn}>")
            raise

        try:
            if idfs == 0:
                # New or empty file
                self.id = bytearray(self.id_size)
                self.write_id_file()
            elif idfs == self.id_size:
                # Existing file
                self.id = self.idf.read(self.id_size)
            else:
                print(
                    f"Found an ID file <{idfn}> with the wrong size, is {idfs} should be {self.id_size}"
                )
                raise IOError
        except:
            print(f"Unable to handle id file <{fn}>")
            raise

        return

    def __del__(self):
        return

    def format(self):
        self.data = bytearray(self.sector_size)
        self.write_d_file()
        self.id = bytearray(self.id_size)
        self.write_id_file()

    def write_d_file(self) -> None:
        self.df.seek(0)
        self.df.write(self.data)
        self.df.flush()
        return

    def write_id_file(self) -> None:
        self.idf.seek(0)
        self.idf.write(self.id)
        self.idf.flush()
        return

    def read(self, length: int) -> bytes:
        if length != self.sector_size:
            print(f"Error, read of {length} bytes when expecting {self.sector_size}")
            raise IOError
        return self.data

    def write(self, indata: bytes) -> None:
        if len(indata) != self.sector_size:
            print(
                f"Error, write of {len(indata)} bytes when expecting {self.sector_size}"
            )
            raise IOError
        self.data = indata
        self.write_d_file()
        return

    def get_sector_id(self) -> bytes:
        return self.id

    def set_sector_id(self, newid: bytes) -> None:
        if len(newid) == 0:
            self.id = b"".join([bytes([0]) for num in range(self.id_size)])
        elif len(newid) != self.id_size:
            print(
                f"Error, bad id {newid} length of {len(newid)} bytes when expecting {self.id}"
            )
            raise IOError
        else:
            self.id = newid
        self.write_id_file()
        print("Wrote New ID: ", end=" ")
        self.dump_id()
        return

    def dump_id(self) -> None:
        print(f"{self.id}")
