import os

OUTLAWED_CHARS_CODES = set((0x22, 0x27, 0x5C, 0x60))
OUTLAWED_CHARS = ('"', "'", '\\', '`')

def isAllowedChars(s : str) -> bool:
	if not s.isprintable():
		print("Non-printable chars detected in isAllowedChars")
	elif not set(ord(c) for c in s).isdisjoint(OUTLAWED_CHARS_CODES):
		print("Quote mark or backslash detected in isAllowedChars")
	else:
		return True
	
	return False

def hasUpper(s : str) -> bool:
	return True in [c.isupper() for c in s]

def hasNumeric(s : str) -> bool:
	return True in [c.isnumeric() for c in s]

def hasSpecial(s : str) -> bool:
	for c in s:
		o = ord(c)
		if o not in OUTLAWED_CHARS_CODES and ( \
			o in range(0x20, 0x30) or \
			o in range(0x3A, 0x41) or \
			o in range(0x5B, 0x60) or \
			o in range(0x7B, 0x7F) \
		):
			return True
	return False

def isStrongPassword(s : str) -> bool:
	if not len(s) > 11:
		print("Password shorter than 12 characters in isStrongPassword")
	elif not hasUpper(s):
		print("No uppercase letter detected in isStrongPassword")
	elif not hasNumeric(s):
		print("No numeral detected in isStrongPassword")
	elif not hasSpecial(s):
		print("No special character (punctuation, symbols) detected in isStrongPassword")
	else:
		return True

	return False
