#
# HexSLayer
# copyright (C) Stephen Fluin 2012
#

# Pawns Classfiles
# provides objects representing different pawns that can be placed on the game board.
#

from __future__ import absolute_import
from __future__ import print_function
import pygame, random
from pygame.locals import *
from hexmath import *

class Pawn(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc,level):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPawnPosition(self.gameMap,xloc,yloc)
		self.xloc,self.yloc = xloc,yloc
		self.startTile = None
		self.moved = False
		self.level = level
		self.spin = 0
		self.player = -1
		self.justPurchased = False
		self.indicator = None
		
	def getHasMoved(self):
		return self.moved
		
		
	def setPos(self,xloc,yloc):
		self.xloc,self.yloc = xloc,yloc
		self.x,self.y = convertGridPawnPosition(self.gameMap,xloc,yloc)
		if not self.justPurchased:
			self.startTile.pawn = None
		self.gameMap.getTile((xloc,yloc)).pawn = self
		self.gameMap.getTile((xloc,yloc)).draw()
		
		# Is this good enough to set the player for all pawns?
		if(self.gameMap.getTile((xloc,yloc))):
			self.player = self.gameMap.getTile((xloc,yloc)).player
		
	# Returns true if attack was successful (movement taken, or false if nothing happened)
	# Should handle moving of sprites, reallocation of space, destruction of victims.
	def attack(self,xloc,yloc):		
		#print "Testing if we can attack this tile"
		#print "Returning the pawn to " , self.startTile.xloc,"X",self.startTile.yloc
		dest = self.gameMap.getTile((xloc,yloc))
		#print "Attacking tile at %sx%s, which belongs to player %s" % (x,y,dest.player)
		tiles = self.gameMap.getTileSet((self.startTile.xloc,self.startTile.yloc))

		#Iterate over current set to determine if x,y are adjacent.
		for tile in tiles:
			if(tile.isAdjacent((xloc,yloc))):
				#The attacked tile is adjacent to a tile in our starting set
				
				
				#Newly organized version of attack code
				# Step 1. Check if just moving within my realm and allow
				if dest.player != self.startTile.player:
					self.moved = True
				else:
					if dest.village:
						return False
					if dest.pawn and dest.pawn != self: 
						if self.level == 1 and dest.pawn.level <= 4:
							
							while self.level <= dest.pawn.level and self != dest.pawn:
								#print "Upgrading because self level is %s and dest pawn level is %s." % (self.level, dest.pawn.level)
								if not isinstance(dest.pawn,Castle) and self.upgrade():
									pass
								else:
									return False
							if dest.pawn not in self.gameMap.renders:
								print("Found a weird fringe case where the unit we are upgrading isn't being rendered!!!!")
							self.gameMap.renders.remove(dest.pawn)
							
							return True
						return False
						
					return True
					
				
				#Step 2 & # Block movement by protection
				if self.level <= dest.getProtection():
					
					self.moved = False
					self.gameMap.message("This hex is protected.",self.startTile.player)
					return False

				#Weird edge case experienced on 20100109
				if dest.pawn and dest.pawn not in self.gameMap.renders:
					print("WEIRD EDGE CASE WITH %s and %s." % (dest.pawn, self.gamemap.renders))
					
					
				# Step 4. Kill whatever is left with your movement.
				#@TODO this should only be dest.pawn
				if dest.pawn:
					dest.pawn.kill(dest)
					print("Killing pawn because of successfull attack.")
				if dest.village:
					dest.village.kill(dest)
				
				

			
				dest.setPlayer(self.startTile.player)
				self.gameMap.cleanUpGame()
				
				return True
				
			
		self.gameMap.message("Destination must be adjacent to region.",self.startTile.player)
		return False
		
	def upgrade(self):
		#print "Upgrading this pawn from level ",self.level
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
		return True
		
	# Kill removes pawn from renders, deletes it from the listed tile, adds a gravesite
	def kill(self,tile):
		print("Pawn at %sx%s is now dead." % (self.xloc, self.yloc))
		if(self in self.gameMap.renders):
			self.gameMap.renders.remove(self)
			tile.pawn = None
			# why do we add graves in case of hunger death? :(
			
			#print "Removed a pawn and added a grave."
	
	def starve(self,tile):
		tile.grave = Grave(self.gameMap,tile.xloc,tile.yloc)
		self.gameMap.renders.insert(0,tile.grave)
		print("Pawn starved.")
		self.kill(tile)
		
	# Updates the render of the spinner around the current unit
	def makeIndicator(self):
		self.indicator = AvailableMove(self.x,self.y)
		
			
# Takes in tile coordinates, not x/y coordinates
class Villager(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,1)
		self.image = pygame.image.load("villager.png")
		self.upkeep = 2
		
class Castle(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,2)
		self.image = pygame.image.load("castle.png")
		self.upkeep = 0
	def getHasMoved(self):
		return True
	def kill(self,tile):
		print("About to kill a legendary castle, my protection is:%s" % (tile.getProtection()))
		Pawn.kill(self,tile)
		
class Village(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,1)
		self.upkeep = 0
		self.balance = 5
		self.image = pygame.image.load("village.png")
		self.player = gameMap.getTile((xloc,yloc)).player
		self.xloc = xloc
		self.yloc = yloc
	def getHasMoved(self):
		return True
	def kill(self,tile):
		tile.village = None
		Pawn.kill(self,tile)
		


class Grave(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("dead.png")
		(self.x,self.y) = convertGridPawnPosition(gameMap,xloc,yloc)
		#print "Grave is created at %sx%s." % (x,y)
		
class AvailableMove(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image =pygame.image.load("sparks.png")
		self.image = pygame.transform.smoothscale(self.image,(40,40))
		
		self.original = self.image
		self.rect = self.image.get_rect()
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rotation = 0
		self.rect.topleft = x-4,y-4
		
	def spin(self):
		center = self.rect.center
		self.rotation += 4
				
		self.image = pygame.transform.rotate(self.original,self.rotation)
		self.rect = self.image.get_rect(center=center)
		
	def render(self, screen):
		screen.blit(self.image,self.rect)
		
		
		
