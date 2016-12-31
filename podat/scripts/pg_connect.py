# pg_connect.py
#
# Work with PostgreSQL and Pyscopg
#

import sys
from sys import version_info
import psycopg2
import pgpass

class PgConnect(object):
	def __init__(self):
		self.user = None
		self.dbname = None
		self.host = None
		self.password = None
		self.port = 0
		self.connStr = "host='{0}' port='{1}' dbname='{2}' user='{3}' password='{4}'"
		self.connection = None

	@classmethod
	def with_user(cls, user):
		pgc = cls()
		pgc.user = user
		pgc.connect()
		return pgc
	@classmethod
	def with_user_db(cls, user, dbname):
		pgc = cls()
		pgc.user = user
		pgc.dbname = dbname
		pgc.connect()
		return pgc
	@classmethod
	def with_user_db_host(cls, user, dbname, host):
		pgc = cls()
		pgc.user = user
		pgc.dbname = dbname
		pgc.host = host
		pgc.connect()
		return pgc
	@classmethod
	def with_all(cls, user, dbname, host, port):
		pgc = cls()
		pgc.user = user
		pgc.dbname = dbname
		pgc.host = host
		pgc.port = port
		pgc.connect()
		return pgc

	def usePgpass(self):
		return (self.dbname == None or self.host == None or self.password == None or self.port == 0)

	def handle_error(self, msg, exception = None, rollback = True):
		if rollback == True:
			self.connection.rollback()		# rollback to the start of the failed pending transaction

		if not exception == None:
			msg = "{0} --- {1}".format(msg, str(exception))

		print msg

	def connect(self):
		if self.user == None:
			self.handle_error("A username is required", None, False)
			sys.exit(100)

		if self.usePgpass():
			pgLoader = pgpass.PgpassLoader()
			pgResults = pgLoader.getEntry(self.user, self.dbname, self.host, self.port)

			if len(pgResults) == 1:
				pg = pgResults[0]
				if pg.isValid:
					self.connStr = self.connStr.format(pg.host, pg.port, pg.database, pg.username, pg.password)
				else:
					self.handle_error("Unable to parse pgpass.conf line", None, False)
					sys.exit(101)
			elif len(pgResults) == 0:
				self.handle_error("No entries found in pgpass.conf", None, False)
				sys.exit(102)
			else:
				self.handle_error("No unique entry found in pgpass.conf", None, False)
				sys.exit(103)
		else:
			self.connStr = self.connStr.format(host, port, dbname, user, password)

		try:
			self.connection = psycopg2.connect(self.connStr)
		except Exception as ex:
			self.handle_error("Unable to connect as {0} to {1} on {2}:{3}".format(user, dbname, host, port), ex, False)
			sys.exit(104)

		return self.connection

	def execute(self, cmd):
		cursor = self.connection.cursor()

		try:
			cursor.execute(cmd)
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

	# Generate a list of dictionary objects
	def execute_select(self, cmd):
		cursor = self.connection.cursor()
		rows = []
		cols = []

		try:
			cursor.execute(cmd)
			rows = cursor.fetchall()
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

		# Select and add the column headers as the first row
		try:
			cols = [desc[0] for desc in cursor.description]
			self.connection.commit()
		except Exception as ex:
			rows = []		# reset the rows in case this is reached
			cols = []
			self.handle_error("Failed to extract or prepend header names", ex, False)

		return self.dictify_rows(cols, rows)

	def insert(self, table, columns, values):		#fixme - update columns to be optional and query the schema for details
		cursor = self.connection.cursor()

		# Add quotes around string values and convert integers to strings for insertion
		newValues = [None]*len(values)
		for index, val in enumerate(values):
			valType = type(val)
			if (type(0) == valType) or (type(0.1) == valType):
				newValues[index] = str(val)
			elif type("") == valType:
				newValues[index] = "'{0}'".format(val)
			else:
				newValues[index] = val

		cmd = """INSERT INTO {0}({1}) VALUES ({2})""".format(table, ", ".join(columns), ", ".join(newValues))

		try:
			cursor.execute(cmd)
			self.connection.commit()
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

	def insert_many(self, table, columns, valSet):		#fixme - update columns to be optional and query the schema for details
		cursor = self.connection.cursor()

		# Build the command string from the column headers
		selectors = [None]*len(columns)
		for index, col in enumerate(columns):
			selectors[index] = "%({0})s".format(col)
		cmd = """INSERT INTO {0}({1}) VALUES ({2})""".format(table, ", ".join(columns), ", ".join(selectors))

		# Build a dictionary set to pass through Psycopg2
		list = []
		for values in valSet:
			dict = {}
			for index, col in enumerate(columns):
				dict.update({col: str(values[index])})
			list.append(dict)
		set = tuple(list)

		try:
			cursor.executemany(cmd, set)
			self.connection.commit()
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

	def delete(self, table, condition = None):
		cursor = self.connection.cursor()
		cmd = """"""

		if condition == None:
			# prompt for validation on this command - checks whether to use python 2, or 3 input
			py3 = version_info[0] > 2
			response = '0'
			while (not response == 'y') and (not response == 'n'):
				if py3:
				  response = input("Delete ALL entries in {0} (Y/N): ".format(table)).lower()
				else:
				  response = raw_input("Delete ALL entries in {0} (Y/N): ".format(table)).lower()

			if response == 'y':
				cmd = """DELETE FROM {0}""".format(table)
			else:
				return
		else:
			cmd = """DELETE FROM {0} WHERE {1}""".format(table, condition)

		try:
			cursor.execute(cmd)
			self.connection.commit()
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

	def select(self, table, columns = ["*"], where = None):
		cursor = self.connection.cursor()
		rows = []

		cmd = """SELECT {1} FROM {0}""".format(table, ", ".join(columns))
		if where == None:
			cmd += """;"""
		else:
			cmd = """{0} WHERE {1}""".format(cmd, where)

		try:
			cursor.execute(cmd)
			rows = cursor.fetchall()
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

		# Select and add the column headers as the first row
		try:
			colNames = [desc[0] for desc in cursor.description]
			rows.insert(0, colNames)
			self.connection.commit()
		except Exception as ex:
			rows = []		# reset the rows in case this is reached
			self.handle_error("Failed to extract or prepend header names", ex, False)

		return rows

	# Print all the rows from a database query with extra whitespace for formatting
	def print_rows(self, rows):
		for row in self.stringify_rows(rows):
			print row

	def dictify_rows(self, columns, rows):
		objects = [None]*len(rows)
		cont = False

		if len(columns) > 0 and len(rows) > 0:
			if len(rows[0]) == len(columns):
				cont = True

		if cont:
			for index, row in enumerate(rows):
				objects[index] = dict(zip(columns, row))

		return objects

	def stringify_rows(self, rows):
		numRows = len(rows)
		retRows = [None]*numRows
		if numRows > 0:
			maxLengths = [0]*len(rows[0])
			for row in rows:
				for index, col in enumerate(row):
					colLength = len(str(col))
					if colLength > maxLengths[index]:
						maxLengths[index] = colLength

			nRows = [None]*numRows
			for rIndex, row in enumerate(rows):
				nCols = [None]*len(row)
				for index, col in enumerate(row):
					nCols[index] = "{0}{1}".format(str(row[index]), " "*(maxLengths[index] - len(str(col))))

				nRows[rIndex] = nCols

			for nrIndex, row in enumerate(nRows):
				retRows[nrIndex] = "\t".join(str(col) for col in row)

		return retRows

	def update(self, table, columns, values, condition):
		cursor = self.connection.cursor()

		changes = []
		for index, col in enumerate(columns):
			val = None
			if type("") == type(values[index]):
				val = "'{0}'".format(values[index])
			else:
				val = str(values[index])

			changes.append("{0} = {1}".format(col, val))

		cmd = """UPDATE {0} SET {1} WHERE {2}""".format(table, ", ".join(changes), condition)

		try:
			cursor.execute(cmd)
			self.connection.commit()
		except Exception as ex:
			self.handle_error("Failed to execute command: {0}".format(cmd), ex)

