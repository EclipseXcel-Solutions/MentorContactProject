from django.shortcuts import render, redirect
from django.views import View
from .models import FormBuilder as FormBuilderModel
from django.urls import reverse
import json
from django.contrib import messages
from .models import Field, Sections, FormFieldAnswers, FormSubmission

# Create your views here.


class FormBuilder(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request=request, template_name='form/builder.html', context=context)


class MentorContactRecordForm(View):

    def get(self, request, *args, **kwargs):

        data = {
            'form': FormBuilderModel.objects.filter(id=kwargs.get('id')).first().to_json,
            'id': kwargs.get('id'),
            'form_list': FormBuilderModel.objects.all()
        }
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
        data = dict(request.POST)
        keys = list(data.keys())

        del keys[0]
        form_data_object_list = []

        submission, created = FormSubmission.objects.get_or_create(
            form=FormBuilderModel.objects.get(id=kwargs.get('id')))

        for key in keys:
            value = data[key]
            form_essentials = key.split("-")
            list_ans = value

            form_data_object_list.append(FormFieldAnswers(
                field=Field.objects.get(id=form_essentials[0]),
                section=Sections.objects.get(id=form_essentials[1]),
                form=FormBuilderModel.objects.get(id=form_essentials[2]),
                array_answer=list_ans,
                answer='',
                submission=submission
            ))

        try:

            FormFieldAnswers.objects.bulk_create(form_data_object_list)

        except Exception as e:
            print(e)
            messages.error(self.request, str(e))

        return redirect(reverse('public_form_view', kwargs={'id': kwargs.get('id')}))
