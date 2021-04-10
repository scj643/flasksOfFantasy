from browser import document, html
import browser.widgets.dialog as dialog

def featureEdit(feature) -> dialog.Dialog:
	d = dialog.Dialog(feature, ok_cancel = True)
	def toggleNumeric(event):
		if event.target.checked:
			del d.select("#value")[0].attrs["readonly"]
		else:
			d.select("#value")[0].attrs["readonly"] = ''
	d.panel <= html.LABEL("Feature Name", For = "name")
	d.panel <= html.INPUT(id = "name")
	d.panel <= html.BR()
	d.panel <= html.LABEL("Feature Description", For = "desc")
	d.panel <= html.INPUT(id = "description")
	d.panel <= html.BR()
	d.panel <= html.LABEL("Is Numeric?", For = "numericCheck")
	numericCheck = html.INPUT(id = "numericCheck", type = "checkbox")
	numericCheck.bind("change", toggleNumeric)
	d.panel <= numericCheck
	d.panel <= html.BR()
	d.panel <= html.LABEL("Feature Value", For = "value")
	d.panel <= html.INPUT(id = "value", readonly = '')

	return d

def featureDelete(feature) -> dialog.Dialog:
	d = dialog.Dialog("Confirm Deletion", ok_cancel = ("Yes", "No"))

	d.panel <= html.B(
		"Are you sure you want to delete the \"" + feature + "\" feature?"
	)
	
	return d
