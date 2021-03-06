from browser import ajax
import json

def ajaxPostJSON(target : str, payload : dict, complete):
	ajax.post(
		target, headers = {"Content-Type": "application/json"},
		data = json.dumps(payload), oncomplete = complete
	)

def ajaxParseJSON(reply : ajax.Ajax) -> dict:
	return json.loads(reply.text)
