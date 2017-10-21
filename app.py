#!/usr/bin/env python
# -*-coding:utf-8 -*-
import web
import json
import time
import rsa
import MySQLdb
import xlwt
import ConfigParser
import socket
import random
#import js2py

from web.wsgiserver import CherryPyWSGIServer
 
# CherryPyWSGIServer.ssl_certificate = "cacert.pem"
# CherryPyWSGIServer.ssl_private_key = "prvtkey.pem"

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

urls = (
	'/ui'	, 'ui',
	'/jquery-tablepage'	, 'jquerytablepage',
	'/BigInt'			, 'BigInt',
	'/Barrett'			, 'Barrett',
	'/RSA'				, 'RSA',
	'/RSA_Stripped'		, 'RSA_Stripped',
	'/singin'	,'singin',
	'/ecs'		,'ecs',		#---1---
	'/epvt'		,'epvt',
	'/epvf'		,'epvf',
	'/sdl'		,'sdl',		#---2---
	'/sm'		,'sm',
	'/ser'		,'ser',
	'/sm_admq'	,'sm_admq',	#---3---
	'/sr_dmw'	,'sr_dmw',
	'/su'		,'su',
	'/'					, 'Login',								# index --> /login
	'/login'			, 'Login',								# Sing in
	'/logout'			, 'Logout',								# Sign out

	'/CurrentState'		,'EnvironmentCurrentState_testClass',	# Current value
	'/value'			,'value_testClass',									# Update Current value
	'/test' 			,'test',

	'/PastValueTable'	,'EnvironmentPastValueTable',			# Past value (table)
	'/PastValueFigure'	,'EnvironmentPastValueFigure',			# Past value (figure)
	'/DoorLock'			,'SafetyDoorLock',						# Door lock
	'/Monitor'			,'SafetyMonitor',						# Camera
	'/EventRecord'		,'SafetyEventRecord',					# Event record
	'/Member/Quire'		,'SystemMemberQuire',					# Member Quire
	'/Member/Add'		,'SystemMemberAdd',						# Member Add
	'/Member/Modify'	,'SystemMemberModify',					# Member Modify
	'/Member/Delete'	,'SystemMemberDeiete',					# Member Deiete
	'/SystemReportDay'	,'SystemReportDay',						# ReportDay
	'/SystemReportWeek'	,'SystemReportWeek',					# ReportWeek
	'/SystemReportMonth','SystemReportMonth',					# ReportMonth
	'/SetUp'			,'SystemSetUp',							# ??
	'/SetUpdata'		,'SystemSetUpdata'						# ??

)

web.config.debug = False
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'privkey':None})      

#################################################
							#		CSS,JS		#
							#####################
	#---ALL---
class ui:
	def GET(self):
		render = web.template.render("css_js")
		return render.ui()
class jquerytablepage:
	def GET(self):
		render = web.template.render("css_js")
		return render.jqueryTablepage()
class BigInt:
	def GET(self):
		render = web.template.render("css_js")
		return render.BigInt()
class Barrett:
	def GET(self):
		render = web.template.render("css_js")
		return render.Barrett()
class RSA:
	def GET(self):
		render = web.template.render("css_js")
		return render.RSA()
class RSA_Stripped:
	def GET(self):
		render = web.template.render("css_js")
		return render.RSA_Stripped()
	#---S---
class singin:
	def GET(self):
		render = web.template.render("css_js")
		return render.singin()
	#---1---
class ecs:
	def GET(self):
		render = web.template.render("css_js")
		return render.ecs()
class epvt:
	def GET(self):
		render = web.template.render("css_js")
		return render.epvt()
class epvf:
	def GET(self):
		render = web.template.render("css_js")
		return render.epvf()
	#---2---
class sdl:
	def GET(self):
		render = web.template.render("css_js")
		return render.sdl()
class sm:
	def GET(self):
		render = web.template.render("css_js")
		return render.sm()		
class ser:
	def GET(self):
		render = web.template.render("css_js")
		return render.ser()
	#---3---
class sm_admq:
	def GET(self):
		render = web.template.render("css_js")
		return render.sm_admq()
class sr_dmw:
	def GET(self):
		render = web.template.render("css_js")
		return render.sr_dmw()
class su:
	def GET(self):
		render = web.template.render("css_js")
		return render.su()

