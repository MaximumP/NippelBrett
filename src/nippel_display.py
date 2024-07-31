import logging
import os
import signal
import socket
import sys
from threading import Thread
from time import sleep

from cysystemd.journal import JournaldLogHandler

from external import I2C_LCD_driver

logger = logging.getLogger("nippel_brett_display")
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.DEBUG)
display = I2C_LCD_driver.lcd()
socket_name = "/tmp/nippel-display.socket"
os.umask(644)

if os.path.exists(socket_name):
    os.remove(socket_name)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


def display_default():
    display.lcd_clear()
    display.lcd_display_string_pos("Nippel Brett", 1, 2)
    display.lcd_display_string("Nature One 2024", 2)


def run_listener():
    server.bind(socket_name)
    server.listen()
    connection, address = server.accept()
    while True:
        server.listen(1)
        data = connection.recv(1024)

        if data:
            logger.info(f"Received Data {data}")
            display.lcd_clear()
            received_text = data.decode("utf-8")
            received_text = received_text.replace("-", " ")
            received_text = received_text.replace("_", " ")
            line1 = received_text[:16].strip()
            line2 = received_text[16:32].strip()
            if line1 == "done":
                display_default()
            else:
                display.lcd_display_string(line1, 1)
                display.lcd_display_string(line2, 2)


display_default()
thread = Thread(target=run_listener())
thread.start()


def signal_handler(sig, frame):
    logger.debug(f"Got signal: {sig}, frame: {frame}. Set stop event for thread")
    server.close()
    os.remove(socket_name)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.pause()
