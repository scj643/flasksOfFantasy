# IMPORTS
import os
import json
import time
import shutil
import flask as fl
import fofDB as db
import fofKEY as key
import fofSTR as strings
import defaultSheet as ds
# CONSTANTS
DEBUG = True
NO_CONFIG_MESSAGE = "Using default SSL and Host configurations " \
	+ "(no https and localhost)"
SQL_WRITE_ERROR = "Failed to write to database.\n" \
	+ "Contact the administrator for further details."
testSheets = [
	{"name": "Foo", "link": "/sheet/foo"},
	{"name": "Jym", "link": "/sheet/jym"}
]
noJSONError = {"error": "No JSON Submitted."}
# Header Control Functions (use with fl.after_this_request in rule functions)
def noCaching(response):
	response.headers["Cache-Control"] = "no-cache"
	return response
# Configurtion Initialization
if os.path.exists("./config.json"):
	try:
		configFile = open("./config.json", "r")
		configDict = json.load(configFile)
		configFile.close()
		SSL_PATH_TO_CERT = configDict["sslPathToCert"]
		SSL_PATH_TO_PRIVKEY = configDict["sslPathToPrivKey"]
		COOKIE_SECURE = configDict["cookieSecure"]
		HOST = configDict["host"]
	except Exception as e:
		print(e)
		print(NO_CONFIG_MESSAGE)
		SSL_PATH_TO_CERT = ""
		SSL_PATH_TO_PRIVKEY = ""
		COOKIE_SECURE = True
		HOST = "localhost"
else:
	print("Could not find 'config.json' in root directory,")
	print(NO_CONFIG_MESSAGE)
	SSL_PATH_TO_CERT = ""
	SSL_PATH_TO_PRIVKEY = ""
	COOKIE_SECURE = True
	HOST = "localhost"
# App Creation
base = fl.Flask(__name__)
if not os.path.exists("./" + key.KEY_FILE):
	key.newKey()
base.secret_key = key.getKey()
base.config.update(
	SESSION_COOKIE_SAMESITE = "Strict",
	SESSION_COOKIE_SECURE = COOKIE_SECURE,
	SESSION_COOKIE_HTTPONLY = True
)
# App Rule Functions
def login():
	if fl.request.method == "GET":
		if "user" in fl.session:
			return fl.redirect(fl.url_for("userpage"))
		else:
			return fl.render_template("login.html")
	elif fl.request.method == "POST":
		if fl.request.is_json:
			credentials = fl.request.get_json()
			userData = db.queryRead(
				"SELECT * FROM USERS WHERE username = :username",
				credentials
			)

			if len(userData) == 0:
				return fl.jsonify({"error": "Bad username."})
			else:
				userData = userData[0]

			if db.checkPassword(
				credentials["password"],
				userData["salt"], userData["hash"]
			):
				fl.session["user"] = credentials["username"]
				return fl.jsonify({"url": fl.url_for("userpage"), "error": "None"})
			else:
				return fl.jsonify({"error": "Bad password."})
		else:
			return fl.jsonify(noJSONError)

def logout():
	del fl.session["user"]
	return fl.redirect(fl.url_for("login"))

def staticCahcingCheck(script):
	noCacheList = ["common.py", "sheetDialog.py"]
	print(script)
	if script in noCacheList:
		fl.after_this_request(noCaching)
		return fl.send_from_directory("./static/", script)
	else:
		fl.redirect("/static/" + script)

def getSheets(user):
	raw = db.queryRead(
		"SELECT * FROM SHEETS WHERE username = :user",
		{"user": user}
	)
	return [
		{"name": sheet["sheetname"], "link": sheet["path"].split(".json")[0][1:]}
		for sheet in raw
	]

sheetQuery = "SELECT * FROM SHEETS WHERE username = :user AND sheetname = :sheet"

checkDBForSheet = lambda user, sheet : sheet == db.queryRead(
	sheetQuery,	{"user": user, "sheet": sheet}
)[0]["sheetname"]

getSheetPath = lambda user, sheet : db.queryRead(
	sheetQuery, {"user": user, "sheet": sheet}
)[0]["path"]

