# Generated by Django 2.0.3 on 2018-03-23 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_sessionhas_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessionhas',
            old_name='owner',
            new_name='is_owner',
        ),
    ]