#########################################################
							#		Log in, log out		#(ERROR!!!)
							#############################
class Login:
	def __init__(self):
		self.render = web.template.render("view")
		self.conf = ConfigParser.ConfigParser()
		self.conf.read("test.conf")
		self.pkey = self.conf.get("prive key", "pkey")

	def GET(self):
		return self.render.SignIn()

	def POST(self):
		i = web.input()
		if i.user == '1' and i.password =='1':
			session.logged_in = True
			raise web.seeother('/CurrentState')
		else:
			session.logged_in = False
			raise web.seeother('/')
	
	# def POST_error(self): # error  Decryption failed
	# 	i = web.input()
	# 	username = i.user
	# 	en_password = i.password
	# 	print("client:" + username + " & " + en_password)
	# 	print("--------------------------------------------")
	# 	priv_key = self.pkey
	# 	#priv_key = session.get('privkey')
	# 	#print("A"+ str(priv_key))
	# 	#session['privkey'] = ""
	# 	#print("B"+ str(priv_key))
	# 	print("--------------------------------------------")
	# 	password = rsa.decrypt(en_password.decode('hex'),priv_key)
		
	# 	print(password)
class Logout:
    def GET(self):
        session.logged_in = False
        raise web.seeother('/')

#####################################################################
							#		Environmental monitoring		#		   
							#########################################
#---------------------------------------------------------------------------

class EnvironmentCurrentState:
	
	def __init__(self):
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.arduinoIP 		= conf.get("arduino address", "ip"		)
		self.arduinoPort 	= conf.get("arduino address", "port"	)

  		self.humidity   = self.Humidity()	#濕度
  		self.TemperC	= self.TemperC()	#溫度(攝氏)
  		self.TemperF 	= self.TemperF()	#溫度(華視)
  		self.sensor 	= self.sensor()		#可燃氣
  		self.Air 		= self.Air ()		#空氣清晰度
  		self.Dust 		= self.Dust()		#粉成濃度
  		self.ampere 	= self.ampere()		#安培量


		self.render = web.template.render("view")
	
	def GET(self):
		
		print("----------------------------------------------")
		print(self.humidity)
		print(self.TemperC)
		print(self.TemperF)
		print(self.sensor)
		print(self.Air)
		print(self.Dust)
		print(self.ampere)

		if session.get('logged_in', False):
			return self.render.EnvironmentCurrentState(self.humidity, self.TemperC, self.TemperF, self.sensor, self.Air, self.Dust, self.ampere )
        
		raise web.seeother('/')
	def POST(self):
		print("----------------------------------------------")
		print(self.humidity)
		print(self.TemperC)
		print(self.TemperF)
		print(self.sensor)
		print(self.Air)
		print(self.Dust)
		print(self.ampere)
		print("----------------------------------------------")
		return self.render.EnvironmentCurrentState(self.humidity, self.TemperC, self.TemperF, self.sensor, self.Air, self.Dust, self.ampere )
		
	def conn(self):
		

		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			sys.exit(1)

		try:
			sock.connect((str(self.arduinoIP), int(self.arduinoPort)))
			print("Arduino connect OK!!")
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			exit(1)

		return sock
	def Humidity(self):
		sock = self.conn()
		sock.send("Humidity")
		data = sock.recv(1024)
		sock.close()
		return data
	def TemperC(self):
		sock = self.conn()
		sock.send("TemperC")
		data = sock.recv(1024)
		sock.close()
		return data
	def TemperF(self):
		sock = self.conn()
		sock.send("TemperF")
		data = sock.recv(1024)
		sock.close()
		return data
	def sensor(self):
		sock = self.conn()
		sock.send("sensor")
		data = sock.recv(1024)
		sock.close()
		return data
	def Air(self):
		sock = self.conn()
		sock.send("Air")
		data = sock.recv(1024)
		sock.close()
		return data
	def Dust(self):
		sock = self.conn()
		sock.send("Dust")
		data = sock.recv(1024)
		sock.close()
		return data
	def ampere(self):
		sock = self.conn()
		sock.send("ampere")
		data = sock.recv(1024)
		sock.close()
		return data
