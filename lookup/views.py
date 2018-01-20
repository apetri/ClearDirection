#system
import hashlib
import urllib

#django
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.urls import reverse
from django.utils import timezone

from .models import Person,Hit,HitCount,Query,OperationalError


#Password hashing
def hashpwd(pwd):
	return hashlib.sha256(bytes(pwd.encode("utf-8"))).hexdigest()

##########################
# Create your views here #
##########################

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
	msg_keys = {"section":"Too bad!","result":"Database query is currently disabled."}
	return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))

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

		#No wildcards allowed
		if "*" in query:
			msg_keys = {"section":"Hey!","result":"No wildcards allowed in query"}
			return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))

		#Log the query
		lquery = query.split("AND password")[0].split("WHERE")[-1]
		lquery = "SELECT * FROM lookup_person WHERE" + lquery
		if "AND password" in query:
			lquery += " AND password='******'"

		qlog = Query(qdate=timezone.now(),query=lquery)	

		###################################################################

		#Query the database 
		try:
			people = list(Person.objects.raw(query))
			qlog.nrecords = len(people)
		except OperationalError:
			msg_keys = {"section":"Too bad!","result":"Invalid SQL query: "+query}
			return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))
		finally:
			qlog.save()

		if not len(people):
			msg_keys = {"section":"Too bad!","result":"No matching records found."}
			return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))
		
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
	msg_keys = {"section":"Too bad!","result":"Insertion into database is currently disabled."}
	return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))

def insertPerson(request):

	#Information to fill
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

	if request.method=="GET":

		##############################
		#Return user insert data form#
		##############################
		
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

		#Parse POST request field by field
		rec = { f[0]:request.POST[f[0]] for f in formfields }
		
		#Check valid insertion
		musthave = ["username","password","first","last","secret"]
		invalid = [ len(rec[f])==0 for f in musthave ]
		if any(invalid):
			msg_keys = { "section":"Too bad!","result":"One between {0} was empty.".format("-".join(musthave)) }
			return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))


		rec["password"] = hashpwd(rec["password"])
		rec["isreal"] = True

		try:

			#If username exists, update it
			person = Person.objects.get(username=rec["username"])
			for f in rec:
				setattr(person,f,rec[f])

			hcount = None

		except Person.DoesNotExist:

			#If it does not exist, create a new one
			person = Person(**rec)
			hcount = HitCount(username=rec["username"])

		#Commit
		person.save()
		if hcount is not None:
			hcount.save()

		#Log success
		msg_keys = {"section":"Congratulations!","result":"Record insertion successful."}
		return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))



#####################
#Secret word logging#
#####################

def logSecretDoNothing(request):
	msg_keys = {"section":"Too bad!","result":"Secret guessing is currently disabled."}
	return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))

def logSecret(request):

	#Fields in the form
	formfields = [  ["source","text"],
					["target","text"],
					["secret","password"],
	]
	
	if request.method=="GET":

		###############################
		#Return user guess secret form#
		###############################
		
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

		#Get values from the request
		source = request.POST["source"]
		target = request.POST["target"]
		secret = request.POST["secret"]

		if len(Person.objects.filter(username=source)):

			#Cannot guess your own secret
			if source==target:
				msg_keys = {"section":"Hey!","result":"You cannot guess your own secret."}
				return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))

			#Construct the attempted guess
			hit_try = Hit(source=source,target=target,secret=secret)

			#Check if you scored a hit
			try:
				hit = Person.objects.get(username=target,secret=secret)
				hit_try.valid = True
				
				if not hit.isreal:
					msg_keys = {"section":"Hey!","result":"You have to guess real people's secrets."}
					return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))	

			except Person.DoesNotExist:
				hit_try.valid = False
				hit_try.save()
				msg_keys = {"section":"Too bad!","result":"Your guess was incorrect."}
				return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))

			#Check that you did not score it before
			try:
				Hit.objects.get(source=source,target=target,secret=secret,valid=True)
				msg_keys = {"section":"Hey!","result":"You already guessed {0}'s secret.".format(target)}
				return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))
			
			except Hit.DoesNotExist:
				hit_try.save()
				count = HitCount.objects.get(username=source)
				count.count += 1
				count.save()
				msg_keys = {"section":"Congratulations!","result":"You guessed {0}'s secret.".format(target)}
				return HttpResponseRedirect(reverse("lookup:logsubmission",kwargs=msg_keys))


		else:
			msg_keys = {"section":"Too bad!","result":"username {0} does not exist".format(source)}
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
