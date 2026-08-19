#!/usr/bin/env bash
echo "==================================================="
echo "          Starting SmartCode AI Server             "
echo "==================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "Installing/Verifying Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting FastAPI Web Server at http://localhost:8000"
echo "Press Ctrl+C to stop the server."
echo ""

if which xdg-open > /dev/null; then
  xdg-open "http://localhost:8000" &
elif which open > /dev/null; then
  open "http://localhost:8000" &
fi

python main.py
