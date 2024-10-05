#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tkinter
import tkinter.filedialog
import os
import os.path
from collections import namedtuple
from PIL import Image

from pddemulate.drive import PDDemulator
from pddemulate.listener import PDDEmulatorListener
from pattern.dump import PatternDumper
from pattern.insert import PatternInserter

from app.gui.gui import ExtendedCanvas, Gui
from app.tkapp.config import Config
from app.tkapp.messages import Messages

Point = namedtuple('Point', 'x y')

class KnittingApp(tkinter.Tk): # pylint: disable=too-many-instance-attributes
    pattern_canvas: ExtendedCanvas

    def __init__(self, parent=None) -> None:
        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.msg = Messages(self)
        self.patterns = []
        self.pattern = None
        self.current_dat_file = None

        self.init_config()

        self.gui = Gui(self)
        self.__update_pattern_canvas_last_size()
        self.patternListBox.bind("<<ListboxSelect>>", self.pattern_selected)
        self.after_idle(self.__canvas_configured)
        self.deviceEntry.set(self.__get_config().device)
        self.datFileEntry.entryText.set(self.__get_config().dat_file)

        self.emu = PDDemulator(self.__get_config().imgdir)
        self.emu.listeners.append(PDDListener(self))
        self.__set_emulator_started(False)

        self.pattern_dumper = PatternDumper()
        self.pattern_dumper.print_info_callback = self.msg.show_info
        self.pattern_inserter = PatternInserter(self.msg.show_info)
        self.pattern_inserter.print_error_callback = self.msg.show_error
        self.after_idle(self.reload_pattern_file)

    def emu_button_clicked(self) -> None:
        self.__get_config().device = self.deviceEntry.get()
        if self.emu.started:
            self.__stop_emulator()
        else:
            self.start_emulator()

    def start_emulator(self) -> None:
        self.msg.show_info("Preparing emulator. . . Please Wait")

        if self.__get_config().simulate_emulator:
            self.msg.show_info("Simulating emulator, emulator is not started...")
            self.__set_emulator_started(True)
        else:
            try:
                port = self.__get_config().device
                self.emu.open(cport=port)
                self.msg.show_info("Emulation ready!")
                self.__set_emulator_started(True)
                self.after_idle(self.emulator_loop)
            except IOError as e:
                self.msg.show_error(
                    "Ensure that TFDI cable is connected to port "
                    + port
                    + "\n\nError: "
                    + str(e)
                )
                self.__set_emulator_started(False)

    def emulator_loop(self) -> None:
        if self.emu.started:
            self.emu.handle_request()
            # repeated call to after_idle() caused all window dialogs to hang
            # out application, using after() each 10 milliseconds
            self.after(100, self.emulator_loop)
        else:
            print("waiting...")

    def __stop_emulator(self) -> None:
        if self.emu is not None:
            self.emu.close()
            self.msg.show_info("PDDemulate stopped.")
            self.__set_emulator_started(False)
        self.init_emulator()

    def quit_application(self) -> None:
        self.__stop_emulator()
        self.after_idle(self.quit)

    def __set_emulator_started(self, started) -> None:
        self.emu.started = started
        if started:
            self.gui.set_emu_button_started()
        else:
            self.gui.set_emu_button_stopped()

    def __get_config(self) -> Config:
        return self.config

    def init_config(self) -> None:
        cfg = Config()
        if not hasattr(cfg, "device"):
            cfg.device = ""
        if not hasattr(cfg, "datFile"):
            cfg.dat_file = ""
        if not hasattr(cfg, "simulateEmulator"):
            cfg.simulate_emulator = False
        self.config = cfg

    def reload_pattern_file(self, path_to_file: str = None) -> None:
        if not path_to_file:
            path_to_file = self.datFileEntry.entryText.get()
        else:
            self.datFileEntry.entryText.set(path_to_file)

        if not path_to_file:
            return
        self.current_dat_file = path_to_file
        try:
            self.patterns = self.pattern_dumper.dump_pattern([path_to_file])
            list_box_model = []
            for p in self.patterns:
                list_box_model.append(self.__get_pattern_title(p))
            selected_index = self.__get_selected_pattern_index()
            self.patternListBox.items.set(list_box_model)
            self.__set_selected_pattern_index(selected_index)
        except IOError as e:
            self.msg.show_error(
                f"Could not open pattern file {path_to_file}" + "\n" + str(e)
            )

    def __store_track(self, path_to_file=None) -> None:
        if not path_to_file:
            path_to_file = self.datFileEntry.entryText.get()
        self.msg.show_info("Storing tracks for file " + path_to_file)
        track_file_1, track_file_2 = "00.dat", "01.dat"
        track_path_1 = os.path.join(self.config.imgdir, track_file_1)
        track_path_2 = os.path.join(self.config.imgdir, track_file_2)
        track_size = 1024

        start_emu = self.emu.started
        if start_emu:
            self.__stop_emulator()

        with open(path_to_file, "rb") as infile:
            try:
                with open(track_path_1, "wb") as track0file, open(track_path_2, "wb") as track1file:
                    t0dat = infile.read(track_size)
                    t1dat = infile.read(track_size)

                    track0file.write(t0dat)
                    track1file.write(t1dat)
                    self.msg.show_info(
                        "Stored file to tracks "
                        + track_file_1
                        + " and "
                        + track_file_2
                        + " in "
                        + self.config.imgdir
                    )
            except IOError as e:
                self.msg.show_error(str(e))
            finally:
                if infile:
                    self.msg.show_debug("Closing infile...")
                if track0file:
                    self.msg.show_debug("Closing track0file...")
                if track1file:
                    self.msg.show_debug("Closing track1file...")
                if start_emu:
                    self.start_emulator()

    def help_button_clicked(self) -> None:
        help_msg = """Commands to execute on Knitting machine:

552: Download patterns from machine to computer
551: Upload patterns from computer to machine
     - before this, make sure that you stored file to track
     - afterfards pressing 551, press 1 to load track with inserted patterns
"""
        self.msg.show_more_info(help_msg)

    def reload_dat_file_button_clicked(self) -> None:
        self.reload_pattern_file()

    def store_track_button_clicked(self) -> None:
        self.__store_track()

    def choose_dat_file_button_clicked(self) -> None:
        file_path = tkinter.filedialog.askopenfilename(
            filetypes=[("DAT file", "*.dat")],
            initialfile=self.datFileEntry.entryText.get(),
            title="Choose dat file with patterns...",
        )
        if len(file_path) > 0:
            self.msg.show_info("Opened dat file " + file_path)
            self.reload_pattern_file(file_path)

    def pattern_selected(self, _) -> None:
        # w = evt.widget
        index = self.__get_selected_pattern_index()
        if index is not None:
            pattern = self.patterns[index]
        else:
            pattern = None
        self.__display_pattern(pattern)

    def __get_selected_pattern_index(self) -> int | None:
        sel = self.patternListBox.curselection()
        if len(sel) > 0:
            return int(sel[0])
        return None

    def __set_selected_pattern_index(self, index) -> None:
        lb = self.patternListBox
        if index is None:
            index = 0
        if lb.size() == 0:
            self.__display_pattern(None)
            return
        if index > lb.size():
            index = 0
        self.patternListBox.selection_set(index)
        self.__display_pattern(self.patterns[index])

    def __display_pattern(self, pattern=None) -> None:
        if not pattern:
            pattern = self.pattern
        self.pattern_canvas.clear()
        self.patternTitle.caption.set(self.__get_pattern_title(pattern))
        if pattern:
            result = self.pattern_dumper.dump_pattern(
                [self.current_dat_file, str(pattern["number"])]
            )
            if result:
                self.__print_pattern_on_canvas(result[0])
        self.pattern = pattern

    def __get_pattern_title(self, pattern) -> str:
        p = pattern
        if p:
            return (
                "Pattern no: "
                + str(p["number"])
                + " (rows x stitches: "
                + str(p["rows"])
                + " x "
                + str(p["stitches"])
                + ")"
            )
        return "No pattern"

    def __print_pattern_on_canvas(self, pattern) -> None: # pylint: disable=too-many-locals
        #        pattern = []
        #        for x in range(8):
        #            row = []
        #            for y in range(13):
        #                row.append((y % 2 + x % 2) % 2)
        #            pattern.append(row)
        pattern_height = len(pattern)
        pattern_width = len(pattern[0])
        margin = Point(10, 10)
        bit_width = (self.pattern_canvas.get_width() - margin.x) / (pattern_width)
        bit_height = (self.pattern_canvas.get_height() - margin.y) / (pattern_height)
        bit_width = min(bit_width, bit_height)
        bit_height = bit_width
        self.__print_pattern_body(pattern, margin, bit_width, bit_height)
        sec_coord_big, sec_coord_small, sec_coord_2 = 0, margin.y / 2, margin.y
        step, big_step = 5, 10
        for i in range(0, max(pattern_width, pattern_height) + 1, step):
            sec_coord = sec_coord_big if i % big_step == 0 else sec_coord_small
            if i < pattern_width:
                x_coord = margin.x + i * bit_width
                self.pattern_canvas.create_line(x_coord, sec_coord, x_coord, sec_coord_2)
            if i < pattern_height:
                y_coord = margin.x + i * bit_height
                self.pattern_canvas.create_line(sec_coord, y_coord, sec_coord_2, y_coord)

    def __print_pattern_body(
        self, pattern, position: Point, bit_width, bit_height
    ) -> None:
        pattern_height = len(pattern)
        pattern_width = len(pattern[0])
        self.pattern_canvas.clear()
        for row in range(pattern_height):
            for stitch in range(pattern_width):
                if (pattern[row][stitch]) == 1:
                    fill = "black"
                    border = "white"
                    # border=fill
                else:
                    fill = "white"
                    border = "black"
                    # border=fill
                row = pattern_height - row - 1
                # stitch = patternWidth - stitch - 1
                self.pattern_canvas.create_rectangle(
                    position.x + stitch * bit_width,
                    position.y + row * bit_height,
                    position.x + (stitch + 1) * bit_width,
                    position.y + (row + 1) * bit_height,
                    width=1,
                    fill=fill,
                    outline=border,
                )
        # pattern border
        self.pattern_canvas.create_rectangle(
            position.x,
            position.y,
            position.x + (pattern_width) * bit_width,
            position.y + (pattern_height) * bit_height,
            width=1,
            outline="black",
        )

    def __update_pattern_canvas_last_size(self) -> None:
        self.pattern_canvas.lastWidth = self.pattern_canvas.get_width()
        self.pattern_canvas.lastHeight = self.pattern_canvas.get_height()

    def __canvas_configured(self) -> None:
        if (
            self.pattern_canvas.lastWidth != self.pattern_canvas.get_width()
            or self.pattern_canvas.lastHeight != self.pattern_canvas.get_height()
        ):
            self.msg.display_messages = False
            self.__update_pattern_canvas_last_size()
            self.__display_pattern()
            self.msg.display_messages = True
        self.after(100, self.__canvas_configured)

    def insert_bitmap_button_clicked(self) -> None:
        sel = self.patternListBox.curselection()
        if len(sel) == 0:
            self.msg.show_error("Target pattern for insertion must be selected!")
            return
        index = int(sel[0])
        pattern = self.patterns[index]
        file_path = tkinter.filedialog.askopenfilename(
            filetypes=[("2-color Bitmap", "*.bmp")],
            title="Choose bitmap file to insert...",
        )
        if len(file_path) > 0:
            self.__insert_bitmap(file_path, pattern["number"])

    def export_bitmap_button_clicked(self) -> None:
        sel = self.patternListBox.curselection()
        if len(sel) == 0:
            self.msg.show_error("Target pattern for saving must be selected!")
            return
        index = int(sel[0])
        pattern = self.patterns[index]
        file_path = tkinter.filedialog.asksaveasfilename(
            filetypes=[("2-color Bitmap", "*.bmp")], title="Save as a bitmap file..."
        )
        if len(file_path) > 0:
            pattern_number = pattern["number"]
            self.msg.show_info(
                f"Saving pattern number {pattern_number} as bmp file {file_path}"
            )
            result = self.pattern_dumper.dump_pattern(
                [self.current_dat_file, str(pattern_number)]
            )
            pattern = result[0]
            pattern_height = len(pattern)
            pattern_width = len(pattern[0])
            img = Image.new("RGB", (pattern_width, pattern_height), None)
            for x in range(pattern_width):
                for y in range(pattern_height):
                    color = (
                        (0, 0, 0)
                        if pattern[pattern_height - y - 1][x] == 1
                        else (255, 255, 255)
                    )
                    img.putpixel((x, y), color)
            img = img.convert("1")
            img.save(file_path, "BMP")
            self.msg.show_info(
                f"Saved pattern number {pattern_number} as bmp file {file_path}"
            )

    def __insert_bitmap(self, bitmap_file, pattern_number):
        self.msg.show_info(
            f"Inserting dat file {bitmap_file} to pattern number {pattern_number}"
        )
        old_brother_file = self.current_dat_file
        self.pattern_inserter.insert_pattern(
            old_brother_file, pattern_number, bitmap_file, old_brother_file
        )
        self.reload_pattern_file()


class PDDListener(PDDEmulatorListener): # pylint: disable=too-few-public-methods

    def __init__(self, inner_app: KnittingApp) -> None:
        self.app = inner_app

    def data_received(self, full_file_path) -> None:
        self.app.reload_pattern_file(full_file_path)


if __name__ == "__main__":
    app = KnittingApp()
    app.mainloop()
