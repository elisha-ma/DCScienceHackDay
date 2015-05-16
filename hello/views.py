from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from .models import StarData

import requests
import os

# Create your views here.
def index(request):
    template = loader.get_template('stars.html')
    context = RequestContext(request,{})
    return HttpResponse(template.render(context))

def input(request):
    ra1 = request.POST(['ra1'])
    dec1 = request.POST(['dec1'])
    dist = request.POST(['dist'])
    ra2 = request.POST(['ra2'])
    dec2 = request.POST(['dec2'])    
  
    return HttpResponseRedirect(reverse('hello:result', args=(ra1, dec1, dist, ra2, dec2,)))

def result(request, ra1, dec1, dist, ra2, dec2):
    return render(request, 'hello/result.html', {'ra1':ra1, 'dec1':dec1, 'dist':dist, 'ra2':ra2, 'dec2':dec2})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
