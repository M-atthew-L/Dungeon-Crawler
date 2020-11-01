import math
import random
from Camera import Camera
from Utilities import Vec2, Rectangle
import FogofWar

class Room():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, data, pos: Vec2, _id):
        self.width = len(data[0])
        self.height = len(data)
        self.overlay = []
        self.data = self._generateMapData(data)
        self.uniqueRoomID = _id
        self.position = pos
        self.rect = Rectangle(Vec2( self.position.x, self.position.y + self.height ), Vec2( self.position.x + self.width, self.position.y ) )
        self._isColliding = False

    #---------------------------------------------------------------------------------------------------------------------------------------

    def _generateMapData(self, data):
        d = []
        for y in range(self.height):
            self.overlay.append([])
            d.append([])
            for x in range(self.width):
                self.overlay[y].append(0)
                d[y].append(data[y][x])
        
        return d

    #---------------------------------------------------------------------------------------------------------------------------------------

    def _updatePos(self, x:int, y:int):
        self._updatePosX(x)
        self._updatePosY(y)

    def _updatePosX(self, x:int):
        self.position.x = x
        self.rect = Rectangle(Vec2( self.position.x, self.position.y + self.height ), Vec2( self.position.x + self.width, self.position.y ) )
    
    def _updatePosY(self, y:int):
        self.position.y = y
        self.rect = Rectangle(Vec2( self.position.x, self.position.y + self.height ), Vec2( self.position.x + self.width, self.position.y ) )

    def isPositionInside(self, x:int, y:int) -> bool:
        if y <= self.rect.bottomLeft.y and self.rect.topRight.y <= y and x >= self.rect.bottomLeft.x and x <= self.rect.topRight.x:
            return True
        else:
            return False

    #---------------------------------------------------------------------------------------------------------------------------------------

