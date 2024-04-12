# Generated by Django 4.2.8 on 2024-04-10 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0039_alter_filedresponses_submission_ref'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsFieldsSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('field', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.field')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder')),
            ],
        ),
    ]
