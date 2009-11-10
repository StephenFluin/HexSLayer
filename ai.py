#
# HexSLayer
# copyright (C) Stephen Fluin 2009
#

# AIs placed in a modular framework. They don't currently leverage state, but they could.


from pawns import *

class AI():
	def takeTurn(self, gameMap,player):
		return
		
class NaiveAI(AI):
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
	def takeTurn(self,gameMap,player):
		return

class AIPlus(AI):
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
							print "Bought a simple pawn and placed at %sx%s for the tile at %sx%s" % (tile.x,tile.y,tile.xloc,tile.yloc)
								
								
							
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

						print "Combining because we found %s+ level 1s for  %s" % (len(army),player)
						dest = army[1][0].getPoint()
						army[0][1].startTile = army[0][0]
						if army[0][1].attack(dest[0],dest[1]):
							tile.pawn.setPos(dest[0],dest[1])
						print "Finished the combining process."
					#else:
						#print "Large army wasn't detected,%s in the army." % (len(army))
		
		
		# move units where appropriate
		for row in gameMap.tiles:
			for tile in row:
				
				if tile.player == player and tile.pawn and not tile.pawn.moved:
					for candidate in tile.realm:
						direction = random.randint(0,6)
						for i in range(0,6):
							dest = candidate.getAdjacentTile((direction + i) % 6)
							if not(not dest or dest.player == tile.player or dest.xloc < 0 or dest.yloc < 0 or dest.xloc >= gameMap.width or dest.yloc >= gameMap.height):
								target = dest
							
					
						
					if target:
						tile.pawn.startTile = tile
						if tile.pawn.attack(target.xloc,target.yloc):
							tile.pawn.moved = True
							tile.pawn.setPos(target.xloc,target.yloc)
					else:
						print "No candidate for attack."