class value:
	
	def __init__(self):
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.arduinoIP 		= conf.get("arduino address", "ip"		)
		self.arduinoPort 	= conf.get("arduino address", "port"	)
		print("----------------------------------------------")

  		self.humidity   = self.Humidity()	#濕度
  		self.TemperC	= self.TemperC()	#溫度(攝氏)
  		self.TemperF 	= self.TemperF()	#溫度(華視)
  		self.sensor 	= self.sensor()		#可燃氣
  		self.Air 		= self.Air ()		#空氣清晰度
  		self.Dust 		= self.Dust()		#粉成濃度
  		self.ampere 	= self.ampere()		#安培量


		self.render = web.template.render("view")

	def GET(self):
		
		print("----------------------------------------------")
		print(self.humidity)
		print(self.TemperC)
		print(self.TemperF)
		print(self.sensor)
		print(self.Air)
		print(self.Dust)
		print(self.ampere)

		if session.get('logged_in', False):
			return self.render.EnvironmentCurrentState(self.humidity, self.TemperC, self.TemperF, self.sensor, self.Air, self.Dust, self.ampere )
        
		raise web.seeother('/')
	def POST(self):
		print("----------------------------------------------")
		print(self.humidity)
		print(self.TemperC)
		print(self.TemperF)
		print(self.sensor)
		print(self.Air)
		print(self.Dust)
		print(self.ampere)
		print("----------------------------------------------")
		return self.render.EnvironmentCurrentState(self.humidity, self.TemperC, self.TemperF, self.sensor, self.Air, self.Dust, self.ampere )

		
	def conn(self):
		

		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			sys.exit(1)

		try:
			sock.connect((str(self.arduinoIP), int(self.arduinoPort)))
			print("Arduino connect OK!!")
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			exit(1)

		return sock
	def Humidity(self):
		sock = self.conn()
		sock.send("Humidity")
		data = sock.recv(1024)
		sock.close()
		return data
	def TemperC(self):
		sock = self.conn()
		sock.send("TemperC")
		data = sock.recv(1024)
		sock.close()
		return data
	def TemperF(self):
		sock = self.conn()
		sock.send("TemperF")
		data = sock.recv(1024)
		sock.close()
		return data
	def sensor(self):
		sock = self.conn()
		sock.send("sensor")
		data = sock.recv(1024)
		sock.close()
		return data
	def Air(self):
		sock = self.conn()
		sock.send("Air")
		data = sock.recv(1024)
		sock.close()
		return data
	def Dust(self):
		sock = self.conn()
		sock.send("Dust")
		data = sock.recv(1024)
		sock.close()
		return data
	def ampere(self):
		sock = self.conn()
		sock.send("ampere")
		data = sock.recv(1024)
		sock.close()
		return data
class EnvironmentPastValueTable:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.time_hour = []
		self.humidity_v = []
		self.humidity_s = []
		self.cgc_v = []
		self.cgc_s = []
		self.ac_v = []
		self.ac_s = []
		self.temp_v = []
		self.temp_s = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		sql = "SELECT year, month, day, time_hour, temp_v ,temp_s FROM monitoring_value"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.temp_v.append(row[4])
   			self.temp_s.append(row[5])
   		self.db.close()

		return self.render.EnvironmentPastValueTable("溫度", self.year, self.month, self.day, self.time_hour, self.temp_v, self.temp_s)
	
	def POST(self):
		self.i = web.input()

		if self.i.index_name == "temp":
			self.temp(self.i.Y, self.i.M, self.i.D)
			return self.render.EnvironmentPastValueTable("溫度", self.year, self.month, self.day, self.time_hour, self.temp_v, self.temp_s)
		elif self.i.index_name == "humidity":
			self.humidity(self.i.Y, self.i.M, self.i.D)
			return self.render.EnvironmentPastValueTable("濕度", self.year, self.month, self.day, self.time_hour, self.humidity_v, self.humidity_s)
		elif self.i.index_name == "cgc":
			self.cgc(self.i.Y, self.i.M, self.i.D)
			return self.render.EnvironmentPastValueTable("可燃氣濃度", self.year, self.month, self.day, self.time_hour, self.cgc_v, self.cgc_s)
		elif self.i.index_name == "ac":
			self.ac(self.i.Y, self.i.M, self.i.D)
			return self.render.EnvironmentPastValueTable("空氣清晰度", self.year, self.month, self.day, self.time_hour, self.ac_v, self.ac_s)

	def temp(self, Y, M, D):
		sql = "SELECT year, month, day, time_hour, temp_v ,temp_s FROM monitoring_value WHERE year = \'" +Y+"\'"
		if M not in "all":
			sql += " AND month = \'" + M + "\'"
		if D not in "all":
			sql += " AND day = \'"   + D + "\'"
		print(sql)
		print(D)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.temp_v.append(row[4])
   			self.temp_s.append(row[5])
   		self.db.close()
		
	def humidity(self, Y, M, D):
		sql = "SELECT year, month, day, time_hour, humidity_v ,humidity_s FROM monitoring_value WHERE year = \'" +Y+"\'"
		if M in "all":
			sql += " AND month = \'" + M + "\'"
		if D in "all":
			sql += " AND day = \'"   + D + "\'"

		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.humidity_v.append(row[4])
   			self.humidity_s.append(row[5])
   		self.db.close()

	def cgc(self, Y, M, D):
		sql = "SELECT year, month, day, time_hour, cgc_v ,cgc_s FROM monitoring_value WHERE year = \'" +Y+"\'"
		if M in "all":
			sql += " AND month = \'" + M + "\'"
		if D in "all":
			sql += " AND day = \'"   + D + "\'"

		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.cgc_v.append(row[4])
   			self.cgc_s.append(row[5])
   		self.db.close()

	def ac(self, Y, M, D):
		sql = "SELECT year, month, day, time_hour, ac_v ,ac_s FROM monitoring_value WHERE year = \'" +Y+"\'"
		if M in "all":
			sql += " AND month = \'" + M + "\'"
		if D in "all":
			sql += " AND day = \'"   + D + "\'"

		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.ac_v.append(row[4])
   			self.ac_s.append(row[5])
   		self.db.close()
