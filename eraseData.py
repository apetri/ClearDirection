#!/usr/bin/env python

#system
import os

#django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cleardirection.settings")
django.setup()

from lookup.models import Person


###################################
#Random components of the database#
###################################

def main():
	print("[+] Erasing data.")
	Person.objects.all().delete()

if __name__=="__main__":
	main()