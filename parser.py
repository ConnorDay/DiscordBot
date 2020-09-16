import re
from datetime import datetime

def word(message):
	spl = message.split(" ", maxsplit=1)
	return spl if len(spl) == 2 else [spl[0],""]

def integer(message):
	spl = word(message)
	try:
		spl[0] = int(spl[0])
	except:
		spl = ["", message]
	finally:
		return spl

def date(message):
	spl = word(message)
	try:
		d = datetime.strptime(spl[0], '%m/%d/%y')
	except:
		try:
			d = datetime.strptime(spl[0], '%m/%d/%Y')
		except:
			return ["", message]
	spl[0] = d.date()
	return spl

def time(message):
	spl = word(message)
	try:
		t = datetime.strptime(spl[0], '%I:%M%p')
	except:
		try:
			t = datetime.strptime(spl[0], '%H:%M')
		except:
			return ["", message]
	spl[0] = t.time()
	return spl

def dateTime(message):
	spl = message.split()
	if len(spl) < 2:
		return ["", message]
	d = date(spl[0])[0]
	if not d:
		return ["", message]
	t = time(spl[1])[0]
	if not t:
		return ["", message]
	res = datetime( d.year, d.month, d.day, t.hour, t.minute)
	return [res, spl[2:]]
	
def user(message):
	spl = word(message)
	res = re.match('<@!(\d+)>', spl[0])
	if res:
		return [ int(res[1]), spl[1] ]
	else:
		return ["", message]

def role(message):
	spl = word(message)
	res = re.match('<@&(\d+)>', spl[0])
	if res:
		return [ int(res[1]), spl[1] ]
	else:
		return ["", message]

def channel(message):
	spl = word(message)
	res = re.match('<#(\d+)>', spl[0])
	if res:
		return [ int(res[1]), spl[1] ]
	else:
		return ["", message]

def all(message):
	return [message, ""]
