from browser import document, html
import browser.widgets.dialog as dialog
from common import *
from sheetDialog import *
import json

data = {}
sheetName = document["sheetName"]["content"]

bioCompoundFields = ("class", "height", "weight")
coins = ("gold", "silver", "copper")
levelsAndEXP = {
	1: 0,
	2: 300,
	3: 900,
	4: 2700,
	5: 6500,
	6: 14000,
	7: 23000,
	8: 34000,
	9: 48000,
	10: 64000,
	11: 85000,
	12: 100000,
	13: 120000,
	14: 140000,
	15: 165000,
	16: 195000,
	17: 225000,
	18: 265000,
	19: 305000,
	20: 355000
}

def toggleEditing(event, group):
	for field in document.select("input." + group):
		#print(field)
		if group == "bio" and field.attrs["id"] in bioCompoundFields:
			continue
		if event.target.checked:
			del field.attrs["readonly"]
		else:
			field.attrs["readonly"] = ''
	#print(data["biography"])

def setBioData(event):
	#print(event.target.parentElement.parentElement.id, event.target.id)

	groupKey = event.target.parentElement.parentElement.id
	fieldKey = event.target.id
	data[groupKey][fieldKey] = document[fieldKey].value

document["biographyEdit"].bind("change", lambda e : toggleEditing(e, "bio"))
for field in document.select("input.bio"):
	if field.id not in bioCompoundFields:
		print(field.id)
		document[field.id].bind("input", setBioData)

def adjustClass(event):
	editClassDialog = classEdit()
	editClassDialog.select("#classList")[0].value = ", ".join(
		data["biography"]["class"]
	)
	editClassDialog.select("#diceList")[0].value = ", ".join(
		[str(data["hit"]["dice"][c]["die"]) for c in data["biography"]["class"]]
	)
	editClassDialog.select("#levelList")[0].value = ", ".join(
		[
			str(data["experience"]["level"]["classes"][c])
			for c in data["biography"]["class"]
		]
	)

	def okHandler(event):
		classListString = editClassDialog.select("#classList")[0].value
		diceListString = editClassDialog.select("#diceList")[0].value
		levelListString = editClassDialog.select("#levelList")[0].value

		classList = list(map(str.strip, classListString.split(',')))
		diceList = list(map(str.strip, diceListString.split(',')))
		levelList = list(map(str.strip, levelListString.split(',')))

		try:
			diceList = list(map(int, diceList))
		except ValueError:
			dialog.InfoDialog(
				"Value Error",
				"Dice entries must be integers!"
			)
			return
		
		try:
			levelList = list(map(int, levelList))
		except ValueError:
			dialog.InfoDialog(
				"Value Error",
				"Level entries must be integers!"
			)
			return

		if len(classList) != len(diceList):
			dialog.InfoDialog(
				"Mismatch Error",
				"Number of classes not equal to number of dice!"
			)
			return
		elif len(classList) != len(levelList):
			dialog.InfoDialog(
				"Mismatch Error",
				"Number of classes not equal to number of levels!"
			)
			return
		elif sum(levelList) != data["experience"]["level"]["character"]:
			dialog.InfoDialog(
				"Level Inequality Notice",
				"The sum of your class level(s) is not equal to your character level. Please make sure to manually check this in the Experience section of the sheet and resynchronize it. Your changes will be still be committed though."
			)

		data["biography"]["class"] = sorted(classList)
		data["hit"]["dice"] = {
			c: {
				"die": diceList[classList.index(c)],
				"count": levelList[classList.index(c)]
			}
			for c in classList
		}
		data["experience"]["level"]["classes"] = {
			c: levelList[classList.index(c)]
			for c in classList
		}

		editClassDialog.close()
		reloadValues()

	editClassDialog.ok_button.bind("click", okHandler)

document["classEdit"].bind("click", adjustClass)

def calculateAbilityBonus(score : int) -> int:
	return (score - 10) // 2

def syncAbilityScore(ability : str, newValue : int):
	newBonus = calculateAbilityBonus(newValue)

	data["abilities"][ability]["score"] = newValue
	document[ability].value = newValue

	data["abilities"][ability]["bonus"] = newBonus
	document[ability + "Bonus"].value = newBonus

