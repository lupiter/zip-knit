import serial
import serial.tools
import serial.tools.list_ports
from tkinter import *
from tkinter.ttk import *
from serial.tools.list_ports_common import ListPortInfo


class Devices:
    def __init__(self, parent, row, column) -> None:
        self.parent = parent
        self.label = StringVar()

        self.options = [port for port in serial.tools.list_ports.comports()]

        if len(self.options) == 0:
            self.options.append("No devices found")
        self.label.set(self.options[0].name)

        self.dropdown = OptionMenu(
            self.parent, self.label, *[option.name for option in self.options]
        )
        self.dropdown.grid(row=row, column=column, stick="EW")

    def scan(self):
        pass

    def get(self) -> ListPortInfo:
        name = self.label.get()
        for option in self.options:
            if option.name == name:
                return option.device

    def set(self, device) -> None:
        for option in self.options:
            if option.device == device:
                self.label.set(device)
