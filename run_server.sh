#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE}" )" &> /dev/null && pwd )"

# Define the absolute path to the python executable in your virtual environment
#!!! REPLACE THIS WITH YOUR ACTUAL PATH FROM THE PREVIOUS STEP!!!
PYTHON_EXEC="$SCRIPT_DIR/.venv/bin/python"

# Define the log file path
LOG_FILE="$SCRIPT_DIR/cbr_server.log"

# Run the uvicorn server, redirecting all output (stdout and stderr) to the log file
"$PYTHON_EXEC" -m uvicorn server:app --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1