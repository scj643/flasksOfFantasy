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
        HOST = configDict["host"]
    except Exception as e:
        print(e)
        print(NO_CONFIG_MESSAGE)
else:
    print("Could not find 'config.json' in root directory,")
    print(NO_CONFIG_MESSAGE)
    SSL_PATH_TO_CERT = ""
    SSL_PATH_TO_PRIVKEY = ""
    HOST = "localhost"
# App Creation
base = fl.Flask(__name__)
if not os.path.exists("./" + key.KEY_FILE):
    key.newKey()
base.secret_key = key.getKey()
base.config.update(
    SESSION_COOKIE_SAMESITE = "Strict",
    SESSION_COOKIE_SECURE = True,
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
        pass

def index():
    return "<h1>Hello World!</h1>"
# App Rule Instanctiation
base.add_url_rule('/', "index", index)
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

