# Generated by Django 4.2.8 on 2024-03-05 20:48

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0014_field_is_disabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormFieldAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('array_answer', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), blank=True, size=20), blank=True, size=20)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.field')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.sections')),
            ],
        ),
    ]