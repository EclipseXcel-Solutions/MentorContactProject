from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from form.models import FormBuilder
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from form.models import FormSubmission
# Create your views here.


class IndexPage(View):

    @method_decorator(login_required)
    def get(self, request):
        return redirect(reverse('admin_dashboard'))


class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request):
        data = {
            'form_list': FormBuilder.objects.all(),
            'mentoring_session': len(FormSubmission.objects.all())
        }
        return render(request, 'analytics/dashboard.html', context=data)
