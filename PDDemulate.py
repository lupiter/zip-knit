#!/usr/bin/env python

# This software emulates the external floppy disk drive used
# by the Brother Electroknit KH-930E computerized knitting machine.
# It may work for other models, but has only been tested with the
# Brother KH-930E
#
# This emulates the disk drive and stores the saved data from
# the knitting machine on the linux file system. It does not
# read or write floppy disks.
#
# The disk drive used by the brother knitting machine is the same
# as a Tandy PDD1 drive. This software does not support the entire
# command API of the PDD1, only what is required for the knitting
# machine.
#

#
# Notes about data storage:
#
# The external floppy disk is formatted with 80 sectors of 1024
# bytes each. These sectors are numbered (internally) from 0-79.
# When starting this emulator, a base directory is specified.
# In this directory the emulator creates 80 files, one for each
# sector. These are kept sync'd with the emulator's internal
# storage of the same sectors. For each sector, there are two
# files, nn.dat, and nn.id, where 00 <= nn <= 79.
#
# The knitting machine uses two sectors for each saved set of
# information, which are referred to in the knitting machine
# manual as 'tracks' (which they were on the floppy disk). Each
# pair of even/odd numbered sectors is a track. Tracks are
# numbered 1-40. The knitting machine always writes sectors
# in even/odd pairs, and when the odd sector is written, both
# sectors are concatenated to a file named fileqq.dat, where
# qq is the sector number.
#

# The Knitting machine does not parse the returned hex ascii values
# unless they are ALL UPPER CASE. Lower case characters a-f appear
# to parse as zeros.

# You will need the (very nice) pySerial module, found here:
# http://pyserial.wiki.sourceforge.net/pySerial

import sys
import os
import os.path
from array import * # type: ignore
import serial

version = "2.0"

#
# Note that this code makes a fundamental assumption which
# is only true for the disk format used by the brother knitting
# machine, which is that there is only one logical sector (LS) per
# physical sector (PS). The PS size is fixed at 1280 bytes, and
# the brother uses a LS size of 1024 bytes, so only one can fit.
#


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


