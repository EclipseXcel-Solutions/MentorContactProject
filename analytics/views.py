from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from form.models import FormBuilder
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from form.models import FormSubmission, AnalyticsFieldsSettings, Field, FormFieldAnswers
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncDay, TruncYear, TruncQuarter
import calendar
from django.db.models import Count
from collections import defaultdict
import json
from django.db.models import F
import calendar
import random
import csv
from django.http import HttpResponse
from .models import TableDisplaySettings, TableFilterSettings
# Create your views here.


class IndexPage(View):

    @method_decorator(login_required)
    def get(self, request):
        return redirect(reverse('select-forms-view'))


class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        date_today = datetime.today()
        if self.kwargs.get('id', None):
            request.session['selected_form_id'] = self.kwargs.get('id', None)
        else:
            return redirect('/404')

        try:
            form = FormBuilder.objects.get(id=self.kwargs.get('id'))
            request.session['fields'] = [{'name': field.title, 'id': field.id} for field in Field.objects.filter(
                input_type='select',
                row__section__form=form
            )]
        except FormBuilder.DoesNotExist:
            return redirect('/404')

        select_fields = Field.objects.filter(
            row__section__form=form, input_type='select')
        select_field_responses = [
            {'field': f'{x.title}', 'color': random.choice(['danger', 'primary', 'success', 'info']), 'count': len(set([x.answer for x in FormFieldAnswers.objects.filter(field=x)]))} for x in select_fields]

        from_date = self.request.GET.get(
            'from_date', datetime(date_today.year, 1, 1).strftime('%Y-%m-%d'))
        to_date = self.request.GET.get(
            'to_date', date_today.date().strftime('%Y-%m-%d'))

        yearly_submissions = (
            FormSubmission.objects.filter(
                form=form)
            .annotate(year=TruncYear('date'))
            .values('year')
            .annotate(submissions_count=Count('id'))
            .order_by('year')
        )
        daily_submissions = (
            FormSubmission.objects.filter(
                date__gte=from_date, date__lte=to_date)
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(submissions_count=Count('id'))
            .order_by('day')
        )
        weekly_submissions = (
            FormSubmission.objects.filter(
                date__gte=from_date, date__lte=to_date)
            .annotate(week=TruncWeek('date'))
            .values('week')
            .annotate(submissions_count=Count('id'))
            .order_by('week')
        )

        print(weekly_submissions)
        monthly_submissions = (
            FormSubmission.objects.filter(
                date__gte=from_date, date__lte=to_date)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(submissions_count=Count('id'))
            .order_by('month')
        )
        quarterly_submissions = (
            FormSubmission.objects.filter(
                date__gte=from_date, date__lte=to_date)
            .annotate(quarter=TruncQuarter('date'))
            .values('quarter')
            .annotate(submissions_count=Count('id'))
            .order_by('quarter')
        )

        data = {
            'from_date': from_date,
            'to_date': to_date,
            'form_list': FormBuilder.objects.all(),
            'mentoring_session': len(FormSubmission.objects.filter(form=form)),
            'total_users': len(User.objects.all()),
            'years': FormSubmission.objects.filter(form=form).annotate(
                year=TruncYear('date')).values('year').distinct('year'),
            'months': [x for x in range(1, 13)],
            'weeks': [x for x in range(1, 5)],
            'subjects': '',
            'analytics': AnalyticsFieldsSettings.objects.filter(form=form, status=True),
            'submissions': {
                'weekly': {
                    'y_axis': [sub['week'].isocalendar()[1] for sub in weekly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in weekly_submissions]
                },
                'monthly': {
                    'y_axis': [calendar.month_name[sub['month'].month] for sub in monthly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in monthly_submissions]
                },
                'daily_time_series': [{'x': sub['day'], 'y': sub['submissions_count']} for sub in daily_submissions],
                'daily': {
                    'y_axis': [sub['day'] for sub in daily_submissions],
                    'x_axis': [sub['submissions_count'] for sub in daily_submissions]
                },
                'quarterly': {
                    'y_axis': [calendar.month_name[sub['quarter'].month] for sub in quarterly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in quarterly_submissions]
                },
                'yearly': {
                    'y_axis': [sub['year'].year for sub in yearly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in yearly_submissions]
                }

            },
            'select_field_responses': select_field_responses

        }
        print(data)
        return render(request, 'analytics/dashboard.html', context=data)


