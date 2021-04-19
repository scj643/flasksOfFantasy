itemIconDict = {
	"0A-clothing": "U1F45A",
	"0A-gi": "U1F94B",
	"0A-sash": "U1F9E3",
	"0A-gloves": "U1F9E4",
	"0A-footwear": "U1F45E",
	"0B-backpack": "U1F392",
	"0B-crown": "U1F451",
	"0B-helmet": "U1FA96",
	"1A-hammer": "U1F528",
	"1A-pickaxe": "U26CFUFE0F",
	"1A-axe": "U1FA93",
	"1B-bow": "U1F3F9",
	"1B-boomerang": "U1FA83",
	"1C-blade": "U1F5E1UFE0F",
	"1C-shield": "U1F6E1UFE0F",
	"1D-chain": "U26D3UFE0F",
	"1D-broom": "U1F9F9",
	"1D-staff": "U1F9AF",
	"1D-wand": "U1FA84",
	"1D-other": "U1FA80",
	"2A-key": "U1F5DDUFE0F",
	"2A-alchemy": "U2697UFE0F",
	"2A-die": "U1F3B2",
	"2A-scale": "U2696UFE0F",
	"2A-box": "U1F4E6",
	"2B-amulet": "U1F3C5",
	"2B-ring": "U1F48D",
	"2B-beads": "U1F4FF",
	"2C-coin": "U1FA99",
	"2C-orb": "U1F52E",
	"2C-gem": "U1F48E",
	"2C-treasure": "U1F4B0",
	"2C-artifact": "U2626UFE0F",
	"2C-urn": "U26B1UFE0F",
	"3A-flower": "U1F33C",
	"3A-fruit": "U1F34E",
	"3A-fish": "U1F41F",
	"3A-meat": "U1F356",
	"4A-camping": "U1F3D5UFE0F",
	"4A-log": "U1FAB5",
	"4A-rope": "U1F9F6",
	"4A-lute": "U1FA95",
	"4B-book": "U1F4D6",
	"4B-scroll": "U1F4DC",
	"4A-candle": "U1F56FUFE0F",
	"4B-brush": "U1F58CUFE0F",
	"4B-quill": "U1FAB6",
	"4B-letter": "U2709UFE0F"
}

prepCodePoint = lambda s : format(s, "0>6s")
makeCodePointBytes = lambda s : bytes.fromhex(prepCodePoint(s))
shaveBytes = lambda b : b[1:3] if b[0] == 0 else b
hexify = lambda n : format(n, 'x')
makeUTF83B = lambda b : \
	'e' + \
	hexify( (b[0] >> 4) & 0xf ) + \
	hexify( ( (b[0] >> 2) & 3 ) + 8 ) + \
	hexify( ( (b[0] & 3) << 2 ) + ( (b[1] >> 6) & 3 ) ) + \
	hexify( ( (b[1] >> 4) & 3 ) + 8 ) + \
	hexify(b[1] & 0xf)
makeUTF84B = lambda b : \
	'f' + \
	hexify( (b[0] >> 2) & 3 ) + \
	hexify( (b[0] & 3) + 8 ) + \
	hexify( b[1] >> 4 ) + \
	hexify( ( (b[1] >> 2) & 3 ) + 8 ) + \
	hexify( ( (b[1] & 3) << 2) + ( (b[2] >> 6) & 3 )) + \
	hexify( ( (b[2] >> 4) & 3 ) + 8 ) + \
	hexify( b[2] & 0xf )
renderUTF83B = lambda s : \
	bytes.fromhex(
		makeUTF83B(
			shaveBytes(
				makeCodePointBytes(s)
			)
		)
	).decode()
renderUTF84B = lambda s : \
	bytes.fromhex(
		makeUTF84B(
			shaveBytes(
				makeCodePointBytes(s)
			)
		)
	).decode()

group = 0
unit = 'A'

for k in itemIconDict.keys():
	newGroup = int(k[0])
	newUnit = k[1]
	if newGroup > group:
		print()
		group = newGroup
		unit = k[1]
	elif newUnit > unit:
		print()
		unit = newUnit

	codes = itemIconDict[k].split('U')[1:]
	p = ''
	utf8Strings = []
	for c in codes:
		if len(c) > 4:
			p += renderUTF84B(c)
			utf8Strings.append(makeUTF84B(shaveBytes(makeCodePointBytes(c))))
			#print(makeCodePointBytes(c), renderUTF84B(c))
		else:
			p += renderUTF83B(c)
			utf8Strings.append(makeUTF83B(shaveBytes(makeCodePointBytes(c))))
			#print(makeCodePointBytes(c), renderUTF83B(c))
	print(k, utf8Strings, p, sep = ": ", end = "; ")

print()
