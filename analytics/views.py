from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.


class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'analytics/dashboard.html', context={})
