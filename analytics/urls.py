
from django.urls import path
from .views import Dashboard, TableDataDisplaySettingsView, TableDataCalculationView, TableDatFilterView, FieldAnalyticsView, ReportsView
urlpatterns = [
    path('admin/<id>/', Dashboard.as_view(), name="admin_dashboard"),
    path('settings/table-data/<str:method>/<int:form>/',
         TableDataDisplaySettingsView.as_view(), name="table_data_display_settings_view"),
    path('settings/table-filter/<str:method>/<int:form>/',
         TableDatFilterView.as_view(), name="table_data_filter_settings_view"),
    path('settings/table-calculation/<str:method>/<int:form>/',
         TableDataCalculationView.as_view(), name="table_data_calculation_settings_view"),
    path('settings/field-analytics/<str:method>/<int:form>/',
         FieldAnalyticsView.as_view(), name="field_analytics"),


    path('reports/<int:field_id>/<int:form>/',
         ReportsView.as_view(), name="reports_view"),

]
