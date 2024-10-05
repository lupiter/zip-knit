import os


class Config:  # pylint: disable=too-few-public-methods
    imgdir: str = "img"
    device: str = "/dev/ttyUSB0"
    dat_file: str
    simulate_emulator: bool = False

    def __init__(self):
        if os.sys.platform == "win32":
            self.device = "com34"
            self.simulate_emulator = True
