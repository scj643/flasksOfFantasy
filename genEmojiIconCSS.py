itemIconDict = {
	"0A-clothing": "U1F45A",
	"0A-gi": "U1F94B",
	"0A-sash": "U1F9E3",
	"0A-gloves": "U1F9E4",
	"0A-footwear": "U1F45E",
	"0B-backpack": "U1F392",
	"0B-crown": "U1F451",
	"0B-amulet": "U1F3C5",
	"0B-ring": "U1F48D",
	"0B-beads": "U1F4FF",
	"1A-hammer": "U1F528",
	"1A-pickaxe": "U26CFUFE0F",
	"1A-axe": "U1FA93",
	"1B-bow": "U1F3F9",
	"1C-blade": "U1F5E1UFE0F",
	"1C-shield": "U1F6E1UFE0F",
	"1D-chain": "U26D3UFE0F",
	"1D-broom": "U1F9F9",
	"1D-staff": "U1F9AF",
	"1D-other": "U1FA80",
	"2A-key": "U1F5DDUFE0F",
	"2A-treasure": "U1F4B0",
	"2A-alchemy": "U2697UFE0F",
	"2A-die": "U1F3B2",
	"2B-orb": "U1F52E",
	"2B-gem": "U1F48E",
	"2B-artiface": "U2626UFE0F",
	"2B-urn": "U26B1UFE0F",
	"3-flower": "U1F33C",
	"3-fruit": "U1F34E",
	"3-fish": "U1F41F",
	"3-meat": "U1F356",
	"4A-camping": "U1F3D5UFE0F",
	"4B-book": "U1F4D6",
	"4B-scroll": "U1F4DC",
	"4A-candle": "U1F56FUFE0F",
	"4B-brush": "U1F58CUFE0F"
}

def makeCSSRule(key : str, id : str, value : str) -> str:
	return id + "::before, button.itemIcon[value = \"" + key + "\"]::before {" \
		+ "\n\tcontent: \"" + value + "\";\n}\n"

iconGroup = 0
cssFile = open("./static/sheetItemIcons.css", 'w')

for k in itemIconDict:
	currentGroup = int(k.split('-')[0][0])
	if currentGroup != iconGroup:
		print()
		iconGroup = currentGroup
	
	codes = itemIconDict[k].split('U')[1:]
	if len(codes) == 1:
		code = codes[0]

		cssID = '#U' + code
		cssString = "\\0" + code
		cssFile.write(makeCSSRule(k, cssID, cssString))

		if len(code) > 4:
			print(
				k,
				bytes.fromhex(
					format(code, "0>8s")
				).decode(
					"UTF-32BE"
				),
				end = ' '
			)
		else:
			print(
				k,
				bytes.fromhex(code).decode("UTF-16BE"),
				end = ' '
			)
	elif len(codes) == 2:
		code = codes[0] + codes[1]

		cssID = "#U" + codes[0] + 'U' + codes[1]
		cssString = "\\0" + codes[0] + "\\0" + codes[1]
		cssFile.write(makeCSSRule(k, cssID, cssString))

		if len(code) == 8:
			print(
				k,
				bytes.fromhex(code).decode("UTF-16BE"),
				end = ' '
			)
		elif len(code) == 9:
			print(
				k,
				bytes.fromhex(
					format(codes[0], "0>8s")
				).decode("UTF-32BE") \
				+ bytes.fromhex(codes[1]).decode("UTF-16BE"),
				end = ' '
			)

cssFile.close()
print()
