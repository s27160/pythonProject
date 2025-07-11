# Generated by Django 5.2.3 on 2025-06-21 21:19

from django.db import migrations


def load_fixtures(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', 'admin_user.json')

def reverse_fixtures(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
        ('tenders', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixtures, reverse_fixtures),
    ]

