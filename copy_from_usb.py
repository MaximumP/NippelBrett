import argparse
import glob
import logging
import os
import shutil
import signal

import psutil
import pyudev
from pyudev import MonitorObserver, Device
from cysystemd.journal import JournaldLogHandler


logger = logging.getLogger("copy_files")
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description="Copies files from an usb block device to a target directory")
parser.add_argument("-t", "--target-dir", type=str, required=False, default="~/Music/NippelBrett")
parser.add_argument("-s", "--source-dir", type=str, required=False, default="NippelBrett")
parser.add_argument("-f", "--filter", type=str, required=False, default="*.wav")


args = parser.parse_args()
TARGET_DIRECTORY = args.target_dir
SOURCE_DIRECTORY = args.source_dir
FILTER = args.filter


def get_mount_point(device: Device) -> str:
    partitions = psutil.disk_partitions(False)
    device_name = device.device_path.rsplit("/", 1)[-1]
    for p in partitions:
        if p.device.rsplit("/", 1)[-1] == device_name:
            return p.mountpoint

    raise RuntimeError("Could not find partition of device")


def delete_files():
    for file in os.listdir(TARGET_DIRECTORY):
        file_path = os.path.join(TARGET_DIRECTORY, file)
        logger.debug(f"Delete file: {file_path}")
        if os.path.isfile(file_path):
            os.remove(file_path)


def copy_files(files: list, directory: str):
    for file in files:
        file_path = os.path.join(directory, file)
        logger.debug(f"Copy file: {file_path}")
        shutil.copy(file_path, os.path.join(TARGET_DIRECTORY, file))


def on_udev_action(action, device: Device):
    logger.debug("Detected udev action")
    if action == "change":
        logger.debug("Detected udev change action")
        mount_point = get_mount_point(device)
        source_directory = f"{mount_point}/{SOURCE_DIRECTORY}"
        new_files = glob.glob(FILTER, root_dir=source_directory)
        if len(new_files):
            delete_files()
            copy_files(new_files, source_directory)


def signal_handler(sig, frame):
    logger.debug("stopping observer")
    if observer:
        observer.stop()
    logger.debug("observer stopped")
    exit(0)


def create_dir():
    if os.path.isfile(TARGET_DIRECTORY):
        os.remove(TARGET_DIRECTORY)
    if not os.path.isdir(TARGET_DIRECTORY):
        os.mkdir(TARGET_DIRECTORY)


create_dir()
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='block')
observer = MonitorObserver(monitor, on_udev_action)
observer.start()
logger.info("Start observer")
signal.signal(signal.SIGINT, signal_handler)
signal.pause()
