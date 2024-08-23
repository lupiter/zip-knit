#!/usr/bin/python
# -*- coding: UTF-8 -*-
import atexit
import signal

from app.tkapp.KnittingApp import KnittingApp
	
if __name__ == "__main__":
	app = KnittingApp()
	atexit.register(app.quitApplication)
	signal.signal(signal.SIGTERM, app.quitApplication)
	try:
		app.mainloop()
	except KeyboardInterrupt:
		app.quitApplication()