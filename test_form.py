#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from axiohm import Axiohm

printer = Axiohm(port = '/dev/ttyS0', baudrate = 19200, xonxoff = True)

print printer.getModel()
print printer.getStatus()

slip = 0

printer.reset()

if slip:
	printer.waitForSlip()
	printer.setBarcodeWidth(2)
else:
	printer.selectReceipt()
	printer.setPitch(printer.PITCH_COMPRESSED)
	printer.setBarcodeWidth(3)
	printer.cut()

printer.setBarcodeHeight(32)

printer.alignCenter()
printer.printLineUnicode(u"┌──────────────────────────────────────────────────────┐")
printer.printLineUnicode(u"│ POTWIERDZENIE NADANIA  przesyłki poleconej nr        │")
printer.printCode128([105, 102, 0, 75, 90, 07, 73, 12, 34, 56, 78, 90])
printer.feedDots(5)
printer.printLineUnicode(u"│               (00) 7 5900773 1 234567890             │")
printer.printLineUnicode(u"├───────────────────────────────┐                      │")
printer.printLineUnicode(u"│ NADAWCA:                      │ Opłata ... zł ... gr │")
printer.printLineUnicode(u"│ Test Testowy                  │ Masa   ... kg ... g  │")
printer.printLineUnicode(u"│ ul. Testowa 1                 │ GABARYT   A[ ] B[ ]  │")
printer.printLineUnicode(u"│ 01-001 Test                   │ Priorytetowa:   [ ]  │")
printer.printLineUnicode(u"│                               │ Potw. odbioru:  [ ]  │")
printer.printLineUnicode(u"│                               │                      │")
printer.printLineUnicode(u"│ ADRESAT:                      │                      │")
printer.printLineUnicode(u"│ Test Testowy                  │    (           )     │")
printer.printLineUnicode(u"│ ul. Testowa 1                 │                      │")
printer.printLineUnicode(u"│ 01-001 Test                   │                      │")
printer.printLineUnicode(u"│                               │ Podpis przyjmującego │")
printer.printLineUnicode(u"└───────────────────────────────┴──────────────────────┘")

if slip:
	printer.ejectSlip()
else:
	printer.cut()
