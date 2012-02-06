#
# HexSLayer
# copyright (C) Stephen Fluin 2012
#

# Interface Classfiles
# provides objects representing different UI elements that interact with the user
#

import pygame, random
from pygame.locals import *
from hexmath import *
from pawns import *

class UI(pygame.sprite.Sprite):
	def __init__(self,gameMap):
		pygame.sprite.Sprite.__init__(self)
		self.gameMap = gameMap
		self.x,self.y = 0,0
		
		
	# Call this as often as you like, it will make sure the UI matches world state. This also reblits its own components
	# Static methods should have no update functionality
	def update(self):
		pass
	
	
	# Each interface item should know how to handle clicks on it, starting from it's own xy
	# Return true if you capture the event 
	def click(self,x,y):
		return False

	def getRect(self):
		return Rect(self.x,self.y,self.image.get_width(),self.image.get_height())
	
class EndTurn(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)
		self.x,self.y = endTurnLocation
		
		self.image = pygame.image.load("endturn.png")
		
	def click(self,x,y):
		self.gameMap.newTurn()
		return True

class GameOver(UI):
	def __init__(self,gameMap,winner):
		UI.__init__(self,gameMap)
		self.x,self.y = 100,100
		self.winner = winner
		print "Winner of game is %s." % (self.winner)
		self.image = pygame.Surface((560,140))
		self.image.fill(bgColor)
		font = pygame.font.Font(fontName,28)
		text = font.render("Player %s (%s) won! Congratulations!" % (self.winner,self.gameMap.players[self.winner].getName()),True,fontColor)
		self.image.blit(text,(0,0))
		
		self.button = pygame.Surface((300,40))
		self.button.fill(bgColor)
		font = pygame.font.Font(fontName,20)
		text = font.render("Start Another Game",True,fontColor)
		self.rect = pygame.draw.rect(self.button,(0,0,0),(0,0,300,40),1)
		self.button.blit(text,(30,5))
		
		self.image.blit(self.button,(0,100))
	def click(self,x,y):
		if y>100:
			self.gameMap.startNewGame = True
		
class Menu(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)

		def newGame(game):
			game.renewGame()
		items = [["New Game", newGame]]
		(self.x,self.y) = 0,0
		self.fontSize = 20
		self.image = pygame.Surface(masterSize)
		
		self.interface = pygame.Surface((masterSize[0]-100,masterSize[1]-100))
		self.interface.fill(pygame.Color("#333333"))
		
		self.setup(items)
		self.update()
	def update(self):
		
		self.rect = (self.x+50,self.y+50,masterSize[0]-100,masterSize[1]-100)
		self.image.blit(self.interface,(50,50))
			
	def click(self,x,y):
		if(x < 50 or y < 50 or x > self.image.get_width()-50 or y > self.image.get_height() - 50) :
			self.close()
		else:
			itemCount = 0
			# Modify for interface click
			y -= 50
			for i in self.items:
				
				if y < (itemCount+1)*self.fontSize*1.2:
					
					i[1](self.gameMap)
					self.close()
					return True
					
				itemCount += 1
			return True
		
	def close(self):
		self.gameMap.interfaces.remove(self)
		return True
		
	def setup(self,itemList):
		height = 0
		for item in itemList:
			font = pygame.font.Font(fontName,self.fontSize)
			text = font.render(item[0],True,fontColor)
			self.interface.blit(text,(0,height))
			height += self.fontSize*1.2
		self.items = itemList
		
		
