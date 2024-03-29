from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .models import FormBuilder as FormBuilderModel
from django.urls import reverse
import json
from django.contrib import messages
from .models import Field, Sections, FormFieldAnswers, FormSubmission
import uuid
from django.contrib.postgres.aggregates import ArrayAgg


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
        self.form_id = self.kwargs.get('id')
        form = FormBuilderModel.objects.filter(id=self.form_id).first()
        print(form)
        if form:
            context = {
                'fields': form.get_all_fields
            }
            return render(request=request, template_name='form/dataImortForm.html', context=context)
        else:
            return redirect(reverse('404'))

    def get_sections(self, fields):

        sections = {}
        for field in fields:
            sections[field['field']] = Field.objects.filter(
                id=field['field']).first()
        return sections

    def post(self, request, *args, **kwargs):
        self.form_id = self.kwargs.get('id')
        data = json.loads(request.body)
        sections = self.get_sections(data[0])
        prepared_data = []
        for fields in data:
            submission_id = uuid.uuid4()
            for field in fields:
                prepared_data.append(FormFieldAnswers(
                    form=sections[field['field']].row.section.form,
                    field=sections[field['field']],
                    submission_id=submission_id,
                    section=sections[field['field']].row.section,
                    answer=None,
                    array_answer=field['array_answer']
                ))

        print(prepared_data[0])

        form_answers = FormFieldAnswers.objects.bulk_create(prepared_data)

        return JsonResponse(data={'message': 'all good'})


class DataTables(View):
    def get(self, request, *args, **kwargs):

        form = FormBuilderModel.objects.filter(
            id=self.kwargs.get('id')).first()

        if form:
            submissions = FormFieldAnswers.objects.values(
                'submission_id').distinct()

            context = {
                'fields': form.get_all_fields,
                'data': [[FormFieldAnswers.objects.filter(field=field['id'], submission_id=submission['submission_id']).first().array_answer if FormFieldAnswers.objects.filter(field=field['id'], submission_id=submission['submission_id']).first() is not None else [] for field in form.get_all_fields] for submission in submissions]
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
