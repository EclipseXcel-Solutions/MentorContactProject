from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import CreateView, UpdateView
from .models import FormBuilder as FormBuilderModel
from django.urls import reverse
import json
from django.contrib import messages
import uuid
from django.core.paginator import Paginator


from collections import defaultdict


from datetime import datetime
from django.utils.dateparse import parse_date
from django.views.generic import UpdateView
from utils.choices import INPUT_TYPES

from .models import Field, FieldOptions, Sections, FormFieldAnswers, Row, FormSubmission, DataFilterSettings, TableDataDisplaySettings, AnalyticsFieldsSettings
from analytics.models import TableDisplaySettings, TableFilterSettings
# Create your views here.


class FormsView(View):

    def get(self, request):
        context = {'forms': FormBuilderModel.objects.all()}
        return render(request, 'dashboard/forms.html', context)


class FormListView(View):

    def get(self, request):

        builders = FormBuilderModel.objects.all()
        return render(request, 'form/builder/forms.html', {'builders': builders, 'total': len(builders)})


class SectionView(View):

    def get_form(self, id):
        try:
            return FormBuilderModel.objects.filter(id=id).first()
        except Exception as e:
            messages.error(self.request, str(e))
            return None

    def get_section(self, id):
        try:
            return Sections.objects.filter(id=id).first()
        except Exception as e:
            messages.error(self.request, str(e))
            return None

    def get(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        form_id = self.kwargs.get('formId')
        form = self.get_form(form_id)

        if form:
            context = {
                'sections': Sections.objects.filter(form=form).all().order_by('position'),
                'form_id': form_id,
                'input_types': [x[0] for x in INPUT_TYPES]
            }
            return render(request, 'form/builder/section.html', context)
        return redirect('/form/builder/')


class FormBuilder(View):

    def get(self, request, *args, **kwargs):
        context = {}
        context.update(self.kwargs)
        return render(request=request, template_name='form/builder.html', context=context)

    def post(self, request, *args, **kwargs):

        form_name = request.POST.get('name')
        form_title = request.POST.get('title')
        form_description = request.POST.get('description')

        form, created = FormBuilderModel.objects.get_or_create(
            name=form_name,
            title=form_title,
            description=form_description,
            created_by=self.request.user
        )

        return redirect(reverse('form_section_view', args=[form.id]))


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
                'fields': [{'id': SYSTEM_DATE_ID, 'title': 'System Date'}] + form.get_all_fields,
                'form_id': self.form_id
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
        print(kwargs)
        data = json.loads(request.body)
        sections = self.get_sections(data[0])
        prepared_data = []
        for fields in data:
            date_field_value = None
            for field in fields:
                if field['field'] == 0:
                    # Assumes 'array_answer' is properly structured.
                    date_field_value = field['array_answer']
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
                        print(field.get('array_answer', None), "aa")
                        prepared_data.append(FormFieldAnswers(
                            field=sections[field['field']],
                            submission_ref=submission,
                            answer=field.get('array_answer', None),
                        ))

        form_answers = FormFieldAnswers.objects.bulk_create(prepared_data)
        return JsonResponse(data={'message': 'all good'})


class DataTables(View):

    def get_answer_value(self, answer, field):
        if field.input_type != 'select':
            return answer.answer
        else:
            options = field.options.all()
            for op in options:
                if op.value == answer.answer:
                    return op.key

        return answer.answer

    def get(self, request, *args, **kwargs):

        form_id = self.kwargs.get('id', None)
        page = self.request.GET.get('page', 1)
        search_term = self.request.GET.get('search_term',
                                           '')
        from_date = self.request.GET.get(
            'from_date', f'{datetime.today().year-1}-01-01')
        to_date = self.request.GET.get(
            'to_date', f'{datetime.today().year-1}-12-30')

        if not from_date and to_date:
            messages.error(request, "Date range should be selected.")
            return redirect(reverse('data_table_view', kwargs={'id': form_id}))
        if from_date and not to_date:
            messages.error(request, "Date range should be selected.")
            return redirect(reverse('data_table_view', kwargs={'id': form_id}))

        filters = dict(self.request.GET)
        if form_id:

            filters.pop('to_date', None)
            filters.pop('from_date', None)
            filters.pop('page', None)

            ultimate_query = None
            submissions_list = FormSubmission.objects.filter(
                date__gte=from_date, date__lte=to_date).order_by('date')
            for filter in filters.keys():
                if filters[filter] != None and filters[filter] != ['None']:
                    print({'field__id': filter.split('_')[
                          1], 'answer__icontains': filters[filter]}, "filter again")

                    dict_filters = {'field__id': filter.split('_')[1], 'answer__icontains': filters[filter][0],
                                    }

                    if len(submissions_list) > 0:
                        dict_filters['submission_ref__in'] = submissions_list

                    ultimate_query = FormFieldAnswers.objects.filter(
                        **dict_filters)

                    submissions_list = FormSubmission.objects.filter(submission_id__in=[
                        x.submission_ref.submission_id for x in ultimate_query])

            form = FormBuilderModel.objects.filter(
                id=form_id).first()
            settings, created = TableDisplaySettings.objects.get_or_create(
                form=form
            )
            filters, created = TableFilterSettings.objects.get_or_create(
                form=form
            )

            if form:
                fields = settings.fields.all()
                submissions = Paginator(
                    submissions_list.order_by('date'), 10)

                aligned_data = []
                items = submissions.get_page(page)
                for submission in items:
                    answer_dict = {answer.field.title: self.get_answer_value(answer, answer.field) for answer in FormFieldAnswers.objects.filter(
                        submission_ref=submission).all()}

                    aligned_row = [answer_dict.get(
                        field.title, None) for field in fields]

                    aligned_data.append({
                        'submission': submission,
                        'answers': aligned_row
                    })
                context = {
                    'headers': fields,
                    'answers': aligned_data,
                    'submissions': items,
                    'filters': [{'filter': fil, 'options': fil.options.all()} for fil in filters.fields.all()],
                    'path': self.request.get_full_path(),

                }
                request_params = self.request.GET.copy()
                if 'page' in request_params:
                    request_params.pop('page', None)
                updated_filters = {}
                for key in dict(self.request.GET):
                    updated_filters[key] = dict(self.request.GET)[key][0]
                context.update(updated_filters)

                context['params'] = request_params.urlencode()

                return render(request=request, template_name='form/dataTable.html', context=context)
            else:
                return redirect('/404')
        else:
            return redirect('/404')


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
            date=datetime.today().date(), submission_id=uuid.uuid4(), form=FormBuilderModel.objects.filter(
                id=kwargs.get('id')
            ).first())
        if created:
            for key in keys:
                value = data[key]
                form_essentials = key.split("-")
                list_ans = value

                form_data_object_list.append(FormFieldAnswers(
                    field=Field.objects.get(id=form_essentials[0]),
                    answer=list_ans[0],
                    submission_ref=submission
                ))

            try:
                FormFieldAnswers.objects.bulk_create(form_data_object_list)
                messages.success(
                    request, 'Whoa !! Your entry has been recorded.')
            except Exception as e:
                print(e)
                messages.error(self.request, str(e))
                messages.error(
                    request, 'Sorry , There was a problem while saving your data')

        return redirect(reverse('public_form_view', kwargs={'id': kwargs.get('id')}))


