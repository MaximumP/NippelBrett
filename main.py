import signal
import sys
from threading import Thread

import RPi.GPIO as GPIO
import pygame
from pyaudio import PyAudio, paContinue
import wave
import glob
import pulsectl
import time

BUTTONS = [2, 3, 4, 5, 6, 7, 8, 9]
file_dir = "/home/max/Music/NippelBoard/"
sound_files = glob.glob('*.wav', root_dir=file_dir)
audio = PyAudio()
stream = None
wav_file = None
print(sound_files)
pulse = pulsectl.Pulse("NippelBoard")

def signal_handler(sig, frame):
    audio.terminate()
    GPIO.cleanup()
    sys.exit(0)

def stream_callback(in_data, frame_count, time_info, status):
    if not wav_file:
        return ([], paContinue)
    data = wav_file.readframes(frame_count)
    return (data, paContinue)


def press_detected(pin):
    print("press detected on pin %s" % pin)
    Thread(target=play_sound, args=(pin,)).start()


def play_sound(channel):
    global stream, wav_file
    if stream or wav_file:
        if stream:
            stream.close()
            print(f"Closed stream now it is: {stream}")
        if wav_file:
            wav_file.close()
        stream = None
        wav_file = None
        return

    file_path = sound_files[BUTTONS.index(channel)]
    wav_file = wave.open(file_dir + file_path, "rb")
    to_mute = pulse.source_list()[-1]
    print("mute bluetooth")
    pulse.mute(to_mute, True)
    stream = audio.open(format=audio.get_format_from_width(wav_file.getsampwidth()), channels=wav_file.getnchannels(), rate=wav_file.getframerate(), output=True, stream_callback=stream_callback)
    print(f"Button {channel} pressed!")
    while stream.is_active():
        time.sleep(.2)
    stream.close()
    stream = None
    wav_file.close()
    wav_file = None
    print("unmute")
    pulse.mute(to_mute, False)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    for button in BUTTONS:
        GPIO.add_event_detect(button, GPIO.RISING, callback=press_detected, bouncetime=500)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()