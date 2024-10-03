#!/usr/bin/env python

# meat and potatos here

import sys
from pddemulate.drive import PDDemulator

VERSION = "2.0"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"{sys.argv[0]} version {VERSION}")
        print(f"Usage: {sys.argv[0]} basedir serialdevice")
        sys.exit()

    print("Preparing . . . Please Wait")
    emu = PDDemulator(sys.argv[1])

    emu.open(cport=sys.argv[2])

    print("Emulator Ready!")
    try:
        while True:
            emu.handle_requests()
    except KeyboardInterrupt:
        pass

    emu.close()
