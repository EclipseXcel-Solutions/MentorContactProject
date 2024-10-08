from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import uuid


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
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'created_by': self.created_by,
            'sections': [section.to_json for section in self.sections]
        }

    @property
    def get_all_fields(self):
        fields = []
        for section in self.sections:
            for row in section.rows:
                for field in row.get_fields:
                    fields.append(field)
        return [{'title': field.title, 'id': field.id, 'type': field.input_type, 'options': field.choices} for field in fields]


class FormSubmission(models.Model):

    date = models.DateField()
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    submission_id = models.UUIDField(default=uuid.uuid4)

    @property
    def get_submission_id(self):
        return self.submission_id

    def __str__(self) -> str:
        return str(self.get_submission_id)


class Sections(models.Model):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    position = models.IntegerField()
    message = models.TextField()

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        print(args, kwargs)
        super(Sections, self).save(*args, **kwargs)

    @property
    def rows(self):
        return Row.objects.filter(section=self.pk).order_by('position')

    @property
    def to_json(self):

        return {
            'id': self.id,
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
        return Field.objects.filter(row=self.pk).order_by('order')

    @property
    def to_json(self):
        return {
            'id': self.id,
            'position': self.position,
            'message': self.message,
            'fields': [field.to_json for field in self.get_fields]
        }


class FieldOptions(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)


class Field(models.Model):

    choices = (
        ('text', 'text'),
        ('select', 'select'),
        ('email', 'email'),
        ('checkbox', 'checkbox'),
        ('textarea', 'textarea'),
        ('date', 'date'),
        ('datetime', 'datetime'), ('time', 'time')
    )
    title = models.CharField(max_length=200)
    input_name = models.CharField(max_length=200)
    placeholder = models.CharField(max_length=200, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    input_type = models.CharField(choices=choices, max_length=100)
    has_other_field = models.BooleanField(default=False)
    is_multiple_choice = models.BooleanField(default=True)
    options = models.ManyToManyField(FieldOptions)

    @property
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'placeholder': self.placeholder,
            'order': self.order,
            'input_type': self.input_type,
            'is_multiple_choice': self.is_multiple_choice,
            "input_name": self.input_name,
            "options": [{
                'key': option.key,
                'value': option.value
            } for option in self.options.all()]
        }

    def __str__(self) -> str:
        return self.title


class FormFieldAnswers(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    answer = models.TextField(null=True, blank=True)
    submission_ref = models.ForeignKey(
        FormSubmission, on_delete=models.SET_NULL, null=True, blank=True)
    json_answer = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return self.field.title


class DataFilterSettings(models.Model):

    """
        Form filters are everything except multiple choice / checkboxes
        - multiple select
        - select
    """

    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


class TableDataDisplaySettings(models.Model):

    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


class AnalyticsFieldsSettings(models.Model):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


class ChoiceModel(models.Model):

    choice_for = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name='field_choices')
    choice_title = models.CharField(max_length=200)
    choice_id = models.IntegerField()

    def __str__(self):
        return f'{self.choice_for.title}:field - { self.choice_title }:value'
