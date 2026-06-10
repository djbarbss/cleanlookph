from django.http import HttpResponse 
from django.views import View 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_view(request):
    return render(request, "app/home.html")