#!/usr/bin/env python

# meat and potatos here

import sys
from PDDemulate.Drive import PDDemulator

version = "2.0"


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
        while True:
            emu.handleRequests()
    except KeyboardInterrupt:
        pass

    emu.close()
