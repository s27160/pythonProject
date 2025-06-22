from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scraper.settings')

app = Celery('scraper')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['scraper'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
