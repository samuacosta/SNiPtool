# Generated by Django 3.0.6 on 2020-10-22 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20201022_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='mutation',
            name='consequence_terms',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
