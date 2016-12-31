#
# prov_classes.py
#

import json_extension as js
from datetime import datetime
import os

next_id = {
	"prov_statute": 0,
	"prov_location": 0,
	"prov_crime": 0
}

class DBHelper(object):
	@classmethod
	def get_next_id(cls, pgConnect, table, force = False):
		next = 0
		if (next_id[table] == 0) or (force == True):
			where = """table_name = '{0}'""".format(table)
			next = pgConnect.select("prov_next_id", ["*"], where)[1][1]
		else:
			next = next_id[table]
		
		next_id[table] = next + 1
		
		return next
	
	@classmethod
	def update_next_id(cls, pgConnect, table, id):
		columns = ["next_id", "date_stored"]
		values = [id, str(datetime.utcnow())]
		where = """table_name = '{0}'""".format(table)
		pgConnect.update("prov_next_id", columns, values, where)
	
	# Will eventually add the location to the database but needs a geocoding function
	@classmethod
	def get_location_id(cls, pgConnect, location):
		id = 0
		
		where = """original_address LIKE '%{0}%'""".format(location)
		rows = pgConnect.select("prov_location", ["id"], where)
		
		if len(rows) == 1:		# only headers
			jStr = """""".format()
		else:
			id = rows[1][0]
		
		return id
	
	
	# Will also add the statute to the database
	@classmethod
	def get_statute_id(cls, pgConnect, statute_code, statute_desc):
		id = 0
		
		where = """statute_code = '{0}'""".format(statute_code)
		rows = pgConnect.select("prov_statute", ["id"], where)
		
		if len(rows) == 1:		# only headers
			jStr = """{{"statute_code":"{0}","statute_desc":"{1}"}}""".format(statute_code, statute_desc)
			stat = Statute(jStr, cls.get_next_id(pgConnect, "prov_statute"), pgConnect)
			stat.insert()
			id = stat.id
			cls.update_next_id(pgConnect, "prov_statute", (id + 1))
		else:
			id = rows[1][0]
		
		return id

class DBInterface(object):
	def __init__(self, jsonStr, id, pgConnect = None, table = None):
		self.__dict__ = js.json_loads_byteified(jsonStr)
		self.id = id
		self.properties = self.__dict__.keys()		# store the properties generated from the json (and id)
		self.pgConnect = pgConnect
		self.table = table
		self.columns = []
		self.values = []
		
		if not hasattr(self, "date_stored"):
			self.date_stored = str(datetime.utcnow())
	
	def __getitem__(self, property):
		return self.__dict__[property]
	
	def print_properties(self):
		for prop in self.properties:
			print "{0} = {1}".format(prop, self[prop])
		return
	
	def print_table(self):
		if not self.pgConnect == None:
			if not self.table == None:
				rows = self.pgConnect.select(self.table)
				self.pgConnect.print_rows(rows)
			else:
				print "No database table name provided"
		else:
			print "No connection to PostgreSQL database provided"
			
	def get_columns(self, asString = False):
		if asString == True:
			return ", ".join(self.columns)
		else:
			return self.columns
	
	def get_values(self, asDbString = False):
		if asDbString == True:
			newValues = [None]*len(self.values)
			for index, val in enumerate(self.values):
				valType = type(val)
				if (type(0) == valType) or (type(0.1) == valType):
					newValues[index] = str(val)
				elif type("") == valType:
					newValues[index] = "'{0}'".format(val)
				else:
					newValues[index] = val
			
			return ", ".join(newValues)
		else:
			return self.values
	
	def insert(self):
		if not self.pgConnect == None:
			if not self.table == None:
				self.pgConnect.insert(self.table, self.get_columns(), self.get_values())
			else:
				print "No database table name provided"
		else:
			print "No connection to PostgreSQL database provided"

class Statute(DBInterface):
	def __init__(self, jsonStr, id, pgConnect = None):
		DBInterface.__init__(self, jsonStr, id, pgConnect, "prov_statute")
		self.columns = ["id", "statute_code", "statute_desc", "date_stored"]
		self.values = self.get_values_list()
	
	def get_values_list(self):
		return [
			int(self["id"]),
			self["statute_code"],
			self["statute_desc"],
			self["date_stored"]
		]

