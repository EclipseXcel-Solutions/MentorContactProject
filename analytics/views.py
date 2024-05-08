from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from form.models import FormBuilder
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from form.models import FormSubmission, FiledResponses, AnalyticsFieldsSettings, Field, FiledResponses
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncDay, TruncYear, TruncQuarter
import calendar
from django.db.models import Count
from collections import defaultdict
import json


# Create your views here.


class IndexPage(View):

    @method_decorator(login_required)
    def get(self, request):
        return redirect(reverse('admin_dashboard'))


class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request):
        year = self.request.GET.get('year', datetime.now().year)
        month = self.request.GET.get('month', datetime.now().month)

        yearly_submissions = (
            FormSubmission.objects
            .annotate(year=TruncYear('date'))
            .values('year')
            .annotate(submissions_count=Count('id'))
            .order_by('year')
        )
        daily_submissions = (
            FormSubmission.objects.filter(
                date__year=year, date__month=month)
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(submissions_count=Count('id'))
            .order_by('day')
        )
        weekly_submissions = (
            FormSubmission.objects.filter(
                date__year=year, date__month=month)
            .annotate(week=TruncWeek('date'))
            .values('week')
            .annotate(submissions_count=Count('id'))
            .order_by('week')
        )
        monthly_submissions = (
            FormSubmission.objects.filter(
                date__year=year)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(submissions_count=Count('id'))
            .order_by('month')
        )
        quarterly_submissions = (
            FormSubmission.objects.filter(
                date__year=year)
            .annotate(quarter=TruncQuarter('date'))
            .values('quarter')
            .annotate(submissions_count=Count('id'))
            .order_by('quarter')
        )

        data = {
            'form_list': FormBuilder.objects.all(),
            'mentoring_session':  len(FiledResponses.objects.values(
                'submission_ref').distinct()),
            'total_users': len(User.objects.all()),
            'years': FormSubmission.objects.annotate(
                year=TruncYear('date')).values('year').distinct('year'),
            'months': [x for x in range(1, 13)],
            'weeks': [x for x in range(1, 5)],
            'subjects': '',
            'analytics': AnalyticsFieldsSettings.objects.filter(form__id=1, status=True),
            'submissions': {
                'weekly': {
                    'y_axis': [sub['week'].isocalendar().week for sub in weekly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in weekly_submissions]
                },
                'monthly': {
                    'y_axis': [sub['month'].month for sub in monthly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in monthly_submissions]
                },
                'daily': {
                    'y_axis': [sub['day'].day for sub in daily_submissions],
                    'x_axis': [sub['submissions_count'] for sub in daily_submissions]
                },
                'quarterly': {
                    'y_axis': [sub['quarter'].month for sub in quarterly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in quarterly_submissions]
                },
                'yearly': {
                    'y_axis': [sub['year'].year for sub in yearly_submissions],
                    'x_axis': [sub['submissions_count'] for sub in yearly_submissions]
                }

            }

        }
        return render(request, 'analytics/dashboard.html', context=data)


class FieldAnalytics(View):

    def get(self, request, *args, **kwargs):
        year = self.request.GET.get('year', datetime.now().year)
        month = self.request.GET.get('month', datetime.now().month)
        field = Field.objects.filter(id=self.kwargs.get(
            'id')).first()
        total_responses = FiledResponses.objects.filter(
            field=field, submission_ref__date__year=year, submission_ref__date__month=month).values('array_answer').annotate(count=Count('array_answer'))

        daily_submissions = [FiledResponses.objects.filter(
            field=field,
            array_answer=x['array_answer'],
            submission_ref__date__year=year, submission_ref__date__month=month)
            .annotate(day=TruncDay('submission_ref__date'))
            .values('day', 'array_answer')
            .annotate(count=Count('array_answer'))
            .order_by('day') for x in total_responses]
        monthly_submissions = [FiledResponses.objects.filter(
            field=field,
            array_answer=x['array_answer'],
            submission_ref__date__year=year, submission_ref__date__month=month)
            .annotate(month=TruncMonth('submission_ref__date'))
            .values('month', 'array_answer')
            .annotate(count=Count('array_answer'))
            .order_by('month') for x in total_responses]
        weekly_submissions = [FiledResponses.objects.filter(
            field=field,
            array_answer=x['array_answer'],
            submission_ref__date__year=year, submission_ref__date__month=month)
            .annotate(week=TruncWeek('submission_ref__date'))
            .values('week', 'array_answer',)
            .annotate(count=Count('array_answer'))
            .order_by('week') for x in total_responses]

        yearly_submissions = [FiledResponses.objects.filter(
            field=field,
            array_answer=x['array_answer'])
            .annotate(year=TruncWeek('submission_ref__date'))
            .values('year', 'array_answer')
            .annotate(count=Count('array_answer'))
            .order_by('year') for x in total_responses]

        context = {
            'analytics': AnalyticsFieldsSettings.objects.filter(form__id=1, status=True),
            'field': field,
            'total_responses': total_responses,
            'total': 0,
            'line_chart': [],
            'submissions': json.dumps({
                'daily': [
                    {
                        'x': [sub['day'].day for sub in x],
                        'y': [sub['count'] for sub in x],
                        'name': x[0]['array_answer'],
                    } for x in daily_submissions
                ],
                'monthly': [
                    {
                        'x': [sub['month'].month for sub in x],
                        'y': [sub['count'] for sub in x],
                        'name': x[0]['array_answer'],
                    } for x in monthly_submissions
                ],
                'weekly': [
                    {
                        'x': [sub['week'].isocalendar().week for sub in x],
                        'y': [sub['count'] for sub in x],
                        'name': x[0]['array_answer'],

                    } for x in weekly_submissions
                ],
                'yearly': [
                    {
                        'x': [sub['year'].year for sub in x],
                        'y': [sub['count'] for sub in x],
                        'name': x[0]['array_answer'],
                    } for x in yearly_submissions
                ],
            }),
            'years': FormSubmission.objects.annotate(
                year=TruncYear('date')).values('year').distinct('year'),
            'months': [x for x in range(1, 13)],
            'weeks': [x for x in range(1, 5)],
        }
        print(context)

        return render(request, 'analytics/fieldStat.html', context)
