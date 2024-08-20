from array import * # type: ignore

from PDDemulate.Disk import Disk
from PDDemulate.Listener import PDDEmulatorListener
from PDDemulate.Serial import SerialConnection


class PDDemulator:
    serial: SerialConnection

    def __init__(self, basename, verbose=True):
        self.listeners = list[PDDEmulatorListener]  # list of PDDEmulatorListener
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
    
    def open(self, cport="/dev/ttyUSB0") -> None:
        self.serial = SerialConnection(cport)

    def close(self) -> None:
        self.serial = None

    def __readFDDRequest(self) -> list[bytes]:
        inbuf = []
        # read through a carriage return
        # parameters are seperated by commas
        while True:
            inc = self.serial.readchar()
            if inc == b"\r":
                break
            elif inc == b" ":
                continue
            else:
                inbuf.append(inc)

        all = b"".join(inbuf)
        rv = all.split(b",")
        return rv


    def __readOpmodeRequest(self, req: int):
        buff = array("b")
        sum = req
        reqlen = ord(self.serial.readchar())
        buff.append(reqlen)
        sum = sum + reqlen

        for x in range(reqlen, 0, -1):
            rb = ord(self.serial.readchar())
            buff.append(rb)
            sum = sum + rb

        # calculate ckecksum
        sum = sum % 0x100
        sum = sum ^ 0xFF

        chkbit = self.serial.readchar()
        cksum = ord(chkbit)

        if cksum == sum:
            # if self.verbose:
            #     print(f"Checksum match! {req} {chkbit}")
            return buff
        else:
            if self.verbose:
                print("Checksum mismatch!!")
            return None

    def handleRequests(self): # never returns
        while True:
            self.handleRequest()

    def handleRequest(self, blocking=True) -> None:
        if not blocking:
            if self.ser.in_waiting == 0:
                return
        inc = self.serial.readchar()
        if self.FDCmode:
            self.__handleFDCmodeRequest(inc)
        else:
            # in OpMode, look for ZZ
            # inc = self.serial.readchar()
            if inc != b"Z":
                return
            inc = self.serial.readchar()
            if inc == b"Z":
                self.__handleOpModeRequest()
            else:
                print(f'Unknown op mode command: {hex(ord(inc))}')

    def __handleOpModeRequest(self) -> None:
        req = ord(self.ser.read())
        print(f"Request: {req}" )
        if req == 0x08:
            # Change to FDD emulation mode (no data returned)
            inbuf = self.__readOpmodeRequest(req)
            if inbuf != None:
                # Change Modes, leave any incoming serial data in buffer
                self.FDCmode = True
        else:
            print("Invalid OpMode request code 0X%02X received" % req)
        return

    def __handleFDCmodeRequest(self, cmd: bytes) -> None:
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
                self.serial.writebytes(b"00000000")
                return

            case b"Z":
                # Hmmm, looks like we got the start of an Opmode Request
                inc = self.serial.readchar()
                if inc == b"Z":
                    # definitely!
                    print("Detected Opmode Request in FDC Mode, switching to OpMode")
                    self.FDCmode = False
                    self.__handleOpModeRequest()

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
                info = self.__readFDDRequest()

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
                    self.serial.writebytes(b"00000000")
                else:
                    self.serial.writebytes(b"000000FF")

                more = self.serial.readchar()
                if more:
                    self.__handleFDCmodeRequest(more)

                # After a format, we always start out with OPMode again
                self.FDCmode = False

            case b"A":
                # Followed by physical sector number (0-79), defaults to 0
                # returns ID data, not sector data
                info = self.__readFDDRequest()
                psn, _ = SerialConnection.getPsnLsn(info)
                print(f"FDC Read ID Section {psn}")

                try:
                    id = self.disk.getSectorID(psn)
                except:
                    print(f"Error getting Sector ID {psn}, quitting")
                    self.serial.writebytes(b"80000000")
                    raise


                resp = b"00" + b"%02X" % psn + b"0000"
                # resp = b"0000" + b"%02X" % psn + b"00"
                print(resp)
                self.serial.writebytes(resp)

                # see whether to send data
                go = self.serial.readchar()
                if go == b"\r":
                    self.serial.writebytes(id)

            case b"R":
                # Followed by Physical Sector Number PSN and Logical Sector Number LSN
                info = self.__readFDDRequest()
                psn, lsn = SerialConnection.getPsnLsn(info)
                print("FDC Read one Logical Sector %d" % psn)

                try:
                    sd = self.disk.readSector(psn, lsn)
                except:
                    print("Failed to read Sector %d, quitting" % psn)
                    self.serial.writebytes(b"80000000")
                    raise

                self.serial.writebytes(b"00" + b"%02X" % psn + b"0000")

                # see whether to send data
                go = self.serial.readchar()
                if go == b"\r":
                    self.serial.writebytes(sd)

            case b"S":
                # We receive (optionally) PSN, (optionally) LSN
                # This is not documented well at all in the manual
                # What is expected is that all sectors will be searched
                # and the sector number of the first matching sector
                # will be returned. The brother machine always sends
                # PSN = 0, so it is unknown whether searching should
                # start at Sector 0 or at the PSN sector
                info = self.__readFDDRequest()
                psn, lsn = SerialConnection.getPsnLsn(info)
                print("FDC Search ID Section %d" % psn)

                # Now we must send status (success)
                self.serial.writebytes(b"00" + b"%02X" % psn + b"0000")

                # self.serial.writebytes(b'00000000')

                # we receive 12 bytes here
                # compare with the specified sector (formatted is apparently zeros)
                id = self.serial.readsomechars(12)
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

                self.serial.writebytes(status)

                # Stay in FDC mode

            case b"B" | b"C":
                # Followed by PSN 0-79, defaults to 0
                # When received, send result status, if not error, wait
                # for data to be written, then after write, send status again
                info = self.__readFDDRequest()
                psn, lsn = SerialConnection.getPsnLsn(info)
                print(f"FDC Write ID section {psn}, lsn {lsn}")

                self.serial.writebytes(b"00" + b"%02X" % psn + b"0000")

                id = self.serial.readsomechars(12)

                try:
                    self.disk.setSectorID(psn, id)
                except:
                    print("Failed to write ID for sector %d, quitting" % psn)
                    self.serial.writebytes(b"80000000")
                    raise

                self.serial.writebytes(b"00" + b"%02X" % psn + b"0000")

                more = self.serial.readchar()
                if more:
                    self.__handleFDCmodeRequest(more)

            case b"W" | b"X":
                info = self.__readFDDRequest()
                psn, lsn = SerialConnection.getPsnLsn(info)
                print("FDC Write logical sector %d" % psn)

                # Now we must send status (success)
                self.serial.writebytes(b"00" + b"%02X" % psn + b"0000")

                indata = self.serial.readsomechars(1024)
                try:
                    self.disk.writeSector(psn, lsn, indata)
                    for l in self.listeners:
                        l.dataReceived(self.disk.lastDatFilePath)
                    print("Saved data in dat file: ", self.disk.lastDatFilePath)
                except:
                    print("Failed to write data for sector %d, quitting" % psn)
                    self.serial.writebytes(b"80000000")
                    raise

                self.serial.writebytes(b"00" + b"%02X" % psn + b"0000")

            case _:
                print(f"Unknown FDC command {cmd} received")

        # return to Operational Mode
        return


