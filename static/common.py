from browser import document, ajax
import browser.widgets.dialog as dialog
import json

def ajaxPostJSON(target : str, payload : dict, complete):
	ajax.post(
		target, headers = {"Content-Type": "application/json"},
		data = json.dumps(payload), oncomplete = complete
	)

def ajaxParseJSON(reply : ajax.Ajax) -> dict:
	return json.loads(reply.text)

def dialogShowHTTPError(response):
	dialog.InfoDialog(
		"HTTP Error",
		str(response.status) + ": " + str(response.text)
	)

def downloadSheetRequest(event, sheet, handler):
	ajax.get(
		"/sheets/" + document["user"].innerHTML + '/' + sheet + "/get/",
		oncomplete = handler
	)

