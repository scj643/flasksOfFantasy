from browser import bind, document, window, html
import browser.widgets.dialog as dialog
from common import ajaxPostJSON, ajaxParseJSON

def dialogShowHTTPError(response):
	dialog.InfoDialog(
		"HTTP Error",
		str(response.status) + ": " + str(response.text)
	)

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
		dialogShowHTTPError(response)

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

def deleteSheetReply(response):
	if response.status == 200:
		reply = ajaxParseJSON(response)
		if reply["error"] == "None.":
			dialog.InfoDialog(
				"Deleted",
				"Sheet \"" + reply["sheetName"] \
				+ " has been deleted."
			)
		else:
			dialog.InfoDialog("Deletion Error", reply["error"])
	else:
		dialogShowHTTPError(response)

def deleteSheetRequest(event, sheet):
	box = dialog.Dialog("Confirm Deletion", ok_cancel = ("Delete", "Cancel"))
	box.panel <= html.P(
		"Are you sure you want to delete sheet \"" \
		+ sheet + "\"? (The file will remain on disk, " \
		+ "but will be inaccessible)"
	)
	def delete(clickEvent):
		box.close()
		ajaxPostJSON(
			"/user/",
			{"method": "delete", "sheetName": sheet},
			deleteSheetReply
		)
	box.ok_button.bind("click", delete)

document["newsheet"].bind("click", newSheetRequest)

for button in document.select(".delete"):
	#print(button["id"].split('`')[1])
	sheet = button["id"].split('`')[1]
	button.bind("click", lambda e : deleteSheetRequest(e, sheet))