def loadSheet(user, sheet):
	if "user" in fl.session:
		if user == fl.session["user"]:
			try:
				if checkDBForSheet(user, sheet):
					return fl.render_template(
						"sheet.html",
						sheetName = sheet,
						username = fl.session["user"],
						abilities = (
							"strength", "dexterity", "constitution",
							"intelligence", "wisdom", "charisma"
						),
						coins = ("gold", "silver", "copper")
					)
				else:
					return fl.redirect(fl.url_for("userpage"))
			except IndexError:
				return fl.redirect(fl.url_for("userpage"))
		else:
			return fl.redirect(fl.url_for("userpage"))
	else:
		return fl.redirect(fl.url_for("login"))

def saveSheet(user, sheet):
	if "user" in fl.session:
		if user == fl.session["user"]:
			if not fl.request.is_json:
				return fl.jsonify({"error": "Bad POST Request."})
			else:
				sheetData = fl.request.get_json()
				sheetPath = getSheetPath(user, sheet)
				print(sheetPath)

			try:
				if checkDBForSheet(user, sheet):
					try:
						sheetFile = open(sheetPath, 'w')
						json.dump(
							sheetData, sheetFile,
							indent = 4, sort_keys = True
						)
						sheetFile.close()
						return fl.jsonify({
							"error": "None."
						})
					
					except OSError as e:
						return fl.jsonify({"error": "OS Error: " + e})
				else:
					return fl.jsonify({
						"error": "Sheet not found." \
						+ "You shouldn't be seeing this error..."
					})
			except IndexError:
				return fl.jsonify({
					"error": "Sheet doesn't exist. " \
					+ "You shouldn't be seeing this error..."
				})
		else:
			return fl.jsonify({"error": "Improper Access."})
	else:
		return fl.jsonify({"error": "Can I see your passport?"})


def sendSheet(user, sheet):
	fl.after_this_request(noCaching)
	if "user" in fl.session:
		if user == fl.session["user"]:
			try:
				sheetPath = db.queryRead(
					"SELECT * FROM SHEETS " \
					+ "WHERE username = :user " \
					+ "AND sheetname = :sheet",
					{"user": user, "sheet": sheet}
				)[0]["path"]
				#print(sheetPath)
				print("\t[" + user + "]: Sending sheet " + sheet)
				return fl.send_from_directory("./sheets/" + user + '/', sheet + ".json")
			except IndexError:
				print("\t[" + user + "]: Sheet \"" + sheet + "\" does not exist")
				return fl.redirect(fl.url_for("userpage"))
		else:
			print("Incorrect user access for " + sheet)
			return fl.redirect(fl.url_for("userpage"))
	else:
		return fl.redirect(fl.url_for("login"))

	#print("End of sendSheet reached, oh no!")

