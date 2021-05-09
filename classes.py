import pygame
import globals
import mathstuff
import math
import random
import worlds
from operator import sub
import functions
clock = pygame.time.Clock()

class Tile:
    def __init__(self,x,y,id,universe):
        if str(id) in globals.tileDictionary:
            tile = globals.tileDictionary[str(id)]
        else:
            tile = globals.tileDictionary[str(globals.tileHash[universe.worldType["ground"]])]
        self.type = tile["behavior"]
        self.spriteId = tile["spriteId"]
        self.name = tile["name"]
        self.id = id
        self.pos = (x,y)
        self.width = 32
        self.height = 32
class Worldtile:
    def __init__(self,x,y,universe,generateStructures=False):
        self.pos = (x,y)
        self.tiles = {}
        for xTile in range(0,globals.chunkSize):
             for yTile in range(0,globals.chunkSize):
                 xPos,yPos = xTile + self.pos[0] * globals.chunkSize,yTile + self.pos[1] * globals.chunkSize
                 if xPos > -1 and yPos > -1 and xPos < globals.worldSize and yPos < globals.worldSize:
                    if (xPos,yPos) in universe.alteredTerrain:
                        terrain = universe.alteredTerrain[xPos,yPos]
                        self.tiles[terrain[0],terrain[1]] = Tile(terrain[0],terrain[1],terrain[2],universe)
                    elif (xPos,yPos) in universe.loadedTerrain:
                        terrain = universe.loadedTerrain[xPos,yPos]
                        self.tiles[terrain[0],terrain[1]] = Tile(terrain[0],terrain[1],terrain[2],universe)
                    else:
                        perlinTile = mathstuff.generateNoise(universe.index, (xPos), (yPos),worlds.worldTerrain[universe.worldType["terrain"]],1,globals.seed)
                        if perlinTile == 1 and universe.worldType["mountains"]:
                            tile = Tile(xPos,yPos,globals.tileHash[universe.worldType["ground"]],universe)
                            self.tiles[(xPos,yPos)] = tile
                        else:
                            tile = Tile(xPos,yPos,globals.tileHash[universe.worldType["grass"]],universe)
                            self.tiles[(xPos,yPos)] = tile
class TextInput:
    def __init__(self,x,y,width,height,mode):
        self.pos = (x,y)
        self.dimensions = (width,height)
        self.active = True
        self.mode = mode
    def process(self,text):
        def teleport():
            actor = globals.multiverse[globals.currentUniverse].actors[0]
            if len(text.split()) > 1:
                if text.split()[0].isdigit() and text.split()[1].isdigit():
                    dest  = (int(text.split()[0]),int(text.split()[1]))
                    WorldManager.loadWorldTile(int(dest[0]/globals.chunkSize),int(dest[1]/globals.chunkSize),2,globals.currentUniverse)
                    actor.pos = int(dest[0]),int(dest[1])
        def teleportstep():
            actor = globals.multiverse[globals.currentUniverse].actors[0]
            newText = text.replace("-",chr(45))
            newText = newText.replace("\r","")
            if newText:
                dest = int(newText)
                functions.attemptTravel(actor,globals.currentUniverse,dest,True)
        modes = {"teleport":teleport,"teleportstep":teleportstep}
        if self.mode in modes:
            modes[self.mode]()
class WorldManager:
    def loadWorldTile(x,y,renderDistance,universe):
        ourUniverse = globals.multiverse[universe]
        chunkMove = x,y
        for number in range(-renderDistance, renderDistance):
            for number1 in range(-renderDistance, renderDistance):
                if (chunkMove[0] + number, chunkMove[1] + number1) in ourUniverse.gameBoards:
                    pass
                else:
                    ourUniverse.gameBoards[chunkMove[0] + number, chunkMove[1] + number1] = Worldtile(
                        chunkMove[0] + number, chunkMove[1] + number1,ourUniverse,True)
    def unloadWorldTile(renderDistance,actor,universe):
        ourUniverse = globals.multiverse[universe]
        toBeDeleted = []
        for object in ourUniverse.gameBoards.values():
            dist = tuple(map(lambda i, j: i - j, actor.tempchunkPos,object.pos))
            if abs(dist[0]) > renderDistance or abs(dist[1]) > renderDistance:
                toBeDeleted.append(object)
        for object in toBeDeleted:
            ourUniverse.gameBoards.pop(object.pos)

class WorldGen:
    def _generate_building(mode,X,Y,width,height,universe):
        def room():
            for x in range(0,width):
                for y in range(0,height):
                    if universe in globals.multiverse:
                        ourUniverse = globals.multiverse[universe]
                        if x==0 or x==width-1 or y==0 or y==height-1:
                            ourUniverse.loadedTerrain[X+x,Y+y] = (X+x,Y+y,2)
                    else:
                        globals.multiverse[universe] = Universe(universe)
                        ourUniverse = globals.multiverse[universe]
                        ourUniverse.loadedTerrain[X + x, Y + y] = (X + x, Y + y,2)
        def square():
            for x in range(0,width):
                for y in range(0,height):
                    if universe in globals.multiverse:
                        ourUniverse = globals.multiverse[universe]
                        ourUniverse.loadedTerrain[X+x,Y+y] = [X+x,Y+y,2]
                    else:
                        globals.multiverse[universe] = Universe(universe)
                        ourUniverse = globals.multiverse[universe]
                        ourUniverse.loadedTerrain[X + x, Y + y] = [X + x, Y + y,2]

        keys = {"room":room,"square":square}
        if mode in keys:
            keys[mode]()

    def populateSquare(universe):
        random.seed(globals.seed+universe)
        locations = []
        for x in range(0,10):
            for y in range(0,10):
                locations.append((int(random.uniform(x*100,y*100)),(int(random.uniform(y*100,x*100)))))
        for number in locations:
            WorldGen._generate_building("room", number[0],number[1],10,10, universe)
