from Crypto.Hash import SHA256 as sha
import sqlite3 as sql
import os

dbName = "fof.db"

def connect() -> sql.Connection:
	conn = sql.connect(dbName, detect_types = sql.PARSE_DECLTYPES)
	conn.row_factory = sql.Row
	conn.cursor().execute("PRAGMA foreign_keys = ON")

	return conn

def query(cursor : sql.Cursor, sql : str, params = None) -> list:
	if params is None:
		return cursor.execute(sql).fetchall()
	else:
		return cursor.execute(sql, params).fetchall()

def dictionize(response : list) -> list:
	return [dict(row) for row in response]

def createTables():
	tableData = ({
		"name" : "USERS",
		"script" : "sql/createUsers.sql"
	}, {
		"name" : "SHEETS",
		"script" : "sql/createSheets.sql"
	})

	conn = connect()
	cursor = conn.cursor()

	for table in tableData:
		if len(
			query(
				cursor,
				"""SELECT * FROM SQLITE_MASTER
WHERE TYPE = 'table'
AND NAME = :name;""",
				table
			)
		) == 0:
			file = open(table["script"], 'r')
			createCommand = file.read()
			file.close()
			cursor.executescript(createCommand)
			print("Created table " + table["name"])
		else:
			print("Table " + table["name"] + " exists, skipping...")
	
	conn.commit()
	cursor.close()
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
	pass

