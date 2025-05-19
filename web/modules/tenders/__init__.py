from django.apps import AppConfig

class TendersAppConfig(AppConfig):
    name = 'web.modules.tenders'
    label = 'tenders'
    verbose_name = 'Tenders'

default_app_config = 'web.modules.tenders.TendersAppConfig'