from multiprocessing import Process, Queue
from queue import Empty
from typing import Callable
import weakref

from pddemulate.drive import PDDemulator
from pddemulate.listener import PDDEmulatorListener


def run_disk(port: Queue, responses: Queue, imgdir: str) -> None:
    emu = PDDemulator(imgdir)
    emu.listeners.append(DiskProcessListener(responses))
    device = None
    changed = False
    while True:
        try:
            new_port = port.get(block=False)
            if new_port != device:
                print(f"swapping port from {device} to {new_port}")
                changed = True
            else:
                changed = False
            if new_port is not None:
                device = new_port
        except Empty:
            changed = False
        if changed:
            if emu.isOpen():
                emu.close()
            emu.open(device)
        if device is not None:
            emu.handle_request()
        else:
            emu.close()


class DiskProcessListener(
    PDDEmulatorListener
):  # pylint: disable=too-few-public-methods
    queue: Queue

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def data_received(self, full_file_path: str):
        self.queue.put(full_file_path)


class DiskProcess:
    process: Process
    port_queue: Queue
    responses: Queue
    callback: Callable[[str], None]
    running: False

    def __init__(self, imgdir: str, callback: Callable[[str], None]) -> None:
        self.port_queue = Queue(10)
        self.responses = Queue(10)
        self.process = Process(
            target=run_disk, args=[self.port_queue, self.responses, imgdir]
        )
        self.callback = callback
        self.running = False
        self._finalizer = weakref.finalize(
            self, self.__exit, self.process, self.port_queue, self.responses
        )

    def exit(self) -> None:
        self._finalizer()

    def __exit(self, process: Process, in_queue: Queue, out_queue: Queue) -> None:
        print("exit")
        in_queue.close()
        out_queue.close()
        if process.is_alive():
            process.terminate()
        process.close()

    def start(self, port: str) -> None:
        self.running = True
        self.port_queue.put(port)
        if not self.process.is_alive():
            self.process.start()

    def stop(self) -> None:
        if self.running:
            self.running = False
            if self.process.is_alive():
                self.port_queue.put(None)

    def queue_check(self) -> None:
        while True:
            try:
                message = self.responses.get(block=False)
                self.callback(message)
            except Empty:
                return
