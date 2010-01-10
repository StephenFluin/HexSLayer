#
# HexSLayer
# copyright (C) Stephen Fluin 2010
#

from hexconfig import *

def getHexAt(x,y):
	s = tilesize
	l = .25
	r = .75
	return ((x+l*s,y), (x+r*s,y), (x+s,y+s/2), (x+r*s,y+s), (x+l*s,y+s), (x,y+s/2))
	
def convertGridPosition(map,x,y):
	return (x*1.5*tilesize+y%2*tilesize*.75+map.x,y*tilesize/2+map.y)


# We define 0 as north, then go clockwise.
def getAdjacent(x,y,direction):
	evenYChanges = ((0,-2),(0,-1),(0,1),(0,2),(-1,1),(-1,-1))
	oddYChanges = ((0,-2),(1,-1),(1,1),(0,2),(0,1),(0,-1))
	dirChanges=(evenYChanges,oddYChanges)
	change = dirChanges[y % 2][direction]
	return (x+change[0],y+change[1])



# adjacency works as:	NW		N		NE		SE		S	SW
# 1,2 is different like:	-1,-1	0,-2		0,-1		0,1		0,2	-1,1
# 0,3 is different like:	0,-1		0,-2		1,-1		1,1		0,2	0,1
# 1,3 is different like:	0,-1		0,-2		1,-1		1,1		0,2	0,1
# 1,4 is different like:	-1,-1	0,-2		0,-1		0,1		0,2	-1,1
def isAdjacent(x1,y1,x2,y2):
	for i in range(6):
		if getAdjacent(x1,y1,i) == (x2,y2):
			return 1
	return 0