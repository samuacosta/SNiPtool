# Generated by Django 3.0.6 on 2020-10-22 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20201021_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mutation',
            name='unified_score',
            field=models.IntegerField(null=True),
        ),
    ]
