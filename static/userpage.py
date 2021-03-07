from browser import bind, document, window
import browser.widgets.dialog as dialog
from common import ajaxPostJSON, ajaxParseJSON

def fooHandler(event):
	box = dialog.EntryDialog("Foobar", "Enter something will ya!")
	def evaluate(entryEvent):
		value = box.value
		box.close()
		print(value)
		dialog.InfoDialog("Foobar", value + "?")
	box.bind("entry", evaluate)

def newSheetReply(response):
	if response.status == 200:
		reply = ajaxParseJSON(response)
		if reply["error"] == "None.":
			dialog.InfoDialog(
				"Success",
				"Created new sheet \"" + reply["newSheetName"] + \
				"\".\nRefresh the page to see it."
			)
		else:
			dialog.InfoDialog("Processing Error", reply["error"])
	else:
		dialog.InfoDialog(
			"HTTP Error",
			str(response.status) + ": " + str(response.text)
		)

def newSheetRequest(event):
	box = dialog.EntryDialog("New Sheet", "Enter the name of the new sheet")
	def evaluate(entryEvent):
		name = box.value
		box.close()
		ajaxPostJSON(
			"/user/",
			{"method": "newSheet", "newSheetName": name},
			newSheetReply
		)
	box.bind("entry", evaluate)

document["newsheet"].bind("click", newSheetRequest)
