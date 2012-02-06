#
# HexSLayer
# copyright (C) Stephen Fluin 2011
#

import pygame, random
from pygame.locals import *
from hexmath import *
from hexconfig import *

			
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
    
			