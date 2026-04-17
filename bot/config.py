services:
  - type: web
    name: seha-saa-injuries-slenquiry
    runtime: python
    rootDir: .
    buildCommand: pip install -r requirements.txt
    startCommand: python bot/bot.py & gunicorn src.main:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
