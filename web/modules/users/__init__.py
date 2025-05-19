from django.apps import AppConfig

class UsersAppConfig(AppConfig):
    name = 'web.modules.users'
    label = 'users'
    verbose_name = 'Users'

default_app_config = 'web.modules.users.UsersAppConfig'