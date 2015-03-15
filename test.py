#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from axiohm import Axiohm

printer = Axiohm(port = '/dev/ttyS0', baudrate = 19200, xonxoff = True)

print printer.getModel()
print printer.getStatus()

printer.reset()
printer.waitForSlip()

printer.feedMilimeters(100)

lines = [
	"Line 1",
	"Line 2",
	"Line 3"
]

for line in lines:
	printer.moveAbsoluteMilimeters(20)
	printer.setDoubleWide()
	printer.printLineUnicode(line)

printer.ejectSlip()
