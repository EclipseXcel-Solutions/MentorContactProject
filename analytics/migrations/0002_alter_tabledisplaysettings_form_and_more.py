# Generated by Django 4.2.8 on 2024-09-03 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0006_remove_field_is_disabled'),
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tabledisplaysettings',
            name='form',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder'),
        ),
        migrations.AlterField(
            model_name='tablefiltersettings',
            name='form',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder'),
        ),
    ]