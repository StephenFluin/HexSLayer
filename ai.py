#
# HexSLayer
# copyright (C) Stephen Fluin 2010
#

# AIs placed in a modular framework. They don't currently leverage state, but they could.


from pawns import *



class AI():
	def takeTurn(self, gameMap,player):
		return

class HumanIntelligence(AI):
	def getName(self):
		return "You"
	def takeTurn(self,gameMap,player):
		return
class NaiveAI(AI):
	def getName(self):
		return "Naive AI"
	def takeTurn(self,gameMap,player):
		# buy units where appropriate
		for row in gameMap.tiles:
			for tile in row:
				if tile.player == player:
					realm = tile.realm
					# TODO: This is really really innefficient (n^2 rather than n)
					for t in realm:
						if t.village and t.village.balance >= 30 and not tile.pawn and not tile.grave and not tile.village:
							
							tile.pawn = Villager(gameMap,tile.xloc,tile.yloc)
							t.village.balance -= 10
							gameMap.renders.append(tile.pawn)
							#print "Bought a simple pawn and placed at %sx%s for the tile at %sx%s" % (tile.x,tile.y,tile.xloc,tile.yloc)
							

							
						else:
							if t.village:
								#print "didn't buy anything, because %s is the balance" % (t.village.balance)
								nothing = None
		# move units where appropriate
		for row in gameMap.tiles:
			for tile in row:
				
				if tile.player == player and tile.pawn and not tile.pawn.moved:
					set = gameMap.getTileSet(tile.getPoint())
					for candidate in set:
						direction = random.randint(0,5)
						for i in range(0,6):
							dest = candidate.getAdjacentTile((direction + i) % 6)
							if not(not dest or dest.player == tile.player or dest.xloc < 0 or dest.yloc < 0 or dest.xloc >= gameMap.width or dest.yloc >= gameMap.height):
								break
							if i == 5:
								dest = None
							
						
					if dest:
						tile.pawn.startTile = tile
						if tile.pawn.attack(dest.xloc,dest.yloc):
							tile.pawn.moved = True
							tile.pawn.setPos(dest.xloc,dest.yloc)

						
class SleepAI(AI):
	def getName(self):
		return "SleepAI"
		
	def takeTurn(self,gameMap,player):
		return

class AIPlus(AI):
	def getName(self):
		return "AIPlus"
		
	def takeTurn(self,gameMap,player):
		# buy units where appropriate
		for row in gameMap.tiles:
			for tile in row:
				if tile.player == player:
					realm = tile.realm
					# TODO: This is really really innefficient (n^2 rather than n)
					for t in realm:
						if t.village and t.village.balance >= 35 and not tile.pawn and not tile.grave and not tile.village:
							
							tile.pawn = Villager(gameMap,tile.xloc,tile.yloc)
							t.village.balance -= 10
							gameMap.renders.append(tile.pawn)
							#print "Bought a simple pawn and placed at %sx%s for the tile at %sx%s" % (tile.x,tile.y,tile.xloc,tile.yloc)
								
								
							
						else:
							if t.village:
								#print "didn't buy anything, because %s is the balance" % (t.village.balance)
								nothing = None
								
		# upgrade units where appropriate
		#If we have high income, upgrade!
		for row in gameMap.tiles:
			for tile in row:
				if tile.player == player:
					army = []
					for t in tile.realm:
						if t.pawn and t.pawn.level < 2:
							army.append((t,t.pawn))
							#print "Counted a unit in the army of %s from %sx%s." % (player,t.xloc,t.yloc)
					if len(army) > 2:

						#print "Combining because we found %s+ level 1s for  %s" % (len(army),player)
						dest = army[1][0].getPoint()
						army[0][1].startTile = army[0][0]
						if army[0][1].attack(dest[0],dest[1]) :
							army[0][1].setPos(dest[0],dest[1])
						#print "Finished the combining process."
					#else:
						#print "Large army wasn't detected,%s in the army." % (len(army))
		
		
		# move units where appropriate		
		for row in gameMap.tiles:
			for tile in row:
				
				if tile.player == player and tile.pawn and not tile.pawn.moved:


					#print "Moving AI at %sx%s for player %s." % (tile.xloc,tile.yloc, tile.player)
					target = None
					for candidate in tile.realm:
						direction = random.randint(0,6)
						for i in range(0,6):
							dest = candidate.getAdjacentTile((direction + i) % 6)
							if dest and dest.player != tile.player and dest.getProtection() < tile.pawn.level:
								target = dest
								#print "Attacking a hum0n with protection of %s-%s." % (dest.getProtectionPair())
								#print "this hum0n has a %s and a %s." % (dest.village, dest.pawn)
								break
						if target:
							break

					if target:
						tile.pawn.startTile = tile
						if tile.pawn.attack(target.xloc,target.yloc):
							tile.pawn.moved = True
							tile.pawn.setPos(target.xloc,target.yloc)
							#print "Attack of %sx%s successful." % (target.xloc, target.yloc)
						else:
							#print "Attack of %sx%s failed! :(" % (target.xloc,target.yloc)
							tile.blueRing()
							target.redRing()

					else:
						#print "This unit had no one to attack."
						pass
		


