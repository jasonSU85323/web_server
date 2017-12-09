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
import platform

try:
	import fcntl
except :
	pass

import struct
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
	'/value'			,'value_testClass',						# Update Current value
	'/test' 			,'test',

	'/PastValueTable'	,'EnvironmentPastValueTable',			# Past value (table)
	'/EPtest'			,'EPtest',

	'/PastValueFigure'	,'EnvironmentPastValueFigure',			# Past value (figure)

	'/DoorLock'			,'SafetyDoorLock',						# Door lock
	'/DLAgent','DLAgent',
	'/DLRecord','DLRecord',
	'/DLadd','DLadd',
	'/DLdel','DLdel',

	'/Monitor'			,'SafetyMonitor',						# Camera
	'/Monitor_two'		,'SafetyMonitor_two',
	
	'/EventRecord'		,'SafetyEventRecord',					# Event record
	'/EventRecord_E'	,'Event_E',
	'/EventRecord_C'	,'Event_C',

	'/Member/Quire'		,'SystemMemberQuire',					# Member Quire
	'/Member/Add'		,'SystemMemberAdd',						# Member Add
	'/Member/Modify'	,'SystemMemberModify',					# Member Modify
	'/Member/Delete'	,'SystemMemberDeiete',					# Member Deiete

	'/SystemReportDay'	,'SystemReportDay',						# ReportDay
	'/SystemReportWeek'	,'SystemReportWeek',					# ReportWeek
	'/SystemReportMonth','SystemReportMonth',					# ReportMonth
	
	'/SetUp'			,'SystemSetUp',							# ??
	'/SetUpdata'		,'SystemSetUpdata',
	'/SystemSetUpcard'	,'SystemSetUpcard',

	'/images'  			,'images'
					# ??

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
class images:
    def GET(self):
    	fp = open("images/3.jpg",'rb+')
        return fp
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
		#Value definition

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
		return self.render.SignIn()

	def POST(self):
		i = web.input()
		usernumb = i.user
		password = i.password

		sql = "SELECT account, password FROM top"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
		dbuasr = data[0][0]
		dbpass = data[0][1]

		if usernumb == dbuasr and password ==dbpass:
			session.logged_in = True
			raise web.seeother('/CurrentState')
		else:
			session.logged_in = False
			raise web.seeother('/')
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
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.host_ip = conf.get("host", "ip")

		#Template definition
		self.render = web.template.render("view")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

   		return self.render.EnvironmentPastValueTable(self.host_ip)
class EPtest:
	def __init__(self):
		#Value definition
		self.mode = []
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

		return self.render.EnvironmentPastValueTable()
	def POST(self):
		i = web.input()
		
		dbname	= i.index_name
		dby		= i.Y
		dbm 	= i.M
		dbd 	= i.D

		sql = "SELECT year, month, day, hour, " + dbname + " FROM monitoring_value WHERE year = \'" +dby+"\'"
		if dbm not in "all":
			sql += " AND month = \'" + dbm + "\'"
		if dbd not in "all":
			sql += " AND day = \'"   + dbd + "\'"		
		print(sql)

		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			v = {'year':int(row[0]), 'month':int(row[1]), 'day':int(row[2]), 'hour':int(row[3]), 'V':int(row[4])}
   			self.mode.append(v)
   		self.db.close()

		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
   	
class EnvironmentPastValueFigure:
	def __init__(self):
		#Value definition
		self.mode = []		
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.host_ip = conf.get("host", "ip")

		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.EnvironmentPastValueFigure(self.host_ip)
	def POST(self):
		i = web.input()
		
		dbname	= i.index_name
		dby		= i.Y
		dbm 	= i.M
		dbd 	= i.D

		sql = "SELECT year, month, day, hour, " + dbname + " FROM monitoring_value WHERE year = \'" +dby+"\'"
		if dbm not in "all":
			sql += " AND month = \'" + dbm + "\'"
		if dbd not in "all":
			sql += " AND day = \'"   + dbd + "\'"		
		print(sql)

		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			v = {'year':int(row[0]), 'month':int(row[1]), 'day':int(row[2]), 'hour':int(row[3]), 'V':int(row[4])}
   			self.mode.append(v)
   		self.db.close()

		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
