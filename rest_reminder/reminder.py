import logging
import os
import subprocess
import sys
import time
import threading
try:
    import queue
except ImportError:
    import Queue as queue
from pynput import mouse


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="[%(levelname)s]%(asctime)s %(name)s:%(message)s")
logger = logging.getLogger(__name__)


class Reminder(object):

    def __init__(self, interval=None):
        self._interval = interval or 20 * 60  # default 20m

    def _start_driver(self, mouse_queue):
        driver = Driver(mouse_queue, interval=self._interval)
        t = threading.Thread(target=driver.start)
        t.start()
        return driver

    def _start_mouse_listener(self, q):  # type: q -> queue.Queue
        def on_mouse_move(x, y):
            try:
                q.put_nowait(1)

            except queue.Full:
                pass

        # listener as daemon Thread
        listener = mouse.Listener(on_move=on_mouse_move)
        listener.start()
        return listener

    def start(self):
        mouse_q = queue.Queue(1)
        listener = self._start_mouse_listener(mouse_q)  # daemon Thread
        driver = self._start_driver(mouse_q)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.debug("KeyboardInterrupt captured")
            listener.stop()
            driver.stop()


class Driver(object):

    def __init__(self, mouse_queue, interval):
        self._mouse_q = mouse_queue  # type: queue.Queue
        self._interval = interval  # type: int # in seconds
        self._first_move_time = None
        self._stop_event = threading.Event()

    def _wait(self, seconds):
        self._stop_event.wait(seconds)
        if self._stop_event.is_set():
            raise Exception("Stop Error")

    def _wait_mouse_move(self):
        try:
            self._mouse_q.get_nowait()  # to empty queue
        except queue.Empty:
            pass
        self._mouse_q.get()

    def start(self):
        logger.debug("Driver: interval " + str(self._interval))
        while True:
            if not self._first_move_time:
                logger.debug("Driver: waiting mouse move...")
                while not self._stop_event.is_set():
                    try:
                        self._mouse_q.get(timeout=1)
                        break
                    except queue.Empty:
                        continue
                else:
                    break
                logger.debug("Driver: mouse move")
                self._first_move_time = time.time()

            if time.time() - self._first_move_time >= self._interval:
                logger.debug("Driver: show ReminderBox")
                ReminderBox("20-20-20").show(block=False)

                # 10s for user to click Ok
                self._wait_mouse_move()
                logger.debug("Driver: count down 10s")
                self._wait(10)
                logger.debug("Driver: 10s drain")

                try:
                    self._mouse_q.get_nowait()  # to empty queue
                except queue.Empty:
                    pass
                self._first_move_time = None

                continue

            self._wait(1)

    def stop(self):
        self._stop_event.set()


class ReminderBox(object):

    def __init__(self, msg):
        self._msg = msg

    def show(self, block=True):
        """show the ReminderBox with msg, block"""
        # shell: "osascript -e 'tell app "System Events" to display dialog
        # "Hello World"'"
        args = [
            "osascript",
            "-e",
            "tell app \"System Events\" to display dialog \"{}\"".format(
                self._msg),
        ]
        try:
            devnull = getattr(subprocess, "DEVNULL")
        except AttributeError:
            with open(os.devnull, "w") as devnull:
                p = subprocess.Popen(args, stdout=devnull,
                                     stderr=subprocess.STDOUT)
        else:
            p = subprocess.Popen(args, stdout=devnull,
                                 stderr=subprocess.STDOUT)

        if block:
            p.wait()

        return

if __name__ == "__main__":
    reminder = Reminder(6)
    # reminder._show_reminder("a")
    reminder.start()
