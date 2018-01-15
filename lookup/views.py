#django
from django.shortcuts import render
from django.http import HttpResponse
from .models import Person

# Create your views here.
def sampletable(request):

	fields = ["username","first","last","age","street_address","city","zipcode","email","secret","isreal"]
	table = [ [getattr(p,c) for c in fields] for p in Person.objects.all() ]
	context = {"title":"Sample table","columns":fields,"table":table}

	return HttpResponse(render(request,"lookup/table.html",context))
