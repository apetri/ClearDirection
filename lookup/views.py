#system
import hashlib
import urllib

#django
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.urls import reverse

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

	return render(request,"lookup/table.html",context)

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

	return render(request,"lookup/form.html",context)

##################
#Database queries#
##################

def queryPersonDoNothing(request):
	raise Http404("Method inactive.")

def queryPerson(request):

	if request.method!="GET":
		raise Http404("Bad request")

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

		return render(request,"lookup/form.html",context)

	else:

		####################
		#Query the database#
		####################

		fields = ["username","first","last","age","street_address","city","zipcode","email","secret","isreal"]

		#Hash password
		username = request.GET["username"]
		password = hashpwd(request.GET["password"])

		#Build query, making sure it permits SQL injection
		query = "SELECT id,{0} FROM lookup_person WHERE username='{1}' AND password='{2}'"
		query = query.format(",".join(fields),urllib.parse.unquote_plus(username),password)
		query = query.split(";")[0]

		###################################################################

		#Query the database 
		try:
			people = list(Person.objects.raw(query))
		except OperationalError:
			raise Http404("Query error.")

		if not len(people):
			raise Http404("No records found.")
		
		table = [ [getattr(p,c) for c in fields] for p in people ]
		context = {
			"pagetitle":"Query results",
			"title":"Query results",
			"columns":fields,
			"table":table
		}

		return render(request,"lookup/table.html",context)



##################
#Record insertion#
##################

def insertPersonDoNothing(request):
	raise Http404("Method inactive.")

def insertPerson(request):

	if request.method=="GET":

		##############################
		#Return user insert data form#
		##############################

		formfields = [  ["username","text"],
						["password","password"],
						["first","text"],
						["last","text"],
						["age","number"],
						["street_address","text"],
						["zipcode","text"],
						["city","text"],
						["email","text"],
						["secret","password"],
		]
		
		context = {
			"pagetitle":"Insert user data",
			"title":"Insert user data",
			"method":"POST",
			"action":"lookup/insert",
			"formfields":formfields,
			"buttonname":"Submit Data"
		}

		return render(request,"lookup/form.html",context)

	else:

		if request.method!="POST":
			raise Http404("Bad request")

		#########################################
		#Parse the request and insert the record#
		#########################################

		msg_keys = {"section":"Congratulations!","result":"Data insertion successful."}
		return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))



#####################
#Secret word logging#
#####################

def logSecretDoNothing(request):
	raise Http404("Method inactive.")

def logSecret(request):
	
	if request.method=="GET":

		###############################
		#Return user guess secret form#
		###############################

		formfields = [  ["source","text"],
						["target","text"],
						["secret","text"],
		]
		
		context = {
			"pagetitle":"Guess secret word",
			"title":"Guess secret word",
			"method":"POST",
			"action":"lookup/log",
			"formfields":formfields,
			"buttonname":"Submit Secret Word"
		}

		return render(request,"lookup/form.html",context)

	else:

		if request.method!="POST":
			raise Http404("Bad request")

		##############################################
		#Check if source guessed target's secret word#
		##############################################

		msg_keys = {"section":"Congratulations!","result":"You guessed Puccio's secret."}
		return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))


#####################
#Generic message log#
#####################

def logSubmission(request,section,result):
	
	context = {
		"title" : urllib.parse.unquote_plus(section),
		"message" : urllib.parse.unquote_plus(result)
	}

	return render(request,"hello/message.html",context)
