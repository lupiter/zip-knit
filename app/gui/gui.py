from tkinter import StringVar, VERTICAL, RIGHT, LEFT, Listbox, Canvas, BOTH, END, Tk, Y
from tkinter.ttk import Button, Label, Entry, Frame, Scrollbar
from tkinter.ttk import Style

from app.gui.devices import Devices


class Gui: # pylint: disable=too-many-instance-attributes
    """Manager for the UI setting up the buttons and layout"""
    __max_columns = 1000
    __max_rows = 1000
    __row = 0
    main_window: Tk

    def __init__(self, window: Tk) -> None:
        self.__init_main_window(window)
        self.__create_device_widgets()
        self.__create_emulator_button()

        self.__row += 1
        self.__create_dat_file_widgets()

        self.__row += 1
        self.__create_patterns_panel()

        self.__row += 1
        self.__create_info_messages_label()

    def __init_main_window(self, main_window: Tk) -> None:
        self.main_window = main_window
        self.main_window.title("Zip Knit")
        self.main_window.geometry("800x600")
        self.main_window.grid()
        self.main_window.grid_columnconfigure(1, weight=10)
        self.main_window.grid_columnconfigure(2, weight=1)
        self.main_window.resizable(True, True)

    def __create_device_widgets(self) -> None:
        label = Label(self.main_window, text="Device:")
        label.grid(column=0, row=self.__row, sticky="E", pady=5, padx=5)

        self.main_window.deviceEntry = Devices(self.main_window, self.__row, 1)

        # entryText = StringVar()
        # self.mainWindow.deviceEntry = Entry(self.mainWindow, textvariable=entryText)
        # self.mainWindow.deviceEntry.grid(column=1,row=self._row,sticky='EW')
        # self.mainWindow.deviceEntry.entryText = entryText

    def __create_emulator_button(self) -> None:
        caption = StringVar()
        self.emu_button = Button(
            self.main_window,
            textvariable=caption,
            command=self.main_window.emu_button_clicked,
        )
        self.emu_button.caption = caption
        self.emu_button.grid(column=2, row=self.__row, columnspan=2, sticky="EW")
        self.set_emu_button_stopped()

        but = Button(
            self.main_window, text="Help...", command=self.main_window.help_button_clicked
        )
        but.grid(column=4, row=self.__row, sticky="E", padx=5, pady=5)

    def __create_dat_file_widgets(self) -> None:
        label = Label(self.main_window, text="Dat file:")
        label.grid(column=0, row=self.__row, sticky="E", padx=5)

        entry_text = StringVar()
        self.main_window.datFileEntry = Entry(self.main_window, textvariable=entry_text)
        self.main_window.datFileEntry.grid(column=1, row=self.__row, sticky="EW")
        self.main_window.datFileEntry.entryText = entry_text

        self.choose_dat_file_button = Button(
            self.main_window,
            text="...",
            command=self.main_window.choose_dat_file_button_clicked,
        )
        self.choose_dat_file_button.grid(column=2, row=self.__row, sticky="W")

        self.reload_dat_file_button = Button(
            self.main_window,
            text="Reload file",
            command=self.main_window.reload_dat_file_button_clicked,
        )
        self.reload_dat_file_button.grid(column=3, row=self.__row, sticky="EW")

        but = Button(
            self.main_window,
            text="Store track",
            command=self.main_window.store_track_button_clicked,
        )
        but.grid(column=4, row=self.__row, sticky="EW", padx=5)
        self.store_track_button = but

    def __create_info_messages_label(self) -> None:
        label_text = StringVar()
        style = Style()
        style.configure("BW.TLabel", foreground="white", background="blue")

        label = Label(
            self.main_window, anchor="w", style="BW.TLabel", textvariable=label_text
        )
        label.grid(column=0, row=self.__row, columnspan=self.__max_columns, sticky="EW")
        label.caption = label_text
        self.main_window.infoLabel = label

    def __create_patterns_panel(self) -> None:
        pattern_frame = Frame(self.main_window)
        pattern_frame.grid(
            column=0, row=self.__row, columnspan=self.__max_columns, sticky="EWNS"
        )
        self.main_window.grid_rowconfigure(self.__row, weight=1)
        pattern_frame.grid_columnconfigure(0, weight=0)
        pattern_frame.grid_columnconfigure(1, weight=1)
        pattern_frame.grid_rowconfigure(1, weight=1)

        listbox_frame = Frame(pattern_frame)
        listbox_frame.grid(column=0, row=0, sticky="EWNS", rowspan=self.__max_rows)
        scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
        listvar = StringVar()
        lb = Listbox(
            listbox_frame,
            listvariable=listvar,
            exportselection=0,
            width=40,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=lb.yview)
        lb.items = ListboxVar(lb, listvar)
        scrollbar.pack(side=RIGHT, fill=Y)
        lb.pack(side=LEFT, fill=BOTH, expand=1)
        self.main_window.patternListBox = lb

        textvar = StringVar()
        label = Label(pattern_frame, anchor="w", textvariable=textvar)
        label.grid(column=1, row=0, sticky="EW")
        label.caption = textvar
        self.main_window.patternTitle = label

        self.insert_bitmap_button = Button(
            pattern_frame,
            text="Insert bitmap...",
            command=self.main_window.insert_bitmap_button_clicked,
        )
        self.insert_bitmap_button.grid(column=2, row=0, sticky="EW")

        self.export_bitmap_button = Button(
            pattern_frame,
            text="Export bitmap...",
            command=self.main_window.export_bitmap_button_clicked,
        )
        self.export_bitmap_button.grid(column=3, row=0, sticky="EW")

        pc = ExtendedCanvas(pattern_frame, bg="white")
        pc.grid(column=1, row=1, sticky="EWNS", columnspan=3)
        self.main_window.pattern_canvas = pc

    def set_emu_button_stopped(self) -> None:
        b = self.emu_button
        b.caption.set("Start emulator")

    def set_emu_button_started(self) -> None:
        b = self.emu_button
        b.caption.set("Stop emulator")


class ExtendedCanvas(Canvas): # pylint: disable=too-many-ancestors
    """Canvas, with convenience method to clear it"""
    def get_width(self) -> int:
        """Width in pixels"""
        w = self.winfo_width()
        return w

    def get_height(self) -> int:
        """Height in pixels"""
        h = self.winfo_height()
        return h

    def clear(self) -> None:
        """Empty the canvas"""
        maxsize = 10000
        self.create_rectangle(0, 0, maxsize, maxsize, width=0, fill=self.cget("bg"))


class ListboxVar: # pylint: disable=too-few-public-methods
    """Items for showing in a Listbox"""
    def __init__(self, listbox, stringvar) -> None:
        self._stringvar = stringvar
        self._listbox = listbox

    def set(self, items) -> None:
        """Replace everything"""
        self._listbox.delete(0, END)
        for item in items:
            self._listbox.insert(END, item)
