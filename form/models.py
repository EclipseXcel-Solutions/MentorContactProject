from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import json
# Create your models here.


class FormBuilder(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    @property
    def sections(self):
        return Sections.objects.filter(form=self.pk).order_by('position')

    @property
    def to_json(self):
        return {
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'created_by': self.created_by,
            'sections': [section.to_json for section in self.sections]
        }


class Sections(models.Model):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    position = models.IntegerField()
    message = models.TextField()

    def __str__(self) -> str:
        return self.title

    @property
    def rows(self):
        return Row.objects.filter(section=self.pk).order_by('position')

    @property
    def to_json(self):

        return {
            'name': self.name,
            'title': self.title,
            'position': self.position,
            'message': self.message,
            'rows': [row.to_json for row in self.rows]
        }


class Row(models.Model):
    position = models.IntegerField()
    section = models.ForeignKey(Sections, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self) -> str:
        return f'{self.section.title} - {str(self.position)} '

    @property
    def get_fields(self):
        return Field.objects.filter(row=self.pk)

    @property
    def to_json(self):
        return {
            'position': self.position,
            'message': self.message,
            'fields': [field.to_json for field in self.get_fields]
        }


class Field(models.Model):
    choices = (('text', 'text'), ('select', 'select'), ('email', 'email'),
               ('checkbox', 'checkbox'), ('textarea', 'textarea'), ('date', 'date'),
               ('datetime', 'datetime'), ('time', 'time'))
    title = models.CharField(max_length=200)
    input_name = models.CharField(max_length=200)
    placeholder = models.CharField(max_length=200, null=True, blank=True)
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    input_type = models.CharField(choices=choices)
    is_multiple_choice = models.BooleanField(default=False)
    has_other_field = models.BooleanField(default=False)

    choices = ArrayField(

        ArrayField(

            models.CharField(max_length=100, blank=True, null=True),
            size=20,
            blank=True,
        ),
        blank=True,
        size=20,

    )

    @property
    def to_json(self):
        return {
            'title': self.title,
            'placeholder': self.placeholder,
            'input_type': self.input_type,
            'is_multiple_choice': self.is_multiple_choice,
            'choices': self.choices,
            "input_name": self.input_name
        }
