#
# HexSLayer
# copyright (C) Stephen Fluin 2011
#

import pygame, random
from pygame.locals import *
from hexmath import *
from hexconfig import *

			
class GameOver(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y,winner):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = x,y
		self.gameMap = gameMap
		self.winner = winner
		print "Winner of game is %s." % (self.winner)
		self.draw()
	def draw(self):
		self.image = pygame.Surface((560,100))
		self.image.fill(bgColor)
		font = pygame.font.Font(fontName,28)
		text = font.render("Player %s (%s) won! Congratulations!" % (self.winner,self.gameMap.players[self.winner].getName()),True,fontColor)
		self.image.blit(text,(0,0))

class NewGame(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = x,y
		self.draw()
	def draw(self):
		self.image = pygame.Surface((300,40))
		self.image.fill(bgColor)
		font = pygame.font.Font(fontName,20)
		text = font.render("Start Another Game",True,fontColor)
		self.rect = pygame.draw.rect(self.image,(0,0,0),(0,0,300,40),1)
		self.image.blit(text,(30,5))
		

	

class Menu(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		pygame.sprite.Sprite.__init__(self)

		self.gameMap = gameMap
		self.gameMap.renders.append(self)
		def newGame(game):
			return "NewGame"
		items = [["New Game", newGame]]
		self.fontSize = 20
		
		self.draw()
		self.setup(items)
	def draw(self):
		(self.x,self.y) = 50,50
		self.rect = (self.x,self.y,masterSize[0]-100,masterSize[1]-100)
		self.image = pygame.Surface((self.rect[2],self.rect[3]))
		
		self.image.fill(pygame.Color("#333333"))
		
			
	def click(self,x,y):
		itemCount = 0
		for i in range(self.fontSize,self.rect[3],int(self.fontSize*1.2)):
			if y < i and len(self.items) > itemCount:
				return self.items[itemCount][1](self.gameMap)
			itemCount += 1
		return False
		
	def setup(self,itemList):
		height = 0
		for item in itemList:
			font = pygame.font.Font(fontName,self.fontSize)
			text = font.render(item[0],True,fontColor)
			self.image.blit(text,(0,height))
			height += self.fontSize*1.2
		self.items = itemList
		
class Dialog(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = 0,0
		self.rect = (self.x,self.y,masterSize[0]-100,masterSize[1]-100)
		self.image = pygame.Surface(self.rect[2],self.rect[3])
		
		okButton = pygame.Rect(100,100,200,50)
		pygame.draw.rect(self.image, bgColor,okButton)
		
	def setMessage(self,string):
		font = pygame.font.Font(fontName,self,20)
		text = font.render(string,True,fontColor)
		self.image.blit(text,(5,5))
		
	def click(self,x,y):
		if okButton.collidepoint(x,y):
			print "Collided with ok button"
		else:
			print "Didn't collide with ok button"
    
			