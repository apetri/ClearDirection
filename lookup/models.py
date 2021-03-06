import datetime
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


#########
#Queries#
#########

class Query(models.Model):

	qdate = models.DateTimeField("date submitted",default=datetime.datetime(2000,1,1))
	query = models.CharField(max_length=200)
	nrecords = models.IntegerField(default=0)