#!/bin/bash

# Create initial empty code file if it doesn’t exist
if [ ! -f /app/code.py ]; then
    echo 'print("Initial empty code")' > /app/code.py
fi

# Loop to check and run code
while true; do
    # Check if code.py has changed (using a basic checksum or timestamp)
    if [ -f /app/last_run ] && [ /app/code.py -nt /app/last_run ]; then
        echo "Code updated, running..."
        python /app/code.py
        touch /app/last_run
    elif [ ! -f /app/last_run ]; then
        echo "Running initial code..."
        python /app/code.py
        touch /app/last_run
    fi
    sleep 1  # Check every second
done