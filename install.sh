#!/usr/bin/bash
sudo apt install build-essential libsystemd-dev vlc git curl -y

#curl -sSL https://raw.githubusercontent.com/tests-always-included/mo/master/mo -o mo
#chmod +x mo
#mkdir ~/.local/bin
#mv mo ~/.local/bin
#
#mo

# todo get the working directory into the .service file
sudo cp ./systemd/copy-from-usb.service /etc/systemd/system/
sudo cp ./systemd/nippel-brett.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable copy-from-usb
sudo systemctl enable nippel-brett

sudo systemctl start copy-from-usb
sudo systemctl start nippel-brett
I2C_LCD_driver
