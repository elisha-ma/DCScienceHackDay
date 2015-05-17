from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from .models import Stars

import requests
import os
import scipy

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
    tilt = request.POST.get('tilt')
    
    #star = Stars.objects.get(starid=1)
    star_list = __get_database()
    
    coordinates_list = [(0, 0), (50, 50), (100, 100)]
    context = {'ra1':len(star_list), 'dec1':dec1, 'dist':dist, 'ra2':ra2, 'dec2':dec2, 'tilt':tilt, "coordinates_list":coordinates_list} 
    return render(request, 'result.html', context)

def __get_database():
    all_stars = Stars.objects.all()
    
    star_list = []
    count = 0
    for star in all_stars:
        star_list.append([star.ra, star.dec, star.distance, star.absmag])
        count = count+1
        if count == 10:
            break

    return star_list

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
