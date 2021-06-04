import globals
import classes
import worlds
## THING DOERS
def alter_tile(tile,id):
    globals.initialize()
    ourUniverse = globals.multiverse[globals.currentUniverse]
    chunkBlock = (int(tile[0]/globals.chunkSize),int(tile[1]/globals.chunkSize))
    if chunkBlock in ourUniverse.gameBoards:
        if tile in ourUniverse.gameBoards[chunkBlock].tiles:
            ourUniverse.gameBoards[chunkBlock].tiles[tile] = classes.Tile(tile[0],tile[1],id,ourUniverse)
            ourUniverse.alteredTerrain[tile] = classes.Tile(tile[0],tile[1],id,ourUniverse)
            ourUniverse.altered = True
        if tile in ourUniverse.objectMap:
            ourUniverse.worldEntities.remove(ourUniverse.objectMap[tile])
    elif chunkBlock not in ourUniverse.gameBoards:
        if chunkBlock[0] > 1 and chunkBlock[1]> 1 and chunkBlock[0] < (globals.worldSize/globals.chunkSize)-2 and chunkBlock[1] < (globals.worldSize/globals.chunkSize)-2:
            ourUniverse.gameBoards[chunkBlock] = classes.Worldtile(chunkBlock[0],chunkBlock[1],ourUniverse,True)
def attemptTravel(actor,index,movement,force=False):
        if movement not in globals.multiverse:
            prepareUniverse(movement)
        if testTravel(actor, index, movement):
            Step(actor,index,movement,True)
        elif force:
            Step(actor, index, movement, True)
def D4C(actor,victim,index,movement):
    prepareUniverse(index,movement)
    if testTravel(actor, index, movement) and testTravel(victim,index,movement):
        Step(actor,index,movement,True)
        Step(victim,index,movement,True)
## CONDITION TESTING????
def spawnActor(pos,universe):
    globals.initialize()
    #globals.multiverse[universe].actors[globals.nextActor] = classes.Enemy(pos[0], pos[1], globals.nextActor,universe)
    #globals.nextActor += 1
def prepareUniverse(movement):
    globals.initialize()
    globals.createUniverse(movement)
    globals.quickload(movement)
    #classes.WorldGen.populateSquare(movement)
def Step(actor,index,movement,follow):
    boardsToBeDeleted = []
    universesToBeDeleted = []
    for object in globals.multiverse[index].gameBoards.values():
        if object.pos not in globals.multiverse[movement].gameBoards:
            globals.multiverse[movement].gameBoards[object.pos] = classes.Worldtile(object.pos[0], object.pos[1],
                                                                                globals.multiverse[movement], True)
    if follow:
        globals.currentUniverse = movement
        globals.multiverse[movement].actors[actor.id] = actor
        globals.multiverse[movement].actors[actor.id].currentUniverse = movement
        globals.multiverse[index].actors.pop(actor.id)

        #deletion
        for object in globals.multiverse:
            if abs(object - globals.currentUniverse) > 2:
                universesToBeDeleted.append(object)
        for board in boardsToBeDeleted:
            globals.multiverse[index].gameBoards.pop(board.pos)
        for universe in universesToBeDeleted:
            if globals.multiverse[universe].altered or globals.multiverse[universe].actors:
                globals.quicksave(universe)
            globals.multiverse.pop(universe)
        globals.insertToActionLog("Teleported to earth " + str(movement))
    else:
        globals.multiverse[movement].actors[actor.id] = actor
        globals.multiverse[index].actors.pop(actor.id)
def testTravel(actor,index,movement):
    prepareUniverse(movement)
    universe = globals.multiverse[movement]
    if (int(actor.pos[0]/globals.chunkSize),int(actor.pos[1]/globals.chunkSize)) not in globals.multiverse[movement].gameBoards:
        classes.WorldManager.loadWorldTile(int(actor.pos[0] / globals.chunkSize), int(actor.pos[1] / globals.chunkSize),
                                           2, movement)
    tiles = universe.gameBoards[int(actor.pos[0]/globals.chunkSize),int(actor.pos[1]/globals.chunkSize)].tiles
    if (actor.pos[0],actor.pos[1]) in tiles:
        if tiles[actor.pos[0],actor.pos[1]].type == "wall":
            globals.insertToActionLog("Path Blocked.")
            return False
        else:
            return True
    else:
        return False