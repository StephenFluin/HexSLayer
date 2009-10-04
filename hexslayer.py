#!/usr/bin/python

import pygame
import random
from pygame.locals import *


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'
tilesize = 30

pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('HexSLayer')

playerColors = ("#003DF5","#FF3366","#66FF33","#33FFCC","#FFCC33","#FF6633")

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))

selected = None


class Tile(pygame.sprite.Sprite):
	def __init__(self,xloc,yloc,x,y):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.Surface([tilesize, tilesize])
		self.x = x
		self.y = y
		self.xloc = xloc
		self.yloc = yloc
		self.player = random.randint(0,5)
		self.color = pygame.Color(playerColors[self.player])
		self.rect = self.draw()
		self.selected = 0
		

		
	def draw(self):
		rect = pygame.draw.polygon(background,self.color,self.getHex(),0)
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
	def select(self):
		#print "Selecting tile."
		pygame.draw.polygon(background,pygame.Color("#000000"),self.getHex(),1)
		self.selected = 1
	def deselect(self):
		#print "Deselecting tile"
		self.draw()
		self.selected = 0
			

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
				row[x] = Tile(x,y,x*1.5*tilesize+y%2*tilesize*.75+self.x,y*tilesize/2+self.y)
				self.alltiles.append(row[x])
			self.tiles.append(row)		
			
	def hexClicked(self,x,y):
		#self.tiles[y][x].color = pygame.Color(0,0,0)
		#self.tiles[y][x].draw()
		print "Tried to flip color of tile:",self.tiles[y][x].xloc,"X",self.tiles[y][x].yloc
		selectedSet = self.getTileSet((x,y))
		for tile in selectedSet:
			if(tile.selected == 0): 
				tile.select()
			else: 
				tile.deselect()
		
	def getTile(self,point):
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
				if searching.player == considered.player:
					#print "Was same color"
					if considered not in searched and considered not in toSearch:
						toSearch.append(considered)
					if considered not in found:
						found.append(considered)
				else:
					#print "Wasn't same color (",tile.player,"!=",self.getTile(tile.getAdjacent(i)).player,")"
		#print "Our search found: ",found
		return found
	
def getHexAt(x,y):
	s = tilesize
	l = .25
	r = .75
	return ((x+l*s,y), (x+r*s,y), (x+s,y+s/2), (x+r*s,y+s), (x+l*s,y+s), (x,y+s/2))
	

		
def main():
	

	gameMap = Map()
	wizard = pygame.image.load("wizard.png");
	

	if pygame.font:
		font = pygame.font.Font(None, 36)
		text = font.render("Welcome to HexSLayer",1,(10,10,10))
		textpos = text.get_rect(centerx=background.get_width()/2)
		background.blit(text,textpos)

	clock = pygame.time.Clock()
	allsprites = pygame.sprite.RenderPlain(())
	

	while 1:
		clock.tick(60)
		#Handle Input Events
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
								
								gameMap.hexClicked(tile.xloc,tile.yloc)
								break
		allsprites.update()

		#Draw Everything
		screen.blit(background, (0, 0))
		screen.blit(wizard,(100,100))
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
