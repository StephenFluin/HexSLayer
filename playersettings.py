import json, random

class PlayerSettings():
	
	
	
	def __init__(self):
		self.prefs = {}
		self.settingsFile = "playersettings.cnf"
		
		self.load()
		
	
	
	def load(self):
		try:
			f = open(self.settingsFile,'r')
			self.prefs.update( json.loads(f.read()))
			print "Loaded settings. Prefs is now %s." % (self.prefs)
			f.close()
		except IOError:
			print "No such player settings file yet."
			self.create()
		
	def create(self):
		#Track tutorial and create player ID to uniquely identify players in Multiplayer
		self.prefs = {"skipTutorial":False}
		self.save()
		
	def save(self):
		try:
			f = open(self.settingsFile,'w')
			f.write(json.dumps(self.prefs))
			f.close()
		except IOError as (errno, strerror):
			print "I/O error({0}): {1}".format(errno, strerror)
			
	def udpate(self,name,value):
		self.prefs[name] = value
		self.save()
			
	def getPlayerId(self):
		if not "playerId" in self.prefs:
			self.prefs["playerId"] = random.randint(1000,1000000000000)
		self.save()
		return self.prefs["playerId"]
	def isOptOut(self):
		return "optOut" in self.prefs
		
			