class Address(DBInterface):
	def __init__(self, jsonStr, id, pgConnect = None):
		DBInterface.__init__(self, jsonStr, id, pgConnect, "prov_location")
		self.columns = [
			"id",
			"number",
			"street",
			"suffix",
			"formatted_street",
			"city",
			"county",
			"state",
			"zip",
			"country",
			"formatted_address",
			"latitude",
			"longitude",
			"accuracy",
			"accuracy_type",
			"source",
			"addresses_returned",
			"original_address",
			"date_geocoded",
			"date_stored"
		]
		self.values = self.get_values_list()
		
	def get_values_list(self):
		if not "number" in self.address_components:
			self.address_components["number"] = ""
		if not "street" in self.address_components:
			self.address_components["street"] = ""
		if not "suffix" in self.address_components:
			self.address_components["suffix"] = ""
		if not "formatted_street" in self.address_components:
			self.address_components["formatted_street"] = ""
			
		aComps = self["address_components"]
		lComps = self["location"]
		
		return [
			int(self["id"]),
			aComps["number"],
			aComps["street"],
			aComps["suffix"],
			aComps["formatted_street"],
			aComps["city"],
			aComps["county"],
			aComps["state"],
			aComps["zip"],
			aComps["country"],
			self["formatted_address"],
			float(lComps["lat"]),
			float(lComps["lng"]),
			float(self["accuracy"]),
			self["accuracy_type"],
			self["source"],
			int(self["addresses_returned"]),
			self["original_address"],
			self["date_geocoded"],
			self["date_stored"]
		]

class Crime(DBInterface):
	def __init__(self, jsonStr, id, pgConnect = None):
		DBInterface.__init__(self, jsonStr, id, pgConnect, "prov_crime")
		self.columns = [
			"id",
			"location_id",
			"case_number",
			"counts",
			"month",
			"offense_desc",
			"reported_date",
			"reporting_officer",
			"statute_id",
			"year",
			"original_address",
			"date_stored"
		]
		if not hasattr(self, "location_id"):
			if hasattr(self, "location"):
				self.location_id = DBHelper.get_location_id(self.pgConnect, self["location"])
			else:
				self.location_id = 0
				self.location = ""
		
		if not hasattr(self, "statute_id"):
			self.statute_id = DBHelper.get_statute_id(self.pgConnect, self["statute_code"], self["statute_desc"])
		
		if not hasattr(self, "reporting_officer"):
			self.reporting_officer = ""
		if not hasattr(self, "original_address"):
			self.original_address = self["location"]
		
		self.values = self.get_values_list()
	
	def get_values_list(self):
		return [
			int(self["id"]),
			int(self["location_id"]),	#add
			self["casenumber"],
			int(self["counts"]),
			int(self["month"]),
			self["offense_desc"],
			self["reported_date"],
			self["reporting_officer"],
			int(self["statute_id"]),	#add
			int(self["year"]),
			self["original_address"],
			self["date_stored"]
		]

class ACollection(object):
	@classmethod
	def add_addresses(self, table, path, pgConnect, debug = False):
		if os.path.isfile(path):
			with open(path) as file:
				lines = file.readlines()
				numLines = len(lines)
				
				for index, line in enumerate(lines):
					if debug == True:
						print "Line {0} of {1}".format(str(index), str(numLines))
					
					sLine = line.strip()
					if sLine.startswith("~*"):
						# enter partial location data
						arry = sLine.split("~*")
						addRet = int(arry[1])
						orig = arry[2]
						cols = ["id", "latitude", "longitude", "addresses_returned", "original_address", "date_stored"]
						vals = [DBHelper.get_next_id(pgConnect, table), 0.0, 0.0, addRet, orig, str(datetime.utcnow())]
						pgConnect.insert(table, cols, vals)
					elif not sLine == "":
						# convert from json and insert
						addr = Address(sLine, DBHelper.get_next_id(pgConnect, table), pgConnect)
						addr.insert()
				if not next_id[table] == 0:
					DBHelper.update_next_id(pgConnect, table, next_id[table])
					
	@classmethod
	def add_crime_data(self, path, pgConnect, debug = False):
		table = "prov_crime"
		
		if os.path.isfile(path):
			with open(path) as file:
				lines = file.readlines()
				numLines = len(lines)
				
				for index, line in enumerate(lines):
					if debug == True:
						print "Line {0} of {1}".format(str(index), str(numLines))
					
					sLine = line.strip()
					crim = Crime(sLine, DBHelper.get_next_id(pgConnect, table), pgConnect)
					crim.insert()
				if not next_id[table] == 0:
					DBHelper.update_next_id(pgConnect, table, next_id[table])
