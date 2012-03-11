#
# HexSLayer
# copyright (C) Stephen Fluin 2012
#

import pygame, random, time, os, math

from pygame.locals import *

try:
    import android
except ImportError:
    android = None
    
# load HexSLayer modules
from pawns import *
from hexmath import *
from hexconfig import *
from interface import *
from ai import *
from playersettings import *
from analytics import *
from tile import *


            

class Map():
    def __init__(self,background):
        #tile metrics
        

        self.background = background       

        self.width = 8#13
        self.height = 17#25
        
        self.x = 10
        self.y = 35
        
        self.zoom = 0
        
        self.turn = 0
        self.gameOver = False
        self.startNewGame = False
        self.selectedSetIncome = 0
        self.selectedSetUpkeep = 0
        self.mouseCarrying = None
        
        self.tiles = []
        self.renders = []
        self.interfaces = []
        self.selectedSet = []
        self.selectedVillage = None
        self.infoBar = None
        self.players = []
        self.messenger = None
        self.winner = 0
        
        
        for y in range(self.height):
            
            row = [None]*self.width
            for x in range(self.width):
                row[x] = Tile(self,x,y)
            self.tiles.append(row)
            
        # Add Human to the game.
        self.players.append(HumanIntelligence())
                
        # Add some AIs to the game.
        for i in range(0,3):
            self.players.append(NaiveAI())
        self.players.append(AIPlus())
        self.players.append(FullAI())
        
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
                        if dest.player == 0:
                            dest.gameMap.message("Your region split",dest.player)
                        
                    
                    # Too many villages, add the gold from the removed village to a remaining village.
                    while len(villages) > 1 or ( len(villages) > 0 and len(tile.realm) < 2):
                        dest = villages.pop(random.randrange(len(villages)))
                        if len(villages) >= 1:
                            villages[0].village.balance += dest.village.balance
                            dest.gameMap.message("Regions merged",dest.player)
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
                                
                        self.message("One of your regions has starved!",tile.player)
                    
                if tile.pawn:
                    
                    tile.pawn.moved = False
                    if(len(tile.realm) == 1):
                        tile.pawn.kill(tile)
        self.turn += 1
        pygame.display.set_caption("HexSLayer - Turn %s" % (str(self.turn)))
        self.runAI()
        self.reRender()
        
        self.save()
        
        
    def changeZoom(self,amount):
        self.zoom += amount
        
        
        
    # Process AI calls for each player. 
    # TODO Make this use a model of handing an AI class a gamemap and have the AI take a single turn.
    def runAI(self):
        #The game currently has no protections from cheating, but do we need them if all of the AI's have moved every turn?
        #yes, we will need protections for the networked versions, also, if the AI wants to save money, we need to stop
        #others from spending their gold.
        for player in range(0,6):
            #print "Running ai for player %s" % (player)
            self.players[player].takeTurn(self,player)
            
            
    # Iterates over tiles, villages, pawns, and add them to renders. Completely re-renders screen.
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
                    
        
        if self.gameOver:
            self.gameOver = False
            self.interfaces.append(GameOver(self,self.winner))
            trackEvent("gameover",{"winner":self.winner})
            ps = PlayerSettings()
            wins = ps.getPlayerStat("wins");
            losses = ps.getPlayerStat("losses")
            
            if self.winner == 0:
                wins += 1
            else:
                losses += 1
            ps.setPlayerStat("wins",wins)
            ps.setPlayerStat("losses",losses)
                    
        
                            
    def message(self,msg,player=0):
        if player == 0 and self.messenger:
            self.messenger.message(msg)
            
    
    def save(self):
        gameData = self.serialize()
        settings = PlayerSettings()
        settings.update("gameData",gameData)
    
    #Returns a a simple dict of map that can be saved
    def serialize(self):
        ret = {}
        ret["MapFormat"] = 1
        ret["Turn"] = self.turn
        ret["Tiles"] = []
        for row in self.tiles:
            rowData = []
            for tile in row:
                tileData = {}
                tileData["player"] = tile.player
                if tile.pawn:
                    tileData["pawn"] = tile.pawn.level
                    if isinstance(tile.pawn,Castle):
                        tileData["pawn"] += .1
                if tile.village:
                    tileData["village"] = tile.village.balance
                rowData.append(tileData)
            ret["Tiles"].append(rowData)
                
        return ret

    def setInterfaces(self, interfaceList):
        self.interfaces = interfaceList
    
    def renewGame(self):
        self.startNewGame = True
    
def MapDeserialize(background,data):
    m = Map(background)
    m.renders = []
    #print "Map tiles before load are ",m.tiles
    #print "length of tiles in data is %s" % (len(data["Tiles"]))
    if "Turn" in data:
        m.turn = data["Turn"]
    rc = 0
    for row in data["Tiles"]:
        tc = 0
        for tile in row:
            
            m.tiles[rc][tc].setPlayer(tile["player"])
            if "pawn" in tile:
                if tile["pawn"] >= 1:
                    #print "Creating villager %s" % (tile["pawn"])
                    m.tiles[rc][tc].pawn = Villager(m,tc,rc)
                    
                if tile["pawn"] >= 2:
                    #print "upgrading pawn to wizard."
                    m.tiles[rc][tc].pawn.upgrade()
                    
                if tile["pawn"] >= 3:
                    #print "upgrading pawn to swords."
                    m.tiles[rc][tc].pawn.upgrade()
                    
                if tile["pawn"] >= 4:
                    # upgrading pawn to knight.
                    m.tiles[rc][tc].pawn.upgrade()
                    
                
                if tile["pawn"] == 2.1:
                    m.tiles[rc][tc].pawn = Castle(m,tc,rc)
                    
                m.tiles[rc][tc].pawn.player = tile["player"]
                    
                m.renders.append(m.tiles[rc][tc].pawn)
            else:
                m.tiles[rc][tc].pawn = None
                
            if "village" in tile:
                m.tiles[rc][tc].village = Village(m,tc,rc)
                m.renders.append(m.tiles[rc][tc].village)
                m.tiles[rc][tc].village.balance = tile["village"]
            else:
                m.tiles[rc][tc].village = None
            
            
            tc += 1
        rc += 1
    m.cleanUpGame()
    m.reRender()
    return m
            
     


            