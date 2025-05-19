CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_BEAT_SCHEDULE = {
    'run-scraper-every-5-minutes': {
        'task': 'scraper.tasks.run_periodic_scraper',
        'schedule': 300.0,
    },
}
CELERY_TIMEZONE = 'Europe/Warsaw'