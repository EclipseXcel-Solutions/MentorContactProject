from django.shortcuts import render
from django.views import View
from django.core import serializers
from .models import FormBuilder as FormBuilderModel
# Create your views here.


class FormBuilder(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request=request, template_name='form/builder.html', context=context)


class MentorContactRecordForm(View):

    def get(self, request, *args, **kwargs):
        form = FormBuilderModel.objects.first()

        return render(request=request, template_name='form/view.html', context={'form': form.to_json})
