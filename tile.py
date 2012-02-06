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
from controls import *
from ai import *
from playersettings import *
from analytics import *
from map import *

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
        rect = pygame.draw.polygon(self.gameMap.background,self.color,self.getHex(),0)
        pygame.draw.polygon(self.gameMap.background,pygame.Color("#000000"),self.getHex(),1)
        
        return rect
        
    def redRing(self):
        pygame.draw.polygon(self.gameMap.background,pygame.Color("#FF0000"),self.getHex(),3)
    
    def blueRing(self):
        pygame.draw.polygon(self.gameMap.background,pygame.Color("#0000FF"),self.getHex(),3)
    
    def getHex(self):
        return getHexAt(self.x,self.y)
        
    def getPoint(self):
        return (self.xloc,self.yloc)
        
    def checkHexCollision(self,point):
        s = tilesize
        l = .25
        x = point[0] - self.x
        y = point[1] - self.y
        
        if ((2*x + y) <  s/2) or ((2*x + (s-y)) < s/2) or ((2*(s-x)+y) < s/2) or ((2*(s-x)+(s-y)) < s/2):
            # Failed hitdetection on hex
            #print "Failed hitdetection on hex %sx%s (tilesize %s) compared to %sx%s." % (x,y,s,point[0],point[1])
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
        pygame.draw.polygon(self.gameMap.background,pygame.Color("#FFFFFF"),self.getHex(),1)
        self.selected = True
    def deselect(self):
        #print "Deselecting tile"
        self.draw()
        self.selected = False
    def addPawn(self,pawn):
        self.pawn = pawn
        return pawn
        
    def __repr__(self):
        return "Tile located at %sx%s." % (self.xloc,self.yloc)
    