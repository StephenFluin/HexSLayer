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


selected = None
background = None
gameMap = None
mouseCarrying = None
screen = None
clock = None
version = "1.0.12pre"




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
	
	gameMap = Map()
	
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
									gameMap.message("Villager Purchased")
									gameMap.renders.append(mouseCarrying)
								if gameMap.selectedVillage.balance >= 20 and x > (storeRight+storeX)/2:
									mouseCarrying = Castle(gameMap,storeX,storeY)
									mouseCarrying.justPurchased = True
									gameMap.selectedVillage.balance -= 20
									mouseCarrying.startTile = gameMap.selectedSet[0]
									gameMap.renders.append(mouseCarrying)
						else:
							print "Why are we mousing down if we are carrying %s??!?!?!" % (mouseCarrying)
					else:
						x,y = pygame.mouse.get_pos()
						box = (gameMap.newGame.x,gameMap.newGame.y,gameMap.newGame.image.get_width(),gameMap.newGame.image.get_height())
						
						if pygame.Rect(box).collidepoint((x,y)):
							print "New Game Time"
							gameMap = Map()
						else:
							print "Not a new game. because %sx%s didn't match %s" % (x,y,gameMap.newGame.image.get_rect())
						
					
				elif event.type == MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0]:
					if mouseCarrying:
						print "At mouse up, Mousecarrying is %s at %sx%s" % (mouseCarrying,x,y)
						validDrop = False
						x = mouseCarrying.x+tilesize/2
						y = mouseCarrying.y+tilesize/2
						
						for row in gameMap.tiles:
							for tile in row:
								if tile.rect.collidepoint((x,y)) and tile.checkHexCollision((x,y)):
									print "Passed collision test"
									validDrop = True
									if(mouseCarrying.attack(tile.xloc,tile.yloc)):
										print "Attack of this square was successful, dropping player there."
										gameMap.hexDropped(mouseCarrying,tile.xloc,tile.yloc)
										mouseCarrying.justPurchased = False
									elif not mouseCarrying.justPurchased:
										print "SetPos because we haven't just purchased"
										mouseCarrying.setPos( mouseCarrying.startTile.xloc,mouseCarrying.startTile.yloc)
									else:
										# We just purchased this pawn and couldn't place it, refund it!
										print "Couldn't drop purchased pawn."
										validDrop = False
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
					pawn.indicator = AvailableMove(pawn.x,pawn.y)
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
	

	while True:

		ev = pygame.event.wait()

		# Android-specific:
		if android:
			if android.check_pause():
				android.wait_for_resume()

		# Draw the screen based on the timer.
		if ev.type == TIMEREVENT:
			screen.fill(color)
			pygame.display.flip()
			if color == GREEN:
				android.vibrate(.1)

		# When the touchscreen is pressed, change the color to green.
		elif ev.type == pygame.MOUSEBUTTONDOWN:
			color = GREEN
			
			

		# When it's released, change the color to RED.
		elif ev.type == pygame.MOUSEBUTTONUP:
			color = RED

		# When the user hits back, ESCAPE is sent. Handle it and end
		# the game.
		elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
			break
		
	
	






	

