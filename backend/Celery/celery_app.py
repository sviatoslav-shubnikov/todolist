from celery import Celery
import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

os.chdir(backend_path)
from celery.signals import worker_ready
from dotenv import load_dotenv
import django
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.ToDoListService.settings')

django.setup()


load_dotenv()

redis_password = os.getenv('REDIS_PASSWORD')
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)

redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
result_backend_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/2"  

app = Celery(
    'todo_list_tasks', 
    broker=redis_url,
    backend=result_backend_url,
    include=['Tasks.tasks']
    )

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True


app.conf.beat_schedule = {
    'check-overdue-tasks-every-1-min': {
        'task': 'Tasks.tasks.check_overdue_tasks',
        'schedule': crontab(minute='*/1'), 
    },
}