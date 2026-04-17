#!/bin/bash
python bot/bot.py &
gunicorn src.main:app
