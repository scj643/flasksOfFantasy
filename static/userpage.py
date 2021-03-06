from browser import bind, document, window
import browser.widgets.dialog as dialog
from common import ajaxPostJSON, ajaxParseJSON

def newSheet(event):
	box = dialog.EntryDialog("Foobar", "Enter something will ya!")
	def evaluate(entryEvent):
		value = box.value
		box.close()
		print(value)
		dialog.InfoDialog("Foobar", value + "?")
	box.bind("entry", evaluate)

document["newsheet"].bind("click", newSheet)
