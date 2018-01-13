# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def welcome(request):
	context = {"title":"Welcome Clear Direction!","message":"This is a demonstration page"}
	return HttpResponse(render(request,"hello/hello_world.html",context))
