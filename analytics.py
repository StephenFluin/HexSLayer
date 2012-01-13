import httplib, urllib, json
from playersettings import *

def trackEvent(event, message={}):
	try:
		settings = PlayerSettings()
		
		if not settings.isOptOut():
			i = settings.getPlayerId()
			conn = httplib.HTTPConnection("mortalpowers.com",80,timeout=2)
			
			conn.request("GET","/event.php?i=%s&e=%s&m=%s" % (i,urllib.quote(event),urllib.quote(json.dumps(message))))
			r1 = conn.getresponse()
			conn.close()
	except:
		pass