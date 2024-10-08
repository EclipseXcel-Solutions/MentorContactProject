from django.contrib import admin
from .models import TableDisplaySettings, TableFilterSettings
# Register your models here.

admin.site.register(TableDisplaySettings)
admin.site.register(TableFilterSettings)
