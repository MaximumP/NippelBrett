import argparse
import logging
import os
import signal
import sys
from threading import Thread, Event

import glob
import pulsectl
import vlc
from cysystemd.journal import JournaldLogHandler
from gpiozero import Button

logger = logging.getLogger("copy_files")
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description="Detects button presses and play sound files")
parser.add_argument("-d", "--sound-files-dir", type=str, required=False, default="~/Music/NippelBrett")
parser.add_argument("-f", "--filter", type=str, required=False, default="*.wav")
args = parser.parse_args()


BUTTONS = [3, 17, 22, 9, 5, 13, 2, 4, 27, 10, 11, 6]
FILE_DIR = args.sound_files_dir
FILTER = args.filter
pulse = pulsectl.Pulse("NippelBoard")
thread: None | Thread = None
stop_event = Event()


def signal_handler(sig, frame):
    logger.debug(f"Got signal: {sig}, frame: {frame}. Set stop event for thread")
    stop_event.set()
    sys.exit(0)


def press_detected(input_device: Button):
    logger.debug(f"Detected button press for button at {input_device.pin.number}")
    global thread, stop_event
    if thread and thread.is_alive():
        logger.debug("Thread is still alive. Set stop event and wait for it to die")
        stop_event.set()
        stop_event.wait()
        logger.debug("Thread died")

    stop_event.clear()
    logger.debug("Start new Thread")
    thread = Thread(target=play_with_vlc, args=(input_device.pin.number, stop_event), daemon=True)
    thread.start()


def play_with_vlc(pin_number, stop: Event):
    files = glob.glob(FILTER, root_dir=FILE_DIR)
    files.sort()
    logger.debug(f"Read files from {FILE_DIR}: {files}")
    try:
        index = BUTTONS.index(pin_number)
        logger.debug(f"Playing file: {files[index]} at index: {index}")
        player = vlc.MediaPlayer(os.path.join(FILE_DIR, files[index]))
        player.play()
        stop.wait(.2)
        logger.debug(f"Is set: {stop.is_set()}, is playing: {player.is_playing()}")
        while not stop.is_set() and player.is_playing():
            stop.wait(.5)
        player.stop()
    except IndexError:
        logger.info(f"No file for button: {pin_number}")
        return


inputs = []
for button_pin in BUTTONS:
    button = Button(button_pin, bounce_time=200)
    button.when_pressed = press_detected
    inputs.append(button)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
