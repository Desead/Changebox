import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Changebox.settings')

app = Celery('Changebox')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# todo получение данных с ЦБ можно настроить раз в час, но тогда ещё надо сделать разовую задачу на получение этих данных
#  при запуске т.к. иначе придёться ждать пока пройдёт час чтобы обновились данные

app.conf.beat_schedule = {
    # 'get-best-files': {  # получаем данные с беста
    #     'task': 'app_main.tasks.best_download',
    #     'schedule': crontab(),  # раз в минуту
    #     # 'schedule': 30.0,  # каждые 30 секунд
    # },
    # 'get-cbr_rates': {  # получаем данные с ЦБ
    #     'task': 'app_main.tasks.cbr_rates',
    #     'schedule': crontab(),  # раз в минуту
    # },
    # 'get-binance_rates': {  # получаем данные с binance
    #     'task': 'app_main.tasks.binance_rates',
    #     'schedule': crontab(),  # раз в минуту
    # },
    'get-rates': {  # получаем данные и меняем котировки
        'task': 'app_main.tasks.set_ratese',
        'schedule': crontab(),  # раз в минуту
    },
    'clear_redis': {  # чистим список заданий от celery в redis
        'task': 'app_main.tasks.clear_redis',
        'schedule': crontab(minute=0, hour=6, day_of_week=1)  # выполняем раз в неделю в 6 утра по TIME_ZONE
    },
}
