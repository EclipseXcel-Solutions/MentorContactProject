# Generated by Django 4.2.8 on 2024-02-28 20:58

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormBuilder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Sections',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('position', models.IntegerField()),
                ('message', models.TextField()),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder')),
            ],
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('message', models.TextField()),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder')),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_type', models.CharField(choices=[('text', 'text'), ('select', 'select'), ('email', 'email'), ('checkbox', 'checkbox'), ('textarea', 'textarea'), ('date', 'date'), ('datetime', 'datetime'), ('time', 'time')])),
                ('is_multiple_choice', models.BooleanField(default=False)),
                ('choices', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), size=20), size=20)),
                ('row', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.row')),
            ],
        ),
    ]
