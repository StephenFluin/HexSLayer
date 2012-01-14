#!/usr/bin/python
#
# HexSLayer
# copyright (C) Stephen Fluin 2009
#

import pygame

try:
	import android
except ImportError:
	android = None

pygame.init()

tilesize = 34
playerColors = ("#717728","#A481AA","#A69781","#E5E8E6","#ACD8E6","#8D1F4A")
bgColor = pygame.Color("#000000")
fontColor = pygame.Color("#FFFFFF")
fontName = "Roboto-Regular.ttf"
#Old Neon Colors ("#66FF33","#003DF5","#FF3366","#33FFCC","#FFCC33","#FF6633")
playerNames = ("Human Player", "AI 1", "AI 2", "AI 3", "AI 4", "AI 5")

size = pygame.display.list_modes()[0]
masterSize = [size[0],size[1]]
if not android:
	masterSize[0] = min(800,size[0])
	masterSize[1] = min(480,size[1])


infobarLocation =(10,masterSize[1]-40)

scoreLocation = (masterSize[0]-210,32)
endTurnLocation = (masterSize[0]-210,masterSize[1]-40)
messengerLocation = (endTurnLocation[0],endTurnLocation[1]-150)
storeLocation = (endTurnLocation[0]-120,masterSize[1]-40)

tileSpaceX = masterSize[0]-210-20
tileSpaceY = masterSize[1]-40-20-30
tilesize = tileSpaceY /9