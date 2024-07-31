[Unit]
Description=Service to display Nippel Brett related data on a LCD

[Service]
Type=notify
WorkingDirectory={{HOME}}/NippelBrett
TimeoutStartSec=900
ExecStartPre={{HOME}}/NippelBrett/install-requirements.sh
ExecStart={{HOME}}/NippelBrett/venv/bin/python3 src/nippel_display.py

[Install]
WantedBy=multi-user.target
