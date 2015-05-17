from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from .models import Stars

import requests
import os
import scipy, numpy

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
    
    [x,y,z] = sphere2cart(dist,ra1,dec1)
    
    coordinates_list = [(0, 0), (50, 50), (100, 100)]
    context = {'ra1':x, 'dec1':y, 'dist':z, 'ra2':ra2, 'dec2':dec2, 'tilt':tilt, "coordinates_list":coordinates_list} 
    return render(request, 'result.html', context)

def __get_database():
    all_stars = Stars.objects.all()
    
    star_list = []
    count = 0
    for star in all_stars:
        star_list.append([star.ra, star.dec, star.distance, star.absmag])
        count = count+1

    return star_list

def calc_view(ra1,dec1,dist,ra2,dec2,tilt,star_list):
    phi_view = 45
    
    [xshift,yshift,zshift] = sphere2cart(dist,ra1,dec1)     # calculate cartesian shift
    star_cart = [sphere2cart(x[2],x[0],x[1]) for x in star_list]    # calculate star cartesian from spherical
    star_cart = [[x[0]-xshift, x[1]-yshift, x[2]-zshift] for x in star_cart]   # perform cartesian shift
    
    star_cart = [scipy.transpose(zrotate(ra2)*scipy.array([[x[0]], [x[1]], [x[2]]])) for x in star_cart]    # Orientation Rotations
    star_cart = [scipy.transpose(yrotate(dec2)*scipy.array([[x[0]], [x[1]], [x[2]]])) for x in star_cart]
    star_cart = [scipy.transpose(xrotate(tilt)*scipy.array([[x[0]], [x[1]], [x[2]]])) for x in star_cart]
    
    star_sphere = [cart2sphere(x[0],x[1],x[2]) for x in star_cart]  # transform back to spherical
    
    star_disp = [];
    for ind in range(len(star_list)):
        if star_sphere[ind][2] > (90-phi_view):
            rdisp = (90-star_sphere[ind][2])/phi_view
            thetadisp = star_sphere[ind][1]
            xdisp = rdisp*scipy.cos(thetadisp)
            ydisp = rdisp*scipy.sin(thetadisp)
            bright = scipy.log10(-star_list[ind][3]/2.5)*scipy.power(star_list[ind][0],2)/scipy.power(star_sphere[ind][0],2)
            star_disp.append([xdisp, ydisp, bright])
    
    return star_disp
        
    
def xrotate(theta):
    return scipy.array([[1, 0, 0], [0, scipy.cos(theta), -scipy.sin(theta)], [0, scipy.sin(theta), scipy.cos(theta)]])

def yrotate(theta):
    return scipy.array([[scipy.cos(theta), 0, -scipy.sin(theta)], [0, 1, 0], [scipy.cos(theta), 0, scipy.sin(theta)]])    

def zrotate(theta):
    return scipy.array([[scipy.cos(theta), -scipy.sin(theta), 0], [scipy.sin(theta), scipy.cos(theta), 0], [0, 0, 1]])
    
def sphere2cart(r,theta,phi):
    x = r*scipy.cos(theta)*scipy.cos(phi)
    y = r*scipy.sin(theta)*scipy.cos(phi)
    z = r*scipy.sin(phi)
    return [x, y, z]

def cart2sphere(x,y,z):
    r = scipy.sqrt(scipy.power(x,2)+scipy.power(y,2)+scipy.power(z,2))
    phi = scipy.arcsin(z/r)
    theta = scipy.arctan2(y,x)
    return [r, theta, phi]

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
