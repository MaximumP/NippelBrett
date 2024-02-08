#!/usr/bin/bash
sudo apt install build-essential libsystemd-dev vlc -y
# todo get the working directory into the .service file
cp ./copy-from-usb.service ~/.config/systemd/user
cp ./nippel-brett ~/.config/systemd/user
systemctl --user daemon-reload
systemctl --user enable copy-from-usb
systemctl --user enable nippel-brett

systemctl --user start copy-from-usb
systemctl --user start nippel-brett
