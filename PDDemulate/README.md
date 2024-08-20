This software emulates the external floppy disk drive used
by the Brother Electroknit KH-930E computerized knitting machine.
It may work for other models, but has only been tested with the
Brother KH-930E

This emulates the disk drive and stores the saved data from
the knitting machine on the linux file system. It does not
read or write floppy disks.

The disk drive used by the brother knitting machine is the same
as a Tandy PDD1 drive. This software does not support the entire
command API of the PDD1, only what is required for the knitting
machine.



Notes about data storage:

The external floppy disk is formatted with 80 sectors of 1024
bytes each. These sectors are numbered (internally) from 0-79.
When starting this emulator, a base directory is specified.
In this directory the emulator creates 80 files, one for each
sector. These are kept sync'd with the emulator's internal
storage of the same sectors. For each sector, there are two
files, nn.dat, and nn.id, where 00 <= nn <= 79.

The knitting machine uses two sectors for each saved set of
information, which are referred to in the knitting machine
manual as 'tracks' (which they were on the floppy disk). Each
pair of even/odd numbered sectors is a track. Tracks are
numbered 1-40. The knitting machine always writes sectors
in even/odd pairs, and when the odd sector is written, both
sectors are concatenated to a file named fileqq.dat, where
qq is the sector number.


The Knitting machine does not parse the returned hex ascii values
unless they are ALL UPPER CASE. Lower case characters a-f appear
to parse as zeros.

You will need the (very nice) pySerial module, found here:
http://pyserial.wiki.sourceforge.net/pySerial