def adjustAbilityScore(event):
	ability = event.target.id.split('`')[0]
	function = event.target.id.split('`')[1]
	oldValue = data["abilities"][ability]["score"]

	if function == "Increment":
		if oldValue + 1 <= 30:
			newValue = oldValue + 1
		else:
			return
	elif function == "Decrement":
		if oldValue - 1 > 0:
			newValue = oldValue - 1
		else:
			return
	elif function == "Set":
		newValueDialog = dialog.EntryDialog(
			"Set " + ability.capitalize(),
			"Enter a score value between 1 and 30 inclusive"
		)
		def entryHandler(e):
			newValue = newValueDialog.value
			newValueDialog.close()
			#print("In Set Handler")
			try:
				newValue = int(newValue)
				if newValue > 0 and newValue <= 30:
					syncAbilityScore(ability, newValue)
				else:
					dialog.InfoDialog(
						"Ability Set Error",
						"Value out of range of 1 to 30!"
					)
			except ValueError:
				dialog.InfoDialog(
					"Ability Set Error",
					"Could not parse value as integer!"
				)

		newValueDialog.bind("entry", entryHandler)
		return
	else:
		return

	syncAbilityScore(ability, newValue)

def toggleAbilityAdjustment(event):
	for button in document.select(".abilityButton"):
		if event.target.checked:
			del button.attrs["disabled"]
		else:
			button.attrs["disabled"] = ''
		#print(button)

document["abilitiesEdit"].bind("change", toggleAbilityAdjustment)

for button in document.select(".abilityButton"):
	#print(button)
	button.bind("click", adjustAbilityScore)

def makeDieDict(count : int, die : int) -> dict:
	return {"count": count, "die": die}

def makeDieString(count : int, die : int) -> str:
	return str(count) + 'd' + str(die)

def makeDiceString(dieDictionaries : list) -> str:
	return " + ".join([makeDieString(die["count"], die["die"]) for die in dieDictionaries])

def updateHitDiceDivs():
	for div in document.select("div.hitDiceDiv"):
		del document[div.id]
	for k in sorted(data["hit"]["dice"].keys()):
		inputID = k + "`HitDice"
		div = html.DIV(id = inputID + "Div", Class = "hitDiceDiv")
		div <= html.LABEL(k, For = inputID)
		div <= html.INPUT(
			id = inputID, value = makeDieString(
				data["hit"]["dice"][k]["count"],
				data["hit"]["dice"][k]["die"]
			), readonly = ''
		)
		document["hitDice"] <= div

def toggleHitAdjustment(event):
	for button in document.select(".hitButton"):
		if event.target.checked:
			del button.attrs["disabled"]
		else:
			button.attrs["disabled"] = ''

	if event.target.checked:
		del document["currentHit"].attrs["readonly"]
	else:
		document["currentHit"].attrs["readonly"] = ''

document["hitEdit"].bind("change", toggleHitAdjustment)

def refreshHitPointBounds():
	document["currentHit"].min = -data["hit"]["max"]
	document["currentHit"].max = data["hit"]["max"]

def syncHitPoints(field, newValue):
	document[field].value = newValue
	field = field.split("Hit")[0]
	data["hit"][field] = newValue

	if field == "max":
		refreshHitPointBounds()
		newCurrent = min(data["hit"]["max"], data["hit"]["current"])
		document["currentHit"].value = newCurrent
		data["hit"]["current"] = newCurrent

def adjustHitPoints(event):
	field = event.target.id.split('`')[0]
	method = event.target.id.split('`')[1]
	fieldKeyword = field.split("Hit")[0]
	oldValue = data["hit"][fieldKeyword]

	if method == "Increment":
		if field == "maxHit" or field == "currentHit" \
			and oldValue + 1 <= data["hit"]["max"]:
			newValue = oldValue + 1
		else:
			newValue = oldValue
	elif method == "Decrement":
		if field == "maxHit" or field == "currentHit" \
			and oldValue - 1 >= -data["hit"]["max"]:
			newValue = oldValue - 1
		else:
			newValue = oldValue
	elif method == "Set":	
		newValueDialog = dialog.EntryDialog(
			"Set " + fieldKeyword.capitalize() + " Hit Points",
			"Enter a new " + fieldKeyword + " hit points value"
		)
		def entryHandler(e):
			newValue = newValueDialog.value
			newValueDialog.close()
			try:
				newValue = int(newValue)
				if newValue < 1 and field == "maxHit":
					dialog.InfoDialog(
						"Hit Points Set Error",
						"Max Hit Points Must Be Positive & Non-Zero!"
					)
				elif newValue < -data["hit"]["max"]:
					dialog.InfoDialog(
						"Hit Point Set Error",
						"Current Hit Points Cannot Fall That Far!"
					)
				elif field == "maxHit" or field == "currentHit" \
					and newValue <= data["hit"]["max"]:
					syncHitPoints(field, newValue)
				else:
					dialog.InfoDialog(
						"Hit Points Set Error",
						"Current Hit Points Cannot Exceed Maximum!"
					)
			except ValueError:
				dialog.InfoDialog(
					"Hit Points Set Error",
					"Could not parse value as integer!"
				)

		newValueDialog.bind("entry", entryHandler)
		return
	else:
		newValue = oldValue
	syncHitPoints(field, newValue)

