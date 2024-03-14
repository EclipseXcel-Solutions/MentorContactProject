from django.shortcuts import render, redirect
from django.views import View
from .models import FormBuilder as FormBuilderModel
from django.urls import reverse
import json
from django.contrib import messages
from .models import Field, Sections, FormFieldAnswers, FormSubmission
import uuid
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
        return redirect(reverse('mentor_contact_record_form_view', kwargs={'id': kwargs.get('id')}))


class DataImportView(View):

    def get(self, request, *args, **kwargs):

        form = FormBuilderModel.objects.first()
        context = {
            'fields': form.get_all_fields
        }
        return render(request=request, template_name='form/dataImortForm.html', context=context)

    def post(self, request, *args, **kwargs):
        return render(json.dumps({'message': 'all good'}), content_type='application/json')


class DataTables(View):
    def get(self, request, *args, **kwargs):

        form = FormBuilderModel.objects.filter(
            id=self.kwargs.get('id')).first()

        if form:
            submissions = FormSubmission.objects.filter(form=form).all()
            context = {
                'fields': form.get_all_fields,
                'data': [[FormFieldAnswers.objects.filter(field=field['id'], submission=submission).first().array_answer for field in form.get_all_fields] for submission in submissions]
            }
            return render(request=request, template_name='form/dataTable.html', context=context)

        else:
            return render(request=request, template_name='404.html')

    def post(self, request, *args, **kwargs):
        return redirect(reverse('data_import_view'))


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
            form=FormBuilderModel.objects.get(id=kwargs.get('id')), submission_id=uuid.uuid4())
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
