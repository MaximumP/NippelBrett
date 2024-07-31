import argparse
import glob
import logging
import os
import re
import shutil
import signal

import pyudev
from pyudev import MonitorObserver, Device
from cysystemd.journal import JournaldLogHandler


logger = logging.getLogger("copy_files")
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description="Copies files from an usb block device to a target directory")
parser.add_argument("-t", "--target-dir", type=str, required=False, default="/home/nippelbrett/Music/NippelBrett")
parser.add_argument("-s", "--source-dir", type=str, required=False, default="NippelBrett")
parser.add_argument("-f", "--filter", type=str, required=False, default="*")


args = parser.parse_args()
TARGET_DIRECTORY = args.target_dir
SOURCE_DIRECTORY = args.source_dir
FILTER = args.filter


def get_mount_point(device: Device) -> str|None:
    device_name = device.device_path.rsplit("/", 1)[-1]
    if re.search(r'\d$', device_name):
        mount_point = f"/mnt/{device_name}"
        if os.path.isdir(mount_point):
            os.rmdir(f"/mnt/{device_name}")
        os.mkdir(mount_point)
        os.system(f"mount /dev/{device_name} {mount_point}")
        logger.debug(f"Mounted usb stick to {mount_point}")
        return mount_point
    else:
        return None


def delete_files():
    for file in os.listdir(TARGET_DIRECTORY):
        file_path = os.path.join(TARGET_DIRECTORY, file)
        logger.info(f"Delete file: {file_path}")
        if os.path.isfile(file_path):
            os.remove(file_path)


def on_udev_action(action, device: Device):
    logger.info(f"Detected udev action: {action}")
    logger.debug(f"{device.device_path}")
    if action == "add":
        logger.info("Detected udev action")
        mount_point = get_mount_point(device)
        if mount_point is None:
            return
        source_directory = f"{mount_point}/{SOURCE_DIRECTORY}"
        logger.info(f"Read files from {source_directory}")
        new_files = glob.glob(FILTER, root_dir=source_directory)
        logger.info(f"Copy ")
        if len(new_files):
            shutil.rmtree(TARGET_DIRECTORY, ignore_errors=True)
            shutil.copytree(source_directory, TARGET_DIRECTORY)


def signal_handler(sig, frame):
    logger.info("stopping observer")
    if observer:
        observer.stop()
    logger.info("observer stopped")
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
