from django.db import models

# Create your models here.

##############
#Person table#
##############

class Person(models.Model):

	username = models.CharField(max_length=40)
	password = models.CharField(max_length=256)
	first = models.CharField(max_length=20)
	last = models.CharField(max_length=20)
	age = models.IntegerField(default=0)
	street_address = models.CharField(max_length=200)
	zipcode = models.CharField(max_length=5)
	city = models.CharField(max_length=20)
	email = models.CharField(max_length=50)
	secret = models.CharField(max_length=20)
	isreal = models.BooleanField(default=False)

############
#Hit counts#
############

class Hit(models.Model):

	source =  models.CharField(max_length=40)
	target =  models.CharField(max_length=40)
	secret = models.CharField(max_length=20)

class HitCount(models.Model):

	username = models.CharField(max_length=40)
	count = models.IntegerField(default=0)