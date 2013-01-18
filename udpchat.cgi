#!/usr/bin/python

import cgi
import cgitb
import re
import socket
import sys

cgitb.enable()  # for troubleshooting

#defaults in case user doesn't supply them
HOST = 'cgi.cselabs.umn.edu'
PORT = 9001
	
def main():
	
	submitForm = cgi.FieldStorage()
	
	action = submitForm.getvalue('action')
	
	if action == 'login':
		login_response(submitForm)
		
	elif action == 'send':
		message_response(submitForm)
		
	elif action == 'logout':
		logout_response(submitForm)
	
	elif action == 'update':
		update_chat(submitForm)
		
	else:
		print_default(submitForm)

def print_default(form):
	default_page = open("html/udpchat.html").read()
	print ("Content-type: text/html\n\n")
	print default_page

def login_response(form):
	global HOST, PORT
	user = form.getvalue('username')
	passwd = form.getvalue('password')
	HOST = str(form.getvalue('domain'))
	PORT = int(form.getvalue('port'))
	data = 'login,' + str(user) + ',' + str(passwd)
	send_request(data)
	
def message_response(form):
	user = form.getvalue('username')
	message = form.getvalue('message')
	session = form.getvalue('session')
	data = 'message,' + str(user) + ',' + str(message) + ',' + str(session)
	send_request(data)
	
def logout_response(form):
	#clear users session so they don't receive more chats
	user = form.getvalue('username')
	session = form.getvalue('session')
	data = 'logout,' + str(user) + ',' + str(session)
	send_request(data)

def update_chat(form):
	user = form.getvalue('username')
	session = form.getvalue('session')
	data = 'update,' + str(user) + ',' + str(session)
	send_request(data)

def send_request(data):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	sock.sendto(data, (HOST, PORT))
	received = sock.recv(2048)

	print 'Content-type: application/json\n\n'
	print received
	
main()