for button in document.select(".hitButton"):
	button.bind("click", adjustHitPoints)

def processDeathSaves(event):
	kind = event.target.id.split('`')[0]
	count = int(event.target.id.split('`')[1])

	#print(kind + str(count), "disabled" in document[kind + '`' + str(count)].attrs)

	if count < 3:
		if event.target.checked:
			try:
				del document[kind + '`' + str(count + 1)].attrs["disabled"]
			except KeyError:
				pass

		else:
			document[kind + '`' + str(count + 1)].attrs["disabled"] = ''
			for box in range(count + 1, 4):
				document[kind + '`' + str(box)].checked = False
			count -= 1
	elif not event.target.checked:
			count -= 1
	
	if kind == "success":
		kind += "es"
	else:
		kind += 's'

	data["hit"]["deathSaves"][kind] = count
	#print(data["hit"]["deathSaves"])

for box in document.select(".deathSaveCheckbox"):
	box.bind("change", processDeathSaves)

def determineLevel():
	level = 1
	while data["experience"]["total"] >= levelsAndEXP[level]:
		level += 1
	return level

def adjustExperience(event):
	method = event.target.id.split('`')[1]

	if method == "Add":
		addExperienceDialog = experienceAdd()

document["experience`Add"].bind("click", adjustExperience)

def updateClassLevelDivs():
	for div in document.select("div.classLevelDiv"):
		del document[div.id]
	for k in sorted(data["experience"]["level"]["classes"].keys()):
		inputID = k + "`ClassLevel"
		div = html.DIV(id = inputID + "Div", Class = "classLevelDiv")
		div <= html.LABEL(k, For = inputID)
		div <= html.INPUT(
			id = inputID,
			value = data["experience"]["level"]["classes"][k],
			readonly = ''
		)
		document["classLevels"] <= div

def adjustFeature(event):
	feature = event.target.id.split('`')[0]
	method = event.target.id.split('`')[2]
	creatingFeature = False

	if method == "New":
		creatingFeature = True
		method = "Edit"

	if method in ("Decrement", "Increment"):
		if method == "Decrement":
			changeValue = -1
		elif method == "Increment":
			changeValue = 1
		
		data["features"][feature]["value"] += changeValue
		document[feature + "`Feature`Value"].value = data["features"][feature]["value"]

	elif method == "Delete":
		deleteFeatDialog = featureDelete(feature)

		def deleteHandler(event):
			del data["features"][feature]
			deleteFeatDialog.close()
			updateFeaturesTable()

		deleteFeatDialog.ok_button.bind("click", deleteHandler)
		
	elif method == "Edit":
		editFeatDialog = featureEdit(feature)
		if not creatingFeature:
			editFeatDialog.select("#name")[0].value = feature
			editFeatDialog.select(
				"#description"
			)[0].value = data["features"][feature]["description"]

			if data["features"][feature]["type"] == "numeric":
				editFeatDialog.select("#numericCheck")[0].checked = True
				del editFeatDialog.select("#value")[0].attrs["readonly"]
				editFeatDialog.select(
					"#value"
				)[0].value = data["features"][feature]["value"]

		def okHandler(event):
			newFeatureName = editFeatDialog.select("#name")[0].value
			if newFeatureName != feature \
				and newFeatureName in data["features"].keys():
				dialog.InfoDialog(
					"Name Error",
					"A feature already exists with that name, please choose another one."
				)
				return
			#print("Everything checks out.")

			newFeatureDescription = editFeatDialog.select(
				"#description"
			)[0].value
			newFeatureType = editFeatDialog.select("#numericCheck")[0].checked
			if newFeatureType:
				newFeatureValue = editFeatDialog.select("#value")[0].value
				try:
					newFeatureValue = int(newFeatureValue)
				except ValueError:
					dialog.InfoDialog(
						"Value Error",
						"The feature's value must be an integer number. Please correct it."
					)
					return

				newFeature = {
					"description": newFeatureDescription,
					"type": "numeric",
					"value": newFeatureValue
				}
			else:
				newFeature = {
					"description": newFeatureDescription,
					"type": "written"
				}

			data["features"][newFeatureName] = newFeature
			if newFeatureName != feature and not creatingFeature:
				del data["features"][feature]
			editFeatDialog.close()
			updateFeaturesTable()

		editFeatDialog.ok_button.bind("click", okHandler)

