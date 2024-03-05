from django.shortcuts import render, redirect
from django.views import View
from django.core import serializers
from .models import FormBuilder as FormBuilderModel
from django.urls import reverse
# Create your views here.


class FormBuilder(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request=request, template_name='form/builder.html', context=context)


class MentorContactRecordForm(View):

    def get(self, request, *args, **kwargs):
        form = FormBuilderModel.objects.filter(
            id=kwargs.get('id')
        ).first()
        data = {'form': form.to_json, 'id': kwargs.get(
            'id'), 'form_list': FormBuilderModel.objects.all()}
        return render(request=request, template_name='form/view.html', context=data)

    def post(self, request, *args, **kwargs):
        print(dict(request.POST))
        return redirect(reverse('mentor_contact_record_form_view', kwargs={'id': kwargs.get('id')}))


class PublicView(View):

    def get(self, request, *args, **kwargs):
        form = FormBuilderModel.objects.filter(
            id=kwargs.get('id')
        ).first()
        return render(request=request, template_name='form/publicview.html', context={'form': form.to_json, 'id': kwargs.get('id')})

    def post(self, request, *args, **kwargs):
        print(dict(request.POST))
        return redirect(reverse('mentor_contact_record_form_view', kwargs={'id': kwargs.get('id')}))
