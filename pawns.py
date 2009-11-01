# Pawns Classfiles
# provides objects representing different pawns that can be placed on the game board.
#
#

import pygame, random
from pygame.locals import *
from hexmath import *

class Pawn(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y,level):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.startTile = None
		self.moved = False
		self.level = level
		
	def setPos(self,x,y):
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.startTile.pawn = None
		self.gameMap.getTile((x,y)).pawn = self
		self.gameMap.getTile((x,y)).draw()
		
	def attack(self,x,y):
		#print "Testing if we can attack this tile"
		#print "Returning the pawn to " , self.startTile.xloc,"X",self.startTile.yloc
		dest = self.gameMap.getTile((x,y))
		tiles = self.gameMap.getTileSet((self.startTile.xloc,self.startTile.yloc))
		for tile in tiles:
			if(tile.isAdjacent((x,y))):
				#The attacked tile is adjacent to a tile in our starting set
				if dest.player != self.startTile.player:
					self.moved = True
					
				# Check if it is a unit and handle cases
				if dest.pawn:
					if (dest.player != self.startTile.player):
						if self.level > dest.pawn.level:
							self.gameMap.renders.remove(dest.pawn)
						else:
							return False
						dest.pawn = None
					else:
						# Handle upgrades by replacing dest
						if self.level == 1 and dest.pawn.level <= 4:
							
							while self.level <= dest.pawn.level:
								self.upgrade()
							self.gameMap.renders.remove(dest.pawn)
							
							return True
						
							
							
						return False
					
				# Check if it is a village to prevent moving pawn into friendly villages
				if dest.village:
					
					if (dest.player != self.startTile.player):
						self.gameMap.renders.remove(dest.village)
						dest.village = None
					else:
						return False
				dest.setPlayer(self.startTile.player)
				self.gameMap.cleanUpGame()
				
				return True
				
		return False
		
	def upgrade(self):
		print "Upgrading this pawn from level ",self.level
		self.level += 1
		if self.level == 2:
			self.image = pygame.image.load("wizard.png")
			self.upkeep = 6
		elif self.level == 3:
			self.image = pygame.image.load("swordsman.png")
			self.upkeep = 18
		elif self.level == 4:
			self.image = pygame.image.load("knight.png")
			self.upkeep = 50
			
		
class Villager(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,1)
		self.image = pygame.image.load("villager.png")
		self.upkeep = 2

class Grave(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("dead.png")
		self.upkeep = 2
		self.x = x
		self.y = y
		print "Grave is created at %sx%s." % (x,y)
