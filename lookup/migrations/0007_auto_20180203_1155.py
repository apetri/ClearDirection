# Generated by Django 2.0.1 on 2018-02-03 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0006_auto_20180203_1152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='city',
        ),
        migrations.AddField(
            model_name='person',
            name='age',
            field=models.IntegerField(default=0),
        ),
    ]