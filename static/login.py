from browser import document, ajax, window
import json

def redirect(reply):
    replyJSON = json.loads(reply.text)
    if reply.status == 200:
        if replyJSON["error"] == "None":
            window.location.href = replyJSON["url"]
        else:
            document["error"].innerHTML = replyJSON["error"]
    else:
        document["error"].innerHTML = "Bad response code: " + str(reply.status)

def login(event):
    username = document["user"].value
    password = document["pass"].value
    if len(username) > 0 and len(password) > 0:
        ajax.post(
            "/login/", headers = {"Content-Type": "application/json"},
            data = json.dumps({"username" : username, "password": password}),
            oncomplete = redirect
        )
    else:
        document["error"].innerHTML = "You need to enter something into both fields!"

document["login"].bind("click", login)
