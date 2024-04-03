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
from django.core.paginator import Paginator

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
            submissions_paginator = Paginator(FormFieldAnswers.objects.values(
                'submission_id').distinct(), 12)  # Adjust the number of items per page as needed
            page_number = request.GET.get('page')
            submissions_page = submissions_paginator.get_page(page_number)

            # Prefetch all relevant FormFieldAnswers in a single query
            answers = FormFieldAnswers.objects.filter(
                submission_id__in=[submission['submission_id']
                                   for submission in submissions_page],
                field__in=[field['id'] for field in form.get_all_fields]
            )

            # Organize answers by submission_id and field_id for efficient access
            answers_by_submission = {
                submission['submission_id']: {} for submission in submissions_page}
            for answer in answers:
                answers_by_submission[answer.submission_id][answer.field_id] = answer.array_answer

            data = [
                [
                    answers_by_submission[submission['submission_id']].get(
                        field['id'], [])
                    for field in form.get_all_fields
                ]
                for submission in submissions_page
            ]

            context = {
                'fields': form.get_all_fields,
                'data': data,
                'submissions_page': submissions_page
            }
            return render(request=request, template_name='form/dataTable.html', context=context)
        else:
            return render(request=request, template_name='404.html')


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
        submission = uuid.uuid4()
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
                submission_id=submission
            ))

        try:
            FormFieldAnswers.objects.bulk_create(form_data_object_list)
            print('data saved')
        except Exception as e:
            print(e)
            messages.error(self.request, str(e))

        return redirect(reverse('public_form_view', kwargs={'id': kwargs.get('id')}))


class Settings(View):

    def get(self, request, *args, **kwargs):
        template_name = 'form/settings.html'
        fields = Field.objects.filter(
            row__section__form__id=self.kwargs.get('form_id', 1))
        context = {
            'form_id': self.kwargs.get('form_id', 1),
            'fields': fields
        }

        return render(request=self.request, template_name=template_name, context=context)