def userpage():
	if fl.request.method == "GET":
		if "user" in fl.session:
			return fl.render_template(
				"userpage.html",
				user = fl.session["user"],
				sheets = getSheets(fl.session["user"])
			)
		else:
			return fl.redirect(fl.url_for("login"))
	elif fl.request.method == "POST":
		if not "user" in fl.session:
			return fl.redirect(fl.url_for("login"))
		elif fl.request.is_json:
			userRequest = fl.request.get_json()
			userRequest["user"] = fl.session["user"]
			if userRequest["method"] == "newSheet":
				if not strings.isAllowedChars(userRequest["newSheetName"]):
					return fl.jsonify({
						"error": "Outlawed characters detected in \"" \
						+ userRequest["newSheetName"] \
						+ "\". Please do not use quote marks or the backslash."
					})
				elif len(
					db.queryRead(
						"SELECT * FROM SHEETS " \
						+ "WHERE username = :user " \
						+ "AND sheetname = :newSheetName",
						userRequest
					)
				) != 0:
					return fl.jsonify({
						"error": "Sheet \"" + userRequest["newSheetName"] \
						+ "\" already exists. Please retry with a different name."
					})
				else:
					userRequest["path"] = "./sheets/" + userRequest["user"] + '/' \
						+ userRequest["newSheetName"] + ".json"

					if len(
						db.queryWrite(
							"INSERT INTO SHEETS VALUES " \
							+ "(:user, :newSheetName, :path)",
							userRequest
						)
					) == 0:
						newFile = open(userRequest["path"], 'w')
						json.dump(ds.defaultSheet, newFile, indent = 4, sort_keys = True)
						newFile.close()

						return fl.jsonify({
							"error": "None.",
							"url": userRequest["path"],
							"newSheetName": userRequest["newSheetName"]
						})
					else:
						return fl.jsonify({
							"error": SQL_WRITE_ERROR,
						})

			elif userRequest["method"] == "delete":
				if len(
					db.queryWrite(
						"DELETE FROM SHEETS " \
						+ "WHERE sheetname = :sheetName",
						userRequest
					)
				) == 0:
					if not os.path.exists("./recycleBin/"):
						os.mkdir("./recycleBin/")
					if not os.path.exists(
						"./recycleBin/" + userRequest["user"] + '/'
					):
						os.mkdir("./recycleBin/" + userRequest["user"] + '/')

					os.rename(
						"./sheets/" + userRequest["user"] + '/' \
						+ userRequest["sheetName"] + ".json",
						"./recycleBin/" + userRequest["user"] + '/' \
						+ userRequest["sheetName"] + '.' \
						+ str(time.time_ns()) + ".json"
					)
					return fl.jsonify({
						"error": "None.",
						"sheetName": userRequest["sheetName"]
					})
				else:
					return fl.jsonify({"error": SQL_WRITE_ERROR})

			elif userRequest["method"] == "duplicate":
				if len(
					db.queryRead(
						"SELECT * FROM SHEETS " \
						+ "WHERE sheetname = :duplicateName",
						userRequest
					)
				) != 0:
					return fl.jsonify(
						{
							"error": "Duplicate name \"" \
							+ userRequest["duplicateName"] \
							+ "\" already in use. Please try again."
						}
					)
				else:
					userRequest["originalPath"] = "./sheets/" + userRequest["user"] \
						+ '/' + userRequest["sheetName"] + ".json"
					userRequest["duplicatePath"] = "./sheets/" + userRequest["user"] \
						+ '/' + userRequest["duplicateName"] + ".json"

				if len(
					db.queryWrite(
						"INSERT INTO SHEETS VALUES " \
						+ "(:user, :duplicateName, :duplicatePath)",
						userRequest
					)
				) != 0:
					return fl.jsonify({"error": SQL_WRITE_ERROR})
				else:
					shutil.copyfile(
						userRequest["originalPath"],
						userRequest["duplicatePath"]
					)
					return fl.jsonify({
						"error": "None.",
						"sheetName": userRequest["sheetName"],
						"duplicateName": userRequest["duplicateName"]
					})

			else:
				return fl.jsonify({"error": "Bad POST Request."})
		else:
			return fl.jsonify(noJSONError)

def index():
	return "<h1>Hello World!</h1>"

# App Rule Instanctiation
base.add_url_rule('/', "index", index)
base.add_url_rule("/login/", "login", login, methods = ("GET", "POST"))
base.add_url_rule("/logout/", "logout", logout)
base.add_url_rule("/user/", "userpage", userpage, methods = ("GET", "POST"))
base.add_url_rule("/user/<script>", "userScripts", staticCahcingCheck)
base.add_url_rule("/sheets/<user>/<sheet>/", "loadsheet", loadSheet)
base.add_url_rule("/sheets/<user>/<sheet>/get/", "getsheet", sendSheet)
base.add_url_rule(
	"/sheets/<user>/<sheet>/save/",
	"saveSheet", saveSheet, methods = ["POST"]
)
base.add_url_rule(
	"/sheets/<user>/<sheet>/<script>", "sheetScripts",
	lambda user, sheet, script : staticCahcingCheck(script)
)
# App Execution
if __name__ == "__main__":
	if len(SSL_PATH_TO_CERT) > 0 and len(SSL_PATH_TO_PRIVKEY) > 0:
		base.run(
			debug = DEBUG,
			ssl_context = (SSL_PATH_TO_CERT, SSL_PATH_TO_PRIVKEY),
			host = HOST
		)
	else:
		base.run(debug = DEBUG, host = HOST)

