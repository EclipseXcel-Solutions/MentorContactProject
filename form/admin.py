
from django.contrib import admin
from .models import FormBuilder, Sections
from .models import Field, Row, FormFieldAnswers, FormSubmission
# Register your models here.

admin.site.register(FormBuilder)
admin.site.register(Field)
admin.site.register(Sections)
admin.site.register(Row)
admin.site.register(FormFieldAnswers)
admin.site.register(FormSubmission)
