from tkinter import StringVar
from tkinter.ttk import OptionMenu
import serial
import serial.tools
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo


class Devices:
    """A dropdown of (potential) serial devices"""

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
        """Refresh the list of available devices"""
        self.options = [port for port in serial.tools.list_ports.comports()]

    def get(self) -> ListPortInfo:
        """Currently selected device"""
        name = self.label.get()
        for option in self.options:
            if option.name == name:
                return option.device
        return None

    def set(self, device) -> None:
        """Set selected device"""
        for option in self.options:
            if option.device == device:
                self.label.set(device)
