# Generated by Django 5.2.3 on 2025-06-21 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publictender',
            name='cpv_code',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Kod CPV'),
        ),
    ]
