#!/usr/bin/env python
# -*-coding:utf-8 -*-
import web
import json
import time
import rsa
import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

urls = (
	'/ui', 'ui',
	'/jquery-tablepage', 'jquerytablepage',
	'/', 'Login',													# Login page
	'/login', 'Login',												# Login to judge
	'/logout', 'Logout',											# Sign out
	'/CurrentState'		,'EnvironmentCurrentState',
	'/PastValueTable'	,'EnvironmentPastValueTable',
	'/PastValueFigure'	,'EnvironmentPastValueFigure',
	'/DoorLock'			,'SafetyDoorLock',
	'/Monitor'			,'SafetyMonitor',
	'/EventRecord'		,'SafetyEventRecord',
	'/Member'			,'SystemMember',
	'/Member/Quire'		,'SystemMemberQuire',
	'/Member/Add'		,'SystemMemberAdd',
	'/Member/Modify'	,'SystemMemberModify',
	'/Member/Delete'	,'SystemMemberDeiete',
	'/Event'			,'SystemEvent',
	'/SystemReportDay'	,'SystemReportDay',
	'/SystemReportWeek'	,'SystemReportWeek',
	'/SystemReportMonth','SystemReportMonth'

)

web.config.debug = False
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))      

#################################################
							#		CSS,JS		#
							#####################
class ui:
	def GET(self):
		render = web.template.render("css_js")
		return render.ui()
class jquerytablepage:
	def GET(self):
		render = web.template.render("css_js")
		return render.jqueryTablepage()

#########################################################
							#		Log in, log out		#(ERROR!!!)
							#############################
class Login:
	session['privkey'] = None
	def GET(self):
		render = web.template.render("view")
		(pub_key, priv_key) = rsa.newkeys(256)
		self.pubkey_e = hex(pub_key.e)
		self.pubkey_n = hex(pub_key.n)
		session['privkey'] = priv_key
		print(session['privkey'])
		print("\n")
		print("e:"+self.pubkey_e)
		print("n:"+self.pubkey_n)
		print("--------------------------------------------")
		return render.SignIn(self.pubkey_e, self.pubkey_n)
	
	def POST_error(self):
		render = web.template.render("view")
		i = web.input()
		username = i.user
		en_password = i.password
		print("client：")
		print(username)
		print(en_password)
		print("--------------------------------------------")
		priv_key = session['privkey']
		print(priv_key)
		session['privkey'] = None
		password = rsa.decrypt(en_password.decode('hex'),priv_key)
		
		print(password)
	def POST(self):
		session.logged_in = True
		raise web.seeother('/CurrentState')
#		if i.user == '1' and i.password =='1':
#			session.logged_in = True
#			raise web.seeother('/CurrentState')
#		else:
#			session.logged_in = False
#			raise web.seeother('/')
		
		
class Logout:
    def GET(self):
        session.logged_in = False
        raise web.seeother('/')

#####################################################################
							#		Environmental monitoring		#		   
							#########################################
class EnvironmentCurrentState:
	
	def __init__(self):
		self.T = 26
		self.H = 60
		self.G = 200
		self.A = 250
		self.C = 0.6
		self.CD = 32.1
	
	def GET(self):
		render = web.template.render("view")
		
		if session.get('logged_in', False):
			return render.EnvironmentCurrentState(self.T,self.H,self.G,self.A,self.C,self.CD)
        
		raise web.seeother('/')
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
		self.db = MySQLdb.connect("127.0.0.1","root","root","topic",charset="utf8")
		self.cursor = self.db.cursor()
		#Template definition
		self.render = web.template.render("view")

	def GET(self):
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
	def GET(self):
		render = web.template.render("view")
		return render.EnvironmentPastValueFigure()

#############################################################
							#		 Safety monitoring		#
							#################################
class SafetyDoorLock:
	def GET(self):
		render = web.template.render("view")
		return render.SafetyDoorLock()
class SafetyMonitor:
	def GET(self):
		render = web.template.render("view")
		return render.SafetyMonitor()
class SafetyEventRecord:
	def GET(self):
		render = web.template.render("view")
		return render.SafetyEventRecord()
		
#########################################################
							#		System program		#
							#############################
#---# 1__Member__
class SystemMemberQuire:
	def GET(self):
		render = web.template.render("view")
		return render.SystemMemberQuire()
class SystemMemberAdd:
	def GET(self):
		render = web.template.render("view")
		return render.SystemMemberAdd()
class SystemMemberModify:
	def GET(self):
		render = web.template.render("view")
		return render.SystemMemberModify()
class SystemMemberDeiete:
	def GET(self):
		render = web.template.render("view")
		return render.SystemMemberDeiete()

#---# 2__Event__
class SystemEvent:
	def GET(self):
		render = web.template.render("view")
		return render.SystemEvent()
	# 3__Report__
class SystemReportDay:
	def GET(self):
		render = web.template.render("view")
		return render.SystemReportDay()

	def POST(self):
		i = web.input(Checkbox=[])
		Y, M, D = i.Y, i.M, i.D
		cks = i.get('Checkbox','')
		print(cks)
		print(Y+">>"+M+">>"+D)
		return render.SystemReportDay()
class SystemReportWeek:
	def GET(self):
		render = web.template.render("view")
		return render.SystemReportWeek()

	def POST(self):
		i = web.input(Checkbox=[])
		Y, M, D = i.Y, i.M, i.D
		cks = i.get('Checkbox','')
		print(cks)
		print(Y+">>"+M+">>"+D)
		return render.SystemReportWeek()
class SystemReportMonth:
	def GET(self):
		render = web.template.render("view")
		return render.SystemReportMonth()

	def POST(self):
		i = web.input(Checkbox=[])
		Y, M = i.Y, i.M
		cks = i.get('Checkbox','')
		print(cks)
		print(Y+">>"+M)
		return render.SystemReportMonth()

if __name__ == '__main__':
	app.run()