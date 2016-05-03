#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from axiohm import Axiohm
import sys

from PIL import Image

printer = Axiohm(port = '/dev/ttyS0', baudrate = 19200, xonxoff = True)
printer.reset()
printer.selectReceipt()

image = Image.open('test_image.png')
printer.printImage(image, printer.IMAGE_MODE_24DOT_DOUBLE)
