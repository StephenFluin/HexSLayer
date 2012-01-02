#!/usr/bin/python
#
# HexSLayer
# copyright (C) Stephen Fluin 2009
#

import pygame

tilesize = 34
playerColors = ("#313328","#695038","#8F825F","#E5E8E6","#BCE8E6","#9C4724")
bgColor = pygame.Color("#000000")
fontColor = pygame.Color("#FFFFFF")
#Old Neon Colors ("#66FF33","#003DF5","#FF3366","#33FFCC","#FFCC33","#FF6633")
playerNames = ("Human Player", "AI 1", "AI 2", "AI 3", "AI 4", "AI 5")

masterSize = (800,480)

infobarLocation =(10,masterSize[1]-40)

scoreLocation = (masterSize[0]-210,30)
endTurnLocation = (masterSize[0]-210,masterSize[1]-40)
storeLocation = (endTurnLocation[0]-70,masterSize[1]-40)

tileSpaceX = masterSize[0]-210-20
tileSpaceY = masterSize[1]-40-20-30
tilesize = tileSpaceY /9