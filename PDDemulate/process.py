from multiprocessing import Process, Queue
from queue import Empty
from typing import Callable

from PDDemulate.Drive import PDDemulator
from PDDemulate.Listener import PDDEmulatorListener
import weakref


def run_disk(port: Queue, responses: Queue, imgdir: str) -> None:
    emu = PDDemulator(imgdir)
    emu.listeners.append(DiskProcessListener(responses))
    device = None
    changed = False
    while True:
        try:
            newPort = port.get(block=False)
            if newPort != None:
                device = newPort
            changed = True
        except Empty:
            pass
        if changed:
            if emu.isOpen():
                emu.close()
            emu.open(device)
        if device != None:
            emu.handleRequest(blocking=True)
        else:
            emu.close()


class DiskProcessListener(PDDEmulatorListener):
    queue: Queue

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def dataReceived(self, fullFilePath: str):
        self.queue.put(fullFilePath)


class DiskProcess:
    process: Process
    portQueue: Queue
    responses: Queue
    callback: Callable[[str], None]
    running: False

    def __init__(self, imgdir: str, callback: Callable[[str], None]) -> None:
        self.portQueue = Queue(10)
        self.responses = Queue(10)
        self.process = Process(target=run_disk, args=[self.portQueue, self.responses, imgdir])
        self.callback = callback
        self.running = False
        self._finalizer = weakref.finalize(self, self.__exit, self.process, self.portQueue, self.responses)

    def exit(self) -> None:
        self._finalizer()

    def __exit(self, process: Process, inQueue: Queue, outQueue: Queue) -> None:
        print("exit")
        inQueue.close()
        outQueue.close()
        if process.is_alive():
            process.terminate()
        process.close()

    def start(self, port: str) -> None:
        self.running = True
        self.portQueue.put(port)
        if not self.process.is_alive():
            self.process.start()

    def stop(self) -> None:
        if self.running:
            self.running = False
            if self.process.is_alive():
                self.portQueue.put(None)

    def queueCheck(self) -> None:
        while True:
            try:
                message = self.responses.get(block=False)
                self.callback(message)
            except Empty:
                return
