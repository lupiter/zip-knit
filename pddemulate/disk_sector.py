"""
Note that this code makes a fundamental assumption which
 is only true for the disk format used by the brother knitting
 machine, which is that there is only one logical sector (LS) per
 physical sector (PS). The PS size is fixed at 1280 bytes, and
 the brother uses a LS size of 1024 bytes, so only one can fit.
"""

import os


class DiskSector:
    sector_size = 1024
    id_size = 12
    data: bytes = b""
    id: bytes = b""

    def __init__(self, file_name: str):
        if not file_name:
            raise IOError("File name must be provided")
        
        data_file_name = file_name + ".dat"
        id_file_name = file_name + ".id"

        try:
            try:
                self.data_file = open(data_file_name, "rb+")
            except IOError:
                self.data_file = open(data_file_name, "wb")  # pylint: disable=consider-using-with

            try:
                self.id_file = open(id_file_name, "rb+")
            except IOError:
                self.id_file = open(id_file_name, "wb")  # pylint: disable=consider-using-with

            data_file_size = os.path.getsize(data_file_name)
            id_file_size = os.path.getsize(id_file_name)

        except:
            print(f"Unable to open files using base name <{file_name}>")
            raise

        try:
            if data_file_size == 0:
                # New or empty file
                self.data = bytearray(self.sector_size)
                self.write_data_file()
            elif data_file_size == self.sector_size:
                # Existing file
                self.data = self.data_file.read(self.sector_size)
            else:
                print(f"Found a data file <{data_file_name}> with the wrong size")
                raise IOError
        except:
            print(f"Unable to handle data file <{file_name}>")
            raise

        try:
            if id_file_size == 0:
                # New or empty file
                self.id = bytearray(self.id_size)
                self.write_id_file()
            elif id_file_size == self.id_size:
                # Existing file
                self.id = self.id_file.read(self.id_size)
            else:
                print(
                    f"Found an ID file <{id_file_name}> with the wrong size,"
                    + f" is {id_file_size} should be {self.id_size}"
                )
                raise IOError
        except:
            print(f"Unable to handle id file <{file_name}>")
            raise

    def __del__(self):
        return

    def format(self):
        self.data = bytearray(self.sector_size)
        self.write_data_file()
        self.id = bytearray(self.id_size)
        self.write_id_file()

    def write_data_file(self) -> None:
        self.data_file.seek(0)
        self.data_file.write(self.data)
        self.data_file.flush()

    def write_id_file(self) -> None:
        self.id_file.seek(0)
        self.id_file.write(self.id)
        self.id_file.flush()

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
        self.write_data_file()

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

    def dump_id(self) -> None:
        print(f"{self.id}")
