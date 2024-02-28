from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
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


class Sections(models.Model):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    position = models.IntegerField()
    message = models.TextField()

    def __str__(self) -> str:
        return self.title


class Row(models.Model):
    position = models.IntegerField()
    section = models.ForeignKey(Sections, on_delete=models.CASCADE)
    message = models.TextField()


class Field(models.Model):
    choices = (('text', 'text'), ('select', 'select'), ('email', 'email'),
               ('checkbox', 'checkbox'), ('textarea', 'textarea'), ('date', 'date'),
               ('datetime', 'datetime'), ('time', 'time'))

    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    input_type = models.CharField(choices=choices)
    is_multiple_choice = models.BooleanField(default=False)
    choices = ArrayField(
        ArrayField(
            models.CharField(max_length=100, blank=True),
            size=20,
        ),
        size=20,
    )
