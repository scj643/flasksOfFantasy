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
			return fl.jsonify({"error": "No JSON Submitted."})

def logout():
	del fl.session["user"]
	return fl.redirect(fl.url_for("login"))

def userpage():
	testSheets = [
		{"name": "Foo", "link": "/sheet/foo"},
		{"name": "Jym", "link": "/sheet/jym"}
	]		
	if "user" in fl.session:
		return fl.render_template(
			"userpage.html",
			user = fl.session["user"],
			sheets = []
		)
	else:
		return fl.redirect(fl.url_for("login"))

def index():
	return "<h1>Hello World!</h1>"

# App Rule Instanctiation
base.add_url_rule('/', "index", index)
base.add_url_rule("/login/", "login", login, methods = ("GET", "POST"))
base.add_url_rule("/logout/", "logout", logout)
base.add_url_rule("/user/", "userpage", userpage)
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

