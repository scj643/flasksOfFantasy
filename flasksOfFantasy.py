# IMPORTS
import os
import json
import flask as fl
import fofDB as db
import fofKEY as key
import fofSTR as strings
# CONSTANTS
DEBUG = True
NO_CONFIG_MESSAGE = "Using default SSL and Host configurations (no https and localhost)"
testSheets = [
	{"name": "Foo", "link": "/sheet/foo"},
	{"name": "Jym", "link": "/sheet/jym"}
]
noJSONError = {"error": "No JSON Submitted."}	
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

def getSheets(user):
	raw = db.queryRead(
		"SELECT * FROM SHEETS WHERE username = :user",
		{"user": user}
	)
	return [
		{"name": sheet["sheetname"], "link": sheet["path"].split(".json")[0][1:]}
		for sheet in raw
	]

def sendSheet(user, sheet):
	if "user" in fl.session:
		if user == fl.session["user"]:
			sheetPath = db.queryRead("""SELECT * FROM SHEETS
WHERE username = :user AND sheetname = :sheet""",
				{"user": user, "sheet": sheet}
			)[0]["path"]
			print(sheetPath)
			if os.path.exists(sheetPath):
				return fl.send_from_directory("./sheets/" + user + '/', sheet + ".json")
		else:
			print("File not found: " + sheet)
			return fl.redirect(fl.url_for("userpage"))
	else:
		return fl.redirect(fl.url_for("login"))

	print("End of sendSheet reached, oh no!")

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
		if fl.request.is_json:
			userRequest = fl.request.get_json()
			userRequest["user"] = fl.session["user"]
			if userRequest["method"] == "newSheet":
				if not strings.isAllowedChars(userRequest["newSheetName"]):
					return fl.jsonify({
						"error": "Outlawed characters detected in \"" \
						+ userRequest["newSheetName"] \
						+ "\". Please do not use quote marks or the backslash."
					})
				elif len(db.queryRead("""SELECT * FROM SHEETS
WHERE username = :user AND sheetname = :newSheetName""",
					userRequest
				)) != 0:
					return fl.jsonify({
						"error": "Sheet \"" + userRequest["newSheetName"] \
						+ "\" already exists. Please retry with a different name."
					})
				else:
					userRequest["path"] = "./sheets/" + userRequest["user"] + '/' \
						+ userRequest["newSheetName"] + ".json"

					newFile = open(userRequest["path"], 'w')
					json.dump({"hello": "world"}, newFile, indent = 4, sort_keys = True)
					newFile.close()
					db.queryWrite(
						"INSERT INTO SHEETS VALUES (:user, :newSheetName, :path)",
						userRequest
					)
					return fl.jsonify({
						"error": "None.",
						"url": userRequest["path"],
						"newSheetName": userRequest["newSheetName"]
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
base.add_url_rule(
	"/user/<script>", "userScripts",
	lambda script : fl.redirect("/static/" + script)
)
base.add_url_rule("/sheets/<user>/<sheet>/", "getsheet", sendSheet)
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

