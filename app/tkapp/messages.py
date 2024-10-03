import tkinter.messagebox as mb
import sys


class Messages:
    def __init__(self, knitting_app):
        self.app = knitting_app
        self.display_messages = True
        self.debug = True

    def show_error(self, msg):
        if self.display_messages:
            self.clear()
            sys.stderr.write("Error: " + str(msg) + "\n")
            mb.showerror("Error:", str(msg))

    def show_more_info(self, msg):
        if self.display_messages:
            self.clear()
            print(msg)
            mb.showinfo("Info:", str(msg))

    def show_info(self, msg):
        if self.display_messages:
            self.clear()
            print(msg)
            self.app.infoLabel.caption.set("Info: " + str(msg))

    def show_debug(self, msg):
        if self.debug:
            print(("DEBUG:", msg))

    def clear(self):
        if self.display_messages:
            self.app.infoLabel.caption.set("")
