#!/bin/bash

LOGFILE="/home/pi/logfiles/nutriscan.txt"
APP_DIR="/home/pi/nutriscan"
VENV="$APP_DIR/venv/bin/activate"
PYTHON="$APP_DIR/venv/bin/python3"
APP="$APP_DIR/app.py"

mkdir -p "$(dirname "$LOGFILE")"

while true
do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starte nutriscan..." | tee -a "$LOGFILE"
    cd "$APP_DIR" || exit 1
    source "$VENV"
    # Hier kommt tee ins Spiel
    $PYTHON "$APP" 2>&1 | tee -a "$LOGFILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Prozess beendet. Neustart in 5 Sekunden..." | tee -a "$LOGFILE"
    sleep 5
done

