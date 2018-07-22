import os
import re
import requests
import json
from urllib2 import urlparse
from collections import deque

import bs4
from bs4 import BeautifulSoup

from editDistance import DistanceCalculator

LARGE = 1000000
webExtensions = set(("htm","html","jsp"))
allowDomains = [".com",".org",".edu",".net",".info",".nyc"]
excludeDomains = ["facebook.com","twitter.com","blogspot.com"]

#Print in color
red = lambda s : '\033[31m' + s + '\033[39m'
green = lambda s : '\033[32m' + s + '\033[39m'
yellow = lambda s : '\033[33m' + s + '\033[39m'

########################################################
#Find website of high school from the DOE central pages#
########################################################

#Check if website has the right domain
def checkDomain(url,domains):
	return sum([d in url for d in domains])

#Find the link to the school website
def findSchoolWebsite(base):
	
	#Download page
	response = requests.get(base)

	#Find weblinks
	soup = BeautifulSoup(response.text,"html.parser")
	links = soup.find_all("a")

	#Filter for links to external websites which are typed in the page
	links_web = filter(lambda l:"href" in l.attrs and l.attrs["href"].startswith("http") and l.contents,links)
	urls = set()

	for link in links_web:
		if checkDomain(link.text,allowDomains):
			if not checkDomain(link.attrs["href"],excludeDomains): 
				urls.add(link.attrs["href"].rstrip("/"))

	#Return
	return urls


#Spot sneaky redirects
def findRedirect(page):

	#Download the page and build the soup
	try:
		response = requests.get(page)
	except:
		return page

	soup = BeautifulSoup(response.text,"html.parser")

	#Filter meta data, look for http-equiv
	meta = soup.find_all("meta")
	redirect = filter(lambda l:"http-equiv" in l.attrs and l.attrs["http-equiv"]=="refresh",meta)

	#Find redirect url
	if len(redirect)==0:
		print("[-] No redirects found for: {0}".format(red(page)))
		return page
	
	elif len(redirect)==1:
		pos = redirect[0].attrs["content"].find("http")
		redirectUrl = redirect[0].attrs["content"][pos:].rstrip("/")
		print("[+] Found redirect: {0}-->{1}".format(red(page),green(redirectUrl)))
		return redirectUrl

	else:
		print("[-] Multiple redirects found for: {0}, doing nothing".format(red(page)))
		return page

#Spot javascript rendering
def findJavascript(page):

	#Download the page
	try:
		response = requests.get(page)
	except:
		return "NO PAGE"

	#Look for pattern
	if "var publicModel" in response.text:
		print("[+] Found WIX Javascript rendering for: {0}".format(green(page)))
		return "WIX"
	else:
		return "NO"

##################################################
#Scrape email addresses from the school home page#
##################################################

#Scrape a website for email addresses
def scrapeEmailsHTML(homePage,maxDepth=1,strict=True):

	##############################################################
	#Split homepage url into scheme, netloc, path; find base path#
	##############################################################

	homeParts = urlparse.urlparse(homePage)
	homeScheme = homeParts.scheme
	homeNetloc = homeParts.netloc

	if "." in homeParts.path:
		homeBase = os.path.dirname(homeParts.path)
	else:
		homeBase = homeParts.path

	#Log
	print("[+] netloc: {0}, homeBase: {1}".format(green(homeNetloc),green(homeBase)))

	###############################################
	#Perform breadth first search of homeBase path#
	###############################################

	#Data structures for pages to visit, visited pages, email addresses found, search depth
	pages = deque([homePage])
	depth = { homePage:0 }
	processed = set()
	emails = set()

	#Proceed with the search
	while len(pages):

		#Parse content of the current page
		url = pages.popleft()

		#If already processed, skip (takes care of duplicate links)
		if url in processed:
			continue

		#If exceeds maximum depth, skip
		if depth[url]>maxDepth:
			continue

		#Process url
		processed.add(url)
		print("[*] Processing url: {0} (depth={1})".format(yellow(url.encode("utf-8")),depth[url]))

		#Download the page, skip if error
		try:
			response = requests.get(url)
		except: 
			continue

		#Parse all emails from the page
		new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",response.text,re.I))
		if new_emails:
			print(green("[+] Found {0} email addresses in page".format(len(new_emails))))
		
		emails.update(new_emails)

		####################
		#Find all sub-pages#
		####################

		#Create a soup object
		soup = BeautifulSoup(response.text,"html.parser")

		#Find all relative links
		for link in soup.find_all("a"):

			if "href" in link.attrs:

				#Parse the found url
				subUrlParts = urlparse.urlparse(link.attrs["href"])
				subUrlPath = subUrlParts.path
				subUrlNetloc = subUrlParts.netloc

				#Condition for being a subordinate url
				subCond = subUrlNetloc in ["",homeNetloc]
				if strict:
					subCond = subCond and (homeBase in subUrlPath)				

				#Check if this a subordinate url
				if subCond:

					#Skip if extension is not an acceptable web extension
					if ("." not in subUrlPath) or (subUrlPath.split(".")[-1] in webExtensions):
						
						#Build full url
						if not subUrlNetloc:
							subUrlabsolute = homeScheme + "://" + homeNetloc + link.attrs["href"]
						else:
							subUrlabsolute = link.attrs["href"]
						
						#Check if already processed, if not add to deque
						if subUrlabsolute not in processed:
							pages.append(subUrlabsolute)

							#Update depth
							if subUrlabsolute not in depth:
								depth[subUrlabsolute] = depth[url] + 1

	#Log progress
	print("\n[+] Found {0} email addresses in total\n".format(len(emails)))

	#Return
	return emails,len(emails)


