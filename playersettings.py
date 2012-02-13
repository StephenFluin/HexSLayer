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
			f.close()
		except IOError:
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
			
	def update(self,name,value):
		self.prefs[name] = value
		self.save()
			
	def getPlayerId(self):
		if not "playerId" in self.prefs:
			self.prefs["playerId"] = random.randint(1000,1000000000000)
			self.save()
		return self.prefs["playerId"]
	def isOptOut(self):
		return "optOut" in self.prefs
	
	def getGameData(self):
		if not "gameData" in self.prefs:
			return None
		return self.prefs["gameData"]

	def getShowTutorialFlag(self):
		if not "tutorialFlag" in self.prefs:
			self.prefs["showTutorialFlag"] = True
			self.save()
		return self.prefs["showTutorialFlag"]
		
	def getPlayerStat(self,stat):
		if not "playerStats" in self.prefs:
			self.prefs["playerStats"] = {}
			self.save()
		if stat in self.prefs["playerStats"]:
			return self.prefs["playerStats"][stat]
		else:
			return 0
	def setPlayerStat(self,stat,value):
		if not "playerStats" in self.prefs:
			self.prefs["playerStats"] = {}
			self.save()
		self.prefs["playerStats"][stat] = value
		self.save()
	
			