class Universe:
    def __init__(self,index):
        self.index = index
        self.objects = []
        self.actors = {}
        self.items = []
        self.board = {}
        self.objectMap = {}
        self.gameBoards = {}
        self.loadedTerrain = {}
        self.alteredTerrain = {}
        self.altered = False
        randNumber = int(self.index/20)
        tempNumber = -500000
        random.seed(randNumber)
        choices = []
        if randNumber != tempNumber:
            tempNumber = randNumber
            choices = (random.choices(list(worlds.worldChances.keys()), list(worlds.worldChances.values()), k=20))
        self.worldType = worlds.worldData[list(choices)[self.index%len(choices)]]
class Actor():
    def __init__(self,x,y,id,universe):
        self.important = True
        self.type = "actor"
        self.spriteId = 3
        self.pos = (x,y)
        self.id = id
        self.tempchunkPos = (int(self.pos[0]/16),int(self.pos[1]/16))
        self.actionPointsMax = 5
        self.actionPointsRegen = 1
        self.HP = 10
        self.maxHP = 10
        self.currentUniverse = universe
        WorldManager.loadWorldTile(self.tempchunkPos[0],self.tempchunkPos[1], 3, self.currentUniverse)
    def _process(self):
        chunkPos = (int(self.pos[0]/globals.chunkSize),int(self.pos[1]/globals.chunkSize))
        if chunkPos != self.tempchunkPos:
            WorldManager.loadWorldTile(chunkPos[0],chunkPos[1],3,globals.currentUniverse)
            WorldManager.unloadWorldTile(3,self,globals.currentUniverse)
            self.tempchunkPos = chunkPos

    def move_object(object, amount):
        globals.initialize()
        ourUniverse = globals.multiverse[globals.currentUniverse]

        if (object.pos[0] + amount[0], object.pos[1] + amount[1]) in ourUniverse.board:
            curBoard = ourUniverse.board[tuple(map(sum, zip(object.pos, amount)))]
            move = tuple(map(sum, zip(object.pos, amount)))
            chunkMove = (int(move[0] / globals.chunkSize), int(move[1] / globals.chunkSize))
            def actor():
                pass
            def wall():
                pass
            def empty():
                object.pos = curBoard.pos
            collisions = {"actor": actor, "wall": wall, "empty": empty}
            if (curBoard.pos) in ourUniverse.objectMap:
                target = ourUniverse.objectMap[curBoard.pos]
                if target.type is not None:
                    if target.type in collisions:
                        collisions[target.type]()
                    else:
                        pass
            elif (curBoard.pos) in ourUniverse.board:
                target = ourUniverse.board[curBoard.pos]
                if target.type in collisions:
                    collisions[target.type]()
            else:
                collisions["empty"]()

class Enemy:
    def __init__(self,x,y,id,universe):
        self.important = True
        self.type = "enemy"
        self.spriteId = 3
        self.pos = (x,y)
        self.id = id
        self.actionPointsMax = 5
        self.actionPointsRegen = 1
        self.HP = 10
        self.maxHP = 10
        self.currentUniverse = 0
    def _process(self):
        globals.initialize()
        ourUniverse = globals.multiverse[globals.currentUniverse]
        if 0 > 3:
            target = ourUniverse.actors[0]
            direction = pygame.math.Vector2(tuple(map(sub,target.pos,self.pos))).normalize()
            direction = (math.floor(direction.x),math.floor(direction.y))
            self.move_object(direction)
    def move_object(object,amount):
        globals.initialize()
        ourUniverse = globals.multiverse[globals.currentUniverse]
        if (tuple(map(sum, zip(object.pos, amount)))) in ourUniverse.board:
            curBoard = ourUniverse.board[tuple(map(sum, zip(object.pos, amount)))]
            def actor():
                pass
            def wall():
                pass
            def empty():
                object.pos=curBoard.pos
            def enemy():
                pass
            collisions = {"actor":actor,"wall":wall,"empty":empty,"enemy":enemy}
            if (curBoard.pos) in ourUniverse.objectMap:
                target = ourUniverse.objectMap[curBoard.pos]
                if target.type is not None:
                    if target.type in collisions:
                        collisions[target.type]()
                    else:
                        pass
            elif (curBoard.pos) in ourUniverse.board:
                target = ourUniverse.board[curBoard.pos]
                if target.type in collisions:
                    collisions[target.type]()
            #else: