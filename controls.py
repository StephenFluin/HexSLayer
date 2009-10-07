import pygame, random
from pygame.locals import *
from hexmath import *

class VillageData(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = x,y

		self.draw()
	def draw(self):
		self.image = pygame.Surface((250,30))
		self.image.fill(pygame.Color("#FFFFFF"))
		if(self.gameMap.income() > 0):
			msg = "Village Income:"+str(self.gameMap.income())
			if(self.gameMap.balance() > 0):
				msg += "  Balance:"+str(self.gameMap.balance())
				
			font = pygame.font.Font(None, 22)
			text = font.render(msg,1,(10,10,10))
			self.image.blit(text,(0,0))
			
class PurchaseUnits(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.gameMap = gameMap
		self.x,self.y = x,y
		self.income = 0
		self.draw()
	def draw(self):
		self.image = pygame.Surface((75,30))
		self.image.fill(pygame.Color("#FFFFFF"))
		if(self.gameMap.balance() >= 5):
			# TODO: Make sure this doesn't load on each call of draw
			self.image.blit(pygame.image.load("villager.png"),(0,0))
			
		
		#if(self.gameMap.balance() > 8):
				# TODO: Castles
		
		
		