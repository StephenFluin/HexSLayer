#!/usr/bin/python
#
# HexSLayer
# copyright (C) Stephen Fluin 2010
#

# Todo: Build a smarter AI that can build any level units and castles.
# Todo: Build a networked branch of the game so you can play online with friends.
# Todo: Build a "restart"/"new Game" button.
# Todo: Try to prevent villages from popping up on people
# Todo: Add trees (or other fun concept)
# Todo: Add interesting maps
# Todo: Add map generation

import pygame, random, time
from pygame.locals import *




if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: 
	print 'Warning, sound disabled'




from pawns import *
from hexmath import *
from hexconfig import *
from controls import *
from ai import *


selected = None

pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('HexSLayer')
pygame.display.set_icon(pygame.image.load("gameicon.png"))

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))



class Village(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPosition(gameMap,xloc,yloc)
		self.xloc = xloc
		self.yloc = yloc
		self.balance = 5
		self.spin = 0
		self.image = pygame.image.load("village.png")
		gameMap.renders.append(self)
		self.player = gameMap.getTile((xloc,yloc)).player


	

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
		#print "Mouse Hit:",x,"X",y," is it less than ",s/2
		#print "1,2,3,4:",(2*x + y),",",(2*x + (s-y)),",",(2*(s-x)+y),",",(2*(s-x)+(s-y))
		
		if ((2*x + y) <  s/2) or ((2*x + (s-y)) < s/2) or ((2*(s-x)+y) < s/2) or ((2*(s-x)+(s-y)) < s/2):
			# Failed hitdetection on hex
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
		self.width = 8#13
		self.height = 17#25
		self.x = 5
		self.y = 30
		
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
		
		
		
		self.infobar = VillageData(self,infobarLocation[0],infobarLocation[1])
		self.store = PurchaseUnits(self,storeLocation[0],storeLocation[1])
		self.score = ScoreCard(self,scoreLocation[0],scoreLocation[1])
		self.renders.append(self.infobar)
		self.renders.append(self.store)
		self.renders.append(self.score)
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
		
	def getTile(self,point):
		#print "Looking for",point
		if point[1] < 0 or point[1] >= self.height or point[0] < 0 or point[0] >= self.width:
			return None
		return self.tiles[point[1]][point[0]]
		
	def selectSet(self,point):
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
						self.renders.remove(dest.village)
						dest.village = None
		#compensate for "human" selections.
		if(self.selectedSet and self.selectedVillage):
			self.selectSet((self.selectedVillage.xloc,self.selectedVillage.yloc))
		
		#Check for endgame situation
		#@TODO! We currently assume the map has a [0][0] tile.
		if len(self.tiles[0][0].realm) == self.width * self.height:
			print "Player %s won the game!" % (self.tiles[0][0].player)
			
			self.gameOver = True
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
					
					# Kill all of the pawns in case of negative balance
					if tile.village.balance < 0:
						for space in realm:
							if space.pawn and not isinstance(space.pawn,Castle):
								space.pawn.kill(space)
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
		
		
		
		if self.gameOver:
			self.newGame = NewGame(20,355)
			self.renders.append(GameOver(self,20,325,self.tiles[0][0].player))
			self.renders.append(self.newGame)
		
		self.infobar.draw()
		self.store.draw()
		self.score.draw()
			
							
						


			
	

		
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
	
	background.blit(pygame.image.load("endturn.png"),(430,450))
	
	

	
	sparks = pygame.image.load("sparks.png")

	while True:
		clock.tick(60)
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
							if(x>430 and y > 450):
								gameMap.newTurn()
							if(x<430 and x > 280 and y > 450):
								print "got click at in the store%sx%s" %(x,y)
								#print "Spawning a new villager, and deducting from bank."
								if gameMap.selectedVillage.balance >= 10 and x < 355:
									mouseCarrying = Villager(gameMap,350,450)
									mouseCarrying.justPurchased = True
									gameMap.selectedVillage.balance -= 10
									mouseCarrying.startTile = gameMap.selectedSet[0]
									gameMap.renders.append(mouseCarrying)
								if gameMap.selectedVillage.balance >= 20 and x > 355:
									mouseCarrying = Castle(gameMap,350,450)
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
						#print "At mouse up, Mousecarrying is %s" % (mouseCarrying)
						validDrop = False
						for row in gameMap.tiles:
							for tile in row:
								if tile.rect.collidepoint(pygame.mouse.get_pos()) and tile.checkHexCollision(pygame.mouse.get_pos()):
								
									
									validDrop = True
									if(mouseCarrying.attack(tile.xloc,tile.yloc)):
										#print "Attack of this square was successful, dropping player there."
										gameMap.hexDropped(mouseCarrying,tile.xloc,tile.yloc)
										mouseCarrying.justPurchased = False
									elif not mouseCarrying.justPurchased:
										print "SetPos because we haven't just purchased"
										mouseCarrying.setPos( mouseCarrying.startTile.xloc,mouseCarrying.startTile.yloc)
									else:
										# We just purchased this pawn and couldn't place it, refund it!
										validDrop = False
										
											
												
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
						mouseCarrying.x -= 15
						mouseCarrying.y -= 15
		allsprites.update()

		
		#Draw Everything
		# A nice spinning graphic 
		screen.blit(background, (0, 0))
		for pawn in gameMap.renders:
			if isinstance(pawn,Pawn) and not pawn.getHasMoved() and pawn.player == 0:
				new = True
			elif isinstance(pawn,Village) and pawn.balance >= 10 and pawn.player == 0:
				new = True
			else:
				new = False
			i = random.randint(0,6)
			if new:
				pawn.spin += 2
				offset = abs(pawn.spin % 90 - 45)/7.5 - 6
				
				screen.blit(pygame.transform.rotate(sparks,pawn.spin),(pawn.x+offset,pawn.y+offset))
			screen.blit(pawn.image,(pawn.x,pawn.y))
		allsprites.draw(screen)
		pygame.display.flip()
		
		# Only add the following line if you want AI-Only mode.
		#if not gameMap.gameOver:
			#gameMap.newTurn()
		#time.sleep(1)




main()
