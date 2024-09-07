#!/usr/bin/env python

import sys

if len(sys.argv) != 2:
    print((f"Usage: {sys.argv[0]} file.dat"))
    print("Splits a 2K file.dat file into two 1K track files track0.dat and track1.dat")
    sys.exit()

with open(sys.argv[1], "rb") as infile:
    t0dat = infile.read(1024)
    t1dat = infile.read(1024)

    with open("track0.dat", "wb") as track0file:
        with open("track1.dat", "wb") as track1file:
            track0file.write(t0dat)
            track1file.write(t1dat)
