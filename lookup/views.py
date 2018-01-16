#system
import hashlib
import urllib

#django
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from .models import Person,Hit,HitCount,OperationalError

# Create your views here.

#Password hashing
def hashpwd(pwd):
	return hashlib.sha256(bytes(pwd.encode("utf-8"))).hexdigest()

#Sample table
def sampleTable(request):

	fields = ["username","first","last","age","street_address","city","zipcode","email","secret","isreal"]
	table = [ [getattr(p,c) for c in fields] for p in Person.objects.all() ]
	context = {"pagetitle":"Sample table","title":"Sample table","columns":fields,"table":table}

	return HttpResponse(render(request,"lookup/table.html",context))

#Sample form
def sampleForm(request):

	formfields = [["username","text"],["password","password"]]
	context = {
		"pagetitle":"Sample form",
		"title":"Sample form",
		"method":"GET",
		"action":"lookup/form",
		"formfields":formfields,
		"buttonname":"SUBMIT"}

	return HttpResponse(render(request,"lookup/form.html",context))

##################
#Database queries#
##################

def queryPerson(request):

	if request.method!="GET":
		return HttpResponseBadRequest("Bad request")

	if not request.GET:

		########################
		#Return user query form#
		########################

		formfields = [["username","text"],["password","password"]]
		context = {
			"pagetitle":"Query user",
			"title":"Query user information",
			"method":"GET",
			"action":"lookup/query",
			"formfields":formfields,
			"buttonname":"Send Query"
		}

		return HttpResponse(render(request,"lookup/form.html",context))

	else:

		####################
		#Query the database#
		####################

		fields = ["username","first","last","age","street_address","city","zipcode","email","secret","isreal"]

		#Hash password
		username = request.GET["username"]
		password = hashpwd(request.GET["password"])

		#Query
		try:
			person = Person.objects.get(username=username,password=password)
		except Person.DoesNotExist:
			return HttpResponseNotFound("No records found.")
		
		table = [ [getattr(person,c) for c in fields] ]
		context = {
			"pagetitle":"Query results",
			"title":"Query results",
			"columns":fields,
			"table":table
		}

		return HttpResponse(render(request,"lookup/table.html",context))



##################
#Record insertion#
##################

def insertPerson(request):
	pass

#####################
#Secret word logging#
#####################

def logSecret(request):
	pass
