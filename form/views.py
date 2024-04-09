import random
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .models import FormBuilder as FormBuilderModel
from django.urls import reverse
import json
from django.contrib import messages
from .models import Field, Sections, FormFieldAnswers, FormSubmission, FiledResponses, DataFilterSettings, TableDataDisplaySettings
import uuid
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models.expressions import RawSQL
from django.db.models import BooleanField
from django.db.models.functions import Cast
from datetime import datetime
from django.utils.dateparse import parse_date

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
        SYSTEM_DATE_ID = 0
        if form:
            context = {
                'fields': [{'id': SYSTEM_DATE_ID, 'title': 'System Date'}] + form.get_all_fields
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
            date_field_value = None
            for field in fields:
                if field['field'] == 0:
                    # Assumes 'array_answer' is properly structured.
                    date_field_value = field['array_answer'][0][0]
                    break

            if date_field_value:
                submission, created = FormSubmission.objects.get_or_create(
                    date=datetime.strptime(date_field_value, '%m/%d/%Y'),
                    form=FormBuilderModel.objects.filter(
                        id=self.form_id).first(),
                    submission_id=uuid.uuid4()
                )
            if submission:
                for field in fields:
                    if field['field'] != 0:
                        prepared_data.append(FiledResponses(
                            form=sections[field['field']].row.section.form,
                            field=sections[field['field']],
                            submission_ref=submission,
                            section=sections[field['field']].row.section,
                            answer=None,
                            array_answer=field['array_answer']
                        ))

        form_answers = FiledResponses.objects.bulk_create(prepared_data)
        return JsonResponse(data={'message': 'all good'})


class DataTables(View):
    def get(self, request, *args, **kwargs):

        # Assuming form retrieval remains the same
        form = FormBuilderModel.objects.filter(
            id=self.kwargs.get('id')).first()

        query: str = self.request.GET.get('query', '')
        if query is not None and query.strip() != '':
            print(query)

        # Retrieval of fields for the data table display and filter settings remains unchanged
        data_table_fields = [
            setting.field for setting in TableDataDisplaySettings.objects.filter(form=1, status=True).all().order_by('field')]
        filter_settings = [
            setting.field for setting in DataFilterSettings.objects.filter(form=1, status=True).all().order_by('field')]

        if form:
            # Adjusting FiledResponses query to work with submission_ref as a model
            submissions_paginator = Paginator(FiledResponses.objects.annotate(
                matches=RawSQL(
                    "SELECT EXISTS(SELECT 1 FROM unnest(array_answer) AS s WHERE s ILIKE %s)",
                    ('%' + query + '%',)
                )
            ).filter(matches=True).values('submission_ref_id').distinct(), 10)  # Note the change to 'submission_ref_id' for distinct values

            page_number = self.request.GET.get('page')
            submissions_page = submissions_paginator.get_page(page_number)

            # Adjusting FiledResponses query for prefetching FormFieldAnswers
            answers = FiledResponses.objects.filter(
                submission_ref_id__in=[submission['submission_ref_id']
                                       for submission in submissions_page],
                field__in=[field.id for field in data_table_fields]
            )

            # Adjusting organization of answers by submission_id for model change
            answers_by_submission = {
                submission['submission_ref_id']: {} for submission in submissions_page}
            for answer in answers:
                # Assuming submission_ref has a submission_id field or equivalent unique identifier
                answers_by_submission[answer.submission_ref_id][answer.field_id] = answer.array_answer

            data = [
                [
                    answers_by_submission[submission['submission_ref_id']].get(
                        field.id, [])
                    for field in data_table_fields
                ]
                for submission in submissions_page
            ]

            context = {
                'fields': data_table_fields,
                'data': data,
                'filter_fields': filter_settings,
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
        filter_fields = DataFilterSettings.objects.filter(
            ~Q(field__input_type='checkbox'),
            field__row__section__form__id=self.kwargs.get('form_id', 1)).order_by('field')
        table_fields = TableDataDisplaySettings.objects.filter(
            field__row__section__form__id=self.kwargs.get('form_id', 1)).order_by('field')
        context = {
            'form_id': self.kwargs.get('form_id', 1),
            'filter_fields': filter_fields,
            'table_fields': table_fields
        }

        return render(request=self.request, template_name=template_name, context=context)

    def post(self, request, *args, **kwargs):

        data = request.POST
        keys = list(data.keys())

        del keys[0]
        del keys[0]

        objs = []

        main_model = DataFilterSettings if data['setting_type'] == 'FILTER' else TableDataDisplaySettings
        checked_models = main_model.objects.filter(
            form=self.kwargs.get('form_id', 1))

        for model in checked_models:
            if str(model.id) not in keys:
                model.status = False
                objs.append(model)
            else:
                model.status = True
                objs.append(model)

        main_model.objects.bulk_update(objs, ['status'])

        return redirect(reverse('form_settings_view', kwargs={'id': 1}))