class PDDemulator:

    def __init__(self, basename):
        self.listeners = list[PDDEmulatorListener]  # list of PDDEmulatorListener
        self.verbose = True
        self.noserial = False
        self.ser: serial.Serial
        self.disk = Disk(basename)
        self.FDCmode = False
        # bytes per logical sector
        self.bpls = 1024
        self.formatLength = {
            b"0": 64,
            b"1": 80,
            b"2": 128,
            b"3": 256,
            b"4": 512,
            b"5": 1024,
            b"6": 1280,
        }
        return

    def __del__(self):
        return

    def open(self, cport="/dev/ttyUSB0") -> None:
        print('trying to open port: ', cport)
        if self.noserial is False:
            self.ser = serial.Serial(
                port=cport,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=False,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )
            #            self.ser.setRTS(True)
            if self.ser == None:
                print("Unable to open serial device %s" % cport)
                raise IOError
        return

    def close(self) -> None:
        if self.noserial is not False:
            if self.ser:
                self.ser.close()
        return

    def dumpchars(self) -> None:
        num = 1
        while 1:
            inc = self.ser.read()
            if len(inc) != 0:
                print("flushed 0x%02X (%d)" % (ord(inc), num))
                num = num + 1
            else:
                break
        return

    def readsomechars(self, num: int) -> bytes:
        sch = self.ser.read(num)
        while len(sch) < num:
            sch += self.ser.read(num - len(sch))
        return sch

    def readchar(self) -> bytes:
        inc = ""
        while len(inc) == 0:
            inc = self.ser.read()
        return inc

    def writebytes(self, b: bytes) -> None:
        self.ser.write(b)
        return

    def readFDDRequest(self) -> list[bytes]:
        inbuf = []
        # read through a carriage return
        # parameters are seperated by commas
        while True:
            inc = self.readchar()
            if inc == b"\r":
                break
            elif inc == b" ":
                continue
            else:
                inbuf.append(inc)

        all = b"".join(inbuf)
        rv = all.split(b",")
        return rv

    def getPsnLsn(self, info: list[bytes]) -> tuple[int, int]:
        psn = 0
        lsn = 1
        if len(info) >= 1 and info[0] != b"":
            val = int(info[0])
            if psn <= 79:
                psn = val
        if len(info) > 1 and info[1] != b"":
            val = int(info[0])
        return psn, lsn

    def readOpmodeRequest(self, req: int):
        buff = array("b")
        sum = req
        reqlen = ord(self.readchar())
        buff.append(reqlen)
        sum = sum + reqlen

        for x in range(reqlen, 0, -1):
            rb = ord(self.readchar())
            buff.append(rb)
            sum = sum + rb

        # calculate ckecksum
        sum = sum % 0x100
        sum = sum ^ 0xFF

        chkbit = self.readchar()
        cksum = ord(chkbit)

        if cksum == sum:
            # if self.verbose:
            #     print(f"Checksum match! {req} {chkbit}")
            return buff
        else:
            if self.verbose:
                print("Checksum mismatch!!")
            return None

    def handleRequests(self):
        synced = False
        while True:
            self.handleRequest()
        # never returns
        return

    def handleRequest(self, blocking=True) -> None:
        if not blocking:
            if self.ser.in_waiting == 0:
                return
        inc = self.readchar()
        if self.FDCmode:
            self.handleFDCmodeRequest(inc)
        else:
            # in OpMode, look for ZZ
            # inc = self.readchar()
            if inc != b"Z":
                return
            inc = self.readchar()
            if inc == b"Z":
                self.handleOpModeRequest()
            else:
                print(f'Unknown op mode command: {hex(ord(inc))}')

    def handleOpModeRequest(self) -> None:
        req = ord(self.ser.read())
        print(f"Request: {req}" )
        if req == 0x08:
            # Change to FDD emulation mode (no data returned)
            inbuf = self.readOpmodeRequest(req)
            if inbuf != None:
                # Change Modes, leave any incoming serial data in buffer
                self.FDCmode = True
        else:
            print("Invalid OpMode request code 0X%02X received" % req)
        return

    def handleFDCmodeRequest(self, cmd: bytes) -> None:
        # Commands may be followed by an optional space
        # PSN (physical sector) range 0-79
        # LSN (logical sector) range 0-(number of logical sectors in a physical sector)
        # LSN defaults to 1 if not supplied
        #
        # Result code information (verbatim from the Tandy reference):
        #
        # After the drive receives a command in FDC-emulation mode, it transmits
        # 8 byte characters which represent 4 bytes of status code in hexadecimal.
        #
        # * The first and second bytes contain the error status. A value of '00'
        #   indicates that no error occurred
        #
        # * The third and fourth bytes usually contain the number of the physical
        #   sector where data is kept in the buffer
        #
        #   For the D, F, and S commands, the contents of these bytes are different.
        #   See the command descriptions in these cases.
        #
        # * The fifth-eighth bytes usual show the logical sector length of the data
        #   kept in the RAM buffer, except the third and fourth digits are 'FF'
        #
        #   In the case of an S, C, or M command -- or an F command that ends in
        #   an error -- the bytes contain '0000'
        #
        print("Handling command", cmd)

        match cmd:

            case b"\r":
                self.writebytes(b"00000000")
                return

            case b"Z":
                # Hmmm, looks like we got the start of an Opmode Request
                inc = self.readchar()
                if inc == b"Z":
                    # definitely!
                    print("Detected Opmode Request in FDC Mode, switching to OpMode")
                    self.FDCmode = False
                    self.handleOpModeRequest()

            case b"M":
                # apparently not used by brother knitting machine
                print("FDC Change Modes")
                raise
                # following parameter - 0=FDC, 1=Operating

            case b"D":
                # apparently not used by brother knitting machine
                print("FDC Check Device")
                raise
                # Sends result in third and fourth bytes of result code
                # See doc - return zero for disk installed and not swapped

            case b"F" | b"G":
                print('FDC Format')
                info = self.readFDDRequest()

                if len(info) != 1:
                    print(
                        "wrong number of params (%d) received, assuming 1024 bytes per sector"
                        % len(info)
                    )
                    bps = 1024
                else:
                    try:
                        bps = self.formatLength[info[0]]
                    except KeyError:
                        print(
                            f"Invalid code {info[0]} for format, assuming 1024 bytes per sector"
                        )
                        bps = 1024
                # we assume 1024 because that's what the brother machine uses
                if self.bpls != bps:
                    print("Bad news, differing sector sizes")
                    self.bpls = bps

                print(f"Formatting disk, {bps}")
                self.disk.format()
                print("Format complete, replying")

                # But this is probably more correct
                if cmd == b"G":
                    self.writebytes(b"00000000")
                else:
                    self.writebytes(b"000000FF")

                more = self.readchar()
                if more:
                    self.handleFDCmodeRequest(more)

                # After a format, we always start out with OPMode again
                self.FDCmode = False

            case b"A":
                # Followed by physical sector number (0-79), defaults to 0
                # returns ID data, not sector data
                info = self.readFDDRequest()
                psn, _ = self.getPsnLsn(info)
                print(f"FDC Read ID Section {psn}")

                try:
                    id = self.disk.getSectorID(psn)
                except:
                    print(f"Error getting Sector ID {psn}, quitting")
                    self.writebytes(b"80000000")
                    raise


                resp = b"00" + b"%02X" % psn + b"0000"
                # resp = b"0000" + b"%02X" % psn + b"00"
                print(resp)
                self.writebytes(resp)

                # see whether to send data
                go = self.readchar()
                if go == b"\r":
                    self.writebytes(id)

            case b"R":
                # Followed by Physical Sector Number PSN and Logical Sector Number LSN
                info = self.readFDDRequest()
                psn, lsn = self.getPsnLsn(info)
                print("FDC Read one Logical Sector %d" % psn)

                try:
                    sd = self.disk.readSector(psn, lsn)
                except:
                    print("Failed to read Sector %d, quitting" % psn)
                    self.writebytes(b"80000000")
                    raise

                self.writebytes(b"00" + b"%02X" % psn + b"0000")

                # see whether to send data
                go = self.readchar()
                if go == b"\r":
                    self.writebytes(sd)

            case b"S":
                # We receive (optionally) PSN, (optionally) LSN
                # This is not documented well at all in the manual
                # What is expected is that all sectors will be searched
                # and the sector number of the first matching sector
                # will be returned. The brother machine always sends
                # PSN = 0, so it is unknown whether searching should
                # start at Sector 0 or at the PSN sector
                info = self.readFDDRequest()
                psn, lsn = self.getPsnLsn(info)
                print("FDC Search ID Section %d" % psn)

                # Now we must send status (success)
                self.writebytes(b"00" + b"%02X" % psn + b"0000")

                # self.writebytes(b'00000000')

                # we receive 12 bytes here
                # compare with the specified sector (formatted is apparently zeros)
                id = self.readsomechars(12)
                print("checking ID for sector %d" % psn)

                try:
                    status = self.disk.findSectorID(psn, id)
                except:
                    print("FAIL")
                    status = "30000000"
                    raise

                print("returning %s" % status)
                # guessing - doc is unclear, but says that S always ends in 0000
                # MATCH 00000000
                # MATCH 02000000
                # infinite retries 10000000
                # infinite retries 20000000
                # blinking error 30000000
                # blinking error 40000000
                # infinite retries 50000000
                # infinite retries 60000000
                # infinite retries 70000000
                # infinite retries 80000000

                self.writebytes(status)

                # Stay in FDC mode

            case b"B" | b"C":
                # Followed by PSN 0-79, defaults to 0
                # When received, send result status, if not error, wait
                # for data to be written, then after write, send status again
                info = self.readFDDRequest()
                psn, lsn = self.getPsnLsn(info)
                print(f"FDC Write ID section {psn}, lsn {lsn}")

                self.writebytes(b"00" + b"%02X" % psn + b"0000")

                id = self.readsomechars(12)

                try:
                    self.disk.setSectorID(psn, id)
                except:
                    print("Failed to write ID for sector %d, quitting" % psn)
                    self.writebytes(b"80000000")
                    raise

                self.writebytes(b"00" + b"%02X" % psn + b"0000")

                more = self.readchar()
                if more:
                    self.handleFDCmodeRequest(more)

            case b"W" | b"X":
                info = self.readFDDRequest()
                psn, lsn = self.getPsnLsn(info)
                print("FDC Write logical sector %d" % psn)

                # Now we must send status (success)
                self.writebytes(b"00" + b"%02X" % psn + b"0000")

                indata = self.readsomechars(1024)
                try:
                    self.disk.writeSector(psn, lsn, indata)
                    for l in self.listeners:
                        l.dataReceived(self.disk.lastDatFilePath)
                    print("Saved data in dat file: ", self.disk.lastDatFilePath)
                except:
                    print("Failed to write data for sector %d, quitting" % psn)
                    self.writebytes(b"80000000")
                    raise

                self.writebytes(b"00" + b"%02X" % psn + b"0000")

            case _:
                print(f"Unknown FDC command {cmd} received")

        # return to Operational Mode
        return


class PDDEmulatorListener:
    def dataReceived(self, fullFilePath: str):
        pass


# meat and potatos here

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("%s version %s" % (sys.argv[0], version))
        print("Usage: %s basedir serialdevice" % sys.argv[0])
        sys.exit()

    print("Preparing . . . Please Wait")
    emu = PDDemulator(sys.argv[1])

    emu.open(cport=sys.argv[2])

    print("Emulator Ready!")
    try:
        while 1:
            emu.handleRequests()
    except KeyboardInterrupt:
        pass

    emu.close()
