#from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import redirect

def index(request):        
    return redirect("Gmapv3/")
