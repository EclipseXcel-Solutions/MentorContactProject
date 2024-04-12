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
            FormSubmission.objects.filter(date__year=year)
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
        field = Field.objects.filter(id=self.kwargs.get('id')).first()
        choices = field.choices
        print(choices)
        context = {
            'analytics': AnalyticsFieldsSettings.objects.filter(form__id=1, status=True)
        }

        for choice in choices:
            context[choice[0]] = [field.array_answer for field in FiledResponses.objects.filter(
                field=field)]

        print(context)
        return render(request, 'analytics/fieldStat.html', context)
