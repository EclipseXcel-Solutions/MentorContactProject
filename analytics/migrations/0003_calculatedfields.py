# Generated by Django 4.2.8 on 2024-09-10 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0007_delete_calculatedfields'),
        ('analytics', '0002_alter_tabledisplaysettings_form_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculatedFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_one', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='greater_field', to='form.field')),
                ('field_two', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='smaller_field', to='form.field')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.formbuilder')),
            ],
        ),
    ]