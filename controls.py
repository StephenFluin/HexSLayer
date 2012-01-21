#
# HexSLayer
# copyright (C) Stephen Fluin 2011
#
import pygame, random
from pygame.locals import *
from hexmath import *
from hexconfig import *


class VillageData(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = infobarLocation

		self.gameMap.renders.append(self)
		self.draw()
	def draw(self):
		self.image = pygame.Surface((500,30))
		self.image.fill(bgColor)
		if(self.gameMap.selectedSetIncome > 0):
			msg = "Region Income:"+str(self.gameMap.selectedSetIncome)+"  Upkeep:"+str(self.gameMap.selectedSetUpkeep)
			if(self.gameMap.selectedVillage.balance > 0):
				msg += "  Balance:%s" % (self.gameMap.selectedVillage.balance)
				
			font = pygame.font.Font(fontName, 22)
			text = font.render(msg,1,fontColor)
			self.image.blit(text,(0,0))
			
class PurchaseUnits(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		pygame.sprite.Sprite.__init__(self)
		self.gameMap = gameMap
		self.x,self.y = storeLocation
		
		self.gameMap.renders.append(self)
		self.draw()
	def draw(self):
		self.image = pygame.Surface((90,30))
		self.image.fill(bgColor)
		if self.gameMap.selectedVillage and self.gameMap.selectedVillage.player == 0:
			if self.gameMap.selectedVillage.balance >= 10:
				# TODO: Make sure this doesn't load on each call of draw
				self.image.blit(pygame.image.load("villager.png"),(0,0))
			if self.gameMap.selectedVillage.balance >= 20:
				self.image.blit(pygame.image.load("castle.png"),(55,0))
			
		
		#if(self.gameMap.balance() > 8):
				# TODO: Castles
				
class Messenger(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		pygame.sprite.Sprite.__init__(self)
		self.gameMap = gameMap
		self.x,self.y = messengerLocation
		
		self.messages = []
		#Currently in # of frames, silly
		self.defaultTime = 120
		
		self.gameMap.renders.append(self)
		self.draw()
		self.allMessagesCount = 1
		
		
	def draw(self):
		self.image = pygame.Surface((200,150))
		self.image.fill(bgColor)
		fsize = 10
		font = pygame.font.Font(fontName,fsize)
		
		msgCount = 0
		for i in self.messages:
			msgCount += 1
			if i[1] > self.defaultTime / 5.0:
				messageColor = fontColor
			elif i[1] > 0:
				color = int((i[1]) / (self.defaultTime /5.0)*255)
				messageColor = pygame.Color(color,color,color,1)
				
			
			if i[1] <= 0:
				self.messages.remove(i)
			else:
				text = font.render("%s. %s" % (i[2], i[0]),True,messageColor)
				self.image.blit(text,(0,msgCount *fsize * 1.2))
		
		
		
	def message(self,string):
		#Only show messages that happen after game start.
		if self.gameMap.turn >0:
			self.messages.append([string,self.defaultTime,self.allMessagesCount])
			self.allMessagesCount+=1
		
	def tick(self):
		for i in self.messages:
			i[1] -= 1
		self.draw()
		
		
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
		
class ScoreCard(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		pygame.sprite.Sprite.__init__(self)
		(self.x,self.y) = scoreLocation
		
		self.gameMap = gameMap
		
		self.gameMap.renders.append(self)
		self.draw()
	def draw(self):
		self.image = pygame.Surface((200,400))
		self.image.fill(bgColor)
		size = 18
		font = pygame.font.Font(fontName,size)
		tileCounts = self.gameMap.countTiles()
		for i in range(0,6):
			
			text = font.render("%s - %s" % (self.gameMap.players[i].getName(),tileCounts[i]),True,fontColor)
			self.image.blit(text,(30,10+(size+10)*i))
			pygame.draw.rect(self.image,pygame.Color(playerColors[i]),pygame.Rect(0,(size+10)*i+10,15,15))
		self.image.blit(font.render("Turn %s" % (self.gameMap.turn),True,fontColor),(30,(size+10)*6+10))

class MenuButton(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		pygame.sprite.Sprite.__init__(self)
		
		self.open = False
		self.gameMap = gameMap
		self.gameMap.renders.append(self)
		self.draw()
	def draw(self):

		(self.x,self.y) = menuButtonLocation
		self.image = pygame.Surface((32,30))
		
		self.image.fill(bgColor)
		pygame.draw.rect(self.image,fontColor,(14,6,4,4))
		pygame.draw.rect(self.image,fontColor,(14,14,4,4))
		pygame.draw.rect(self.image,fontColor,(14,22,4,4))
	

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
			
			
			
		
		
		
		
		
		
		