class EnvironmentPastValueFigure:
	def __init__(self):
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.EnvironmentPastValueFigure()

#---------------------------------------------------------------------------testClass
class EnvironmentCurrentState_testClass:
	def __init__(self):
		self.render = web.template.render("view")

	def GET(self):
		return self.render.EnvironmentCurrentState()
class value_testClass:
	def __init__(self):
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.arduinoIP 		= conf.get("arduino address", "ip"		)
		self.arduinoPort 	= conf.get("arduino address", "port"	)

  		self.humidity   = self.Humidity()	#濕度
  		self.TemperC	= self.TemperC()	#溫度(攝氏)
  		self.TemperF 	= self.TemperF()	#溫度(華視)
  		self.sensor 	= self.sensor()		#可燃氣
  		self.Air 		= self.Air ()		#空氣清晰度
  		self.Dust 		= self.Dust()		#粉成濃度
  		self.ampere 	= self.ampere()		#安培量


		self.render = web.template.render("view")
	
	def GET(self):
		value = {	'Humidity'	:self.TemperC,
					'TemperC'	:self.TemperF,
					'TemperF'	:self.sensor,
					'sensor'	:self.Air,
					'Air'		:self.Dust,
					'Dust'		:self.Dust,
					'ampere'	:self.ampere
				}
		web.header('Content-Type', 'application/json')
		return json.dumps(value)
		
	def conn(self):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			sys.exit(1)

		try:
			sock.connect((str(self.arduinoIP), int(self.arduinoPort)))
			print("Arduino connect OK!!")
		except socket.error, msg:
			sys.stderr.write("[ERROR] %s\n" % msg[1])
			exit(1)

		return sock
	def Humidity(self):
		sock = self.conn()
		sock.send("Humidity")
		data = sock.recv(1024)
		sock.close()
		return data
	def TemperC(self):
		sock = self.conn()
		sock.send("TemperC")
		data = sock.recv(1024)
		sock.close()
		return data
	def TemperF(self):
		sock = self.conn()
		sock.send("TemperF")
		data = sock.recv(1024)
		sock.close()
		return data
	def sensor(self):
		sock = self.conn()
		sock.send("sensor")
		data = sock.recv(1024)
		sock.close()
		return data
	def Air(self):
		sock = self.conn()
		sock.send("Air")
		data = sock.recv(1024)
		sock.close()
		return data
	def Dust(self):
		sock = self.conn()
		sock.send("Dust")
		data = sock.recv(1024)
		sock.close()
		return data
	def ampere(self):
		sock = self.conn()
		sock.send("ampere")
		data = sock.recv(1024)
		sock.close()
		return data


