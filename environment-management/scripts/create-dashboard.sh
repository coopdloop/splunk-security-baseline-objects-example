#!/bin/bash
# Wrapper script for the Python dashboard generator
# Usage: ./create-dashboard.sh [template_name] [--environment=env] [--output-dir=path]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/create-dashboard.py"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: Dashboard generator script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Run the Python script with all arguments
python3 "$PYTHON_SCRIPT" "$@"