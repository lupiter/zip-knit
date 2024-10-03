import serial


class SerialConnection:
    ser: serial.Serial

    def __init__(self, port: str) -> None:
        print("trying to open port: ", port)
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=False,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
        #            self.ser.setRTS(True)
        if self.ser is None:
            print(f"Unable to open serial device {port}")
            raise IOError

    def close(self) -> None:
        if self.ser:
            self.ser.close()

    def dump_chars(self) -> None:
        num = 1
        while 1:
            inc = self.ser.read()
            if len(inc) != 0:
                print(f"flushed 0x{ord(inc)}X ({num})")
                num = num + 1
            else:
                break

    def read(self) -> bytes:
        return self.ser.read()

    def read_some_chars(self, num: int) -> bytes:
        sch = self.ser.read(num)
        while len(sch) < num:
            sch += self.ser.read(num - len(sch))
        return sch

    def read_char(self) -> bytes:
        inc = ""
        while len(inc) == 0:
            inc = self.ser.read()
        return inc

    def write_bytes(self, b: bytes) -> None:
        self.ser.write(b)

    @staticmethod
    def get_physical_logical_sector_numbers(info: list[bytes]) -> tuple[int, int]:
        physical = 0
        logical = 1
        if len(info) >= 1 and info[0] != b"":
            val = int(info[0])
            if physical <= 79:
                physical = val
        if len(info) > 1 and info[1] != b"":
            val = int(info[0])
        return physical, logical
