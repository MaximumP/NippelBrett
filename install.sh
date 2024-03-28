#!/usr/bin/bash
sudo apt install build-essential libsystemd-dev vlc git curl gcc python3-dev pulseaudio pulseaudio-utils -y

if [ ! -f ./mo ]; then
  echo "Installing mustache template engine"
  curl -sSL https://raw.githubusercontent.com/tests-always-included/mo/master/mo -o mo
  chmod +x mo
fi

echo "Compile mustache templates to /etc/systemd/service directory"
./mo ./systemd/copy-from-usb.service.mo | sudo tee /etc/systemd/system/copy-from-usb.service > /dev/null
./mo ./systemd/nippel-brett.service.mo > ~/.config/systemd/user/nippel-brett.service
./mo ./systemd/nippel-brett-display.service.mo | sudo tee /etc/systemd/system/nippel-brett-display.service > /dev/null
sudo cp ./systemd/nippel-brett-display.socket /etc/systemd/system/


echo "Reload systemd daemon"
sudo systemctl daemon-reload
sudo systemctl enable copy-from-usb
systemctl --user enable nippel-brett
sudo systemctl enable nippel-brett-display.socket

echo "Restart services"
sudo systemctl restart copy-from-usb
systemctl --user restart nippel-brett
sudo systemctl restart nippel-brett-display.service