#---------------------------------------------------------------------------testClass
class EnvironmentCurrentState_testClass:		
	def __init__(self):
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.host_ip = conf.get("host", "ip")

		self.render = web.template.render("view")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.EnvironmentCurrentState(self.host_ip)
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
		value = {	'Humidity'	:self.humidity,
					'TemperC'	:self.TemperC,
					'TemperF'	:self.TemperF,
					'sensor'	:self.sensor,
					'Air'		:self.Air,
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
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.host_ip = conf.get("host", "ip")

	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyDoorLock(self.host_ip)
class DLAgent:
	def __init__(self):
		#Value definition
		self.mode = []
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

	def POST(self):
		i = web.input()
		tt = i.tt
		print(tt)
		sql = "SELECT year, month, day, hour, min, w_card FROM agent"
				
		print(sql)

		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			print(row[0])
   			print(row[1])
   			print(row[2])
   			print(row[3])
   			print(row[4])
   			print(row[5])
   			v = {'year':int(row[0]), 'month':str(row[1]), 'day':int(row[2]), 'hour':int(row[3]), 'min':int(row[4]), 'w_card':str(row[5])}
   			self.mode.append(v)
   		self.db.close()

		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
class DLRecord:
	def __init__(self):
		#Value definition
		self.mode = []
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

	def POST(self):
		i = web.input()
		y = i.Y
		m = i.M
		d = i.D
		
		sql = "SELECT year, month, day, hour, min, event FROM swipe"
				
		print(sql)

		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			v = {'year':int(row[0]), 'month':int(row[1]), 'day':int(row[2]), 'hour':int(row[3]), 'min':int(row[4]), 'event':str(row[5])}
   			self.mode.append(v)
   		self.db.close()

		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
class DLadd:
	def __init__(self):
		#Value definition
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
	def POST(self):
		self.i = web.input()
		
		# 1.QQQ
		sql = "SELECT phone FROM member_information WHERE phone=\'" + self.i.phone + "\'"
		print(sql)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
		if len(data) == 0 :
			return "無此手機號碼"

		# 2.ADD
		sql = "UPDATE member_information SET card = \'"+ self.i.card_id +"\' WHERE phone=\'" + self.i.phone + "\'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()

		# 3.del
		sql = "DELETE FROM agent WHERE w_card = '" + self.i.card_id + "'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()

		self.db.close()
		return "OK"
class DLdel:
	def __init__(self):
		#Value definition
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
	def POST(self):
		self.i = web.input()
		
		sql = "DELETE FROM agent "
		sql += "WHERE w_card = '" + self.i.card_id + "'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		return "OK"

class SafetyMonitor:
	def __init__(self):
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyMonitor()
class SafetyMonitor_two:
	def __init__(self):
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyMonitor_two()

class SafetyEventRecord:
	def __init__(self):
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		self.host_ip = conf.get("host", "ip")
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyEventRecord(self.host_ip)
class Event_E:
	def __init__(self):
		#Value definition
		self.mode = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		self.host_ip = conf.get("host", "ip")
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyEventRecord(self.host_ip)
		
	def POST(self):
		self.i = web.input()

		sql = "SELECT year, month, day, hour, min, event FROM event_environment WHERE year = \'" +self.i.Y+"\'"
		if self.i.M not in "all":
			sql += " AND month = \'" + self.i.M + "\'"
		if self.i.D not in "all":
			sql += " AND day = \'"   + self.i.D + "\'"
		print(sql)

		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			v = {'year':int(row[0]), 'month':int(row[1]), 'day':int(row[2]), 'hour':int(row[3]), 'min':int(row[4]), 'event':str(row[5])}
   			self.mode.append(v)
   		self.db.close()
   		print(self.mode)
		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
class Event_C:
	def __init__(self):
		#Value definition
		self.mode = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		self.host_ip = conf.get("host", "ip")
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')
		return self.render.SafetyEventRecord(self.host_ip)
		
	def POST(self):
		self.i = web.input()

		sql = "SELECT year, month, day, hour, min, event FROM event_security WHERE year = \'" +self.i.Y+"\'"
		if self.i.M not in "all":
			sql += " AND month = \'" + self.i.M + "\'"
		if self.i.D not in "all":
			sql += " AND day = \'"   + self.i.D + "\'"
		print(sql)

		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			v = {'year':int(row[0]), 'month':int(row[1]), 'day':int(row[2]), 'hour':int(row[3]), 'min':int(row[4]), 'event':str(row[5])}
   			self.mode.append(v)
   		self.db.close()
   		print(self.mode)
		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
		
		
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
		sql = "INSERT INTO member_information(phone, email) VALUES "
		sql += "('" + self.i.phone +"', '"+self.i.email+"')" 
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/SetUp')
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
		
		sql = "SELECT phone FROM member_information"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.number.append(row[0])
   		self.db.close()

		return render.SystemMemberModify(self.number)
	def POST(self):
		self.i = web.input()
		sql = "UPDATE member_information SET "
		sql += self.i.setname + "='" + self.i.settxt + "' WHERE phone = '" + self.i.account + "'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/SetUp')
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

		sql = "SELECT phone FROM member_information"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.number.append(row[0])
   		self.db.close()

		return render.SystemMemberDeiete(self.number)
	def POST(self):
		self.i = web.input()
		sql = "DELETE FROM member_information "
		sql += "WHERE phone = '" + self.i.account + "'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/SetUp')

#---# 2__Report__
class SystemReportDay:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.hour = []
		self.Humidity = []
		self.TemperC = []
		self.TemperF = []
		self.sensor = []
		self.Air = []
		self.Dust = []
		self.ampere = []
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
		self.dictionarName = {	'Humidity'	: "濕度", 
								'TemperC'	: "溫度(攝氏)",
								'TemperF'	: "溫度(華視)", 
								'sensor'	: "可燃氣",
								'Air'		: "空氣清晰度", 
								'Dust'		: "粉成濃度",
								'ampere'	: "安培量", }
		self.dictionarClass = {	'Humidity'	: self.Humidity, 
								'TemperC'	: self.TemperC,
								'TemperF'	: self.TemperF, 
								'sensor'	: self.sensor,
								'Air'		: self.sensor, 
								'Dust'		: self.Dust,
								'ampere'	: self.Dust, }
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
			str_cks +=", " +  ck
		sql = "SELECT year, month, day, hour" + str_cks + " FROM monitoring_value"
		sql += " WHERE year = '" + Y + "' AND month = '" + M + "' AND day = '" + D + "'"
		print(sql)
		
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.hour.append(row[3])
   			num = 4
   			for ck in cks:
   				self.dictionarClass[str(ck)].append(row[num])
   				num +=1
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
   			sheet1.write(0, num	 , self.dictionarName[str(ck)].decode('utf-8'))
   			num +=1
		for c in range(1,len(self.year)):
			sheet1.write(c,0, self.year[c-1])
			sheet1.write(c,1, self.month[c-1])
			sheet1.write(c,2, self.day[c-1])
			sheet1.write(c,3, self.hour[c-1])
			l = 4
			for ck in cks:
				sheet1.write(c,l  , self.dictionarClass[str(ck)][c-1])
   				l += 1
		#保存該excel文件
		A = str(self.DownloadAddress) + "/Day" + Y + "_" + M + "_" + D + ".xls"
		workbook.save(A)
		print("創建excel文件完成!".decode('utf-8'))
		path = str(self.DownloadIP) +  "/Day" + Y + "_" + M + "_" + D + ".xls"
		log = "yes"
		return self.render.SystemReportDay(path, log)
class SystemReportWeek:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.hour = []
		self.Humidity = []
		self.TemperC = []
		self.TemperF = []
		self.sensor = []
		self.Air = []
		self.Dust = []
		self.ampere = []
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
		self.dictionarName = {	'Humidity'	: "濕度", 
								'TemperC'	: "溫度(攝氏)",
								'TemperF'	: "溫度(華視)", 
								'sensor'	: "可燃氣",
								'Air'		: "空氣清晰度", 
								'Dust'		: "粉成濃度",
								'ampere'	: "安培量", }
		self.dictionarClass = {	'Humidity'	: self.Humidity, 
								'TemperC'	: self.TemperC,
								'TemperF'	: self.TemperF, 
								'sensor'	: self.sensor,
								'Air'		: self.sensor, 
								'Dust'		: self.Dust,
								'ampere'	: self.Dust, }
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
			str_cks +=", " + ck
		sql = "SELECT year, month, day, hour" + str_cks + " FROM monitoring_value"
		sql	+= " WHERE year = '" + Y + "' AND month = '" + M +"' AND day IN ("
		sql	+= "'" + str(int(D)) + "', '"+ str(int(D)+1) + "', '"+ str(int(D)+2) + "', '"+ str(int(D)+3) + "', '"+ str(int(D)+4) + "', '"+ str(int(D)+5) + "', '"+ str(int(D)+6) + "')"
		print(sql)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.hour.append(row[3])
   			num = 4
   			for ck in cks:
   				self.dictionarClass[str(ck)].append(row[num])
   				num +=1
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
   			sheet1.write(0, num	 , self.dictionarName[str(ck)].decode('utf-8'))
   			num +=1
		for c in range(1,len(self.year)):
			sheet1.write(c,0, self.year[c-1])
			sheet1.write(c,1, self.month[c-1])
			sheet1.write(c,2, self.day[c-1])
			sheet1.write(c,3, self.hour[c-1])
			l = 4
			for ck in cks:
				sheet1.write(c,l  , self.dictionarClass[str(ck)][c-1])
   				l += 1
		#保存該excel文件
		A = str(self.DownloadAddress) + "/Week" + Y + "_" + M + "_" + D + "_" + str(int(D)+6) + ".xls"
		workbook.save(A)
		print("創建excel文件完成!".decode('utf-8'))
		path = str(self.DownloadIP) + "/Week" + Y + "_" + M + "_" + D + "_" + str(int(D)+6) + ".xls"
		log = "yes"
		return self.render.SystemReportWeek(path, log)
class SystemReportMonth:
	def __init__(self):
		#Value definition
		self.year = []
		self.month = []
		self.day = []
		self.hour = []
		self.Humidity = []
		self.TemperC = []
		self.TemperF = []
		self.sensor = []
		self.Air = []
		self.Dust = []
		self.ampere = []
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
		self.dictionarName = {	'Humidity'	: "濕度", 
								'TemperC'	: "溫度(攝氏)",
								'TemperF'	: "溫度(華視)", 
								'sensor'	: "可燃氣",
								'Air'		: "空氣清晰度", 
								'Dust'		: "粉成濃度",
								'ampere'	: "安培量", }
		self.dictionarClass = {	'Humidity'	: self.Humidity, 
								'TemperC'	: self.TemperC,
								'TemperF'	: self.TemperF, 
								'sensor'	: self.sensor,
								'Air'		: self.sensor, 
								'Dust'		: self.Dust,
								'ampere'	: self.Dust, }
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
			str_cks +=", " + ck
		sql = "SELECT year, month, day, hour" + str_cks + " FROM monitoring_value"
		sql += " WHERE year = '" + Y + "' AND month = '" + M + "'"
		print(sql)
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.year.append(row[0])
   			self.month.append(row[1])
   			self.day.append(row[2])
   			self.hour.append(row[3])
   			num = 4
   			for ck in cks:
   				self.dictionarClass[str(ck)].append(row[num])
   				num +=1
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
   			sheet1.write(0, num	 , self.dictionarName[str(ck)].decode('utf-8'))
   			num +=1
		for c in range(1,len(self.year)):
			sheet1.write(c,0, self.year[c-1])
			sheet1.write(c,1, self.month[c-1])
			sheet1.write(c,2, self.day[c-1])
			sheet1.write(c,3, self.hour[c-1])
			l = 4
			for ck in cks:
				sheet1.write(c,l  , self.dictionarClass[str(ck)][c-1])
   				l += 1
		#保存該excel文件
		A = str(self.DownloadAddress) + "/Month" + Y + "_" + M + ".xls"
		workbook.save(A)
		print("創建excel文件完成!".decode('utf-8'))
		path = str(self.DownloadIP) + "/Month" + Y + "_" + M + ".xls"
		log = "yes"
		return self.render.SystemReportMonth(path, log)

#---# 3__Set__

class SystemSetUp():
	def __init__(self):
		#Value definition
		self.mode = []
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		self.host_ip = conf.get("host", "ip")
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")

	def GET(self):
		render = web.template.render("view")
		if session.logged_in == False:
			raise web.seeother('/')

		return self.render.SystemSetUp(self.host_ip)
	def POST(self):
		i = web.input()
		if i.postdata == "UandP":
			return self.UandP()
		elif i.postdata == "homedata":
			return self.homedata()

	def UandP(self):
		sql = "SELECT account, password FROM top"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
		dbuasr = data[0][0]
		dbpass = data[0][1]
		v = {'user':dbuasr, 'pass':dbpass}
		web.header('Content-Type', 'application/json')
		return json.dumps(v)

	def homedata(self):
		sql = "SELECT phone,email,card FROM member_information"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()

   		for row in data:
   			v = {'phone':str(row[0]), 'email':str(row[1]), 'card':str(row[2])}
   			self.mode.append(v)
   		self.db.close()

		web.header('Content-Type', 'application/json')
		return json.dumps(self.mode)
class SystemSetUpdata():
	def __init__(self):
		#Databse definition
		conf = ConfigParser.ConfigParser()
		conf.read("test.conf")
		IPAddress 		= conf.get("MySQL Database", "IP address"		)
		AccountNumber 	= conf.get("MySQL Database", "account number"	)
		Password 		= conf.get("MySQL Database", "password"			)
		DataSheet 		= conf.get("MySQL Database", "Data sheet"		)
		self.host_ip = conf.get("host", "ip")
		
		self.db = MySQLdb.connect(IPAddress,AccountNumber,Password,DataSheet,charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")
	
	def GET(self):
		if session.logged_in == False:
			raise web.seeother('/')

		return self.render.SystemSetUpdate(self.host_ip)
	def POST(self):
		self.i = web.input()

		sql = "UPDATE top SET "
		sql += "account='" + self.i.account + "' Limit 1"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()

		sql = "UPDATE top SET "
		sql += "password='" + self.i.password + "' Limit 1"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()

		self.db.close()

		raise web.seeother('/SetUp')
class SystemSetUpcard:
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

		sql = "SELECT phone FROM member_information"
		self.cursor.execute(sql)
		data = self.cursor.fetchall()
   		for row in data:
   			self.number.append(row[0])
   		self.db.close()

		return render.SystemSetUpcard(self.number)
	def POST(self):
		self.i = web.input()
		sql = "UPDATE member_information SET card = \'None\' WHERE phone=\'" + self.i.account + "\'"
		print(sql)
		self.cursor.execute(sql)
		self.db.commit()
		self.db.close()
		raise web.seeother('/SetUp')

if __name__ == '__main__':
	# host_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname(  )))
	# host_ip = "192.168.1.126"

	#config
	# fh = open("test.conf","r+")
	# conf = ConfigParser.ConfigParser()
	# conf.read("test.conf")
	# conf.set("host","ip",'http://' + host_ip + ':8001')
	# fh.close()

	# fo = open('css_js/ui.css','r+')
	# fo.seek(77, 1)
	# ip = host_ip
	# number = 15 - len(ip)
	# if number != 0:
	# 	for x in range(0,number):
	# 		ip = ip + " "
	# fo.write(ip);

	# os_name = platform.system()
	# if os_name == 'Windows':
	# 	host_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname(  )))
	# 	print(host_ip)
	# 	conf.set("host","ip",'http://' + host_ip + ':8000')
	# 	conf.write(fh)
	# 	fh.close()
	# elif os_name == 'Linux':
	# 	ifname = 'wlan0'
	# 	skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# 	pktString = fcntl.ioctl(skt.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
	# 	ipString  = socket.inet_ntoa(pktString[20:24])
	# 	print(ipString)
	# 	conf.set("host","ip",'http://' + ipString + ':8000')
	# 	conf.write(fh)
	# 	fh.close()

	app.run()