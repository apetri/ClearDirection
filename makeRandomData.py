#!/usr/bin/env python

#system
import os
import hashlib
import random

#3rd party
from faker import Faker

#django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cleardirection.settings")
django.setup()

from lookup.models import Person


###################################
#Random components of the database#
###################################

def hashpwd(pwd):
	return hashlib.sha256(bytes(pwd.encode("utf-8"))).hexdigest()

def main():
	
	fake = Faker()
	for n in range(100):

		#Generate fake data for person N
		first = fake.first_name()
		last = fake.last_name()
		
		rec = {
			"first" : first,
			"last" : last,
			"username" : first.lower() + last.lower(),
			"password" : hashpwd(last.upper()),
			"age" : random.randint(18,80),
			"street_address" : fake.street_address(),
			"city" : fake.city(),
			"zipcode" : fake.zipcode(),
			"email" : first.lower() + last.lower() + "@" + fake.domain_name(),
			"secret" : fake.password(),
			"isreal" : False
		}

		#Commit person N to database
		person = Person(**rec)
		person.save()
		print("[+] Committed person {0} to database".format(person.id))

if __name__=="__main__":
	main()