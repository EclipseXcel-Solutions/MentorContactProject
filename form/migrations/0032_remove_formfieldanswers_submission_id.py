# Generated by Django 4.2.8 on 2024-04-09 03:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0031_alter_formfieldanswers_submission_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formfieldanswers',
            name='submission_id',
        ),
    ]
