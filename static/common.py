from browser import document, ajax
import browser.widgets.dialog as dialog
import json

class PseudoEvent:
	def __init__(self, id):
		self.target = {"id": id}

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

def sheetReplyGeneric(response, dialogStrings, replyKeys):
	if response.status == 200:
		reply = ajaxParseJSON(response)
		if reply["error"] == "None.":
			dialog.InfoDialog(
				dialogStrings["noErrorTitle"],
				dialogStrings["noErrorBody"].format([
					reply[key] for key in replyKeys
				])
			)
		else:
			dialog.InfoDialog(dialogStrings["errorTitle"], reply["error"])
	else:
		dialogShowHTTPError(response)


def downloadSheetRequest(event, handler):
	print(event.target)
	sheet = event.target["id"].split('`')[1]
	ajax.get(
		"/sheets/" + document["user"].innerHTML + '/' + sheet + "/get/",
		oncomplete = handler
	)

