"""
keep_alive.py - يبقي المشروع مستيقظاً على Glitch
استخدم UptimeRobot لإرسال طلب كل 5 دقائق
"""
from threading import Thread
import requests
import time
import os

def ping_self():
    """يرسل طلب لنفسه كل 4 دقائق"""
    url = os.environ.get('WEBSITE_URL', '')
    if not url:
        return
    while True:
        try:
            requests.get(url, timeout=10)
        except:
            pass
        time.sleep(240)

def keep_alive():
    t = Thread(target=ping_self)
    t.daemon = True
    t.start()
