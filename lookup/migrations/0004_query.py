# Generated by Django 2.0.1 on 2018-01-20 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0003_hit_valid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=200)),
                ('nrecords', models.IntegerField(default=0)),
            ],
        ),
    ]
