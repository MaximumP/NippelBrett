import RPi.GPIO as GPIO
import signal
import sys


GPIO.setmode(GPIO.BCM)
BUTTONS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


def signal_handler(sig, frame):
    #audio.terminate()
    GPIO.cleanup()
    sys.exit(0)


def button_pressed_callback(channel):
    print(f"Hallo {channel}")


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    for button in BUTTONS:
        GPIO.add_event_detect(button, GPIO.FALLING, callback=button_pressed_callback, bouncetime=100)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