#WIX webpage scraper
def scrapeEmailsWIX(homePage,maxDepth=1,strict=True):

	#Return this on failure
	fail = list(),0

	#Download homepage, look for var publicModel
	try:
		print("[*] Scraping WIX webpage: {0}".format(yellow(homePage.encode("utf-8"))))
		response = requests.get(homePage)
		soup = BeautifulSoup(response.text,"html.parser")
	except:
		print("[-] No response\n")
		return fail

	#Find relevant javascript tag
	script = filter(lambda s:"var publicModel" in s.text,soup.find_all("script"))
	if not script:
		print("[-] This is not a WIX rendered webpage.\n")
		return fail

	#Fild the location of the publicModel tree
	lines = script[0].text.split("\n")
	publicModel = filter(lambda l:"var publicModel" in l,lines)[0]
	pos = publicModel.find("=")

	#Parse json into a tree
	try:
		tree = json.loads(publicModel[pos+1:].rstrip(";"))
	except:
		print("[-] Error parsing var publicModel JSON tree on: {0}\n".format(red(homePage.encode("utf-8"))))
		return fail

	#Look for subordinated pages
	try:
		pages_json = [ pg["pageJsonFileName"] for pg in tree["pageList"]["pages"] ]
		print("[+] Found {0} static WIX page references on: {1}\n".format(len(pages_json),green(homePage.encode("utf-8"))))
	except KeyError:
		print("[-] No 'pageJsonFileName' key in tree, skipping")
		return fail

	#Download each of them from https://static.wixstatic.com/sites
	emails = set()
	for pg in pages_json:

		#Request
		wix_page = "https://static.wixstatic.com/sites/{0}.z".format(pg)

		try:
			print("[*] Requesting WIX static url: {0}".format(yellow(wix_page.encode("utf-8"))))
			wix_response = requests.get(wix_page)
		except:
			continue

		#Find emails in the json tree, add to the already found ones
		new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",wix_response.text,re.I))
		print("[+] Found {0} email addresses on page".format(len(new_emails)))
		emails.update(new_emails)

	#Return
	print("\n[+] Found {0} email addresses in total\n".format(len(emails)))
	return emails,len(emails)

###################################################################################################
###################################################################################################

#############################
#Approximate string matching#
#############################

#Find the email address that is most likely to match the person's name
def matchEmail(emails,person):

	#Initialize
	email = None
	distance = LARGE

	print("[*] Looking up email address for: {0}".format(yellow(person)))

	#Cycle over emails and calculate edit distance
	for eml in emails:
		dc = DistanceCalculator()
		d = dc.editDistance(eml.split("@")[0],person)
		if d<distance:
			distance = d
			email = eml

	#Return email address
	print("[+] Best match: {0}\n".format(green(email)))
	return email

###################################################################################################
###################################################################################################

######################################
#DataFrame methods: iterate over rows#
######################################

#Look in the schools DataFrame for the school coordinates, find the websites
def findWebsiteInRow(row):

	#Build base url
	base = "http://schools.nyc.gov/SchoolPortals/{0:02d}/{1}/default.htm".format(row.GeographicalDistrictCode,row.LocationCode)
	print("[*] Looking for school website in: {0}".format(base))

	#Find school websites (they are usually typed)
	urls = findSchoolWebsite(base)
	
	#Return
	if not urls:
		print("[-] No websites found for '{0}', falling back on: {1}".format(red(row.LocationName),green(base)))
		return base,0
	elif len(urls)==1:
		website = urls.pop()
		print("[+] Found unique website for '{0}': {1}".format(yellow(row.LocationName),green(website)))
		return website,1
	else:
		print("[-] Multiple websites found: {0}, cannot decide.".format(red(",".join(urls))))
		return None,len(urls)


#Correct for redirects in row
def findRedirectInRow(row):

	#If the website is the DOE one, do nothing
	if row.nWebsites!=1:
		return row.SchoolWebsite
	else:
		return findRedirect(row.SchoolWebsite)


#Find javascripts in row
def findJavascriptInRow(row):

	if row.nWebsites!=1:
		return "NOT AVAILABLE"
	else:
		return findJavascript(row.SchoolWebsite)


#Look in the schools DataFrame for the principal's email address
def findEmailInRow(row,maxDepth=1,strict=True,scraper=None):

	#If no website, skip
	if not row.SchoolWebsite:
		return None,0,"NO WEBSITE" 
	
	#Scrape emails
	emails,num_emails = scraper(row.SchoolWebsite,maxDepth=maxDepth,strict=strict)

	#Best match using edit distance
	if num_emails:

		match = matchEmail(emails,row.PrincipalName)
		parts = row.PrincipalName.split(" ")
		pfirst,plast = parts[0],parts[-1]

		#Check if email starts by first letter of first,last name
		if match[0].lower()==pfirst[0].lower():
			return match,num_emails,"FIRST MATCH"
		elif match[0].lower()==plast[0]:
			return match,num_emails,"LAST MATCH"
		else:
			return match,num_emails,"LIKELY WRONG"

	else:
		return None,0,"NOT FOUND"


#Check if this is the another person's email (super, etc...)
def checkIfOther(row,field="Superintendent"):

	#Check if we have super name
	if row["field"]!=row["field"]:
		return row.EmailStatus

	#Calculate distance difference
	user = row.PrincipalEmail.split("@")[0]
	dc = DistanceCalculator()
	dp = dc.editDistance(user,row.PrincipalName)
	dc = DistanceCalculator()
	do = dc.editDistance(user,row["field"].replace(",",""))

	#Check which one is closer
	if do<dp:
		return "MAYBE "+field
	else:
		return row.EmailStatus





