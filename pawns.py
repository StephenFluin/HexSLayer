import pygame, random
from pygame.locals import *
from hexmath import *

class Pawn(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.image = pygame.image.load("wizard.png")
		self.startTile = None
		
	def setPos(self,x,y):
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.startTile.pawn = None
		self.gameMap.getTile((x,y)).pawn = self
		self.gameMap.getTile((x,y)).draw()
		
	def attack(self,x,y):
		#print "Testing if we can attack this tile"
		#print "Returning the pawn to " , self.startTile.xloc,"X",self.startTile.yloc
		tiles = self.gameMap.getTileSet((self.startTile.xloc,self.startTile.yloc))
		for tile in tiles:
			if(tile.isAdjacent((x,y))):
				#The attacked tile is adjacent to a tile in our starting set
				if self.gameMap.getTile((x,y)).village:
					if (self.gameMap.getTile((x,y)).player != self.startTile.player):
						self.gameMap.renders.remove(self.gameMap.getTile((x,y)).village)
						self.gameMap.getTile((x,y)).village = None
					else:
						return False
				self.gameMap.getTile((x,y)).setPlayer(self.startTile.player)
				self.gameMap.cleanUpGame()
				return True
		return False
			
		
class Villager(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc)