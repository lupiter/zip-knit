#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""An application for emulating a FB-100 floppy disk drive 
   connected to a Brother knitting machine."""
import atexit
import signal

from app.tkapp.knitting_app import KnittingApp

if __name__ == "__main__":
    app = KnittingApp()
    atexit.register(app.quit_application)
    signal.signal(signal.SIGTERM, app.quit_application)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.quit_application()
