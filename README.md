# Zipknit

## What?

This is an attempt to emulate the FB-100 drive. If you're using a knitting machine, you're probably looking for one of the following projects instead:

* [img2track](https://daviworks.com/knitting/) works with Brother 900-series knitting machines with a FB-100 port and a special cable
* [AYAB](http://www.ayab-knitting.com/) is a guts replacement hardware and software solution, particularly targeting those machines with a broken mylar reader

## Goals

To be able to:

1. Talk to a KH-970 ✅
2. Read the "floppy" format produced by "formatting" ✅
3. Read the "floppy" data produced by saving the CB-1 stored patterns 
4. Replace/modify patterns
5. Replace/modify garments
6. Create new pattersn and garments
7. Create new disks

### Status

Step 3: It can kind of read the data, but is very confused by the format of what I've saved so far which is just garment shapes.

I should find somewhere to archive the saved binary data for future use.

## Start

```bash
brew install python-tk

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

python3 main.py
```


# Prior Art

This is a fork of https://github.com/adafruit/knitting_machine and maintains the GPL 2.0 License

The work that Steve Conklin did was based on earlier work by John R. Hogerhuis.

This was extended by Becky and Limor and others, including Travis Goodspeed:

http://travisgoodspeed.blogspot.com/2010/12/hacking-knitting-machines-keypad.html
