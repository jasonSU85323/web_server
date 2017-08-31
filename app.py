#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import json
import time

urls = (
	'/ui', 'ui',
	'/jquery-tablepage', 'jquerytablepage',
	'/', 'SignIn',													# Login page
	'/login', 'Login',												# Login to judge
	'/logout', 'Logout',											# Sign out

	'/CurrentState'		,'EnvironmentCurrentState',
	'/PastValueTable'	,'EnvironmentPastValueTable',
	'/PastValueFigure'	,'EnvironmentPastValueFigure',
	'/DoorLock'			,'SafetyDoorLock',
	'/Monitor'			,'SafetyMonitor',
	'/EventRecord'		,'SafetyEventRecord',
	'/Member'			,'SystemMember',
	'/Event'			,'SystemEvent',
	'/Report'			,'SystemReport'
)

web.config.debug = False
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))      

class ui:
	def GET(self):
		render = web.template.render("css_js")
		return render.ui()
class jquerytablepage:
	def GET(self):
		render = web.template.render("css_js")
		return render.jquery-tablepage()
#############################
#		Log in, log out		#
#############################
class Login:
    def POST(self):
        render = web.template.render("view")
        i = web.input()
        if i.user == '1' and i.password =='1':
            session.logged_in = True
            raise web.seeother('/CurrentState')
        else:
            session.logged_in = False
            raise web.seeother('/')
		
class Logout:
    def GET(self):
        session.logged_in = False
        raise web.seeother('/')

class SignIn:
	def GET(self):
		render = web.template.render("view")
		return render.SignIn()
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
		self.strT = []
		self.strH = []
		self.strG = []
		self.strA = []
		with open('from.json', 'r') as f:
			self.data = json.load(f,"UTF-8")

		for i in range(0,4,1):
			self.strT.append([self.data['temperature'][i][0]		,self.data['temperature'][i][1]		,self.data['temperature'][i][2]])
			self.strH.append([self.data['humidity'][i][0]			,self.data['humidity'][i][1]		,self.data['humidity'][i][2]])
			self.strG.append([self.data['gasConcentration'][i][0]	,self.data['gasConcentration'][i][1],self.data['gasConcentration'][i][2]])
			self.strA.append([self.data['airClarity'][i][0]			,self.data['airClarity'][i][1]		,self.data['airClarity'][i][2]])

		self.render = web.template.render("view")

	def GET(self):
		#print(self.strT)
		#time.sleep(5)
		return self.render.EnvironmentPastValueTable(self.strT, self.strH, self.strG, self.strA)
		
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
class SystemMember:
	def GET(self):
		render = web.template.render("view")
		return render.SystemMember()
class SystemEvent:
	def GET(self):
		render = web.template.render("view")
		return render.SystemEvent()
class SystemReport:
	def GET(self):
		render = web.template.render("view")
		return render.SystemReport()
if __name__ == '__main__':
	app.run()