# Generated by Django 4.2.8 on 2024-04-09 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0032_remove_formfieldanswers_submission_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfieldanswers',
            name='submission_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='form.formsubmission'),
            preserve_default=False,
        ),
    ]
