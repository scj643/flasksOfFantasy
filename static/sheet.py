from browser import document
from common import *
import json

data = {}
sheetName = document["sheetName"]["content"]

bioCompoundFields = ("class", "height", "weight")

def toggleEditing(event, group):
	for field in document.select("input." + group):
		#print(field)
		if group == "bio" and field.attrs["id"] in bioCompoundFields:
			continue
		if event.target.checked:
			del field.attrs["readonly"]
		else:
			field.attrs["readonly"] = ''
	print(data["biography"])

def setBioData(event, key):
	#print(document[key].value, document[key].attrs["value"])
	data["biography"][key] = document[key].value

document["biographyEdit"].bind("change", lambda e : toggleEditing(e, "bio"))
document["race"].bind("input", lambda e, : setBioData(e, "race"))

def reloadValues():
	global data
	for k in data["biography"].keys():
		#print(k, data["biography"][k], sep = ": ")
		if k not in ("class", "height", "weight"):
			document[k].value = data["biography"][k]
			#print("(regular)")
		elif k == "class":
			document[k].value = ", ".join(data["biography"][k])
			#print("(class)")
		else:
			document[k].value = str(data["biography"][k]["measure"]) \
				+ ' ' + data["biography"][k]["unit"]
			#print("(height/weight)")

def jsonHandler(response):
	global data
	if response.status == 200:
		data = ajaxParseJSON(response)
		reloadValues()
	else:
		dialogShowHTTPError(response)

def saveSheet(event):
	ajaxPostJSON(
		"save/", data,
		lambda r : sheetReplyGeneric(
			r, {
				"noErrorTitle": "foo",
				"noErrorBody": "bar",
				"errorTitle": "E R R O R"
			},
			()
		)
	)

document["save"].bind("click", saveSheet)

#print(document["sheetName"])

downloadSheetRequest(None, sheetName, jsonHandler)
