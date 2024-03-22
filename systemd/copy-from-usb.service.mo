[Unit]
Description=Listen to udev block change events and copies files from the block device to the internal file system
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory={{HOME}}/NippelBrett/
TimeoutStartSec=900
ExecStartPre={{HOME}}/NippelBrett/install-requirements.sh
ExecStart={{HOME}}/NippelBrett/venv/bin/python3 src/copy_from_usb.py

[Install]
WantedBy=multi-user.target
