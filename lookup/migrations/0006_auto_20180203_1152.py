# Generated by Django 2.0.1 on 2018-02-03 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0005_query_qdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='age',
        ),
        migrations.RemoveField(
            model_name='person',
            name='street_address',
        ),
        migrations.RemoveField(
            model_name='person',
            name='zipcode',
        ),
    ]
