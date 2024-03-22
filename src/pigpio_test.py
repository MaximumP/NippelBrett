import signal
import sys
import pigpio


def signal_handler(sig, frame):
    sys.exit(0)


pi = pigpio.pi()
pi.set_mode(5, pigpio.INPUT)
pi.set_pull_up_down(5, pigpio.PUD_UP)
pi.set_glitch_filter(5, 100)
pi.callback(5, pigpio.RISING_EDGE, lambda x, y, z: print(f"Pin: {x}, y: {y}, z: {z}"))

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
