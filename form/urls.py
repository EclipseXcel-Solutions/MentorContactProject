"""mcp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import (FormBuilder, MentorContactRecordForm, PublicView, DataImportView, DataTables,
                    Settings, FieldChoicesView, SectionView, FieldView, SectionAPIView, RowApiView, FormListView, FormsView, DeleteField)
urlpatterns = [
    path('builder/<id>/',
         FormBuilder.as_view(), name="form_builder_view"),
    path('builders/', FormListView.as_view(), name="form_list_view"),
    path('sections/<formId>/',
         SectionView.as_view(), name='form_section_view'),
    path('import/data/<id>/', DataImportView.as_view(),
         name="data_import_view"),
    path('mentor-contact-record/<id>/', MentorContactRecordForm.as_view(),
         name="mentor_contact_record_form_view"),
    path('public/<id>/', PublicView.as_view(),
         name="public_form_view"),
    path('data-table/<id>/', DataTables.as_view(),
         name="data_table_view"),
    path('settings/<id>/', Settings.as_view(),
         name="form_settings_view"),
    path('field-choices/<id>/', FieldChoicesView.as_view(),
         name='field_choices_view'),
    # JS API VIEWS
    path('field-view/', FieldView.as_view(), name="field_view"),
    path('section-view/', SectionAPIView.as_view(), name="section_view"),
    path('row-view/', RowApiView.as_view(), name="row_view"),

    # UI VIEWS
    path('select-forms/', FormsView.as_view(), name='select-forms-view'),
    path('delete-field/<int:field>/<int:form>/',
         DeleteField.as_view(), name='delete-field-view')
]
