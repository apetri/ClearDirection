# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def welcome(request):
	context = {"title":"Welcome Clear Direction!","message":"May the force be with you"}
	return HttpResponse(render(request,"hello/message.html",context))
