import os

class Config:
    imgdir: str = "img"
    device: str = "/dev/ttyUSB0"
    datFile: str
    simulateEmulator: bool = False

    def __init__(self):
        if os.sys.platform == "win32":
            self.device = "com34"
            #            self.datFile = 'C:/Documents and Settings/ondro/VirtualBox shared folder/knitting/knitting_machine-master/img/zaloha vzory stroj python.dat'
            self.datFile = "C:/Documents and Settings/ondro/VirtualBox shared folder/knitting/knitting_machine-master/file-06.dat"
            self.simulateEmulator = True
