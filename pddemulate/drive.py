from array import array  # type: ignore

from pddemulate.disk import Disk
from pddemulate.listener import PDDEmulatorListener
from pddemulate.serial import SerialConnection

FORMAT_LENGTH = {
    b"0": 64,
    b"1": 80,
    b"2": 128,
    b"3": 256,
    b"4": 512,
    b"5": 1024,
    b"6": 1280,
}


class PDDemulator:
    serial: SerialConnection = None
    listeners: list[PDDEmulatorListener] = []  # list of PDDEmulatorListener
    fdc_mode = False
    disk: Disk
    # bytes per logical sector
    bpls = 1024

    def __init__(self, basename):
        self.disk = Disk(basename)

    def open(self, cport="/dev/ttyUSB0") -> None:
        self.serial = SerialConnection(cport)

    def is_open(self) -> None:
        return self.serial is not None

    def close(self) -> None:
        self.serial = None

    def __read_fdd_request(self) -> list[bytes]:
        inbuf = []
        # read through a carriage return
        # parameters are seperated by commas
        while True:
            inc = self.serial.read_char()
            if inc == b"\r":
                break
            if inc == b" ":
                continue
            inbuf.append(inc)

        all_data = b"".join(inbuf)
        rv = all_data.split(b",")
        return rv

    def __read_opmode_request(self, req: int):
        buff = array("b")
        checksum = req
        reqlen = ord(self.serial.read_char())
        buff.append(reqlen)
        checksum = checksum + reqlen

        for _ in range(reqlen, 0, -1):
            rb = ord(self.serial.read_char())
            buff.append(rb)
            checksum = checksum + rb

        # calculate ckecksum
        checksum = checksum % 0x100
        checksum = checksum ^ 0xFF

        chkbit = self.serial.read_char()
        cksum = ord(chkbit)

        if cksum == checksum:
            # if self.verbose:
            #     print(f"Checksum match! {req} {chkbit}")
            return buff
        print("Checksum mismatch!!")
        return None

    def handle_requests(self):  # never returns
        while True:
            self.handle_request()

    def handle_request(self) -> None:
        inc = self.serial.read_char()
        if self.fdc_mode:
            self.__handle_fdc_mode_request(inc)
        else:
            # in OpMode, look for ZZ
            # inc = self.serial.readchar()
            if inc != b"Z":
                return
            inc = self.serial.read_char()
            if inc == b"Z":
                self.__handle_op_mode_request()
            else:
                print(f"Unknown op mode command: {hex(ord(inc))}")

    def __handle_op_mode_request(self) -> None:
        req = ord(self.serial.read())
        print(f"Request: {req}")
        if req == 0x08:
            # Change to FDD emulation mode (no data returned)
            inbuf = self.__read_opmode_request(req)
            if inbuf is not None:
                # Change Modes, leave any incoming serial data in buffer
                self.fdc_mode = True
        else:
            print(f"Invalid OpMode request code {req} received")

    def __handle_fdc_mode_request(self, cmd: bytes) -> None:
        # Commands may be followed by an optional space
        # physical sector number range 0-79
        # logical sector number range 0-(number of logical sectors in a physical sector)
        # logical sector defaults to 1 if not supplied
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
                self.serial.write_bytes(b"00000000")
                return

            case b"Z":
                # Hmmm, looks like we got the start of an Opmode Request
                inc = self.serial.read_char()
                if inc == b"Z":
                    # definitely!
                    print("Detected Opmode Request in FDC Mode, switching to OpMode")
                    self.fdc_mode = False
                    self.__handle_op_mode_request()

            case b"M":
                # apparently not used by brother knitting machine
                print("FDC Change Modes")
                raise ValueError()
                # following parameter - 0=FDC, 1=Operating

            case b"D":
                # apparently not used by brother knitting machine
                print("FDC Check Device")
                raise ValueError()
                # Sends result in third and fourth bytes of result code
                # See doc - return zero for disk installed and not swapped

            case b"F" | b"G":
                self.__format(with_check=cmd == b"G")

            case b"A":
                self.__read_id_section()

            case b"R":
                self.__read_logical_sector()

            case b"S":
                self.__search_id_section()

            case b"B" | b"C":
                self.__write_id_section(with_check=cmd == b"B")

            case b"W" | b"X":
                self.__write_logical_sector(with_check=cmd == b"W")

            case _:
                print(f"Unknown FDC command {cmd} received")

        # return to Operational Mode
        return

    def __format(self, with_check=False) -> None:
        print("FDC Format")
        info = self.__read_fdd_request()

        if len(info) != 1:
            print(
                f"wrong number of params ({len(info)}) received, assuming 1024 bytes per sector"
            )
            bps = 1024
        else:
            try:
                bps = FORMAT_LENGTH[info[0]]
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
        if with_check:
            self.serial.write_bytes(b"00000000")
        else:
            self.serial.write_bytes(b"000000FF")

        more = self.serial.read_char()
        if more:
            self.__handle_fdc_mode_request(more)

        # After a format, we always start out with OPMode again
        self.fdc_mode = False

    def __read_id_section(self) -> None:
        # Followed by physical sector number (0-79), defaults to 0
        # returns ID data, not sector data
        info = self.__read_fdd_request()
        physical_sector, _ = SerialConnection.get_physical_logical_sector_numbers(info)
        print(f"FDC Read ID Section {physical_sector}")

        try:
            sector_id = self.disk.get_sector_id(physical_sector)
        except:
            print(f"Error getting Sector ID {physical_sector}, quitting")
            self.serial.write_bytes(b"80000000")
            raise

        resp = b"00" + b"%02X" % physical_sector + b"0000"
        # resp = b"0000" + b"%02X" % physical_sector + b"00"
        print(resp)
        self.serial.write_bytes(resp)

        # see whether to send data
        go = self.serial.read_char()
        if go == b"\r":
            self.serial.write_bytes(sector_id)

    def __read_logical_sector(self) -> None:
        # Followed by Physical Sector Number and Logical Sector Number
        info = self.__read_fdd_request()
        physical_sector, logical_sector = (
            SerialConnection.get_physical_logical_sector_numbers(info)
        )
        print(f"FDC Read one Logical Sector {physical_sector}")

        try:
            sd = self.disk.read_sector(physical_sector, logical_sector)
        except:
            print(f"Failed to read Sector {physical_sector}, quitting")
            self.serial.write_bytes(b"80000000")
            raise

        self.serial.write_bytes(b"00" + b"%02X" % physical_sector + b"0000")

        # see whether to send data
        go = self.serial.read_char()
        if go == b"\r":
            self.serial.write_bytes(sd)

    def __search_id_section(self) -> None:
        # We receive (optionally) physical sector number, (optionally) logical sector number
        # This is not documented well at all in the manual
        # What is expected is that all sectors will be searched
        # and the sector number of the first matching sector
        # will be returned. The brother machine always sends
        # physical sector = 0, so it is unknown whether searching should
        # start at Sector 0 or at the physical sector
        info = self.__read_fdd_request()
        physical_sector, _ = SerialConnection.get_physical_logical_sector_numbers(info)
        print(f"FDC Search ID Section {physical_sector}")

        # Now we must send status (success)
        self.serial.write_bytes(b"00" + b"%02X" % physical_sector + b"0000")

        # self.serial.writebytes(b'00000000')

        # we receive 12 bytes here
        # compare with the specified sector (formatted is apparently zeros)
        sector_id = self.serial.read_some_chars(12)
        print(f"checking ID for sector {physical_sector}")

        try:
            status = self.disk.find_sector_id(physical_sector, sector_id)
        except:
            print("FAIL")
            status = "30000000"
            raise

        print(f"returning {status}")
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

        self.serial.write_bytes(status)

        # Stay in FDC mode

    def __write_id_section(self, with_check=False) -> None: # pylint: disable=unused-argument
        # Followed by physical sector number 0-79, defaults to 0
        # When received, send result status, if not error, wait
        # for data to be written, then after write, send status again
        info = self.__read_fdd_request()
        physical_sector, logical_sector = (
            SerialConnection.get_physical_logical_sector_numbers(info)
        )
        print(
            f"FDC Write ID section {physical_sector}, logical sector {logical_sector}"
        )

        self.serial.write_bytes(b"00" + b"%02X" % physical_sector + b"0000")

        sector_id = self.serial.read_some_chars(12)

        try:
            self.disk.set_sector_id(physical_sector, sector_id)
        except:
            print(f"Failed to write ID for sector {physical_sector}, quitting")
            self.serial.write_bytes(b"80000000")
            raise

        self.serial.write_bytes(b"00" + b"%02X" % physical_sector + b"0000")

        more = self.serial.read_char()
        if more:
            self.__handle_fdc_mode_request(more)

    def __write_logical_sector(self, with_check=False) -> None: # pylint: disable=unused-argument
        info = self.__read_fdd_request()
        physical_sector, logical_sector = (
            SerialConnection.get_physical_logical_sector_numbers(info)
        )
        print(f"FDC Write logical sector {physical_sector}")

        # Now we must send status (success)
        self.serial.write_bytes(b"00" + b"%02X" % physical_sector + b"0000")

        indata = self.serial.read_some_chars(1024)
        try:
            self.disk.write_sector(physical_sector, logical_sector, indata)
            for l in self.listeners:
                l.dataReceived(self.disk.last_dat_file_path)
            print("Saved data in dat file: ", self.disk.last_dat_file_path)
        except:
            print(f"Failed to write data for sector {physical_sector}, quitting")
            self.serial.write_bytes(b"80000000")
            raise

        self.serial.write_bytes(b"00" + b"%02X" % physical_sector + b"0000")