class LevelGenerator():
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, roomTemplates):
        self.rooms = []
        self.roomTemplates = roomTemplates

    #---------------------------------------------------------------------------------------------------------------------------------------

    def GetCurrentMapData(self, camera, overlays) -> list(list()):
        return self._getDrawRoomData(camera, overlays)

    def GetRandomPointInCircle(self, radius) -> Vec2:
        t = 2*math.pi*random.random()
        u = random.random()+random.random()
        r = 0
        if u > 1:
            r = 2-u 
        else: 
            r = u
        return Vec2(round(radius*r*math.cos(t)), round(radius*r*math.sin(t)))

    #---------------------------------------------------------------------------------------------------------------------------------------

    def GenerateStartingRooms(self, numRooms, rad, roomSpacing:int):
        for i in range(numRooms):
            self.rooms.append(Room(random.choice([self.roomTemplates]), self.GetRandomPointInCircle(rad), i))

        self._bounceRooms(roomSpacing)

    def GenerateLevel(self, roomCap, minMainRooms, maxMainRooms, maxCorridorLength):
        lastX = 0
        lastY = 0
        lastDirection = 0
        numberOfRooms = 0
        numberOfMainRooms = 0
        mainRoomCap = random.randint(minMainRooms, maxMainRooms)
        while numberOfMainRooms < mainRoomCap:
            directionsToGo = random.randint(1,2)
            direction = 1
            if directionsToGo == 1:
                direction = random.randint(2, 3)
            elif directionsToGo == 2:
                direction = random.randint(1, 2)
            lastDirection = direction
            for d in range(1,4):
                rand = random.randint(1,3)
                if rand == 1 or d == direction:
                    corridorLength = random.randint(1, maxCorridorLength)
                    x = lastX
                    y = lastY
                    room = Room(random.choice(self.roomTemplates),Vec2(x,y), numberOfRooms)
                    if len(self.rooms) > 0:
                        if d == 1:
                            room.position.y -= (room.height + corridorLength)
                        elif d == 2:
                            room.position.x += self.rooms[len(self.rooms) - 1].width + corridorLength
                        elif d == 3:
                            room.position.y += self.rooms[len(self.rooms) - 1].height + corridorLength
                    if lastDirection != 0:
                        holeX = 0
                        holeY = 0
                        if lastDirection == 1:
                            holeX = math.ceil(room.width / 2)
                            holeY = room.height - 1
                        elif lastDirection == 2:
                            holeX = 0
                            holeY = math.ceil(room.height / 2)
                        elif lastDirection == 3:  
                            holeX = math.ceil(room.width / 2)
                            holeY = 0
                        room.data[holeY][holeX] = " "
                    if d == direction:
                        holeX = 0
                        holeY = 0
                        if d == 1:
                            holeX = math.ceil(room.width / 2)
                            holeY = 0
                        elif d == 2:
                            holeX = room.width - 1
                            holeY = math.ceil(room.height / 2)
                        elif d == 3:  
                            holeX = math.ceil(room.width / 2)
                            holeY = room.height - 1
                        room.data[holeY][holeX] = " "
                    if numberOfRooms < roomCap or d == direction:
                        numberOfRooms += 1
                        self.rooms.append(room)
                    if d == direction:
                        lastX = room.position.x
                        lastY = room.position.y
                        lastDirection = d
                        numberOfMainRooms += 1

    def BuildMapFromRoomData(self) -> list(list()):
        
        for room in self.rooms:
            room.hasBuiltRoom = False
        
        width = 0
        height = 0
        for room in self.rooms:
            topRightX = room.rect.topRight.x
            bottomLeftY = room.rect.bottomLeft.y
            width = topRightX if topRightX > width else width
            height =  bottomLeftY if bottomLeftY > height else height

        map = []
        for y in range(height):
            map.append([])
            for x in range(width):
                for room in self.rooms:
                    if room.isPositionInside(x, y):
                        roomY = y - room.rect.topRight.y
                        if roomY >= len(room.data):
                            continue

                        roomX = x - room.rect.bottomLeft.x
                        if roomX >= len(room.data[roomY]):
                            continue
                       
                        map[y].append(room.data[roomY][roomX])
                        break
                    else:
                        map[y].append(" ")
        
        return map

            

    #player can spawn in any of the main rooms, not just top right.
    #---------------------------------------------------------------------------------------------------------------------------------------

    def _bounceRooms(self, bounceAmount:int):
        colRooms = 1
        iter = 1
        while colRooms > 0:
            print(iter)
            iter += 1
            for room in self.rooms:
                col = False
                for otherRoom in self.rooms:
                    if room.uniqueRoomID != otherRoom.uniqueRoomID:
                        if room.rect.DoesIntersect(otherRoom.rect):
                            absDX = abs(room.position.x - otherRoom.position.x)
                            absDY = abs(room.position.y - otherRoom.position.y)
                            if absDX >= absDY:
                                room._updatePosX(room.position.x + bounceAmount if room.position.x > otherRoom.position.x else room.position.x - bounceAmount)
                                otherRoom._updatePosX(otherRoom.position.x - bounceAmount if room.position.x > otherRoom.position.x else otherRoom.position.x + bounceAmount)
                                col = True
                            else:
                                room._updatePosY(room.position.y + bounceAmount if room.position.y > otherRoom.position.y else room.position.y - bounceAmount)
                                otherRoom._updatePosY(otherRoom.position.y - bounceAmount if room.position.y > otherRoom.position.y else otherRoom.position.y + bounceAmount)
                                col = True

                        '''
                        absDX = abs(room.position.x - otherRoom.position.x)
                        absDY = abs(room.position.y - otherRoom.position.y)
                        if absDX < min(room.width, otherRoom.width):
                            room.position.x = room.position.x + bounceAmount if room.position.x > otherRoom.position.x else room.position.x - bounceAmount
                            otherRoom.position.x = otherRoom.position.x - bounceAmount if room.position.x > otherRoom.position.x else otherRoom.position.x + bounceAmount
                            col = True
                        elif absDY < min(room.height, otherRoom.height):
                            room.position.y = room.position.y + bounceAmount if room.position.y > otherRoom.position.y else room.position.y - bounceAmount
                            otherRoom.position.y = otherRoom.position.y - bounceAmount if room.position.y > otherRoom.position.y else otherRoom.position.y + bounceAmount
                            col = True
                        '''

                room._isColliding = col
                        
            colRooms = 0
            for room in self.rooms:
                if room._isColliding == True:
                    colRooms += 1

    #---------------------------------------------------------------------------------------------------------------------------------------

    def _getDrawRoomData(self, camera, overlays):

        roomsToRender = []
        intersectionData = []
        for i in range(len(self.rooms)):
            room = self.rooms[i]
            if room.rect.DoesIntersect(camera.rect):
                intersection = room.rect.GetIntersection(camera.rect)
                roomsToRender.append(room)
                intersectionData.append(intersection)

        mapToRender = []
        

        #add border after last row
        #mapToRender.append(rowData) 
        col = 0
        row = 0

        for y in range(camera.rect.topRight.y, camera.rect.bottomLeft.y + 1):
            mapToRender.append([])
            for x in range(camera.rect.bottomLeft.x, camera.rect.topRight.x + 1):
                foundRoom = False
                for i in range(len(intersectionData)):
                    intersectedRoom = intersectionData[i]
                    if y <= intersectedRoom.bottomLeft.y and intersectedRoom.topRight.y <= y and x >= intersectedRoom.bottomLeft.x and x <= intersectedRoom.topRight.x:
                        topLeftX = roomsToRender[i].rect.bottomLeft.x 
                        topLeftY = roomsToRender[i].rect.topRight.y
                        
                        
                        roomY = y - topLeftY
                        if roomY >= len(roomsToRender[i].data):
                            continue

                        roomX = x - topLeftX
                        if roomX >= len(roomsToRender[i].data[roomY]):
                            row += 1
                            continue
                        
                        mapToRender[col].append(roomsToRender[i].data[roomY][roomX])
                        foundRoom = True
                        row += 1
                        break
                
                if not foundRoom:
                    mapToRender[col].append(" ")

                

            row = 0
            col += 1
        
        #add border after last row
        #mapToRender.append(rowData)
        for lst in overlays:
            for e in lst:
                x = e.position.x
                y = e.position.y
                if x >= camera.rect.bottomLeft.x and x <= camera.rect.topRight.x and y <= camera.rect.bottomLeft.y and y >= camera.rect.topRight.y:
                    mapToRender[y - camera.rect.topRight.y][x - camera.rect.bottomLeft.x] = e.displayCharacter
                    
                    
        return mapToRender
                    
    def DrawRooms(self, cam:Camera, overlays, enableFogOfWar = False):
        mapToRender = self._getDrawRoomData(cam, overlays)
        if enableFogOfWar:
            visibleTiles = FogofWar.FogofWar.determine_vision(7, (cam.position.x, cam.position.y), mapToRender)
        rowData = ""
        #create border data
        for __ in range(cam.width + 3):
            rowData += cam.borderCharacter
        print(rowData)
        for y in range(len(mapToRender)):
            builtRow = cam.borderCharacter
            for x in range(len(mapToRender[y])):
                if enableFogOfWar:
                    foundTile = False
                    for tile in visibleTiles:
                        if tile[0] == x + cam.rect.bottomLeft.x and tile[1] == y + cam.rect.topRight.y:
                            builtRow += mapToRender[y][x]
                            visibleTiles.remove(tile)
                            foundTile = True
                            break
                    if not foundTile:
                        builtRow += " "
                else:
                    builtRow += mapToRender[y][x]
            builtRow += cam.borderCharacter
            print(builtRow)
        print(rowData)
        self.culledMapData = mapToRender
    
    def DrawEntities(self): 
        pass

    #---------------------------------------------------------------------------------------------------------------------------------------