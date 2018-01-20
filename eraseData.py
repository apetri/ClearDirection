#!/usr/bin/env python

#system
import os
import argparse

#django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cleardirection.settings")
django.setup()

from lookup.models import Person,Hit,HitCount,Query


###################################
#Random components of the database#
###################################

def main():

	#Command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("--person",action="store_true",default=False,help="Erase Person table")
	parser.add_argument("--hits",action="store_true",default=False,help="Erase Hit table")
	parser.add_argument("--count",action="store_true",default=False,help="Erase HitCount table")
	parser.add_argument("--query",action="store_true",default=False,help="Erase Query table")

	cmd_args = parser.parse_args()

	#Erase tables
	if cmd_args.person:
		print("[+] Erasing Person.")
		Person.objects.all().delete()

	if cmd_args.hits:
		print("[+] Erasing Hit.")
		Hit.objects.all().delete()

	if cmd_args.count:
		print("[+] Erasing HitCount.")
		HitCount.objects.all().delete()

	if cmd_args.query:
		print("[+] Erasing Query.")
		Query.objects.all().delete()


if __name__=="__main__":
	main()