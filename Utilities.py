class Vec2():

    #---------------------------------------------------------------------------------------------------------------------------------------
   
    def __init__(self, x, y):
        #determines position of player or enemy
        self.x = x
        self.y = y

    #---------------------------------------------------------------------------------------------------------------------------------------

class Rectangle():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, bottomLeft: Vec2, topRight: Vec2):
        self.bottomLeft = bottomLeft
        self.topRight = topRight 

    #---------------------------------------------------------------------------------------------------------------------------------------

    def DoesIntersect(self, other):
        #return self.topRight.x>=other.topRight.x>=self.bottomLeft.x and self.topRight.x>=other.bottomLeft.x>=self.bottomLeft.x and self.topRight.y>=other.topRight.y>=self.bottomLeft.y and self.topRight.x>=other.bottomLeft.x>=self.bottomLeft.x
        if(self.bottomLeft.x > other.topRight.x or other.bottomLeft.x >= self.topRight.x): 
            return False
        if(self.bottomLeft.y < other.topRight.y or other.bottomLeft.y <= self.topRight.y): 
            return False
        return True

    #---------------------------------------------------------------------------------------------------------------------------------------

    def GetIntersection(self, other):
        x1 = max(self.bottomLeft.x, other.bottomLeft.x)
        y1 = min(self.bottomLeft.y, other.bottomLeft.y)
        x2 =  min(self.topRight.x, other.topRight.x)
        y2 = max(self.topRight.y, other.topRight.y)
        return Rectangle(Vec2(x1, y1), Vec2(x2, y2))

    #---------------------------------------------------------------------------------------------------------------------------------------