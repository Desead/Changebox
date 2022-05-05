import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Changebox.settings')
app = Celery('Changebox')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