class TableDataDisplaySettingsView(View):

    def get(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        form = FormBuilder.objects.filter(id=form_id).first()
        if form:
            settings, created = TableDisplaySettings.objects.get_or_create(
                form=form
            )
            fields = Field.objects.filter(row__section__form=form).all()
            context = {
                'settings': settings,
                'enabled': [field for field in fields if field in settings.fields.all()],
                'disabled': [field for field in fields if field not in settings.fields.all()]
            }
            return render(request, 'analytics/table_data.html', context)
        else:
            return redirect(reverse('404'))

    def post(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        form = FormBuilder.objects.filter(id=form_id).first()
        if form:
            settings = TableDisplaySettings.objects.get(
                form=form
            )

            checked_fields = self.request.POST
            settings.fields.clear()
            for key in checked_fields.keys():
                if key not in ['csrfmiddlewaretoken']:
                    print(key)
                    field = Field.objects.filter(
                        id=int(key.split('__')[1])).first()
                    if field and field not in settings.fields.all():
                        settings.fields.add(field.id)
                        settings.save()

            return redirect(reverse('table_data_display_settings_view', args=['GET', form_id]))
        else:
            return redirect(reverse('404'))


class TableDatFilterView(View):

    def get(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        form = FormBuilder.objects.filter(id=form_id).first()
        if form:
            settings, created = TableFilterSettings.objects.get_or_create(
                form=form
            )
            fields = Field.objects.filter(
                row__section__form=form, input_type='select').all()
            context = {
                'settings': settings,
                'enabled': [field for field in fields if field in settings.fields.all()],
                'disabled': [field for field in fields if field not in settings.fields.all()]
            }
            return render(request, 'analytics/table_filter.html', context)
        else:
            return redirect(reverse('404'))

    def post(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        form = FormBuilder.objects.filter(id=form_id).first()
        if form:
            settings = TableFilterSettings.objects.get(
                form=form
            )

            checked_fields = self.request.POST
            settings.fields.clear()
            for key in checked_fields.keys():
                if key not in ['csrfmiddlewaretoken']:
                    print(key)
                    field = Field.objects.filter(
                        id=int(key.split('__')[1])).first()
                    if field and field not in settings.fields.all():
                        settings.fields.add(field.id)
                        settings.save()

            return redirect(reverse('table_data_filter_settings_view', args=['GET', form_id]))
        else:
            return redirect(reverse('404'))


class TableDataCalculationView(View):

    def get(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        form = FormBuilder.objects.filter(id=form_id).first()
        if form:
            settings = TableDisplaySettings.objects.get_or_create(
                form=form
            )
            context = {
                'settings': settings,
                'fields': Field.objects.filter(row__section__form=form).all()
            }
            return render(request, 'analytics/field_caculation.html', context)
        else:
            return redirect(reverse('404'))


class FieldAnalyticsView(View):

    def get(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        form = FormBuilder.objects.filter(id=form_id).first()
        if form:
            settings = TableDisplaySettings.objects.get_or_create(
                form=form
            )
            context = {
                'settings': settings
            }
            return render(request, 'analytics/field_analytics.html', context)
        else:
            return redirect(reverse('404'))


class ReportsView(View):

    def get_length(self, arguments, from_dt, to_dt):
        return len(FormFieldAnswers.objects.filter(**arguments, submission_ref__date__gte=from_dt, submission_ref__date__lte=to_dt))

    def get_progress_chart(self, arguments, from_dt, to_dt):
        from_date = datetime.strptime(from_dt, '%Y-%m-%d')
        to_date = datetime.strptime(to_dt, '%Y-%m-%d')

        months = [x for x in range(from_date.month, to_date.month+1)]

        monthly_data = FormFieldAnswers.objects.annotate(
            month=TruncMonth('submission_ref__date')
        ).values('month').annotate(total=Count('id')).filter(
            **arguments, submission_ref__date__gte=from_dt, submission_ref__date__lte=to_dt
        ).order_by('month')

        data = {
            'x_axis': [calendar.month_name[x] for x in months],
            'y_axis': []
        }
        for index, month in enumerate(months):
            for d in monthly_data:
                if d['month'].month == month:
                    data['y_axis'].append(d['total'])

            if len(data['y_axis']) < index + 1:
                data['y_axis'].append(0)
        return data

    def get(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form', None)
        field = self.kwargs.get('field_id', None)
        date_today = datetime.today()
        # req params
        from_date = self.request.GET.get(
            'from_date', datetime(date_today.year, 1, 1).strftime('%Y-%m-%d'))
        to_date = self.request.GET.get(
            'to_date', date_today.date().strftime('%Y-%m-%d'))

        form = FormBuilder.objects.filter(id=form_id).first()
        fields = Field.objects.filter(
            input_type='select',
            row__section__form=form_id,
            id=field
        )

        if not form or len(fields) < 1:
            return redirect('/404')
        context = {
            'from_date': from_date,
            'to_date': to_date,
            'chart_name': f'{fields[0].title} Chart',
            'chart_data': {
                'x_axis': [option.key for option in fields[0].options.all()],
                'y_axis': [
                    self.get_length({
                        "field": field,
                        "answer": option.value
                    },
                        from_dt=from_date,
                        to_dt=to_date
                    ) for option in fields[0].options.all()
                ]
            },
            'fields': [
                {
                    'field': field,
                    'options': [{
                        'color': random.choice(['info', 'success', 'primary', 'danger', 'warning']),
                        'count': (self.get_length({
                            "field": field,
                            "answer": option.value,
                        },
                            from_dt=from_date,
                            to_dt=to_date
                        )),
                        'progress_chart': self.get_progress_chart({
                            "field": field,
                            "answer": option.value,
                        },
                            from_dt=from_date,
                            to_dt=to_date
                        ),
                        'percentage': 0,
                        'option': option,
                    } for option in field.options.all()]
                } for field in fields
            ],
        }

        for field in context['fields']:

            for option in field['options']:

                option['comparisons'] = [
                    {
                        'Phrase': 'More by' if op['count'] < option['count'] else 'Less by',
                        'difference': option['count'] - op['count'] if op['count'] < option['count'] else op['count'] - option['count'],
                        'percentage': 100 - round(option['count'] / op['count'] if op['count'] > option['count'] else op['count'] / option['count'], 2)*100,
                        'name': op['option'].key,
                        'arrow': 'up' if op['count'] < option['count'] else 'down',
                        'color': 'success' if op['count'] < option['count'] else 'danger',
                    } for op in field['options'] if option != op and option['count'] != 0 and op['count'] != 0
                ]

        print(context)
        return render(request, 'analytics/reports.html', context=context)


class CSVDownloader(View):

    def get_answer_value(self, answer, field):
        if field.input_type != 'select':
            return answer.answer
        else:
            options = field.options.all()
            for op in options:
                if op.value == answer.answer:
                    return op.key

        return answer.answer

    def clean_data(self, value):
        if value != None:
            return value
        else:
            return "None"

    def get(self, request, *args, **kwargs):

        form_id = self.kwargs.get('id', None)
        from_date = self.request.GET.get(
            'from_date', f'{datetime.today().year-1}-01-01')
        to_date = self.request.GET.get(
            'to_date', f'{datetime.today().year-1}-12-30')

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

            form = FormBuilder.objects.filter(
                id=form_id).first()

            if form:
                settings, created = TableDisplaySettings.objects.get_or_create(
                    form=form
                )
                filters, created = TableFilterSettings.objects.get_or_create(
                    form=form
                )
                aligned_data = []
                fields = settings.fields.all()
                submissions = submissions_list.order_by('date')

                for submission in submissions:
                    answer_dict = {answer.field.title: self.get_answer_value(answer, answer.field) for answer in FormFieldAnswers.objects.filter(
                        submission_ref=submission).all()}

                    aligned_row = [answer_dict.get(
                        field.title, None) for field in fields]

                    aligned_data.append({
                        'submission': submission,
                        'answers': aligned_row
                    })

                print(aligned_data)

                response = HttpResponse(
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": 'attachment; filename="report.csv"'},
                )

                writer = csv.writer(response)
                writer.writerow(['Date']+[field.title for field in fields])
                for data in aligned_data:
                    print(data)
                    if data.get('answers') != None:
                        cleaned_data = [data['submission'].date]+[self.clean_data(
                            x) for x in data.get("answers")]
                        writer.writerow(cleaned_data)
                return response
            else:
                return redirect('/404')
