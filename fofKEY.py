import os

KEY_FILE = "secret.key"

def newKey():
    keyFile = open(KEY_FILE, "wb")
    newKey = os.urandom(32)
    keyFile.write(newKey)
    keyFile.close()
    closeWriteOnKey()

def getKey() -> bytes:
    keyFile = open(KEY_FILE, "rb")
    key = keyFile.read()
    keyFile.close()
    return key

def openWriteOnKey():
    os.chmod("./" + KEY_FILE, 0o600)

def closeWriteOnKey():
    os.chmod("./" + KEY_FILE, 0o400)
