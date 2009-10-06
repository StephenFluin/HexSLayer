#!/usr/bin/python

import pygame
import random
from pygame.locals import *


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'
tilesize = 32

pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('HexSLayer')

playerColors = ("#003DF5","#FF3366","#66FF33","#33FFCC","#FFCC33","#FF6633")

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))

selected = None
class Pawn(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.image = pygame.image.load("wizard.png");
		self.startTile = None
	def setPos(self,x,y):
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.startTile.pawn = None
		self.gameMap.getTile((x,y)).pawn = self
		self.gameMap.getTile((x,y)).draw()
	def attack(self,x,y):
		print "Testing if we can attack this tile"
		print "Returning the pawn to " , self.startTile.xloc,"X",self.startTile.yloc
		tiles = self.gameMap.getTileSet((self.startTile.xloc,self.startTile.yloc))
		for tile in tiles:
			if(tile.isAdjacent((x,y))):
				#The attacked tile is adjacent to a tile in our starting set
				self.gameMap.getTile((x,y)).setPlayer(self.startTile.player)
				return True
		return False
			
		
class Villager(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc)
	
		

class Tile(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.Surface([tilesize, tilesize])
		self.x,self.y = convertGridPosition(gameMap,xloc,yloc)
		self.xloc = xloc
		self.yloc = yloc
		self.setPlayer(random.randint(0,5))
		self.rect = self.draw()
		self.selected = False
		self.pawn = None
		

	def setPlayer(self,player):
		self.player = player
		self.color = pygame.Color(playerColors[self.player])
		
	def draw(self):
		rect = pygame.draw.polygon(background,self.color,self.getHex(),0)
		pygame.draw.polygon(background,pygame.Color("#000000"),self.getHex(),1)
		#pygame.display.update()
		
		return rect
	
	def getHex(self):
		return getHexAt(self.x,self.y)
		
	def getPoint(self):
		return (self.xloc,self.yloc)
		
	def checkHexCollision(self,point):
		s = tilesize
		l = .25
		x = point[0] - self.x
		y = point[1] - self.y
		#print "Mouse Hit:",x,"X",y," is it less than ",s/2
		#print "1,2,3,4:",(2*x + y),",",(2*x + (s-y)),",",(2*(s-x)+y),",",(2*(s-x)+(s-y))
		
		if ((2*x + y) <  s/2) or ((2*x + (s-y)) < s/2) or ((2*(s-x)+y) < s/2) or ((2*(s-x)+(s-y)) < s/2):
			# Failed hitdetection on hex
			return 0
		else:
			return 1
	def getAdjacent(self,direction):
		return getAdjacent(self.xloc,self.yloc,direction)
	def isAdjacent(self,point):
		#print "Checking for adjacency."
		for dir in range(6):
			target = self.getAdjacent(dir)
			if(target == point):
				print "Target was adjacent to this square"
				return True
		return False
			
	def select(self):
		#print "Selecting tile."
		pygame.draw.polygon(background,pygame.Color("#FFFFFF"),self.getHex(),1)
		self.selected = True
	def deselect(self):
		#print "Deselecting tile"
		self.draw()
		self.selected = False
	def addPawn(self,pawn):
		self.pawn = pawn
		return pawn
			

class Map():
	def __init__(self):
		self.width = 13
		self.height = 25
		self.x = 5
		self.y = 30
		
		self.tiles = []
		self.alltiles = []
		
		for y in range(self.height):
			
			row = [None]*self.width
			for x in range(self.width):
				row[x] = Tile(self,x,y)
				self.alltiles.append(row[x])
			self.tiles.append(row)		
			
	def hexClicked(self,x,y):
		retval = None
		print "Clicked tile:",self.tiles[y][x].xloc,"X",self.tiles[y][x].yloc
		clickedTile = self.tiles[y][x]
		if(clickedTile.pawn != None):
			retval = clickedTile.pawn
		
		selectedSet = self.getTileSet((x,y))
		if not retval:
			for tile in selectedSet:
				if(tile.selected == 0): 
					tile.select()
				else: 
					tile.deselect()
					
		return retval
		
	def hexDropped(self,carry,x,y):
		clickedTile = self.tiles[y][x]
		carry.setPos(x,y)
		print "Set the position of the carry to ",x,"X",y
		
	def getTile(self,point):
		if point[1] < 0 or point[1] >= self.height or point[0] < 0 or point[0] > self.width:
			return None
		return self.tiles[point[1]][point[0]]
		
			
	
	#We are going to do a breadth first search to find all connected tiles of same color
	def getTileSet(self,point):
		tile = self.getTile(point)
		searched = []
		toSearch = [tile]
		found = [tile]
		while(len(toSearch) >0):
			searching = toSearch.pop()
			searched.append(searching)
		
			for i in range(6):
				considered = self.getTile(searching.getAdjacent(i))
				if considered and searching.player == considered.player:
					#print "Was same color"
					if considered not in searched and considered not in toSearch:
						toSearch.append(considered)
					if considered not in found:
						found.append(considered)
		#print "Our search found: ",found
		return found
		
	
	
def getHexAt(x,y):
	s = tilesize
	l = .25
	r = .75
	return ((x+l*s,y), (x+r*s,y), (x+s,y+s/2), (x+r*s,y+s), (x+l*s,y+s), (x,y+s/2))
	
def convertGridPosition(map,x,y):
	return (x*1.5*tilesize+y%2*tilesize*.75+map.x,y*tilesize/2+map.y)
		
def main():
	

	gameMap = Map()
	mouseCarrying = None
	

	if pygame.font:
		font = pygame.font.Font(None, 36)
		text = font.render("Welcome to HexSLayer",1,(10,10,10))
		textpos = text.get_rect(centerx=background.get_width()/2)
		background.blit(text,textpos)

	clock = pygame.time.Clock()
	allsprites = pygame.sprite.RenderPlain(())
	
	
	pawns = []
	pawns.append(gameMap.tiles[3][7].addPawn(Villager(gameMap,7,3)))
	

	while True:
		clock.tick(60)
		#Handle Input Events
		if True:
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == MOUSEBUTTONDOWN:
					#print "Looking for collisions"
					for row in gameMap.tiles:
						for tile in row:
							if tile.rect.collidepoint(pygame.mouse.get_pos()):
								
								if tile.checkHexCollision(pygame.mouse.get_pos()):
									
									mouseCarrying = gameMap.hexClicked(tile.xloc,tile.yloc)
									if mouseCarrying:
										mouseCarrying.startTile = tile
										print "I have set the startTile of the carry."
									break
				elif event.type == MOUSEBUTTONUP:
					if mouseCarrying:
						for row in gameMap.tiles:
							for tile in row:
								if tile.rect.collidepoint(pygame.mouse.get_pos()):
									if tile.checkHexCollision(pygame.mouse.get_pos()):
										if(mouseCarrying.attack(tile.xloc,tile.yloc)):
											print "Attack of this square was successful, dropping player there."
											gameMap.hexDropped(mouseCarrying,tile.xloc,tile.yloc)
										else:
											mouseCarrying.setPos( mouseCarrying.startTile.xloc,mouseCarrying.startTile.yloc)
						mouseCarrying = None
				elif event.type == MOUSEMOTION:
					if mouseCarrying != None:
						mouseCarrying.x,mouseCarrying.y = pygame.mouse.get_pos()
						mouseCarrying.x -= 5
						mouseCarrying.y -= 5
		allsprites.update()

		#Draw Everything
		screen.blit(background, (0, 0))
		for pawn in pawns:
			screen.blit(pawn.image,(pawn.x,pawn.y))
		allsprites.draw(screen)
		pygame.display.flip()

# adjacency works as:	NW		N		NE		SE		S	SW
# 1,2 is different like:	-1,-1	0,-2		0,-1		0,1		0,2	-1,1
# 0,3 is different like:	0,-1		0,-2		1,-1		1,1		0,2	0,1
# 1,3 is different like:	0,-1		0,-2		1,-1		1,1		0,2	0,1
# 1,4 is different like:	-1,-1	0,-2		0,-1		0,1		0,2	-1,1
def isAdjacent(x1,y1,x2,y2):
	for i in range(6):
		if getAdjacent(x1,y1,i) == (x2,y2):
			return 1
	return 0

# We define 0 as north, then go clockwise.
def getAdjacent(x,y,direction):
	evenYChanges = ((0,-2),(0,-1),(0,1),(0,2),(-1,1),(-1,-1))
	oddYChanges = ((0,-2),(1,-1),(1,1),(0,2),(0,1),(0,-1))
	dirChanges=(evenYChanges,oddYChanges)
	change = dirChanges[y % 2][direction]
	return (x+change[0],y+change[1])



main()
