import sys,os
import smtplib
from email.mime.text import MIMEText
import getpass
import argparse

import pandas as pd

from getEmails import red,green,yellow

#Connect to mail server
def connectSMTP(mail_server,port):
	
	print("[*] Connecting to: {0}:{1}.".format(yellow(mail_server),yellow(str(port))))
	smtpServer = smtplib.SMTP(mail_server,port)
	smtpServer.ehlo()

	print("[*] Starting encrypted session.")
	smtpServer.starttls()
	smtpServer.ehlo()

	print("[*] Let's log you in on your account:")
	user = raw_input("[*] Username for {0}: ".format(yellow(mail_server)))
	password = getpass.getpass("[*] Password for {0} on {1}: ".format(yellow(user),yellow(mail_server)))

	print("[*] Logging in into: {0}.".format(yellow(mail_server)))
	try:
		smtpServer.login(user,password)
		print("[+] Connection to: {0} open.".format(green(mail_server)))
		return smtpServer
	
	except smtplib.SMTPAuthenticationError:
		print("[-] Authentication to: {0} failed, check your security settings".format(red(mail_server)))
		return None

#Send emails to recipient, for each row of the DataFrame
def sendEMail(r,server=None,sender=None,subject=None,text=None):

	#Last name of principal
	principalLast = r.PrincipalName.split(" ")[-1].lower()
	principalLast = principalLast[0].upper() + principalLast[1:]

	#Compose message
	message = MIMEText(text.format(principalLast,r.LocationName))
	message["From"] = sender
	message["To"] = r.PrincipalEmail
	message["Subject"] = subject

	#Deliver message
	try:

		print("[*] Sending Mail to: {0}.".format(yellow(message["To"])))
		server.sendmail(message["From"],message["To"],message.as_string())
		print("[+] Mail sent succesfully to: {0}.".format(green(message["To"])))
		return "OK"

	except Exception,e:
		print("[-] Sending Mail to: {0} failed".format(red(message["To"])),e)
		return "ERROR"

#Send emails: main execution
def customizeAndSend():
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-f","--from",dest="frm",default=None,help="sender of the email notification")
	parser.add_argument("-s","--subject",dest="subject",default="some subject",help="subject of the email")
	parser.add_argument("-S","--server",dest="server",default="smtp.gmail.com",help="mail server that delivers the message")
	parser.add_argument("-p","--port",dest="port",default=587,help="mail server port")
	parser.add_argument("-t","--text",dest="text",default=None,help="name of the file with the text to be formatted")
	parser.add_argument("-d","--data",dest="data",default=None,help="CSV file name with the recipient data")
	parser.add_argument("-o","--output",dest="output",default=None,help="CSV file name with sending status information")

	#Parse arguments from command line
	cmd_args = parser.parse_args()
	if cmd_args.text is None or cmd_args.data is None:
		parser.print_help()
		sys.exit(1)

	#Read text and recipients
	print("[*] Reading email body from: {0}".format(yellow(cmd_args.text)))
	with open(cmd_args.text,"r") as fp:
		text = fp.read()

	print("[*] Reading recipient database from: {0}".format(yellow(cmd_args.data)))
	recipientData = pd.read_csv(cmd_args.data)

	#Log recipients, text to user
	print("[+] We are sending the following message:\n\nSubject: {0}\n\n''\n{1}\n''\n\nto:\n".format(cmd_args.subject,text.format("<Principal Last Name>","<School Name>")))
	recipientData.apply(lambda r:r.PrincipalName+" --> "+r.PrincipalEmail,axis=1).to_csv(sys.stdout,sep=":")
	print("")

	#Wait confirmation from user
	uinpt = raw_input("To proceed please type 'PROCEED': ")

	if uinpt=="PROCEED":

		#Connect to server
		smtpServer = connectSMTP(cmd_args.server,cmd_args.port)
		if smtpServer is None:
			sys.exit(1)

		#Wait confirmation from user
		uinpt = raw_input("Emails will be sent now, to proceed please type 'SEND': ")
		if uinpt!="SEND":
			print("[-] Goodbye.")
			smtpServer.close()
			sys.exit(1)	
		
		#Send emails, close connection
		recipientData["SendStatus"] = recipientData.apply(sendEMail,axis=1,server=smtpServer,sender=cmd_args.frm,subject=cmd_args.subject,text=text)
		smtpServer.close()
		print("[+] Closed connection to mail server.")
		
		#Save status to file
		if cmd_args.output is not None:
			print("[*] Saving email sending status to: {0}".format(yellow(cmd_args.output)))
			recipientData.to_csv(cmd_args.output)

	else:
		print("[-] Goodbye.")



