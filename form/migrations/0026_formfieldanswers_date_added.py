# Generated by Django 4.2.8 on 2024-03-31 01:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0025_formfieldanswers_submission_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfieldanswers',
            name='date_added',
            field=models.DateTimeField(
                auto_now_add=True, default=datetime.datetime(2024, 3, 31, 1, 28, 23, 133859)),
            preserve_default=False,
        ),
    ]