class test:
	def GET(self):
		i = web.input()
		print(i.name)
		print(i.time)
		v1,v2,v3,v4,v5,v6,v7 = random.randint(0,99),random.randint(0,99),random.randint(0,99),random.randint(0,99),random.randint(0,99),random.randint(0,99),random.randint(0,99)
		value = {	'Humidity'	:v1,
					'TemperC'	:v2,
					'TemperF'	:v3,
					'sensor'	:v4,
					'Air'		:v5,
					'Dust'		:v6,
					'ampere'	:v7
				}
		web.header('Content-Type', 'application/json')
		return json.dumps(value)

#############################################################
							#		 Safety monitoring		#
							#################################
class SafetyDoorLock:
	def __init__(self):
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyDoorLock()
class SafetyMonitor:
	def __init__(self):
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyMonitor()
class SafetyEventRecord:
	def __init__(self):
		#Value definition
		self.year = []		#year
		self.month = []		#month
		self.day = []		#day
		self.time_hour = []	#time_hour
		self.event = []		#event_description
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		sql = "SELECT year, month, day, time_hour, event_description FROM event"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.event.append(row[4])
   		self.db.close()

		return self.render.SafetyEventRecord(self.year, self.month, self.day, self.time_hour, self.event)
	def POST(self):
		self.i = web.input()

		sql = "SELECT year, month, day, time_hour, event_description FROM event WHERE year = \'" +self.i.Y+"\'"
		if self.i.M not in "all":
			sql += " AND month = \'" + self.i.M + "\'"
		if self.i.D not in "all":
			sql += " AND day = \'"   + self.i.D + "\'"
		print(sql)
		print(self.i.D)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			self.event.append(row[4])
   		self.db.close()

		return self.render.SafetyEventRecord(self.year, self.month, self.day, self.time_hour, self.event)
		
#########################################################
							#		System program		#
							#############################
#---# 1__Member__
class SystemMemberQuire:
	def __init__(self):
		#Value definition
		self.number = []
		self.password = []
		self.phone = []
		self.email = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		sql = "SELECT account, passwore, phone, email FROM member_information"

		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.number.append(row[0])
   			self.password.append(row[1])
   			self.phone.append(row[2])
   			self.email.append(row[3])
   		self.db.close()

		return self.render.SystemMemberQuire(self.number, self.password, self.phone, self.email)
class SystemMemberAdd:
	def __init__(self):
		#Value definition
		self.number = []
		self.password = []
		self.phone = []
		self.email = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		render = web.template.render("view")
		if session.logged_in == False:
			raise web.seeother('/')
		return render.SystemMemberAdd()
	def POST(self):
		self.i = web.input()
		sql = "INSERT INTO member_information(account, passwore, phone, email) VALUES "
		sql += "('" + self.i.account +"', '"+ self.i.password +"', '"+ self.i.phone +"', '"+self.i.email+"')" 
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/Member/Quire')
class SystemMemberModify:
	def __init__(self):
		#Value definition
		self.number = []
		self.password = []
		self.phone = []
		self.email = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		render = web.template.render("view")
		if session.logged_in == False:
			raise web.seeother('/')
		
		sql = "SELECT account FROM member_information"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.number.append(row[0])
   		self.db.close()

		return render.SystemMemberModify(self.number)
	def POST(self):
		self.i = web.input()
		sql = "UPDATE member_information SET "
		sql += self.i.setname + "='" + self.i.settxt + "' WHERE account = '" + self.i.account + "'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/Member/Quire')
class SystemMemberDeiete:
	def __init__(self):
		#Value definition
		self.number = []
		self.password = []
		self.phone = []
		self.email = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		render = web.template.render("view")
		if session.logged_in == False:
			raise web.seeother('/')

		sql = "SELECT account FROM member_information"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.number.append(row[0])
   		self.db.close()

		return render.SystemMemberDeiete(self.number)
	def POST(self):
		self.i = web.input()
		sql = "DELETE FROM member_information "
		sql += "WHERE account = '" + self.i.account + "'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/Member/Quire')

