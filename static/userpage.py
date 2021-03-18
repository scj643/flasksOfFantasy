from browser import bind, document, window, html, ajax
import browser.widgets.dialog as dialog
from common import *

def fooHandler(event):
	box = dialog.EntryDialog("Foobar", "Enter something will ya!")
	def evaluate(entryEvent):
		value = box.value
		box.close()
		print(value)
		dialog.InfoDialog("Foobar", value + "?")
	box.bind("entry", evaluate)

def newSheetRequest(event):
	box = dialog.EntryDialog("New Sheet", "Enter the name of the new sheet")
	def evaluate(entryEvent):
		name = box.value
		box.close()
		ajaxPostJSON(
			"/user/",
			{"method": "newSheet", "newSheetName": name},
			lambda r : sheetReplyGeneric(r, {
				"noErrorTitle": "New Sheet Created",
				"noErrorBody": "Created new sheet \"{0[0]}\".\n" \
					+ "Refresh the page to see it.",
				"errorTitle": "Processing Error"
			}, [
				"newSheetName"
			])
		)
	box.bind("entry", evaluate)

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
			lambda r : sheetReplyGeneric(r, {
				"noErrorTitle": "Deleted",
				"noErrorBody": "Sheet \"{0[0]}\" has been deleted.\n" \
					+ "A backup copy will remain in the server's recycle bin, " \
					+ "just in case.",
				"errorTitle": "Deletion Error"
			}, [
				"sheetName"
			])
		)
	box.ok_button.bind("click", delete)

def duplicateSheetRequest(event, sheet):
	box = dialog.EntryDialog("Duplicate Sheet", "Enter a name for the duplicate")
	def evaluate(entryEvent):
		duplicateName = box.value
		box.close()
		ajaxPostJSON(
			"/user/",
			{"method": "duplicate", "sheetName": sheet, "duplicateName": duplicateName},
			lambda r : sheetReplyGeneric(r, {
				"noErrorTitle": "Duplicated",
				"noErrorBody": "Copied sheet \"{0[0]}\" to \"{0[1]}\".\n" \
					+ "Refresh the page to see it.",
				"errorTitle": "Duplication Error"
			}, [
				"sheetName", "duplicateName"
			])
		)
	box.bind("entry", evaluate)

def downloadSheet(response):
	if response.status == 200:
		downloadLink = document.createElement('A')
		downloadLink.attrs["href"] = window.URL.createObjectURL(
			window.Blob.new(
				[response.text],
				{"type": "application/json"}
			)
		)
		downloadLink.attrs["target"] = "_blank"

		document.body.appendChild(downloadLink)
		downloadLink.click()
		document.body.removeChild(downloadLink)
	else:
		dialogShowHTTPError(response)


document["newsheet"].bind("click", newSheetRequest)

for button in document.select(".delete"):
#	print(button["id"].split('`')[1])
	sheet = button["id"].split('`')[1]
	button.bind("click", lambda e : deleteSheetRequest(e, sheet))

for button in document.select(".download"):
	sheet = button["id"].split('`')[1]
	button.bind("click", lambda e : downloadSheetRequest(e, sheet, downloadSheet))

for button in document.select(".duplicate"):
	sheet = button["id"].split('`')[1]
	button.bind("click", lambda e : duplicateSheetRequest(e, sheet))
