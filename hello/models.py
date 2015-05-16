from django.db import models

# Create your models here.
'''
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)
'''
class StarData(models.Model):
    ra1 = models.FloatField()
    dec1 = models.FloatField()
    dist = models.FloatField()
    ra2 = models.FloatField()
    dec2 = models.FloatField()
