from Changebox.redis import REDIS_HOST, REDIS_PORT
from celery.schedules import crontab

from Changebox.settings import TIME_ZONE

CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ALWAYS_EAGER = True
CELERY_IGNORE_RESULT = True

CELERY_BEAT_SCHEDULE = {
    'get-rates': {  # получаем данные и меняем котировки
        'task': 'app_main.tasks.set_rates',
        'schedule': crontab(),  # раз в минуту
        # 'schedule': 30.0,  # каждые 30 секунд
    },
    'clear_redis': {  # чистим список заданий от celery в redis
        'task': 'app_main.tasks.clear_redis',
        'schedule': crontab(minute=0, hour=6, day_of_week=1)  # выполняем раз в неделю в 6 утра по TIME_ZONE
    },
}
