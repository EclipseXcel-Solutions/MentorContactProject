# Generated by Django 4.2.8 on 2024-03-05 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0013_field_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='is_disabled',
            field=models.BooleanField(default=False),
        ),
    ]
