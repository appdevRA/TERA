# Generated by Django 3.2.8 on 2021-12-15 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ra', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='added_by',
        ),
        migrations.RemoveField(
            model_name='site',
            name='date_added',
        ),
    ]
