from django.contrib import admin
from .models import FormBuilder, Field, Sections, Row
# Register your models here.

admin.site.register(FormBuilder)
admin.site.register(Field)
admin.site.register(Sections)
admin.site.register(Row)
