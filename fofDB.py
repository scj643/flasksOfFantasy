# IMPORTS
from hashlib import sha256
import sqlite3 as sql
import os
# NAME OF DB FILE
dbName = "fof.db"
# Establish a connection that enforces foreign keys and returns Row objects
# from all queries
def connect() -> sql.Connection:
	conn = sql.connect(dbName)
	conn.row_factory = sql.Row
	conn.cursor().execute("PRAGMA foreign_keys = ON")

	return conn
# Execute a SQL command over an existing connection
def query(conn : sql.Connection, sql : str, params : dict = {}) -> list:
	if len(params) == 0:
		return conn.cursor().execute(sql).fetchall()
	else:
		return conn.cursor().execute(sql, params).fetchall()
# Convert Row objects in a query response to dictionaries
def dictionize(response : list) -> list:
	return [dict(row) for row in response]
# Wrap dictionize around query for ease of code
def qd(conn : sql.Connection, sql : str, params : dict = {}) -> list:
	return dictionize(query(conn, sql, params))
# Make a one-time connection and run one read query
def queryRead(query : str, params : list = []) -> list:
	conn = connect()

	try:
		response = qd(conn, query, params)
	except sql.DatabaseError as e:
		print("SQL Error: " + str(e))
		return []
	else:
		conn.close()
		return response
# Make a one-time connection and run one write query
def queryWrite(query : str, params : dict = {}) -> list:
	conn = connect()

	try:
		response = qd(conn, query, params)
	except sql.DatabaseError as e:
		print("SQL Error: " + str(e))
		return [{}]
	else:
		conn.commit()
		conn.close()
		return response
# Create the tables needed for FoF using scripts in ./sql
def createTables():
	tableData = ({
		"name" : "USERS",
		"script" : "sql/createUsers.sql"
	}, {
		"name" : "SHEETS",
		"script" : "sql/createSheets.sql"
	})

	conn = connect()

	for table in tableData:
		if len(
			query(
				conn,
				"""SELECT * FROM SQLITE_MASTER
WHERE TYPE = 'table'
AND NAME = :name;""",
				table
			)
		) == 0:
			file = open(table["script"], 'r')
			createCommand = file.read()
			file.close()
			conn.cursor().executescript(createCommand)
			print("Created table " + table["name"])
		else:
			print("Table " + table["name"] + " exists, skipping...")
	
	conn.commit()
	conn.close()

	if not os.path.exists("./sheets"):
		os.mkdir("./sheets")
# Computer a hash h(p || s) for a password p and salt s
def doHash(password : str, salt : str) -> str:
	h = sha256(bytes(password + salt, "utf8"))
	return h.hexdigest()
# Check if an inputted password matches the recorded salted-hash
def checkPassword(password : str, salt : str, hash : str) -> bool:
	hashComputed = doHash(password, salt)
	return hash == hashComputed
# Add a new row to the users table without storing the password
# ONLY USE AFTER VALIDATING THE PASSWORD AS STRONG
def createUser(username : str, password : str):
	duplicateSalts = [None]
	while len(duplicateSalts) > 0:
		salt = os.urandom(16).hex()
		duplicateSalts = queryRead(
			"SELECT * FROM USERS WHERE salt = :salt",
			{"salt" : salt}
		)

	hash = doHash(password, salt)

	queryWrite(
		"INSERT INTO USERS VALUES (:u, :s, :h)",
		{'u' : username, 's' : salt, 'h' : hash}
	)

	if not os.path.exists("./sheets/" + username):
		os.mkdir("./sheets/" + username)

