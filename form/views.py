from django.shortcuts import render
from django.views import View 
# Create your views here.

class FormBuilder(View):

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request=request , template_name='form/builder.html' , context=context)