# IMPORTS
import os
# Characters not allowed in usernames and passwords (quote marks and backslash)
# as ASCII codes and characters
OUTLAWED_CHARS_CODES = set((0x22, 0x27, 0x5C, 0x60))
OUTLAWED_CHARS = ('"', "'", '\\', '`')
# Evaluate if all characters in a string s are allowed
def isAllowedChars(s : str) -> bool:
	if not s.isprintable():
		print("Non-printable chars detected in isAllowedChars")
	elif not set(ord(c) for c in s).isdisjoint(OUTLAWED_CHARS_CODES):
		print("Quote mark or backslash detected in isAllowedChars")
	else:
		return True
	
	return False
# Wrapper for isupper string method, only requires one success
def hasUpper(s : str) -> bool:
	return True in [c.isupper() for c in s]
# Wrapper for isnumeric string method, only requires one success
def hasNumeric(s : str) -> bool:
	return True in [c.isnumeric() for c in s]
# Checks if any allowed punctuation/formatting/special ASCII
# characters are in a string s, requires one success
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
# Check if a password s is of minimum length 12 and
# has at least one uppercase letter, one number, and one special character
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

