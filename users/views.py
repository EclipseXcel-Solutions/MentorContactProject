from django.shortcuts import render , redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login
# Create your views here.

class Login(View):

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request=request , template_name='users/login.html',context=context)

    def post(self,request,*args,**kwargs):

        form_data = request.POST 
        username = form_data.get('username','')
        password = form_data.get('password','')
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            return redirect(reverse('login_view'))
        
        if user:
            if authenticate(request=request ,username = username,password = password):
                login(request=request , user = user)
                return redirect('admin_dashboard')
            else:
                return redirect('login_view')