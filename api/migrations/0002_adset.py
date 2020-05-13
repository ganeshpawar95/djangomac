# Generated by Django 3.0.5 on 2020-05-13 16:07

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adset',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('targeting', jsonfield.fields.JSONField(default=dict, max_length=200)),
            ],
        ),
    ]