#---# 2__Report__
class SystemReportDay:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.time_hour = []
		self.humidity_v = []
		self.humidity_s = []
		self.cgc_v = []
		self.cgc_s = []
		self.ac_v = []
		self.ac_s = []
		self.temp_v = []
		self.temp_s = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
		#Dictionary
		self.dictionarSQL = {	'1':'temp', 
								'2':'humidity',
								'3':'cgc',
								'4':'ac',
								'5':'acurrent', 
								'6':'current'		}
		self.dictionarName = {	'1_v': "溫度", 
								'1_s': "狀態",
								'2_v': "濕度", 
								'2_s': "狀態",
								'3_v': "可燃氣濃度", 
								'3_s': "狀態",
								'4_v': "空氣清晰度", 
								'4_s': "狀態",		}
		self.dictionarClass = {	'1_v': self.temp_v, 
								'1_s': self.temp_s,
								'2_v': self.humidity_v, 
								'2_s': self.humidity_s,
								'3_v': self.cgc_v, 
								'3_s': self.cgc_s,
								'4_v': self.ac_v, 
								'4_s': self.ac_s,	}
		#config
		self.conf = ConfigParser.ConfigParser()
		self.conf.read("test.conf")
		self.DownloadAddress = self.conf.get("download address", "address")
		self.DownloadIP = self.conf.get("download address", "ip")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		path = ""
		log = "no"
		return self.render.SystemReportDay(path, log)

	def POST(self):
		if session.logged_in == False:
			raise web.seeother('/')

		i = web.input(Checkbox=[])
		Y, M, D = i.Y, i.M, i.D
		cks = i.get('Checkbox','')
		str_cks = ""
		for ck in cks:
			str_cks +=", " + self.dictionarSQL[ck] + "_v, " + self.dictionarSQL[ck] + "_s" 
		sql = "SELECT year, month, day, time_hour" + str_cks + " FROM monitoring_value"
		sql += " WHERE year = '" + Y + "' AND month = '" + M + "' AND day = '" + D + "'"
		print(sql)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			num = 4
   			for ck in cks:
   				self.dictionarClass[str(ck)+"_v"].append(row[num])
   				self.dictionarClass[str(ck)+"_s"].append(row[num+1])
   				num +=2
   		self.db.close()
		
		#創建workbook和sheet對象
		workbook = xlwt.Workbook() #註意Workbook的開頭W要大寫
		sheet1 = workbook.add_sheet('sheet1',cell_overwrite_ok=True)
		#向sheet頁中寫入數據
		sheet1.write(0,0, "年".decode('utf-8'))
		sheet1.write(0,1, "月".decode('utf-8'))
		sheet1.write(0,2, "日".decode('utf-8'))
		sheet1.write(0,3, "時間(時)".decode('utf-8'))
   		num = 4
   		for ck in cks:
   			sheet1.write(0, num	 , self.dictionarName[str(ck)+"_v"].decode('utf-8'))
			sheet1.write(0, num+1, self.dictionarName[str(ck)+"_s"].decode('utf-8'))
   			num +=2
		for c in range(1,len(self.year)):
			sheet1.write(c,0, self.year[c-1])
			sheet1.write(c,1, self.month[c-1])
			sheet1.write(c,2, self.day[c-1])
			sheet1.write(c,3, self.time_hour[c-1])
			l = 4
			for ck in cks:
				sheet1.write(c,l  , self.dictionarClass[str(ck)+"_v"][c-1])
				sheet1.write(c,l+1, self.dictionarClass[str(ck)+"_s"][c-1])
   				l += 2
		#保存該excel文件
		A = str(self.DownloadAddress) + "/日報表" + Y + "年" + M + "月" + D + "日.xls"
		workbook.save(A)
		print("創建excel文件完成!".decode('utf-8'))
		path = str(self.DownloadIP) +  "/日報表" + Y + "年" + M + "月" + D + "日.xls"
		log = "yes"
		return self.render.SystemReportDay(path, log)