#***
#***
#***EXAMPLE USAGES***
#***
#***

#*** Import, connect to database, and establish table to work with - necessary for any execution
#import pg_connect as pgc
#pgConnect = pgc.PgConnect.with_user("<username>")
#table = "<tableName>"
#*** Import, connect to database, and establish table to work with - necessary for any execution

#*** Execute a list of commands
#cmds = ["""INSERT INTO prov_statute(id,statute_code,statute_desc,date_stored) VALUES (2,'0-1-2','just a test','2016-05-18T00:29:00.000');""",
#	"""SELECT * FROM prov_statute;"""]
#for cmd in cmds:
#	pgConnect.execute(cmd)
#*** Execute a list of commands

#*** Insert a single row into a table
#pgConnect.insert(table, ["id", "statute_code", "statute_desc", "date_stored"], [2, "0-1-3", "Another TEST", "2016-05-18T00:29:00.000"])
#*** Insert a single row into a table

#*** Delete rows in a table - all rows (includes verification prompt) or by a condition
#pgConnect.delete(table)
#pgConnect.delete(table, "id = 3")
#*** Delete rows in a table - all rows (includes verification prompt) or by a condition

#*** Insert multiple rows into a table
#columns = ["id", "statute_code", "statute_desc", "date_stored"]
#valSet = (
#	[1, "0-1-1", "FIRST", "2016-05-18T00:29:00.000"],
#	[2, "0-1-2", "Another TEST", "2016-05-18T00:29:00.000"],
#	[3, "0-1-3", "STUFF", "2016-05-18T00:29:00.000"]
#)
#pgConnect.insert_many(table, columns, valSet)
#*** Insert multiple rows into a table

#*** Select rows from a table and print them - all rows or specific rows
#rows = pgConnect.select(table)
#pgConnect.print_rows(rows)
#rows = pgConnect.select(table, ["id", "date_stored"])
#pgConnect.print_rows(rows)
#*** Select rows from a table and print them - all rows or specific rows

#***
#***
#***EXAMPLE USAGES***
#***
#***
