#!/usr/bin/python

import SocketServer
import socket
import random
import datetime
import string

# this way, server always runs on machine the script is run from
#HOST = socket.gethostname()
HOST = 'cgi.cselabs.umn.edu'
PORT = 9001


sessions = dict() #stores session time indexed by session ID
chat = dict() #stores chat messages for each client indexed by session
passwords = dict() #stores user passwords
users_online = [] #simple list of online usernames

#username/password pairs
passwords['michael'] = 'password'
passwords['bob'] = '123'
passwords['joe'] = 'abc'
passwords['graham'] = 'shazam'
passwords['skelly'] = 'belly'
passwords['trev'] = 'stix'

class MyUDPHandler(SocketServer.DatagramRequestHandler):
	def handle(self):
		data = self.rfile.read().split(',')
		print 'Request type: {' + data[0] + '}  Request details: {' + str(data[1:]) + '}'
		response = respond(data)
		self.wfile.write( response )

def respond(data):
	response = ''
	#handle login
	if data[0] == 'login':
		username = data[1]
		passw = data[2]
		validation = check_login(username, passw) #data has user and pass
		if validation:
			# check if user is already logged in
			if username in users_online:
				# send all online users to new login
				response = '{ "response": "ERROR", "users": ['
				for i in users_online[:-1]:
					response += '{ "name": "' + i + '"},'
				response += '{ "name": "' + users_online[-1] + '"}], "session": "invalid" }'

			else:
				session_id = get_session_id()
				sessions[session_id] = datetime.datetime.now()
				chat[session_id] = []
			
				# send new user to all currently logged in
				for session in sessions.keys():
					if session != session_id:
						chat[session].append(data[1] + " has come online")
			
				# send all online users to new login
				if len(users_online) > 0:
					response = '{ "response": "OK", "users": ['
					for i in users_online[:-1]:
						response += '{ "name": "' + i + '"},'
					response += '{ "name": "' + users_online[-1] + '"}], "session": "' + session_id + '" }'
				else:
					response = '{ "response": "OK", "users": [{}], "session": "' + session_id + '" }'
			
				# log to server console, and add user to list of online users
				print 'User', username, 'logged in'
				users_online.append(username)
		else:
			response = '{ "response": "ERROR", "users": [{}], "session": "failed" }'
		print response
		return response

	#handle message
	if data[0] == 'message':
		session_key = data[3]
		username = data[1]
		message = data[2]
		if check_session(session_key):
			for session in sessions.keys():
				if session != session_key:
					chat[session].append(username + ": " + message)
			response = '{ "response": "OK", "message": "delivered", "session": "valid" }'
		else:
			#arrange other logout behavior here
			response = '{ "response": "ERROR", "message": "undelivered", "session": "expired" }'
		print response
		return response

	#handle update
	if data[0] == 'update':
		session_id = data[2]
		username = data[1]
		if check_session_norenew(session_id):
			if len(chat[session_id]) > 0:
				response = '{ "response": "OK", "chats": ['
				for i in chat[data[2]][:-1]:
					response += '{ "message": "' + i + '"},'
				response += '{ "message": "' + chat[session_id][-1] + '"}], "session": "valid" }'
			else:
				response = '{ "response": "OK", "chats": [{}], "session": "valid" }'
			chat[session_id] = []
		else:
			# send user offline message to all currently logged in
			for session in sessions.keys():
				if session != session_id:
					chat[session].append(data[1] + " has gone offline")
			print 'user ', username, ' timed out'
			del chat[session_id]
			del sessions[session_id]
			users_online.remove(username)
			response = '{ "response": "ERROR", "chats": [{}], "session": "expired" }'
		print response
		return response

	#handle logout
	if data[0] == 'logout':
		username = data[1]
		session_id = data[2]
		if check_session_norenew(session_id):
			# send user offline message to all currently logged in
			for session in sessions.keys():
				if session != session_id:
					chat[session].append(data[1] + " has gone offline")

			print 'user ', username, ' logged out'
			del chat[session_id]
			del sessions[session_id]
			users_online.remove(username)
			response += '{ "response" : "OK", "session": "loggedout" }'
		else:
			response += '{ "response" : "OK", "session": "invalid" }'
		print response
		return response

# generates new session id from random letters/digits
def get_session_id():
	return "".join(random.choice(string.letters + string.digits) for i in range(20))

# checks if login is valid
def check_login(user, passw):
	if user in passwords:
		if passwords[user] == passw:
			return True
		return False

# checks if session is valid and renews it
def check_session(session_id):
	now = datetime.datetime.now()
	if session_id in sessions:
		session_time = sessions[session_id]
		time_delta = now - session_time
		if time_delta.days == 0 and time_delta.seconds < 300:
			print 'renewing session ', session_id
			sessions[session_id] = now
			return True
	return False
	
# checks if session is valid but does not renew it
def check_session_norenew(session_id):
	#print 'validating session ', session_id
	now = datetime.datetime.now()
	if session_id in sessions:
		session_time = sessions[session_id]
		time_delta = now - session_time
		if time_delta.days == 0 and time_delta.seconds < 300:
			return True
	return False
	

	
server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
print 'Server running on', HOST, PORT
server.serve_forever()