class SystemReportWeek:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.time_hour = []
		self.humidity_v = []
		self.humidity_s = []
		self.cgc_v = []
		self.cgc_s = []
		self.ac_v = []
		self.ac_s = []
		self.temp_v = []
		self.temp_s = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
		#Dictionary
		self.dictionarSQL = {	'1':'temp', 
								'2':'humidity',
								'3':'cgc',
								'4':'ac',
								'5':'acurrent', 
								'6':'current'		}
		self.dictionarName = {	'1_v': "溫度", 
								'1_s': "狀態",
								'2_v': "濕度", 
								'2_s': "狀態",
								'3_v': "可燃氣濃度", 
								'3_s': "狀態",
								'4_v': "空氣清晰度", 
								'4_s': "狀態",		}
		self.dictionarClass = {	'1_v': self.temp_v, 
								'1_s': self.temp_s,
								'2_v': self.humidity_v, 
								'2_s': self.humidity_s,
								'3_v': self.cgc_v, 
								'3_s': self.cgc_s,
								'4_v': self.ac_v, 
								'4_s': self.ac_s,	}
		#config
		self.conf = ConfigParser.ConfigParser()
		self.conf.read("test.conf")
		self.DownloadAddress = self.conf.get("download address", "address")
		self.DownloadIP = self.conf.get("download address", "ip")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		path = ""
		log = "no"
		return self.render.SystemReportWeek(path, log)

	def POST(self):
		if session.logged_in == False:
			raise web.seeother('/')

		i = web.input(Checkbox=[])
		Y, M, D = i.Y, i.M, i.D
		cks = i.get('Checkbox','')
		str_cks = ""
		for ck in cks:
			str_cks +=", " + self.dictionarSQL[ck] + "_v, " + self.dictionarSQL[ck] + "_s" 
		sql = "SELECT year, month, day, time_hour" + str_cks + " FROM monitoring_value"
		sql	+= " WHERE year = '" + Y + "' AND month = '" + M +"' AND day IN ("
		sql	+= "'" + str(int(D)) + "', '"+ str(int(D)+1) + "', '"+ str(int(D)+2) + "', '"+ str(int(D)+3) + "', '"+ str(int(D)+4) + "', '"+ str(int(D)+5) + "', '"+ str(int(D)+6) + "')"
		print(sql)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			num = 4
   			for ck in cks:
   				self.dictionarClass[str(ck)+"_v"].append(row[num])
   				self.dictionarClass[str(ck)+"_s"].append(row[num+1])
   				num +=2
   		self.db.close()
		
		#創建workbook和sheet對象
		workbook = xlwt.Workbook() #註意Workbook的開頭W要大寫
		sheet1 = workbook.add_sheet('sheet1',cell_overwrite_ok=True)
		#向sheet頁中寫入數據
		sheet1.write(0,0, "年".decode('utf-8'))
		sheet1.write(0,1, "月".decode('utf-8'))
		sheet1.write(0,2, "日".decode('utf-8'))
		sheet1.write(0,3, "時間(時)".decode('utf-8'))
   		num = 4
   		for ck in cks:
   			sheet1.write(0, num	 , self.dictionarName[str(ck)+"_v"].decode('utf-8'))
			sheet1.write(0, num+1, self.dictionarName[str(ck)+"_s"].decode('utf-8'))
   			num +=2
		for c in range(1,len(self.year)):
			sheet1.write(c,0, self.year[c-1])
			sheet1.write(c,1, self.month[c-1])
			sheet1.write(c,2, self.day[c-1])
			sheet1.write(c,3, self.time_hour[c-1])
			l = 4
			for ck in cks:
				sheet1.write(c,l  , self.dictionarClass[str(ck)+"_v"][c-1])
				sheet1.write(c,l+1, self.dictionarClass[str(ck)+"_s"][c-1])
   				l += 2
		#保存該excel文件
		A = str(self.DownloadAddress) + "/周報表" + Y + "年" + M + "月" + D + "至" + str(int(D)+6) + "日.xls"
		workbook.save(A)
		print("創建excel文件完成!".decode('utf-8'))
		path = str(self.DownloadIP) + "/周報表" + Y + "年" + M + "月" + D + "至" + str(int(D)+6) + "日.xls"
		log = "yes"
		return self.render.SystemReportWeek(path, log)