class Messenger(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)
		
		self.x,self.y = messengerLocation
		
		self.image = pygame.Surface((200,150))
		
		self.messages = []
		#Currently in # of frames, silly
		self.defaultTime = 120
	
		self.update()
		self.allMessagesCount = 1
		
		
	def update(self):
		self.tick()
		self.image.fill(bgColor)
		#self.image.fill(pygame.Color("#88DD88"))
		
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

			
class PurchaseUnits(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)
		self.x,self.y = (endTurnLocation[0]-120,masterSize[1]-50)
		
		self.update()
	def update(self):
		self.image = pygame.Surface((120,40))
		if self.gameMap.selectedVillage and self.gameMap.selectedVillage.player == 0:
			if self.gameMap.selectedVillage.balance >= 10:
				# TODO: Make sure this doesn't load on each call of draw
				self.image.blit(pygame.image.load("villager.png"),(0,10))
			if self.gameMap.selectedVillage.balance >= 20:
				self.image.blit(pygame.image.load("castle.png"),(65,10))
				
	def click(self,x,y):
		#We fuzz these locations because it's hard to tap on
		# Store Interaction
		g = self.gameMap
		
		
		if g.selectedVillage:
			# got click at in the store %sx%s" %(x,y)
			#print "Spawning a new villager, and deducting from bank."
			if g.selectedVillage.balance >= 10 and x < self.image.get_width()/2:
				g.mouseCarrying = Villager(g,self.x+x,self.y+y)
				g.mouseCarrying.x,g.mouseCarrying.y = self.x+x-tilesize/2,self.y+y-tilesize/2
									
				g.mouseCarrying.justPurchased = True
				g.selectedVillage.balance -= 10
				g.mouseCarrying.startTile = g.selectedSet[0]
				g.message("Villager Purchased",g.selectedVillage.player)
			if g.selectedVillage.balance >= 20 and x > self.image.get_width()/2:
				g.mouseCarrying = Castle(g,self.x+x,self.y+y)
				g.mouseCarrying.x,g.mouseCarrying.y = self.x+x-tilesize/2,self.y+y-tilesize/2
				g.mouseCarrying.justPurchased = True
				g.selectedVillage.balance -= 20
				g.mouseCarrying.startTile = g.selectedSet[0]
				g.message("Castle Purchased",g.selectedVillage.player)
				
class ScoreCard(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)
		self.x,self.y = scoreLocation
		
		
		self.update()
	def update(self):
		size = 18
		self.image = pygame.Surface((200,int(10+(size+10)*(len(self.gameMap.players)+1))))
		
		
		font = pygame.font.Font(fontName,size)
		tileCounts = self.gameMap.countTiles()
		for i in range(0,6):
			
			text = font.render("%s - %s" % (self.gameMap.players[i].getName(),tileCounts[i]),True,fontColor)
			self.image.blit(text,(30,10+(size+10)*i))
			pygame.draw.rect(self.image,pygame.Color(playerColors[i]),pygame.Rect(0,(size+10)*i+10,15,15))
		self.image.blit(font.render("Turn %s" % (self.gameMap.turn),True,fontColor),(30,(size+10)*6+10))
		
class TopBar(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)
		self.x,self.y = (0,0)
		
		self.open = False

		
		self.image = pygame.Surface((masterSize[0],32))
		
		self.image.fill(bgColor)
		menuButtonX = masterSize[0]-32+14
		pygame.draw.rect(self.image,fontColor,(menuButtonX ,6,4,4))
		pygame.draw.rect(self.image,fontColor,(menuButtonX ,14,4,4))
		pygame.draw.rect(self.image,fontColor,(menuButtonX ,22,4,4))
		
		font = pygame.font.Font(fontName, 24)
		text = font.render("HexSLayer",1,fontColor)
		self.image.blit(text,(15,0))
		pygame.draw.rect(self.image,pygame.Color("#33b5e5"),(0,30,self.image.get_width(),2))
		
			
	def click(self,x,y):
		if x > (self.image.get_width() - 32):
			self.gameMap.interfaces.append(Menu(self.gameMap))
		#Allow menu click
		#
		#		menubutton.open = Menu(gameMap) 
		#		gameMap.renders.append(menubutton.open)
		# Menu already open
		#				else:
		#					print "menu open"
		#					if not pygame.Rect(menubutton.open.x,menubutton.open.y,menubutton.open.image.get_width(),menubutton.open.image.get_height()).collidepoint(x,y):
		#						print "Menu closing, rect was %sx%s %s,%s compared to %sx%s" % (menubutton.open.x,menubutton.open.y,menubutton.image.get_width(),menubutton.image.get_height(),x,y)
		#						
		#						menubutton.open = False
		#					else:
		#						result = menubutton.open.click(x-menubutton.open.x,y-menubutton.open.y)
		#						if result == "NewGame":
		#							gameMap = Map(gameMap.background)


class VillageData(UI):
	def __init__(self,gameMap):
		UI.__init__(self,gameMap)
		
		self.x,self.y = (10,masterSize[1]-40)

		self.update()
	def update(self):
		self.image = pygame.Surface((500,30))
		self.image.fill(bgColor)
		if(self.gameMap.selectedSetIncome > 0):
			msg = "Region Income:"+str(self.gameMap.selectedSetIncome)+"  Upkeep:"+str(self.gameMap.selectedSetUpkeep)
			if(self.gameMap.selectedVillage.balance > 0):
				msg += "  Balance:%s" % (self.gameMap.selectedVillage.balance)
				
			font = pygame.font.Font(fontName, 22)
			text = font.render(msg,1,fontColor)
			self.image.blit(text,(0,0))		
		

