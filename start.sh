#!/bin/bash
mkdir -p /tmp/output
cd /app 2>/dev/null || true
python bot/bot.py &
gunicorn src.main:app --bind 0.0.0.0:${PORT:-5000} --workers 2
