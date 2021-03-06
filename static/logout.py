from browser import document, window

def logout(event):
	window.location.href = "/logout/"

document["logout"].bind("click", logout)
