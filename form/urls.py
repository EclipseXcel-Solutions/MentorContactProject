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
from .views import FormBuilder, MentorContactRecordForm, PublicView
urlpatterns = [
    path('builder/', FormBuilder.as_view(), name="form_builder_view"),
    path('mentor-contact-record/<id>', MentorContactRecordForm.as_view(),
         name="mentor_contact_record_form_view"),
    path('form/public/<id>', PublicView.as_view(),
         name="public_form_view")
]
