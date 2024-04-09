from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from form.models import FormBuilder
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from form.models import FormSubmission, FiledResponses
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncDay
import calendar
# Create your views here.


class IndexPage(View):

    @method_decorator(login_required)
    def get(self, request):
        return redirect(reverse('admin_dashboard'))


class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request):
        year = self.request.GET.get('year', 2023)
        daily_submissions = (
            FormSubmission.objects
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(submissions_count=Count('id'))
            .order_by('day')
        )
        weekly_submissions = (
            FormSubmission.objects
            .annotate(week=TruncWeek('date'))
            .values('week')
            .annotate(submissions_count=Count('id'))
            .order_by('week')
        )
        monthly_submissions = (
            FormSubmission.objects
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(submissions_count=Count('id'))
            .order_by('month')
        )

        data = {
            'form_list': FormBuilder.objects.all(),
            'mentoring_session':  len(FiledResponses.objects.values(
                'submission_ref').distinct()),
            'total_users': len(User.objects.all()),
            'subjects': '',
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
                }
            }

        }
        print(data)
        return render(request, 'analytics/dashboard.html', context=data)
