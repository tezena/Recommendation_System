from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from data_loader import data_loader

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(data_loader.load_data, 'interval', minutes=5)
    scheduler.start()