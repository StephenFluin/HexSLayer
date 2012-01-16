#!/usr/bin/python
#
# HexSLayer
# copyright (C) Stephen Fluin 2012
#

# Todo: Build a smarter AI that can build any level units and castles.
# Todo: Build a networked branch of the game so you can play online with friends.
# Todo: Try to prevent villages from popping up on people
# Todo: Add trees (or other fun concept)
# Todo: Add interesting maps
# Todo: Add map generation

import pygame, random, time, os, math

from pygame.locals import *

try:
	import android
except ImportError:
	android = None



if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: 
	print 'Warning, sound disabled'


# load HexSLayer modules
from pawns import *
from hexmath import *
from hexconfig import *
from controls import *
from ai import *
from playersettings import *
from analytics import *
from map import *

selected = None
background = None
gameMap = None
mouseCarrying = None
screen = None
clock = None
version = "1.0.14pre"




def main():
	global screen, background, clock, mouseCarrying,version
	settings = PlayerSettings()
	pygame.init()
	screen = pygame.display.set_mode(masterSize)
	pygame.display.set_caption('HexSLayer')
	pygame.display.set_icon(pygame.image.load("gameicon.png"))

	# Map the back button to the escape key.
	if android:
		android.init()
		android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
	
	trackEvent("startup",{"version":version,"android":'ANDROID_ASSETS' in os.environ,"screenSize":masterSize})
	
	
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(bgColor)
	
	gData = settings.getGameData()
	if gData:
		gameMap = MapDeserialize(background,settings.getGameData())
	else:
		gameMap = Map(background)
	
	
	#gameMap.newTurn()
	
	if pygame.font:
		font = pygame.font.Font(fontName, 24)
		text = font.render("HexSLayer",1,fontColor)
		background.blit(text,(15,0))
		pygame.draw.rect(background,pygame.Color("#33b5e5"),(0,30,background.get_width(),2))
	else:
		print "Fonts aren't supported by this system."
		
	clock = pygame.time.Clock()
	allsprites = pygame.sprite.RenderPlain(())
	
	background.blit(pygame.image.load("endturn.png"),endTurnLocation)
	
	sparks = pygame.image.load("sparks.png")
	
	while True:
		clock.tick(15)
		#Handle Input Events
		if True:
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == KEYDOWN and event.key == K_RETURN:
					gameMap.newTurn()
				elif event.type == KEYDOWN and event.key == K_BACKSPACE:
					gameMap.gameOver = True
					gameMap.reRender()
				elif event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
					
					if not gameMap.gameOver:
						# Picking something up
						if not mouseCarrying:
							#Select a region
							for row in gameMap.tiles:
								for tile in row:
									if tile.rect.collidepoint(pygame.mouse.get_pos()):
										
										if tile.checkHexCollision(pygame.mouse.get_pos()):
											
											mouseCarrying = gameMap.hexClicked(tile.xloc,tile.yloc)
											if mouseCarrying:
												mouseCarrying.startTile = tile
												#print "I have set the startTile of the carry."
											break
											
							x,y =pygame.mouse.get_pos()
							# End Turn Button
							if(x>endTurnLocation[0] and y > endTurnLocation[1]):
								gameMap.newTurn()
								
							#We fuzz these locations because it's hard to tap on
							# Store Interaction
							storeX = gameMap.store.x-10
							storeY = gameMap.store.y-20
							storeRight = gameMap.store.image.get_width() + storeX + 20
							if(x<storeRight and x > storeX and y > storeY):
								# got click at in the store %sx%s" %(x,y)
								#print "Spawning a new villager, and deducting from bank."
								if gameMap.selectedVillage.balance >= 10 and x < (storeRight+storeX)/2:
									mouseCarrying = Villager(gameMap,storeX,storeY)
									mouseCarrying.justPurchased = True
									gameMap.selectedVillage.balance -= 10
									mouseCarrying.startTile = gameMap.selectedSet[0]
									gameMap.message("Villager Purchased",gameMap.selectedVillage.player)
									gameMap.renders.append(mouseCarrying)
								if gameMap.selectedVillage.balance >= 20 and x > (storeRight+storeX)/2:
									mouseCarrying = Castle(gameMap,storeX,storeY)
									mouseCarrying.justPurchased = True
									gameMap.selectedVillage.balance -= 20
									mouseCarrying.startTile = gameMap.selectedSet[0]
									gameMap.message("Castle Purchased",gameMap.selectedVillage.player)
									gameMap.renders.append(mouseCarrying)
						else:
							print "Why are we mousing down if we are carrying %s??!?!?!" % (mouseCarrying)
					else:
						x,y = pygame.mouse.get_pos()
						box = (gameMap.newGame.x,gameMap.newGame.y,gameMap.newGame.image.get_width(),gameMap.newGame.image.get_height())
						
						if pygame.Rect(box).collidepoint((x,y)):
							print "New Game Time"
							gameMap = Map(background)
						else:
							print "Not a new game. because %sx%s didn't match %s" % (x,y,gameMap.newGame.image.get_rect())
						
					
				elif event.type == MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0]:
					if mouseCarrying:
						x,y = event.pos
						validDrop = False
						
						for row in gameMap.tiles:
							for tile in row:
								if tile.rect.collidepoint((x,y)) and tile.checkHexCollision((x,y)):
									validDrop = True
									if(mouseCarrying.attack(tile.xloc,tile.yloc)):
										#print "Attack of this square was successful, dropping player there."
										gameMap.hexDropped(mouseCarrying,tile.xloc,tile.yloc)
										mouseCarrying.justPurchased = False
										
									elif not mouseCarrying.justPurchased:
										#print "SetPos because we haven't just purchased"
										mouseCarrying.setPos( mouseCarrying.startTile.xloc,mouseCarrying.startTile.yloc)
									else:
										# We just purchased this pawn and couldn't place it, refund it!
										#print "Couldn't drop purchased pawn."
										validDrop = False
									
									if not mouseCarrying.moved:
										mouseCarrying.makeIndicator()
									break
									
									
												
						# @TODO! What else do we need to do to clean this up?
						if not validDrop:
							if mouseCarrying.startTile:
								mouseCarrying.startTile.pawn = None
							gameMap.renders.remove(mouseCarrying)
							if isinstance(mouseCarrying,Castle):
								value = 20
							else:
								value = 10
							gameMap.selectedVillage.balance += value
						mouseCarrying = None	
					gameMap.reRender()
				elif event.type == MOUSEMOTION:
					if mouseCarrying != None:
						mouseCarrying.x,mouseCarrying.y = pygame.mouse.get_pos()
						mouseCarrying.x -= tilesize/2
						mouseCarrying.y -= tilesize/2
		allsprites.update()

		#Update time on messenger
		gameMap.messenger.tick()
		
		
		#Draw Everything
		screen.blit(background, (0, 0))
		for pawn in gameMap.renders:
			if isinstance(pawn,Pawn) and not pawn.getHasMoved() and pawn.player == 0:
				availableMove = True
				
			elif isinstance(pawn,Village) and pawn.balance >= 10 and pawn.player == 0:
				availableMove = True
			else:
				availableMove = False
			
			#Section handles move indicators, @TODO move to add and remove indicators at action time, not render time
			if availableMove:
				if not pawn.indicator:
					pawn.makeIndicator()
				pawn.indicator.render(screen)
				pawn.indicator.spin()
				
			elif isinstance(pawn,Pawn) and pawn.indicator:
				pawn.indicator = None

			
			#Show carried item at 2x size, better for touchscreens
			if pawn == mouseCarrying:
				screen.blit(pygame.transform.scale2x(pawn.image),(pawn.x,pawn.y))
			else:
				screen.blit(pawn.image,(pawn.x,pawn.y))
		allsprites.draw(screen)
		pygame.display.flip()
		
		# Only add the following line if you want AI-Only mode.
		#if not gameMap.gameOver:
			#gameMap.newTurn()
		#time.sleep(1)
	
		


if __name__ == "__main__":
    main()