class FullAI(AI):
	def getName(self):
		return "FullAI"
		
	def takeTurn(self,gameMap,player):
		# buy units where appropriate, and detect level of play
		levelOfPlay = 0
		
		for row in gameMap.tiles:
			for tile in row:
				# Detect level of play.
				if tile.pawn and tile.player != player:
					levelOfPlay = max(levelOfPlay,tile.pawn.level)
					
				
				if tile.player == player:
					realm = tile.realm
					# TODO: This is really really innefficient (n^2 rather than n)
					for t in realm:
						if t.village and t.village.balance >= 15 and not tile.pawn and not tile.grave and not tile.village:
							
							tile.pawn = Villager(gameMap,tile.xloc,tile.yloc)
							t.village.balance -= 10
							gameMap.renders.append(tile.pawn)
							#print "Bought a simple pawn and placed at %sx%s for the tile at %sx%s" % (tile.x,tile.y,tile.xloc,tile.yloc)
								
								
							
						else:
							if t.village:
								#print "didn't buy anything, because %s is the balance" % (t.village.balance)
								nothing = None
		
		print "Level of play determined to be %s." % (levelOfPlay)
								
		# upgrade units where appropriate
		#If we have high income, upgrade!
		# This section iterates through all of my realms and assembles an army of level 1s.
		for row in gameMap.tiles:
			for tile in row:
				if tile.player == player:
					army = []
					for t in tile.realm:
						if t.pawn:
							army.append((t,t.pawn))
							#print "Counted a unit in the army of %s from %sx%s." % (player,t.xloc,t.yloc)
							
					#Randomly sort the list so we only have a chance of combining.
					random.shuffle(army)
					if len(army) > 2:

						#print "Combining because we found %s+ level 1s for  %s" % (len(army),player)
						# Attack unit 1 of army
						dest = army[1][0]
						army[0][1].startTile = army[0][0]
						
						upkeeps = [0,2,6,18,50]
						validMove = army[0][1].level == 1 and army[1][1].level <= levelOfPlay
						
						validMove = validMove and len(dest.realm) > upkeeps[levelOfPlay]
						if  validMove and army[0][1].attack(dest.getPoint()[0],dest.getPoint()[1]) :
							
							army[0][1].setPos(dest.getPoint()[0],dest.getPoint()[1])
						#print "Finished the combining process."
					#else:
						#print "Large army wasn't detected,%s in the army." % (len(army))
		
		
		# move units where appropriate		
		for row in gameMap.tiles:
			for tile in row:
				
				if tile.player == player and tile.pawn and not tile.pawn.moved:


					#print "Moving AI at %sx%s for player %s." % (tile.xloc,tile.yloc, tile.player)
					target = None
					for candidate in tile.realm:
						direction = random.randint(0,6)
						for i in range(0,6):
							dest = candidate.getAdjacentTile((direction + i) % 6)
							if dest and dest.player != tile.player and dest.getProtection() < tile.pawn.level:
								target = dest
								#print "Attacking a hum0n with protection of %s-%s." % (dest.getProtectionPair())
								#print "this hum0n has a %s and a %s." % (dest.village, dest.pawn)
								break
						if target:
							break

					if target:
						tile.pawn.startTile = tile
						if tile.pawn.attack(target.xloc,target.yloc):
							tile.pawn.moved = True
							tile.pawn.setPos(target.xloc,target.yloc)
							#print "Attack of %sx%s successful." % (target.xloc, target.yloc)
						else:
							#print "Attack of %sx%s failed! :(" % (target.xloc,target.yloc)
							tile.blueRing()
							target.redRing()

					else:
						#print "This unit had no one to attack."
						pass