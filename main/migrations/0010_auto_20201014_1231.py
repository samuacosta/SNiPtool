# Generated by Django 3.0.6 on 2020-10-14 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20201007_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mutationbatch',
            name='date_time',
            field=models.DateTimeField(),
        ),
    ]
