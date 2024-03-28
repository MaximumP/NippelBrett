import argparse
import logging
import os
import signal
import sys
from threading import Thread, Event
import pigpio
import glob
import pulsectl
from vlc import MediaPlayer
from cysystemd.journal import JournaldLogHandler

logger = logging.getLogger("nippel_brett")
logger.addHandler(JournaldLogHandler())
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description="Detects button presses and play sound files")
parser.add_argument("-d", "--sound-files-dir", type=str, required=False, default="/home/nippelbrett/Music/NippelBrett")
parser.add_argument("-f", "--filter", type=str, required=False, default="*.wav")
args = parser.parse_args()


BUTTONS = [26, 17, 22, 9, 5, 13, 19, 4, 27, 10, 11, 6]
FILE_DIR = args.sound_files_dir
FILTER = args.filter
pulse = pulsectl.Pulse("NippelBoard")


class NippelBrett:
    thread: Thread | None = None
    player: MediaPlayer | None = None

    def __init__(self):
        self.stop_event = Event()

    def __del__(self):
        self.stop_event.set()

    def button_pressed(self, pin, level, tick):
        logger.debug(f"Detected button press for button at {pin}, level {level}, tick {tick}")
        if self.thread and self.thread.is_alive():
            logger.debug("Thread is still alive. Set stop event and wait for it to die")
            self.stop_event.set()
            self.stop_event.wait()
            logger.debug("Thread died")

        self.stop_event.clear()
        logger.debug("Start new Thread")
        play_sound = self.play_sound
        self.thread = Thread(target=play_sound, args=(pin, ), daemon=True)
        self.thread.start()

    def play_sound(self, pin: int):
        files = glob.glob(FILTER, root_dir=FILE_DIR)
        files.sort()
        logger.debug(f"Read files from {FILE_DIR}: {files}")
        try:
            index = BUTTONS.index(pin)
            logger.debug(f"Playing file: {files[index]} at index: {index}")
            if self.player is not None:
                self.player.stop()
            self.player = MediaPlayer(os.path.join(FILE_DIR, files[index]))

            self.player.play()
            self.stop_event.wait(.2)
            logger.debug(f"Is set: {self.stop_event.is_set()}, is playing: {self.player.is_playing()}")
            while not self.stop_event.is_set() and (self.player is not None and self.player.is_playing()):
                self.stop_event.wait(.5)
            self.player.stop()
            self.player = None
        except IndexError:
            logger.info(f"No file for button: {pin}")
            return


pi = pigpio.pi()


def signal_handler(sig, frame):
    logger.debug(f"Got signal: {sig}, frame: {frame}. Set stop event for thread")
    pi.stop()
    sys.exit(0)


nippel_brett = NippelBrett()
button_pressed_ref = nippel_brett.button_pressed
for button in BUTTONS:
    logger.info(f"add event detect to pin: {button}")
    pi.set_pull_up_down(button, pigpio.PUD_UP)
    pi.set_mode(button, pigpio.INPUT)
    pi.set_glitch_filter(button, 100)
    pi.callback(button, pigpio.RISING_EDGE, button_pressed_ref)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
