from Crypto.Hash import SHA256 as sha
import sqlite3 as sql
import os

dbName = "fof.db"

def connect() -> sql.Connection:
	conn = sql.connect(dbName)
	conn.row_factory = sql.Row
	conn.cursor().execute("PRAGMA foreign_keys = ON")

	return conn

def query(conn : sql.Connection, sql : str, params : dict = {}) -> list:
	if len(params) == 0:
		return conn.cursor().execute(sql).fetchall()
	else:
		return conn.cursor().execute(sql, params).fetchall()

def dictionize(response : list) -> list:
	return [dict(row) for row in response]

def qd(conn : sql.Connection, sql : str, params : dict = {}) -> list:
	return dictionize(query(conn, sql, params))

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

def queryWrite(query : str, params : dict = {}) -> list:
	conn = connect()

	try:
		response = qd(conn, query, params)
	except sql.DatabaseError as e:
		print("SQL Error: " + str(e))
		return []
	else:
		conn.commit()
		conn.close()
		return response

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

def doHash(password : str, salt : str) -> str:
	h = sha.new()
	h.update(bytes(password + salt, "utf8"))
	return h.hexdigest()

def checkPassword(password : str, salt : str, hash : str) -> bool:
	hashComputed = doHash(password, salt)
	print(hash)
	print(hashComputed)
	return hash == hashComputed

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

