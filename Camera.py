import math
from Utilities import Vec2, Rectangle

class Camera():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, width, height):
        self.position = Vec2(x, y)
        self.width = width
        self.height = height
        self.borderCharacter = "/"
        self.rect = Rectangle(Vec2(self.position.x-math.floor(self.width / 2), self.position.y+math.floor(self.height / 2)), Vec2(self.position.x+math.floor(self.width / 2), self.position.y-math.floor(self.height / 2)))

    #---------------------------------------------------------------------------------------------------------------------------------------

    def update(self, playerPosition):
        self.position = playerPosition
        self.rect = Rectangle(Vec2(self.position.x-math.floor(self.width / 2), self.position.y+math.floor(self.height / 2)), Vec2(self.position.x+math.floor(self.width / 2), self.position.y-math.floor(self.height / 2)))

    #---------------------------------------------------------------------------------------------------------------------------------------