document["Create Feature``New"].bind("click", adjustFeature)

def updateFeaturesTable():
	for row in document.select("tr.featureRow"):
		del document[row.id]
	for k in sorted(data["features"].keys()):
		inputID = k + "`Feature"
		row = html.TR(id = inputID + "`Row", Class = "featureRow")
		row <= html.TD(k)
		row <= html.TD(data["features"][k]["description"])

		numericCell = html.TD()
		if data["features"][k]["type"] == "numeric":
		#	decrementButton = html.INPUT(
		#		id = inputID + "`Decrement", Class = "featureButton",
		#		type = "button", value = "-"
		#	)
		#	decrementButton.bind("click", adjustFeature)
		#	numericCell <= decrementButton

			numericCell <= html.INPUT(
				id = inputID + "`Value",
				value = data["features"][k]["value"],
				type = "number", readonly = ''
			)

		#	incrementButton = html.INPUT(
		#		id = inputID + "`Increment", Class = "featureButton",
		#		type = "button", value = "+"
		#	)
		#	incrementButton.bind("click", adjustFeature)
		#	numericCell <= incrementButton

		row <= numericCell

		featSettings = html.TD()

		featEditButton = html.INPUT(
			id = inputID + "`Edit", Class = "featureButton",
			type = "button", value = "Edit"
		)
		featEditButton.bind("click", adjustFeature)
		featSettings <= featEditButton
		featDeleteButton = html.INPUT(
			id = inputID + "`Delete", Class = "featureButton",
			type = "button", value = "Delete"
		)
		featDeleteButton.bind("click", adjustFeature)
		featSettings <= featDeleteButton

		row <= featSettings

		document["features"] <= row

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

	#print(data["hit"]["deathSaves"])

	for k in data["abilities"].keys():
		document[k].value = data["abilities"][k]["score"]
		document[k + "Bonus"].value = data["abilities"][k]["bonus"]

	document["currentHit"].value = data["hit"]["current"]
	document["maxHit"].value = data["hit"]["max"]
	refreshHitPointBounds()

	updateHitDiceDivs()

	try:
		del document["success`1"].attrs["disabled"]
	except KeyError:
		pass
	for box in range(1, data["hit"]["deathSaves"]["successes"] + 1):
		if document["success`" + str(box)].checked:
			break
		document["success`" + str(box)].checked = True
		if box < 3:
			del document["success`" + str(box + 1)].attrs["disabled"]

	try:
		del document["failure`1"].attrs["disabled"]
	except KeyError:
		pass
	for box in range(1, data["hit"]["deathSaves"]["failures"] + 1):
		if document["failure`" + str(box)].checked:
			break
		document["failure`" + str(box)].checked = True
		if box < 3:
			del document["failure`" + str(box + 1)].attrs["disabled"]

	document["characterLevel"].value = data["experience"]["level"]["character"]
	document["currentExperience"].value = data["experience"]["total"]
	document["nextExperience"].value = data["experience"]["next"]
	updateClassLevelDivs()

	document["armorClass"].value = data["armorClass"]

	for coin in coins:
		document[coin].value = data["currency"][coin]

	updateFeaturesTable()

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
				"noErrorTitle": "Sheet Saved",
				"noErrorBody": "Your sheet was saved successfully.",
				"errorTitle": "E R R O R"
			},
			()
		)
	)

document["save"].bind("click", saveSheet)

#print(document["sheetName"])

downloadSheetRequest(PseudoEvent(" `" + sheetName), jsonHandler)
