# run.py

from app import create_app, db
from app.models import User, Category, Task, Reminder
from scheduler import scheduler

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Category': Category, 'Task': Task, 'Reminder': Reminder}

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
    scheduler.start()