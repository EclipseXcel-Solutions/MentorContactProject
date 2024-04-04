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

    date_time = models.DateTimeField(auto_now_add=True)
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
        return Field.objects.filter(row=self.pk)

    @property
    def to_json(self):
        return {
            'id': self.id,
            'position': self.position,
            'message': self.message,
            'fields': [field.to_json for field in self.get_fields]
        }


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

    date_type_choices = (
        ('TODAY', 'TODAY'),
        ('CUSTOM', 'CUSTOM')
    )
    title = models.CharField(max_length=200)
    input_name = models.CharField(max_length=200)
    placeholder = models.CharField(max_length=200, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    input_type = models.CharField(choices=choices)
    date_type = models.CharField(
        choices=date_type_choices, max_length=10, default='CUSTOM')
    is_multiple_choice = models.BooleanField(default=False)
    has_other_field = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
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
            'id': self.id,
            'title': self.title,
            'placeholder': self.placeholder,
            'input_type': self.input_type,
            'is_multiple_choice': self.is_multiple_choice,
            'choices': self.choices,
            "input_name": self.input_name,
            'date_field_choices': self.date_type,

        }

    def __str__(self) -> str:
        return self.title


class FormFieldAnswers(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE)
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE)
    answer = models.TextField(null=True, blank=True)
    submission_id = models.UUIDField()
    array_answer = ArrayField(
        ArrayField(
            models.CharField(max_length=100, blank=True, null=True),
            size=20,
            blank=True,
        ),
        blank=True,
        size=20,
    )

    def __str__(self) -> str:
        return self.field.title


class CalculatedFields(models.Model):
    """
        Note: this can only be used in fields like
        numbers,date,time
    """
    CALCULATION_TYPES = (
        ('MINUTES', 'MINUTES'),
        ('HOURS', 'HOURS'),
        ('SECONDS', 'SECONDS'),
        ('DIFFERENCE', 'DIFFERENCE'),
        ('SUM', 'SUM'),
    )
    name = models.CharField(max_length=100)
    field1 = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name='greater_calculation_field')
    field2 = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name='smaller_calculation_field')
    return_type = models.CharField(max_length=10, choices=CALCULATION_TYPES)


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
