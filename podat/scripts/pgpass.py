# pgpass.py
#
# Contains classes and functions to load the pgpass.conf file for postgresql
#

import os

class Pgpass(object):
	def __init__(self, str):
		self.entry = str
		self.host = None
		self.port = 0
		self.database = None
		self.username = None
		self.password = None
		self.isValid = self.parseEntry()

	def parseEntry(self):
		isValid = True
		indices = []

		escaped = False
		for index, char in enumerate(self.entry):
			if char == '\\':
				escaped = True		# only remains true to the next character
			elif char == ':':
				if not escaped:
					indices.append(index)

				escaped = False
			else:
				escaped = False

		if len(indices) == 4:
			try:
				self.host = self.entry[:indices[0]]
				self.port = int(self.entry[(indices[0] + 1):indices[1]])
				self.database = self.entry[(indices[1] + 1):indices[2]]
				self.username = self.entry[(indices[2] + 1):indices[3]]
				self.password = self.entry[(indices[3] + 1):]
			except:
				isValid = False
		else:
			isValid = False

		return isValid

class PgpassLoader(object):
	config = None
	if (os.name == "nt"):	#windows
		config = os.getenv("APPDATA") + r"\postgresql\pgpass.conf"
	else:	#for unix (name='posix')
		config = os.environ["HOME"] + r"/.pgpass"

	def __init__(self):
		self.entries = []
		self.configExists = False
		self.osLoaded = True
		try:
			self.configExists = os.path.isfile(self.config)
		except:
			self.osLoaded = False
		self.loadConfig()

	def loadConfig(self):
		if self.configExists:
			with open(self.config) as file:
				lines = file.readlines()
				for line in lines:
					sLine = line.strip()
					if not sLine.startswith('#'):
						self.entries.append(Pgpass(sLine))

	# user is required - db, host, and port narrow down the selection(s)
	def getEntry(self, user, db, host, port):
		entries = []

		for entry in self.entries:
			if entry.username == user:
				if not db == None:
					if entry.database == db:
						if not host == None:
							if entry.host == host:
								if not port == 0:
									if entry.port == port:
										entries.append(entry)
								else:
									entries.append(entry)
						else:
							entries.append(entry)
				else:
					entries.append(entry)

		return entries
