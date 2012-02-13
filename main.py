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

import pygame, random, time, os, math, sys

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
from interface import *
from ai import *
from playersettings import *
from analytics import *
from map import *

selected = None
background = None
gameMap = None
screen = None
version = open('version.txt','r').read()

def main():
	global screen, background, mouseCarrying,version
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
		ps = PlayerSettings()
		games = ps.getPlayerStat("games")
		games += 1
		ps.setPlayerStat("games",games)
		

	
	
	
	gameMap.setInterfaces(setupUI(gameMap))
	
	clock = pygame.time.Clock()
	allsprites = pygame.sprite.RenderPlain(())
	
	
		
	while True:
		clock.tick(15)
		
		#If the game is over, make a new map
		if gameMap.startNewGame:
			gameMap = Map(background)
			gameMap.setInterfaces(setupUI(gameMap))
			gameMap.save()
			ps = PlayerSettings()
			games = ps.getPlayerStat("games")
			games += 1
			ps.setPlayerStat("games",games)
			
		#Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				interface = gameMap.interfaces
				captured = False
				for i in range(len(interface)-1,-1,-1):
					if interface[i].back():
						captured = True
						break
				if not captured:
					print "Wasn't captured, quitting."
					sys.exit()
			elif event.type == KEYDOWN and event.key == K_RETURN:
				gameMap.newTurn()
			elif event.type == KEYDOWN and event.key == K_BACKSPACE:
				gameMap.gameOver = True
				gameMap.reRender()
			elif event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
				x,y = pygame.mouse.get_pos()
				interface = gameMap.interfaces
				# Pass a click through all interfaces, go through opposite render order to start on top
				for i in range(len(interface)-1,-1,-1):
					if interface[i].getRect().collidepoint(x,y):
						captured = interface[i].click(x-interface[i].x,y-interface[i].y)
						if captured:
							break
											
				#@todo: Perhaps we should move this elsewhere
				if not gameMap.mouseCarrying:
					#Select a region
					for row in gameMap.tiles:
						for tile in row:
							if tile.rect.collidepoint(pygame.mouse.get_pos()):
								
								if tile.checkHexCollision(pygame.mouse.get_pos()):
									
									gameMap.mouseCarrying = gameMap.hexClicked(tile.xloc,tile.yloc)
									if gameMap.mouseCarrying:
										gameMap.mouseCarrying.startTile = tile
										#print "I have set the startTile of the carry."
									break
				
			elif event.type == MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0]:
				if gameMap.mouseCarrying:
					x,y = event.pos
					validDrop = False
					
					for row in gameMap.tiles:
						for tile in row:
							if tile.rect.collidepoint((x,y)) and tile.checkHexCollision((x,y)):
								validDrop = True
								if(gameMap.mouseCarrying.attack(tile.xloc,tile.yloc)):
									#print "Attack of this square was successful, dropping player there."
									gameMap.hexDropped(gameMap.mouseCarrying,tile.xloc,tile.yloc)
									gameMap.mouseCarrying.justPurchased = False
									
								elif not gameMap.mouseCarrying.justPurchased:
									#print "SetPos because we haven't just purchased"
									gameMap.mouseCarrying.setPos( gameMap.mouseCarrying.startTile.xloc,gameMap.mouseCarrying.startTile.yloc)
								else:
									# We just purchased this pawn and couldn't place it, refund it!
									#print "Couldn't drop purchased pawn."
									validDrop = False
								
								if not gameMap.mouseCarrying.moved:
									gameMap.mouseCarrying.makeIndicator()
								break
								
								
											
					# @TODO! What else do we need to do to clean this up?
					if not validDrop:
						if gameMap.mouseCarrying.startTile:
							gameMap.mouseCarrying.startTile.pawn = None
						
						if isinstance(gameMap.mouseCarrying,Castle):
							value = 20
						else:
							value = 10
						for t in gameMap.mouseCarrying.startTile.realm:
							if t.village:
								gameMap.message("Unit sold")
								t.village.balance += value
					gameMap.mouseCarrying = None	
				gameMap.reRender()
			elif event.type == MOUSEMOTION:
				if gameMap.mouseCarrying != None:
					gameMap.mouseCarrying.x,gameMap.mouseCarrying.y = pygame.mouse.get_pos()
					gameMap.mouseCarrying.x -= tilesize/2
					gameMap.mouseCarrying.y -= tilesize/2
		allsprites.update()

		
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

			if not gameMap.mouseCarrying == pawn:
				screen.blit(pawn.image,(pawn.x,pawn.y))
		
		#Draw interface first so that mousecarryings can go on top
		for face in gameMap.interfaces:
			face.update()
			screen.blit(face.image,(face.x,face.y))
			
		#Show carried item at 2x size, better for touchscreens
		if gameMap.mouseCarrying:
				screen.blit(pygame.transform.scale2x(gameMap.mouseCarrying.image),(gameMap.mouseCarrying.x,gameMap.mouseCarrying.y))
		
			
		allsprites.draw(screen)
		pygame.display.flip()
		
		# Only add the following line if you want AI-Only mode.
		#if not gameMap.gameOver:
			#gameMap.newTurn()
		#time.sleep(1)


def setupUI(gameMap):
	interface = []
	interface.append(VillageData(gameMap))
	interface.append(PurchaseUnits(gameMap))
	gameMap.messenger = Messenger(gameMap)
	interface.append(gameMap.messenger)
	interface.append(ScoreCard(gameMap))
	interface.append(TopBar(gameMap))
	interface.append(EndTurn(gameMap))
	if PlayerSettings().getShowTutorialFlag():
		print "Appending tutorial because flag was true (%s) " % (PlayerSettings().getShowTutorialFlag())
		interface.append(Tutorial(gameMap))
	return interface

if __name__ == "__main__":
	main()
