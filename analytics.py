from __future__ import absolute_import
import six.moves.http_client, six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error, json
from playersettings import *

def trackEvent(event, message={}):
	try:
		settings = PlayerSettings()
		
		if not settings.isOptOut():
			i = settings.getPlayerId()
			conn = six.moves.http_client.HTTPConnection("mortalpowers.com",80,timeout=2)
			
			conn.request("GET","/event.php?i=%s&e=%s&m=%s" % (i,six.moves.urllib.parse.quote(event),six.moves.urllib.parse.quote(json.dumps(message))))
			r1 = conn.getresponse()
			conn.close()
	except:
		pass