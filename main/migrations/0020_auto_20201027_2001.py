# Generated by Django 3.0.6 on 2020-10-27 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_mutation_consequence_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='mutation',
            name='biotype',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='mutation',
            name='cadd_phred',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='mutation',
            name='metalr_pred',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
