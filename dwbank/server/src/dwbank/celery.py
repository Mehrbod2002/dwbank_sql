import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dwbank.settings')
celery_app = Celery('dwbank')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()