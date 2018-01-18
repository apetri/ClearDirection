from django.db import models, OperationalError

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

	#################################################

	def __str__(self):
		return "user: {0}, {1} {2}, {3}".format(self.username,self.first,self.last,self.isreal)

############
#Hit counts#
############

class Hit(models.Model):

	source =  models.CharField(max_length=40)
	target =  models.CharField(max_length=40)
	secret = models.CharField(max_length=20)
	valid = models.BooleanField(default=False)

	#################################################

	def __str__(self):
		return "{0}-->{1}".format(self.source,self.target)

class HitCount(models.Model):

	username = models.CharField(max_length=40)
	count = models.IntegerField(default=0)

	#################################################

	def __str__(self):
		return "user: {0}".format(self.username)