class Settings(View):

    def get(self, request, *args, **kwargs):
        template_name = 'form/settings.html'
        filter_fields = DataFilterSettings.objects.filter(
            ~Q(field__input_type='checkbox'),
            field__row__section__form__id=self.kwargs.get('form_id', 1)).order_by('field')
        table_fields = TableDataDisplaySettings.objects.filter(
            field__row__section__form__id=self.kwargs.get('form_id', 1)).order_by('field')
        analytics = AnalyticsFieldsSettings.objects.filter(
            field__row__section__form__id=self.kwargs.get('form_id', 1)).order_by('field')
        fields = Field.objects.filter(Q(input_type='checkbox') | Q(
            input_type='select'), row__section__form__id=self.kwargs.get('form_id', 1))

        context = {
            'form_id': self.kwargs.get('form_id', 1),
            'filter_fields': filter_fields,
            'table_fields': table_fields,
            'analytics': analytics,
            'fields': fields
        }

        return render(request=self.request, template_name=template_name, context=context)

    def post(self, request, *args, **kwargs):

        data = request.POST
        keys = list(data.keys())

        del keys[0]
        del keys[0]

        objs = []

        main_model = None

        if data['setting_type'] == 'FILTER':
            main_model = DataFilterSettings
        elif data['setting_type'] == 'TABLE':
            main_model = TableDataDisplaySettings
        else:
            main_model = AnalyticsFieldsSettings

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


