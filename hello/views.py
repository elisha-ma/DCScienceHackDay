from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from operator import itemgetter
from .models import Stars

import requests
import os
import scipy, numpy

# Create your views here.
def index(request):
    template = loader.get_template('stars.html')
    #context = RequestContext(request,{})
    #return HttpResponse(template.render(context))
    
    context = {"constellations" : sorted(__get_constellations())}
    return render(request, 'stars.html', context)

def input(request):
    ra1 = float(request.POST.get('ra1', 0)) * scipy.pi / 180
    dec1 = float(request.POST.get('dec1', 0)) * scipy.pi / 180
    dist = float(request.POST.get('dist', 0))
    ra2 = float(request.POST.get('ra2', 0)) * scipy.pi / 180
    dec2 = float(request.POST.get('dec2', 0)) * scipy.pi / 180
    tilt = float(request.POST.get('tilt', 0)) * scipy.pi / 180
    const = request.POST.get('constellation')

    star_list = __get_stars()
    stars_in_const = __get_stars_in_constellation(const)
    print stars_in_const
    
    # Get Image info for all stars within view
    star_disp = calc_view(ra1,dec1,dist,ra2,dec2,tilt,star_list, False)
    coordinates_list = adjust_for_image(star_disp, False)
    
    #Get image info for all stars in constellation
    const_disp = calc_view(ra1, dec1, dist, ra2, dec2, tilt, stars_in_const, True)
    const_coord_list = adjust_for_image(const_disp, True)
    
    #coordinates_list = [(0, 0), (50, 50), (100, 100)]
    #context = {'ra1':ra1, 'dec1':dec1, 'dist':dist, 'ra2':ra2, 'dec2':dec2, 'tilt':tilt, "coordinates_list":coordinates_list}
    coordinates_list = sorted(coordinates_list, key=itemgetter(2)) 
    context = {"coordinates_list":coordinates_list, "const_coordinates":const_coord_list}
    return render(request, 'result.html', context)

def __get_stars_in_constellation(const_filt):
    stars = Stars.objects.filter(constellation=const_filt)
    return [[star.ra, star.dec, star.distance, star.absmag] for star in stars]

def __get_stars():
    all_stars = Stars.objects.all()
    return [[star.ra, star.dec, star.distance, star.absmag] for star in all_stars]

def __get_constellations():
    all_stars = Stars.objects.all()
    return list(set([star.constellation for star in all_stars]))

def adjust_for_image(star_disp, in_const):
    visible_flux = .01
    visible_rgb = 10
    if (in_const):
        return [[x[0] * 256 + 256, 256 - x[1] * 256, int(scipy.maximum(scipy.minimum(x[2]/visible_flux*visible_rgb,255), 75)) ] for x in star_disp]

    return [[x[0] * 256 + 256, 256 - x[1] * 256, int(scipy.minimum(x[2]/visible_flux*visible_rgb,255)) ] for x in star_disp]

def calc_view(ra1,dec1,dist,ra2,dec2,tilt,star_list, in_const):
    phi_view = 60 * scipy.pi / 180
    
    [xshift,yshift,zshift] = sphere2cart(dist,ra1,dec1)     # calculate cartesian shift
    star_cart = [sphere2cart(x[2],x[0],x[1]) for x in star_list]    # calculate star cartesian from spherical
    star_cart = [[x[0]-xshift, x[1]-yshift, x[2]-zshift] for x in star_cart]   # perform cartesian shift
    star_cart = [scipy.transpose(scipy.matrix(x)) for x in star_cart]
    
    #star_cart = [scipy.array(scipy.transpose(zrotate(ra2)*scipy.transpose(scipy.matrix(x)))) for x in star_cart]
    #star_cart = [scipy.array(scipy.transpose(zrotate(ra2)*scipy.matrix([[x[0]], [x[1]], [x[2]]]))) for x in star_cart]  # Orientation Rotations
    star_cart = [zrotate(ra2)*x for x in star_cart]
    star_cart = [yrotate(dec2)*x for x in star_cart]
    star_cart = [xrotate(tilt)*x for x in star_cart]
    #star_cart = [yrotate(-scipy.pi/2)*x for x in star_cart]
    print star_cart
    
    star_sphere = [cart2sphere(x.item(0),x.item(1),x.item(2)) for x in star_cart]  # transform back to spherical
    print star_sphere
    
    star_disp = [];
    for ind in range(len(star_list)):
        phi = scipy.arcsin(star_cart[ind].item(0)/star_sphere[ind][0][0])
        print "PHI: " + phi
        if phi > (90 * scipy.pi / 180 - phi_view):
            rdisp = (90 * scipy.pi / 180 - phi)/phi_view
            thetadisp = scipy.arctan2(star_cart[ind][2],star_cart[ind][1])
            xdisp = rdisp*scipy.cos(thetadisp)
            ydisp = rdisp*scipy.sin(thetadisp)
            bright = scipy.power(10,star_list[ind][3]/-2.5)*scipy.power(star_list[ind][0],2)/scipy.power(star_sphere[ind][0],2)
        #    #print bright
            if bright>.01 or in_const:
                star_disp.append([xdisp, ydisp, bright])
        
        #if star_sphere[ind][2] > (90 * scipy.pi / 180 - phi_view):
        #    rdisp = (90 * scipy.pi / 180 - star_sphere[ind][2])/phi_view
        #    thetadisp = star_sphere[ind][1]
        #    xdisp = rdisp*scipy.cos(thetadisp)
        #    ydisp = rdisp*scipy.sin(thetadisp)
        #    bright = scipy.power(10,star_list[ind][3]/-2.5)*scipy.power(star_list[ind][0],2)/scipy.power(star_sphere[ind][0],2)
        #    #print bright
        #    if bright>.01 or in_const:
        #        star_disp.append([xdisp, ydisp, bright])
    
    return star_disp
        
    
def xrotate(theta):
    return scipy.matrix([[1, 0, 0], [0, scipy.cos(theta), -scipy.sin(theta)], [0, scipy.sin(theta), scipy.cos(theta)]])

def yrotate(theta):
    return scipy.matrix([[scipy.cos(theta), 0, -scipy.sin(theta)], [0, 1, 0], [scipy.sin(theta), 0, scipy.cos(theta)]])    

def zrotate(theta):
    return scipy.matrix([[scipy.cos(theta), -scipy.sin(theta), 0], [scipy.sin(theta), scipy.cos(theta), 0], [0, 0, 1]])
    
def sphere2cart(r,theta,phi):
    x = r*scipy.cos(theta)*scipy.cos(phi)
    y = r*scipy.sin(theta)*scipy.cos(phi)
    z = r*scipy.sin(phi)
    return [x, y, z]

def cart2sphere(x,y,z):
    r = scipy.real(scipy.sqrt(scipy.power(x,2)+scipy.power(y,2)+scipy.power(z,2)))
    phi = scipy.arcsin(z/r)
    theta = scipy.arctan2(y,x)
    return [r, theta, phi]

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
