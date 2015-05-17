from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from .models import Stars

import requests
import os

# Create your views here.
def index(request):
    template = loader.get_template('stars.html')
    #context = RequestContext(request,{})
    #return HttpResponse(template.render(context))
    return render(request, 'stars.html', {})

def input(request):
    ra1 = request.POST.get('ra1')
    dec1 = request.POST.get('dec1')
    dist = request.POST.get('dist')
    ra2 = request.POST.get('ra2')
    dec2 = request.POST.get('dec2')    
    
    star = Stars.objects.get(starid=1)
    context = {'ra1':ra1, 'dec1':dec1, 'dist':dist, 'ra2':ra2, 'dec2':dec2, 'name':star.propername} 
    return render(request, 'result.html', context)

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
