from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FormBuilder
from analytics.models import TableDisplaySettings, TableFilterSettings


@receiver(post_save, sender=FormBuilder)
def create_settings(sender, instance, **kwargs):
    TableFilterSettings.objects.get_or_create(form=instance)
    TableDisplaySettings.objects.get_or_create(form=instance)

    # check and create settings for forms that do not have settings

    forms = FormBuilder.objects.all()

    for form in forms:
        if TableDisplaySettings.objects.filter(form=form).first() is None:
            TableDisplaySettings.objects.get_or_create(form=form)
        if TableFilterSettings.objects.filter(form=form).first() is None:
            TableFilterSettings.objects.get_or_create(form=form)
