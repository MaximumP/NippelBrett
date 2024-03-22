[Unit]
Description=Detects gpio inputs and plays sound files from the users ~/Music/NippelBrett/ directory

[Service]
Type=simple
Restart=always
WorkingDirectory={{HOME}}/NippelBrett
TimeoutStartSec=900
ExecStartPre={{HOME}}/NippelBrett/install-requirements.sh
ExecStart={{HOME}}/NippelBrett/venv/bin/python3 src/nippel_brett.py

[Install]
WantedBy=default.target
