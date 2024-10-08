from django.db import models
from form.models import FormBuilder, Field
# Create your models here.


class TableDisplaySettings(models.Model):

    form = models.OneToOneField(FormBuilder, on_delete=models.CASCADE)
    fields = models.ManyToManyField(Field)

    def __str__(self):
        return self.form.name


class TableFilterSettings(models.Model):

    form = models.OneToOneField(FormBuilder, on_delete=models.CASCADE)
    fields = models.ManyToManyField(Field)

    def __str__(self):
        return self.form.name


class CalculatedFields(models.Model):

    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    field_one = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name='greater_field')
    field_two = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name='smaller_field')

    def __str__(self) -> str:
        return f'calculated fields for {self.form} field1-{self.field_one.title} field2-{self.field_two.title}'