class SystemReportMonth:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.time_hour = []
		self.humidity_v = []
		self.humidity_s = []
		self.cgc_v = []
		self.cgc_s = []
		self.ac_v = []
		self.ac_s = []
		self.temp_v = []
		self.temp_s = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
		#Dictionary
		self.dictionarSQL = {	'1':'temp', 
								'2':'humidity',
								'3':'cgc',
								'4':'ac',
								'5':'acurrent', 
								'6':'current'		}
		self.dictionarName = {	'1_v': "溫度", 
								'1_s': "狀態",
								'2_v': "濕度", 
								'2_s': "狀態",
								'3_v': "可燃氣濃度", 
								'3_s': "狀態",
								'4_v': "空氣清晰度", 
								'4_s': "狀態",		}
		self.dictionarClass = {	'1_v': self.temp_v, 
								'1_s': self.temp_s,
								'2_v': self.humidity_v, 
								'2_s': self.humidity_s,
								'3_v': self.cgc_v, 
								'3_s': self.cgc_s,
								'4_v': self.ac_v, 
								'4_s': self.ac_s,	}
		#config
		self.conf = ConfigParser.ConfigParser()
		self.conf.read("test.conf")
		self.DownloadAddress = self.conf.get("download address", "address")
		self.DownloadIP = self.conf.get("download address", "ip")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		path = ""
		log = "no"
		return self.render.SystemReportMonth(path, log)

	def POST(self):
		if session.logged_in == False:
			raise web.seeother('/')

		i = web.input(Checkbox=[])
		Y, M = i.Y, i.M
		cks = i.get('Checkbox','')
		str_cks = ""
		for ck in cks:
			str_cks +=", " + self.dictionarSQL[ck] + "_v, " + self.dictionarSQL[ck] + "_s" 
		sql = "SELECT year, month, day, time_hour" + str_cks + " FROM monitoring_value"
		sql += " WHERE year = '" + Y + "' AND month = '" + M + "'"
		print(sql)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.time_hour.append(row[3])
   			num = 4
   			for ck in cks:
   				self.dictionarClass[str(ck)+"_v"].append(row[num])
   				self.dictionarClass[str(ck)+"_s"].append(row[num+1])
   				num +=2
   		self.db.close()
		
		#創建workbook和sheet對象
		workbook = xlwt.Workbook() #註意Workbook的開頭W要大寫
		sheet1 = workbook.add_sheet('sheet1',cell_overwrite_ok=True)
		#向sheet頁中寫入數據
		sheet1.write(0,0, "年".decode('utf-8'))
		sheet1.write(0,1, "月".decode('utf-8'))
		sheet1.write(0,2, "日".decode('utf-8'))
		sheet1.write(0,3, "時間(時)".decode('utf-8'))
   		num = 4
   		for ck in cks:
   			sheet1.write(0, num	 , self.dictionarName[str(ck)+"_v"].decode('utf-8'))
			sheet1.write(0, num+1, self.dictionarName[str(ck)+"_s"].decode('utf-8'))
   			num +=2
		for c in range(1,len(self.year)):
			sheet1.write(c,0, self.year[c-1])
			sheet1.write(c,1, self.month[c-1])
			sheet1.write(c,2, self.day[c-1])
			sheet1.write(c,3, self.time_hour[c-1])
			l = 4
			for ck in cks:
				sheet1.write(c,l  , self.dictionarClass[str(ck)+"_v"][c-1])
				sheet1.write(c,l+1, self.dictionarClass[str(ck)+"_s"][c-1])
   				l += 2
		#保存該excel文件
		A = str(self.DownloadAddress) + "/月報表" + Y + "年" + M + "月.xls"
		workbook.save(A)
		print("創建excel文件完成!".decode('utf-8'))
		path = str(self.DownloadIP) + "/月報表" + Y + "年" + M + "月.xls"
		log = "yes"
		return self.render.SystemReportMonth(path, log)

#---# 3__Set__
class SystemSetUp():
	def __init__(self):
		self.conf = ConfigParser.ConfigParser()
		self.conf.read("test.conf")
		self.DownloadAddress = self.conf.get("download address", "address")

	def GET(self):
		render = web.template.render("view")
		if session.logged_in == False:
			raise web.seeother('/')

		return render.SystemSetUp(self.DownloadAddress)
class SystemSetUpdata():
	def __init__(self):
		self.conf = ConfigParser.ConfigParser()
		self.conf.read("test.conf")
		self.DownloadAddress = self.conf.get("download address", "address")
		self.render = web.template.render("view")
	
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		return self.render.SystemSetUpdate(self.DownloadAddress)
	
	def POST(self):
		self.i = web.input()
		self.DownloadAddress = self.i.download_address
		self.conf.set("download address", "address", self.DownloadAddress)
		with open("test.conf","w+") as f:
			self.conf.write(f)	
		return self.render.SystemSetUp(self.DownloadAddress)

if __name__ == '__main__':
	app.run()