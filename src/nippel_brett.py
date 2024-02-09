import argparse
import logging
import os
import signal
import sys
from threading import Thread, Event
import RPi.GPIO as GPIO
import glob
import pulsectl
from vlc import MediaPlayer
from cysystemd.journal import JournaldLogHandler

logger = logging.getLogger("copy_files")
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description="Detects button presses and play sound files")
parser.add_argument("-d", "--sound-files-dir", type=str, required=False, default="/home/nippelbrett/Music/NippelBrett")
parser.add_argument("-f", "--filter", type=str, required=False, default="*.wav")
args = parser.parse_args()


BUTTONS = [3, 17, 22, 9, 5, 13, 2, 4, 27, 10, 11, 6]
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

    def button_pressed(self, pin):
        logger.debug(f"Detected button press for button at {pin}")
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
                self.player = None
            self.player = MediaPlayer(os.path.join(FILE_DIR, files[index]))
            self.player.play()
            self.stop_event.wait(.2)
            logger.debug(f"Is set: {self.stop_event.is_set()}, is playing: {self.player.is_playing()}")
            while not self.stop_event.is_set() and self.player.is_playing():
                self.stop_event.wait(.5)
            self.player.stop()
        except IndexError:
            logger.info(f"No file for button: {pin}")
            return



def signal_handler(sig, frame):
    logger.debug(f"Got signal: {sig}, frame: {frame}. Set stop event for thread")
    GPIO.cleanup()
    sys.exit(0)


nippel_brett = NippelBrett()
button_pressed_ref = nippel_brett.button_pressed
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for button in BUTTONS:
    GPIO.add_event_detect(button, GPIO.RISING, callback=button_pressed_ref, bouncetime=500)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
