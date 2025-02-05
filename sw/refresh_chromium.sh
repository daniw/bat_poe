#!/bin/bash

# Wait for the system to fully load Chromium
sleep 60

# Set the DISPLAY environment variable
export DISPLAY=:0

# Find the Chromium window and send the refresh command
CHROMIUM_WINDOW=$(wmctrl -l | grep "Chromium" | awk '{print $1}')
if [ -n "$CHROMIUM_WINDOW" ]; then
    xdotool windowactivate $CHROMIUM_WINDOW key F5
else
    echo "Chromium window not found!"
fi

