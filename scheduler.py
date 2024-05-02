from datetime import datetime
from app import create_app, db
from app.models import Reminder
from app.utils import send_reminders
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app()
scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=1)
def send_reminders_job():
    send_reminders(app)

if __name__ == '__main__':
    scheduler.start()
    try:
        scheduler._thread.join()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()