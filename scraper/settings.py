CELERY_BROKER_URL = 'redis://:zaq1@WSX@redis:6379/0'
CELERY_BEAT_SCHEDULE = {
    'run-scraper-every-2-hours': {
        'task': 'scraper.tasks.run_periodic_scraper',
        'schedule': 7200.0,
    },
}
CELERY_TIMEZONE = 'Europe/Warsaw'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'web.modules.tenders',
    'web.modules.users',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scrapper',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'db',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}