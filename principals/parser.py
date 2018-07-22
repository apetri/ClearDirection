from __future__ import division

import pandas as pd
from bs4 import BeautifulSoup

#Parse school data in pandas DataFrame
def parseXML(fname,block=40):

	#Build the XML soup
	with open(fname,"r") as fp:
		soup = BeautifulSoup(fp.read(),"xml")

	#Find all cells
	cells = soup.find_all("Cell")

	#Column names
	cols = [ c.contents[0].contents[0] for c in cells[:block] ]
	cols = map(lambda c:c.replace(" ",""),cols)

	#Parse records
	nRecords = len(cells)//block - 1
	records = list()

	for n in range(1,nRecords+1):
		records.append([ c.contents[0].contents[0] if c.contents[0].contents else None for c in cells[block*n:block*(n+1)] ])

	#Build DataFrame
	df = pd.DataFrame.from_records(records,columns=cols)

	#Return
	return df
