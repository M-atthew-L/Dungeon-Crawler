import math
Scan(depth, startslope, endslope)
 
init y
init x

    while current_slope has not reached endslope do
     if (x,y) within visual range then
       if (x,y) blocked and prior not blocked then
         Scan(depth + 1, startslope, new_endslope)
       if (x,y) not blocked and prior blocked then
         new_startslope
       set (x,y) visible
     progress (x,y)

   regress (x,y)

   if depth < visual range and (x,y) not blocked
     Scan(depth + 1, startslope, endslope)
 end

class FogofWar():

    @staticmethod
    def calculateSlope(self, x1, y1, x2, y2):
        rise = y2 - y1
        run = x2 - x1
        slope = rise / run
        return slope

    @staticmethod
    def calculateVisionforOctant(self, map, octant, vision):
        if octant == 1:
            counter = 1
            for y in range(vision):
                for x in range(counter):
                    character = map    

        if octant == 2:
        if octant == 3:
        if octant == 4:
        if octant == 5:
        if octant == 6:
        if octant == 7:
        if octant == 8:

    @staticmethod
    def prepareBlankMap(self, vision):
        blankMap = []
        for y in range((vision * 2) + 1):
            blankMap.append([])
            for x in range((vision * 2) + 1):
                blankMap[y].append(".")
        return blankMap