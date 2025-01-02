#!/usr/bin/env python

# meat and potatos here

import sys
# from pddemulate.drive import PDDemulator
from pddemulate.process import DiskProcess

VERSION = "2.0"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"{sys.argv[0]} version {VERSION}")
        print(f"Usage: {sys.argv[0]} basedir serialdevice")
        sys.exit()

    print("Preparing . . . Please Wait")
    
    processor = DiskProcess(sys.argv[1], print)
    # emu = PDDemulator(sys.argv[1])

    processor.start(port=sys.argv[2])
    # emu.open(cport=sys.argv[2])

    print("Emulator Ready!")
    try:
        processor.queue_check()
        # while True:
        #     emu.handle_requests()
    except KeyboardInterrupt:
        pass

    processor.exit()
    # emu.close()
