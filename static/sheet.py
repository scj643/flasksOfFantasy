from browser import document
from common import *
import json

data = {}
sheetName = document["sheetName"]["content"]

def reloadValues():
	global data
	#print(data)
	for k in data["biography"].keys():
		print(k, data["biography"][k], sep = ": ", end = '\t')
		if k not in ("class", "height", "weight"):
			document[k].attrs["value"] = data["biography"][k]
			print("(regular)")
		elif k == "class":
			document[k].attrs["value"] = ", ".join(data["biography"][k])
			print("(class)")
		else:
			document[k].attrs["value"] = str(data["biography"][k]["measure"]) \
				+ ' ' + data["biography"][k]["unit"]
			print("(height/weight)")

def jsonHandler(response):
	global data
	if response.status == 200:
		data = ajaxParseJSON(response)
		reloadValues()
	else:
		dialogShowHTTPError(response)

#print(document["sheetName"])

downloadSheetRequest(None, sheetName, jsonHandler)
