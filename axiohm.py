from __future__ import division

import serial

class Axiohm:
	CODEPAGE_437 = 0
	CODEPAGE_850 = 1
	CODEPAGE_852 = 2
	CODEPAGE_860 = 3
	CODEPAGE_863 = 4
	CODEPAGE_865 = 5
	CODEPAGE_858 = 6
	CODEPAGE_866 = 7
	
	codepage_mapping = {
		CODEPAGE_437: 'cp437',
		CODEPAGE_850: 'cp850',
		CODEPAGE_852: 'cp852',
		CODEPAGE_860: 'cp860',
		CODEPAGE_863: 'cp863',
		CODEPAGE_865: 'cp865',
		CODEPAGE_866: 'cp866',
	}
	
	CUT_MODE_PARTIAL = 0
	CUT_MODE_PARTIAL_FEED = 66
	CUT_MODE_FULL = 1
	CUT_MODE_FULL_FEED = 65
	
	BARCODE_TEXT_NONE = 0
	BARCODE_TEXT_ABOVE = 1
	BARCODE_TEXT_BELOW = 2
	BARCODE_TEXT_BOTH = 3
	
	BARCODE_UPCA = 65
	BARCODE_UPCE = 66
	BARCODE_EAN13 = 67
	BARCODE_EAN8 = 68
	BARCODE_CODE39 = 69
	BARCODE_INT2OF5 = 70
	BARCODE_CODABAR = 71
	BARCODE_CODE93 = 72
	BARCODE_CODE128 = 73
	BARCODE_PDF417 = 75
	
	STATION_RECEIPT = 1
	STATION_SLIP = 4
	
	ALIGN_LEFT = 0
	ALIGN_CENTER = 1
	ALIGN_RIGHT = 2
	
	PITCH_STANDARD = 0
	PITCH_COMPRESSED = 1
	
	def __init__(self, **kwargs):
		self.serial = serial.Serial(**kwargs)
		self.currentStation = self.STATION_RECEIPT
		self.currentCodepage = self.CODEPAGE_437
	
	# CONTROL
	
	def beep(self):
		self.serial.write("\x1b\x07")

	def reset(self):
		self.currentStation = self.STATION_RECEIPT
		self.currentCodepage = self.CODEPAGE_437
		self.serial.write("\x1b\x40")
	
	def selectReceipt(self):
		self.currentStation = self.STATION_RECEIPT
		self.serial.write("\x1e")
	
	def selectSlip(self):
		self.currentStation = self.STATION_SLIP
		self.serial.write("\x1c")

	def getStatus(self):
		self.serial.write("\x1b\x76")
		data = ord(self.serial.read(1))
		return {
			'receiptPaperLow':  ((data & 0x01) != 0),
			'receiptCoverOpen': ((data & 0x02) != 0),
			'receiptPaperOut':  ((data & 0x04) != 0),
			'jam':              ((data & 0x08) != 0),
			'leadingEdge':      ((data & 0x20) != 0),
			'trailingEdge':     ((data & 0x40) != 0),
			'headOverheat':     ((data & 0x80) != 0),
		}
	
	def getModel(self):
		self.serial.write("\x1d\x49\x01")
		model = ord(self.serial.read(1))
		self.serial.write("\x1d\x49\x02")
		type = ord(self.serial.read(1))
		
		knownModels = {
			28: "Axiohm A758",
			26: "Axiohm A756",
		}
		modelName = "Unknown"
		if model in knownModels:
			modelName = knownModels[model]
		
		return {
			'model':       model,
			'modelName':   modelName,
			'twoByteCode': ((type & 0x01) != 0),
			'knife':       ((type & 0x02) != 0),
			'micr':        ((type & 0x08) != 0),
		}
	
	# CUTTING
	
	def cutMode(self, mode, offset=0):
		self.serial.write("\x1d\x56" + chr(mode))
		if mode == 65 or mode == 66:
			self.serial.write(chr(offset))
	
	def cutFeedFull(self):
		self.cutMode(Axiohm.CUT_MODE_FULL_FEED)
	
	def cutFeedPartial(self):
		self.cutMode(Axiohm.CUT_MODE_PARTIAL_FEED)
	
	def cutFull(self):
		self.serial.write("\x1b\x69")
	
	def cutPartial(self):
		self.serial.write("\x1b\x6d")
	
	def cut(self):
		self.cutFeedFull()
	
	# FORMATTING
	
	def clear(self):
		self.serial.write("\x10")
	
	def setDoubleWide(self):
		self.serial.write("\x12")
	
	def setSingleWide(self):
		self.serial.write("\x13")
	
	def setPitch(self, pitch = PITCH_STANDARD):
		self.serial.write("\x1b\x16" + chr(pitch))
	
	def setCodePage(self, codepage):
		self.currentCodepage = codepage
		self.serial.write("\x1b\x52" + chr(codepage))
	
	def rotateCCW(self):
		self.serial.write("\x1b\x12")
	
	def rotateCW(self):
		self.serial.write("\x1b\x56\x01")
	
	def upsideDown(self):
		self.serial.write("\x1b\x7b\x01")
	
	def align(self, alignment):
		assert self.currentStation != self.STATION_SLIP, 'Slip station prints cannot be aligned'
		self.serial.write("\x1b\x61" + chr(alignment))
	
	def alignLeft(self):
		self.align(self.ALIGN_LEFT)
	
	def alignCenter(self):
		self.align(self.ALIGN_CENTER)
	
	def alignRight(self):
		self.align(self.ALIGN_RIGHT)
	
	def setBarcodeTextLocation(self, location = BARCODE_TEXT_NONE):
		self.serial.write("\x1d\x48" + chr(location))
	
	def setBarcodeTextPitch(self, pitch = PITCH_STANDARD):
		self.serial.write("\x1d\x66" + chr(pitch))
	
	def setBarcodeHeight(self, width):
		self.serial.write("\x1d\x68" + chr(width))
	
	def setBarcodeHeightInches(self, inches = 1):
		if self.currentStation == self.STATION_SLIP:
			self.setBarcodeHeight(int(inches * 216))
		else:
			self.setBarcodeHeight(int(inches * 203))
	
	def setBarcodeHeightMilimeters(self, milimeters = 8.5):
		if self.currentStation == self.STATION_SLIP:
			self.setBarcodeHeight(int(milimeters / 8.5))
		else:
			self.setBarcodeHeight(int(milimeters / 8))
	
	# FEEDING
	
	def feedLines(self, lines = 1):
		if lines < 0:
			assert self.currentStation != self.STATION_SLIP, 'Receipt station cannot be reverse feed'
			lines = -lines
			self.serial.write("\x1d")
		self.serial.write("\x14" + chr(lines))
	
	def feedDots(self, dots = 1):
		if dots < 0:
			assert self.currentStation != self.STATION_SLIP, 'Receipt station cannot be reverse feed'
			dots = -dots
			self.serial.write("\x1d")
		
		while(dots > 255):
			self.serial.write("\x15\xff")
			dots -= 255
		
		self.serial.write("\x15" + chr(dots))
	
	def feedInches(self, inches = 0.1):
		if self.currentStation == self.STATION_SLIP:
			self.feedDots(int(inches * 72))
		else:
			self.feedDots(int(inches * 203))
	
	def feedMilimeters(self, milimeters = 10):
		if self.currentStation == self.STATION_SLIP:
			self.feedDots(int(milimeters * 19 / 2.388))
		else:
			self.feedDots(int(milimeters * 7 / 2.47))
	
	# PRINT POSITION
	
	def moveAbsolute(self, dots):
		self.serial.write("\x1b\x24" + chr(dots % 256) + chr(int(dots/256)))
	
	def moveAbsoluteInches(self, inches):
		if self.currentStation == self.STATION_SLIP:
			self.moveAbsolute(int(inches * 660 / 4.752))
		else:
			self.moveAbsolute(int(inches * 576 / 2.835))
	
	def moveAbsoluteMilimeters(self, milimeters):
		if self.currentStation == self.STATION_SLIP:
			self.moveAbsolute(int(milimeters * 660 / 120.7))
		else:
			self.moveAbsolute(int(milimeters * 576 / 72))
	
	def moveRelative(self, dots):
		if dots < 0:
			dots = 65536 + dots
		self.serial.write("\x1b\x5c" + chr(dots % 256) + chr(int(dots/256)))
	
	def moveRelativeInches(self, inches):
		if self.currentStation == self.STATION_SLIP:
			self.moveRelative(int(inches * 660 / 4.752))
		else:
			self.moveRelative(int(inches * 576 / 2.835))
	
	def moveRelativeMilimeters(self, milimeters):
		if self.currentStation == self.STATION_SLIP:
			self.moveRelative(int(milimeters * 660 / 120.7))
		else:
			self.moveRelative(int(milimeters * 576 / 72))
	
	# PRINTING
	
	def printUnicode(self, line=""):
		printData = ""
		for char in line:
			try:
				printData += char.encode(self.codepage_mapping[self.currentCodepage])
			except ValueError:
				for codepage, encoding in self.codepage_mapping.iteritems():
					try:
						charEncoded = char.encode(encoding)
						self.currentCodepage = codepage
						printData += "\x1b\x52" + chr(codepage) + charEncoded
						break
					except ValueError:
						pass
				else:
					raise
		self.printText(printData)
	
	def printText(self, lines):
		self.serial.write(lines)
	
	def printLine(self, line=""):
		self.printText(line + "\r\n")
	
	def printLineUnicode(self, line=""):
		self.printUnicode(line + "\r\n")
	
	def printBarcode(self, type, data):
		assert(type > 64)
		self.serial.write("\x1d\x6b" + chr(type) + chr(len(data)) + data)
	
	def printLinesRotatedCCW(self, lines, startingPosition = 0):
		maxLineLength = max([len(line) for line in lines])
		lines = [line.ljust(maxLineLength, ' ') for line in lines]
		
		self.rotateCCW()
		for column in xrange(maxLineLength-1, -1, -1):
			if startingPosition != 0:
				self.moveAbsolute(startingPosition)
			self.printLineUnicode(''.join([line[column] for line in lines]))
	
	# SLIP
	
	def waitForSlip(self):
		self.serial.write("\x1b\x63\x30\x04")
	
	def ejectSlip(self):
		self.serial.write("\x0c")