class Tile(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.Surface([tilesize, tilesize])
		self.x,self.y = convertGridPosition(gameMap,xloc,yloc)
		self.xloc = xloc
		self.yloc = yloc
		
		self.selected = False
		self.pawn = None
		self.village = None
		self.gameMap = gameMap
		self.grave = None
		self.realm = None
		
		self.setPlayer(random.randint(0,5))
		
		self.rect = self.draw()
		

	# Changes the owner of a tile, redraws, and fixes the realm.
	def setPlayer(self,player):
		self.player = player
		self.color = pygame.Color(playerColors[self.player])
		self.draw()
		
		
	def draw(self):
		rect = pygame.draw.polygon(background,self.color,self.getHex(),0)
		pygame.draw.polygon(background,pygame.Color("#000000"),self.getHex(),1)
		
		return rect
		
	def redRing(self):
		pygame.draw.polygon(background,pygame.Color("#FF0000"),self.getHex(),3)
	
	def blueRing(self):
		pygame.draw.polygon(background,pygame.Color("#0000FF"),self.getHex(),3)
	
	def getHex(self):
		return getHexAt(self.x,self.y)
		
	def getPoint(self):
		return (self.xloc,self.yloc)
		
	def checkHexCollision(self,point):
		s = tilesize
		l = .25
		x = point[0] - self.x
		y = point[1] - self.y
		print "Mouse Hit:",x,"X",y," is it less than ",s/2
		print "1,2,3,4:",(2*x + y),",",(2*x + (s-y)),",",(2*(s-x)+y),",",(2*(s-x)+(s-y))
		
		if ((2*x + y) <  s/2) or ((2*x + (s-y)) < s/2) or ((2*(s-x)+y) < s/2) or ((2*(s-x)+(s-y)) < s/2):
			# Failed hitdetection on hex
			print "Failed hitdetection on hex %sx%s (tilesize %s) compared to %sx%s." % (x,y,s,point[0],point[1])
			return 0
		else:
			return 1
	def getAdjacent(self,direction):
		return getAdjacent(self.xloc,self.yloc,direction)
	def getAdjacentTile(self,direction):
		return self.gameMap.getTile(self.getAdjacent(direction))
	def isAdjacent(self,point):
		#print "Checking for adjacency."
		for dir in range(6):
			target = self.getAdjacent(dir)
			if(target == point):
				#print "Target was adjacent to this square"
				return True
		return False
		
	def getProtection(self):
		return self.getProtectionPair()[0]
		
	def getProtectionPair(self):
	
		level = 0
		protectors = []
		
		# Diagnose powerful allies
		if self.pawn:
			level = max(level, self.pawn.level)
			protectors.append((self.pawn.level,self.pawn))
		for i in range(0,6):
			if self.getAdjacentTile(i) and self.getAdjacentTile(i).player == self.player and  self.getAdjacentTile(i).pawn:
				level = max(level, self.getAdjacentTile(i).pawn.level)
				protectors.append((self.getAdjacentTile(i).pawn.level,self.getAdjacentTile(i).pawn))
			elif self.getAdjacentTile(i) and self.getAdjacentTile(i).pawn and  self.getAdjacentTile(i).pawn.level >1:
				pass
			else:
				if self.getAdjacentTile(i):
					if self.getAdjacentTile(i).pawn:
						pass
						
		
		# Diagnose villages near.
		if self.village:
			level = max(level,1)
			protectors.append(self.village)
		for i in range(0,6):
			if self.getAdjacentTile(i) and self.getAdjacentTile(i).player == self.player and self.getAdjacentTile(i).village:
				level = max(level,1)
				protectors.append(self.getAdjacentTile(i).village)
		return (level,protectors)
		
			
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
		#tile metrics
		#@TODO WHat the? I only count 9x15?????
		self.width = 8#13
		self.height = 17#25
		
		self.x = 10
		self.y = 35
		
		self.turn = 0
		self.gameOver = False
		self.selectedSetIncome = 0
		self.selectedSetUpkeep = 0
		
		self.tiles = []
		self.alltiles = []
		self.renders = []
		self.selectedSet = []
		self.selectedVillage = None
		self.infoBar = None
		self.players = []
		self.messenger = None
		
		for y in range(self.height):
			
			row = [None]*self.width
			for x in range(self.width):
				row[x] = Tile(self,x,y)
				self.alltiles.append(row[x])
			self.tiles.append(row)
			
		# Add Human to the game.
		self.players.append(HumanIntelligence())
				
		# Add some AIs to the game.
		for i in range(0,3):
			self.players.append(NaiveAI())
		self.players.append(AIPlus())
		self.players.append(FullAI())
		
		
		
		self.infobar = VillageData(self)
		self.store = PurchaseUnits(self)
		self.messenger = Messenger(self)
		self.score = ScoreCard(self)
		
		self.cleanUpGame()
		
		self.newTurn()

			
	def hexClicked(self,x,y):
		retval = None
		#print "Clicked tile: %sx%s" % (self.tiles[y][x].xloc,self.tiles[y][x].yloc)
		clickedTile = self.tiles[y][x]
		if(clickedTile.pawn != None and clickedTile.pawn.getHasMoved() == False and clickedTile.player == 0):
			retval = clickedTile.pawn
			
		
		
		if not retval:
			for tile in self.selectedSet:
				tile.deselect()
			self.selectSet((x,y))
					
					
		return retval
		
	def hexDropped(self,carry,x,y):
		clickedTile = self.tiles[y][x]
		carry.setPos(x,y)
		#print "Set the position of the carry to ",x,"X",y
		
	# Takes in a tile coordinate, returns a tile
	def getTile(self,point):
		#@TODO Performance problem is here, this is called like a million times for the smallest changes
		# Kill the cheerleader, kill the world.
		#print "Looking for",point
		if not point:
			print "CRITICAL ERROR, getTile called without a point in space. point was %s" % (point) 
		if point[1] < 0 or point[1] >= self.height or point[0] < 0 or point[0] >= self.width:
			#print "Failed to get tile because point was out of bounds. 0-%s, 0-%s" % (self.width,self.height), point
			#@TODO THis is weird, why do we have code repeatedly failing all of the time. perhaps this is okay?
			return None
		return self.tiles[point[1]][point[0]]
		
	# Takes in a tile x y tile location, selects the set in the UI and stores it.
	def selectSet(self,point):
		if not point:
			print "CRITICAL ERROR, selectSet called without a point in space. point was %s" % (point) 
		self.selectedSet = self.getTileSet(point)
		
		income = 0
		balance = 0
		upkeep = 0
		for tile in self.selectedSet:
			tile.select()
			income += 1
			if tile.pawn:
				upkeep += tile.pawn.upkeep
			if(tile.village):
				balance = tile.village.balance
				self.selectedVillage = tile.village
		if(income == 1):
			income = 0
		self.selectedSetUpkeep = upkeep
		self.changeIncome(income)

			
		
			
	
	#We are going to do a breadth first search to find all connected tiles of same color
	def getTileSet(self,point):
		if not point:
			print "CRITICAL ERROR, getTileSet called without a point in space. point was %s" % (point) 
		
		tile = self.getTile(point)
		
		if not tile:
			print "Failed to find a tile for point %s." % (point)
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
		
	# Return a list of tiles counts for all players.
	def countTiles(self):
		counts = [0,0,0,0,0,0]
		for row in self.tiles:
			for tile in row:
				counts[tile.player] += 1
		#print "After counting all of the tiles, we have: %s." % (counts)
		return counts
				
	
	# Adds, splits villages
	# @TODO, clean up this method, it is super redudant (checks each set once for each tile in the set)
	def cleanUpGame(self):
		#clean all realms
		for row in self.tiles:
			for tile in row:
				tile.realm = None
		
		
		for row in self.tiles:
			for tile in row:
				# Only clean and update if realm hasn't already been handled
				if not tile.realm:
					tile.realm = self.getTileSet(tile.getPoint())
					villagecount = 0
					villages = []
					# Count villages
					for spot in tile.realm:
						spot.realm = tile.realm
						if(spot.village):
							villagecount += 1
							villages.append(spot)
							#print "found village at ",spot.getPoint()
							
					#print "Found ",villagecount,"villages in this realm of ",len(realm),", ",len(villages)," of which were villages"
					#Add a village if none found, this means the city has been split, reset the realm on tiles in the new realm.
					if villagecount == 0 and len(tile.realm) > 1:
						dest =tile.realm[random.randrange(len(tile.realm))]
						dest.village = Village(dest.gameMap,dest.xloc,dest.yloc)
					
					# Too many villages, add the gold from the removed village to a remaining village.
					while len(villages) > 1 or ( len(villages) > 0 and len(tile.realm) < 2):
						dest = villages.pop(random.randrange(len(villages)))
						if len(villages) >= 1:
							villages[0].village.balance += dest.village.balance
						dest.village.kill(dest)
		
		#compensate for "human" selections in UI
		if(self.selectedSet and self.selectedVillage):
			
			
			villageTileLocation = (self.selectedVillage.xloc,self.selectedVillage.yloc)
			self.selectSet(villageTileLocation)
		
		#Check for endgame / gameover situation by counting players with villages
		foundOwners = {}
		for row in self.tiles:
			for tile in row:
				if tile.village:
					foundOwners[tile.player] = True
		# print "Found %s as remaining village owners." % (foundOwners)
		if len(foundOwners) == 1:
			print "Player %s won the game!" % (foundOwners.keys()[0])
			self.gameOver = True
			self.winner = foundOwners.keys()[0]
			self.reRender()
			
		
					

	def changeIncome(self,income):
		self.selectedSetIncome = income
		self.infobar.draw()
		self.store.draw()
		
	def newTurn(self):
		#End turn case
		print "End of turn %s" % (self.turn)
		
		#Remove graven images
		for row in self.tiles:
			for tile in row:
				if tile.grave:
					self.renders.remove(tile.grave)
					tile.grave = None
					#print "Removed a grave."
		
		#For each set, add balance to village, and remove upkeeps
		for row in self.tiles:
			for tile in row:
				if tile.village:
					realm = tile.realm
					#print "Village balance was %s " %(tile.village.balance),
					tile.village.balance += len(realm)
					for space in realm:
						if space.pawn:
							tile.village.balance -= space.pawn.upkeep
					if tile.selected:
						self.selectedSetBalance = tile.village.balance
					#print "Village balance became %s" % (tile.village.balance)
					
					# Kill any pawns without a village
					if tile.pawn and len(tile.realm) == 1:
						tile.pawn.kill(tile)
					
					# Starve all of the pawns in case of negative balance
					if tile.village.balance < 0:
						for space in realm:
							if space.pawn and not isinstance(space.pawn,Castle):
								space.pawn.starve(space)
								tile.village.balance = 0
					
				if tile.pawn:
					
					tile.pawn.moved = False
					if(len(tile.realm) == 1):
						tile.pawn.kill(tile)
		self.turn += 1
		pygame.display.set_caption("HexSLayer - Turn %s" % (str(self.turn)))
		self.runAI()
		self.reRender()
		

		
		
		
	# Process AI calls for each player. 
	# TODO Make this use a model of handing an AI class a gamemap and have the AI take a single turn.
	def runAI(self):
		#The game currently has no protections from cheating, but do we need them if all of the AI's have moved every turn?
		#yes, we will need protections for the networked versions, also, if the AI wants to save money, we need to stop
		#others from spending their gold.
		for player in range(0,6):
			#print "Running ai for player %s" % (player)
			self.players[player].takeTurn(self,player)
			
	def reRender(self):
			#@TODO, decide if I want to keep this refreshing of renders, or manage it like malloc
		self.renders = []
		for row in self.tiles:
			for tile in row:
			
				if tile.grave:
					self.renders.append(tile.grave)
				if tile.village:
					self.renders.append(tile.village)
				if tile.pawn:
					self.renders.append(tile.pawn)
					
		self.renders.append(self.infobar)
		self.renders.append(self.store)
		self.renders.append(self.score)
		self.renders.append(self.messenger)
		
		
		
		if self.gameOver:
			self.newGame = NewGame(20,355)
			self.renders.append(GameOver(self,20,325,self.winner))
			self.renders.append(self.newGame)
		
		self.infobar.draw()
		self.store.draw()
		self.score.draw()
		self.messenger.draw()
			
							
	def message(self,msg):
		self.messenger.message(msg)


			
	

		




if __name__ == "__main__":
    main()
