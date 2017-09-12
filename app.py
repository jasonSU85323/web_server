#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import json
import time
import rsa
import MySQLdb

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

							#####################
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


							#############################
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


							#########################################
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
		self.year = []
		self.month = []
		self.day = []
		self.time_hour = []
		self.temp_v = []
		self.temp_s = []
		self.db = MySQLdb.connect("127.0.0.1","root","root","topic" )
		self.cursor = self.db.cursor()
#		self.strT = []
#		self.strH = []
#		self.strG = []
#		self.strA = []
#		with open('from.json', 'r') as f:
#			self.data = json.load(f,"UTF-8")
#
#		for i in range(0,4,1):
#			self.strT.append([self.data['temperature'][i][0]		,self.data['temperature'][i][1]		,self.data['temperature'][i][2]])
#			self.strH.append([self.data['humidity'][i][0]			,self.data['humidity'][i][1]		,self.data['humidity'][i][2]])
#			self.strG.append([self.data['gasConcentration'][i][0]	,self.data['gasConcentration'][i][1],self.data['gasConcentration'][i][2]])
#			self.strA.append([self.data['airClarity'][i][0]			,self.data['airClarity'][i][1]		,self.data['airClarity'][i][2]])

		self.render = web.template.render("view")

	def GET(self):
		#print(self.strT)
		#time.sleep(5)
		#$def with(str, date_y, date_m, date_d, time, data_v, data_s)
		#------MySQL-----
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
   		for i in range(0,10):
   			print(self.year[i]+"/"+self.month[i]+"/"+self.day[i]+" Time:"
   				+self.time_hour[i]+":00---!!!^_^")
   		self.db.close()

		#return self.render.EnvironmentPastValueTable("溫度", "2017", "9", "1", "13", "25", "涼爽")

		
	def POST(self):
		i = web.input()

		if i.Submit == "temperature":
			self.temperature(i.Y, i.M, i.D)
			#print(self.strT)
			#time.sleep(5)
			return self.render.EnvironmentPastValueTable(self.strT, self.strH, self.strG, self.strA)
		elif i.Submit == "humidity":
			self.humidity(i.Y, i.M, i.D)
			return self.render.EnvironmentPastValueTable(self.strT, self.strH, self.strG, self.strA)
		elif i.Submit == "gasConcentration":
			self.gasConcentration(i.Y, i.M, i.D)
			return self.render.EnvironmentPastValueTable(self.strT, self.strH, self.strG, self.strA)
		elif i.Submit == "airClarity":
			self.airClarity(i.Y, i.M, i.D)
			return self.render.EnvironmentPastValueTable(self.strT, self.strH, self.strG, self.strA)
	def temperature(self, Y, M, D):
		self.strT = []


		for i in range(1, 8, 1):
			self.strT.append([i, 9+i, D])
		web.setcookie('strCT', self.strT, 60*60*24*365)			
		#print(self.strT)
		#for a in self.strT:
		#	print(str(a[0])+"__"+str(a[1])+"__"+str(a[2])+"\n")
		

	def humidity(self, Y, M, D):
		for i in self.strH:
			i.pop()

		for i in range(1, 8, 1):
			self.strH.append([i, 9+i, 7+i])
		web.setcookie('strCH', self.strH, 60*60*24*365)
	def gasConcentration(self, Y, M, D):
		for i in self.strG:
			i.pop()

		for i in range(1, 8, 1):
			self.strG.append([i, 9+i, 7+i])
		web.setcookie('strCG', self.strG, 60*60*24*365)
	def airClarity(self, Y, M, D):
		for i in self.strA:
			i.pop()

		for i in range(1, 8, 1):
			self.strA.append([i, 9+i, 7+i])
		web.setcookie('strCA', self.strA, 60*60*24*365)
class EnvironmentPastValueFigure:
	def GET(self):
		render = web.template.render("view")
		return render.EnvironmentPastValueFigure()
							#################################
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

		
							#############################
							#		System program		#
							#############################
	# 1__Member__
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
	# 2__Event__
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