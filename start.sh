#!/bin/bash
mkdir -p /tmp/output
pip3 install -r requirements.txt --quiet
python bot/bot.py &
gunicorn src.main:app --bind 0.0.0.0:${PORT:-3000} --workers 1 --timeout 120