class FieldChoicesView(CreateView, UpdateView):

    def post(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def put(self, *args: str, **kwargs) -> HttpResponse:
        return super().put(*args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class SectionAPIView(View):

    def post(self, request, *args, **kwargs):

        json_data = json.loads(request.body)
        errors = []

        for key in json_data.keys():
            if json_data[key] != None:
                if json_data[key].strip() == "":
                    errors.append(f'{key} field cannot be empty')
            else:
                errors.append(f'{key} field cannot be null')

        if errors != []:
            return JsonResponse({
                'success': False,
                'errors': errors
            })

        try:
            form = FormBuilderModel.objects.get(id=json_data.get('form', None))

            if json_data['method'] == 'POST':
                Sections.objects.create(
                    form=form,
                    name=json_data.get('name', None),
                    title=json_data.get('title', None),
                    position=json_data.get('position', None),
                    message=json_data.get('message', None)
                )

            elif json_data['method'] == 'UPDATE':
                section = Sections.objects.get(id=json_data['section'])
                section.form = form
                section.position = json_data['position']
                section.name = json_data['name']
                section.title = json_data['title']
                section.message = json_data['message']
                section.save()

        except Exception as e:
            return JsonResponse({
                                'success': False,
                                'errors': [str(e)]
                                })

        return JsonResponse({
            'success': True,
            'message': json_data
        })


@method_decorator(csrf_exempt, name='dispatch')
class RowApiView(View):

    def post(self, request, *args, **kwargs):

        json_data = json.loads(request.body)
        errors = []

        for key in json_data.keys():
            if json_data[key] != None:
                if json_data[key].strip() == "":
                    errors.append(f'{key} field cannot be empty')
            else:
                errors.append(f'{key} field cannot be null')

        if errors != []:
            return JsonResponse({
                'success': False,
                'errors': errors
            })

        try:
            section = Sections.objects.get(id=json_data.get('section', None))
            if json_data['method'] == 'POST':
                Row.objects.create(
                    position=json_data.get('position', None),
                    section=section,
                    message=json_data.get('message', None),
                )
            elif json_data['method'] == 'UPDATE':
                row = Row.objects.get(id=json_data.get('row', None))
                row.position = json_data.get('position', None)
                row.message = json_data.get('message', None)
                row.save()

        except Exception as e:
            return JsonResponse({
                                'success': False,
                                'errors': [str(e)]
                                })

        return JsonResponse({
            'success': True,
            'message': json_data
        })


@method_decorator(csrf_exempt, name='dispatch')
class FieldView(View):

    def post(self, request, *args, **kwargs):
        errors = []
        field_data = json.loads(request.body)
        choices_dict = []
        print(request.body)
        for key in ['title', 'type']:
            if field_data[key] is not None:
                if field_data[key].strip() == '' or field_data[key] == 'None':
                    errors.append(f'Please make sure to add {key}')
            else:
                errors.append(f'Please make sure to add {key}')

        if field_data['type'] in ['select', 'checkbox']:
            choices = field_data['choices']
            if choices != None or choices.strip() != "":
                key_val_pairs = choices.split(',')
                if len(key_val_pairs) > 1:
                    for key_val_pair in key_val_pairs:
                        if len(key_val_pair.split('/')) <= 1 or len(key_val_pair.split('/')) > 2:
                            errors.append(
                                'Please make sure to put the choices in correct format')
                        else:
                            choices_dict.append({"key": key_val_pair.split(
                                "/")[0], "val": key_val_pair.split("/")[1]})
                else:
                    errors.append(
                        'Please make sure to put choices in correct format')
                field_data['choices'] = choices_dict

        if len(set([x['val'] for x in choices_dict])) < len(choices_dict):

            errors.append("Please make sure not to repeat the values ")

        if len(errors) == 0:
            options = []
            try:
                for x in choices_dict:
                    option, created = FieldOptions.objects.get_or_create(
                        key=x['key'], value=x['val'])
                    if created or option:
                        options.append(option)
            except Exception as e:
                print(errors, e)
                return JsonResponse({'success': False, 'errors': [str(e)]})
            try:

                if field_data['method'] == 'POST':
                    field, created = Field.objects.get_or_create(
                        title=field_data['title'],
                        input_name=field_data['title'],
                        placeholder=field_data['title'],
                        order=field_data['position'],
                        row=Row.objects.get(id=field_data['row']),
                        input_type=field_data['type'],
                        has_other_field=False,
                        is_multiple_choice=False,
                    )
                    if len(options) > 0:
                        for op in options:
                            field.options.add(op)
                            field.save()
                elif field_data['method'] == 'UPDATE':
                    field = Field.objects.get(id=field_data.get('field', None))
                    field.title = field_data.get('title', None)
                    field.input_name = field_data.get('title', None)
                    field.input_type = field_data.get('type', None)
                    field.order = field_data.get('position', 0)
                    field.save()
                    if len(options) > 0:
                        field.options.clear()
                        for op in options:
                            field.options.add(op)
                            field.save()
                    field.save()
            except Exception as e:
                print(errors, e)
                return JsonResponse({'success': False, 'errors': [str(e)]})
            print(errors)
            return JsonResponse({'success': True, 'data': field_data})
        else:
            print(errors)
            return JsonResponse({'success': False, 'errors': errors})


class DeleteField(View):

    def get(self, request, *args, **kwargs):

        try:
            field = Field.objects.get(id=self.kwargs.get('field'))

            if field:

                field_responses = FormFieldAnswers.objects.filter(
                    field=field
                )

                if len(field_responses) > 0:

                    messages.error(
                        request, "Field contains important information , cannot delete it")
                else:
                    field.delete()
                    messages.success(request, "Field Deleted")

            return redirect(reverse('form_section_view', args=[self.kwargs.get('form')]))

        except Exception as e:

            messages.error(request, str(e))

            return redirect(reverse('form_section_view', args=[self.kwargs.get('form')]))


class ValueAnalyticsView(View):
    template_name = 'form/fielddataanalytics.html'

    def get(self, request):
        forms = FormBuilderModel.objects.all()  # Changed from FormBuilderModel
        context = {
            'forms': forms,
            'show_results': False,
            'available_fields': Field.objects.all()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form_id = request.POST.get('form_id')
        primary_field_id = request.POST.get('primary_field_id')
        analysis_field_id = request.POST.get(
            'analysis_field_id')  # Changed from secondary_field_id
        display_field_ids = request.POST.getlist('display_field_ids')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Get form and fields
        selected_form = FormBuilderModel.objects.get(
            id=form_id)  # Changed from FormBuilderModel
        available_fields = Field.objects.filter(
            row__section__form=selected_form)

        # Get selected fields
        primary_field = Field.objects.get(id=primary_field_id)
        # Changed from secondary_field_id
        analysis_field = Field.objects.get(id=analysis_field_id)
        display_fields = Field.objects.filter(id__in=display_field_ids)

        # Get submissions
        submissions = FormSubmission.objects.filter(
            form=selected_form,  # Changed from form_id to selected_form
            date__range=[start_date, end_date]
        ).order_by('date')

        analysis_results = {}

        for submission in submissions:
            # Get primary and analysis field answers
            primary_answer = FormFieldAnswers.objects.filter(
                submission_ref=submission,
                field=primary_field
            ).first()

            analysis_answer = FormFieldAnswers.objects.filter(  # Changed from secondary_answer
                submission_ref=submission,
                field=analysis_field
            ).first()

            if primary_answer and analysis_answer:
                # Get display field values
                display_values = []
                for field in display_fields:
                    answer = FormFieldAnswers.objects.filter(
                        submission_ref=submission,
                        field=field
                    ).first()
                    display_values.append(answer.answer if answer else '')

                result_data = {
                    'date': submission.date,
                    'analysis_value': analysis_answer.answer,
                    'display_values': display_values
                }

                # Add to results
                primary_value = primary_answer.answer
                if primary_value not in analysis_results:
                    analysis_results[primary_value] = {
                        'primary_value': primary_value,
                        'primary_field_name': primary_field.title,
                        'analysis_field_name': analysis_field.title,
                        'total_occurrences': 0,
                        'occurrences': []
                    }

                analysis_results[primary_value]['occurrences'].append(
                    result_data)
                analysis_results[primary_value]['total_occurrences'] += 1

        # Convert to list for template
        analysis_results = list(analysis_results.values())

        context = {
            'forms': FormBuilderModel.objects.all(),  # Changed from FormBuilder
            'available_fields': available_fields,
            'selected_form': selected_form,
            'primary_field': primary_field,
            'analysis_field': analysis_field,  # Changed name
            'display_fields': display_fields,
            'start_date': start_date,
            'end_date': end_date,
            'analysis_results': analysis_results,
            'show_results': True,
            # Added this
            'display_field_ids': [int(id) for id in display_field_ids] if display_field_ids else []
        }

        return render(request, self.template_name, context)
