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
        if self.ser == None:
            print("Unable to open serial device %s" % port)
            raise IOError
        return

    def close(self) -> None:
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
    
    def read(self) -> bytes:
        return self.ser.read()

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
    
    @staticmethod
    def getPhysicalLogicalSectorNumbers(info: list[bytes]) -> tuple[int, int]:
        physical = 0
        logical = 1
        if len(info) >= 1 and info[0] != b"":
            val = int(info[0])
            if physical <= 79:
                physical = val
        if len(info) > 1 and info[1] != b"":
            val = int(info[0])
        return physical, logical