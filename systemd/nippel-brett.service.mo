[Unit]
Description=Detects gpio inputs and plays sound files from the users ~/Music/NippelBrett/ directory
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory={{HOME}}/NippelBrett
User={{USER}}
TimeoutStartSec=900
ExecStartPre={{HOME}}/NippelBrett/install-requirements.sh
ExecStart={{HOME}}/NippelBrett/venv/bin/python3 src/nippel_brett.py

[Install]
WantedBy=default.target
