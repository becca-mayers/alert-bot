# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:31:57 2021

@author: beccamayers
"""
import schedule
from datetime import datetime
from alert_bot import get_alert
import time


now = datetime.now()
timestamp = now.strftime("%b%d%Y %H%M%p")

def job():
    print("Launching Alert Bot app...")
    get_alert()


schedule.every().hour.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)