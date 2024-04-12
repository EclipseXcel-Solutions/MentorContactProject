
from django.contrib import admin
from .models import FormBuilder, Sections
from .models import (Field, Row, FormFieldAnswers, FormSubmission, CalculatedFields,
                     DataFilterSettings, TableDataDisplaySettings, FiledResponses, AnalyticsFieldsSettings)
# Register your models here.

admin.site.register(FormBuilder)
admin.site.register(Field)
admin.site.register(Sections)
admin.site.register(Row)
admin.site.register(FormFieldAnswers)
admin.site.register(FormSubmission)
admin.site.register(DataFilterSettings)
admin.site.register(CalculatedFields)
admin.site.register(TableDataDisplaySettings)
admin.site.register(FiledResponses)
admin.site.register(AnalyticsFieldsSettings)
