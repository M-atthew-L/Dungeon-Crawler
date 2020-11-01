from dungeon_crawler import Text_Attributes
import math

class FogofWar():

    OPAQUE_CHARACTERS = ['-', '|', '/', '\\']

    @staticmethod
    def calculateSlope(x1, y1, x2, y2):
        rise = y2 - y1
        run = x2 - x1
        slope = rise / run
        return slope

    @staticmethod
    def taxicab_distance(p1 : (int,int), p2 : (int,int)):
      if type(p1[0]) != int or type(p2[0]) != int or type(p1[1]) != int or type(p2[1]) != int:
        raise TypeError("Coordinate tuples must be integer values")
      return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


    '''
    the is_cell_transparent method takes in a 2 integer tuple parameter for the coordinate of a cell, and a nested list of strings parameter map, and returns whether the cell can transmit light
    '''
    @staticmethod
    def is_cell_transparent(cell_coords : (int,int), map : [[str]]) -> bool:
      return True if not (map[cell_coords[1]][cell_coords[0]] in FogofWar.OPAQUE_CHARACTERS) else False

    '''
    the is_char_transparent method takes in a string parameter for the character in question and returns whether the cell can transmit light, this is very similar to the is_cell_transparent method but only takes a character
    '''
    def is_char_transparent(char : str) -> bool:
      return True if not (char in FogofWar.OPAQUE_CHARACTERS) else False

    '''
    The is_in_map_bounds takes in a 2 integer tuple parameter for the coordinate of a cell and a nested list of strings parameter for the map, and returns whether the coordinate in question is inside the map bounds
    (whether the coordinate actually exists inside the map). This method assumes that the width of the map remains constant
    '''
    def is_in_map_bounds(coord : (int, int), map : [[str]]) -> bool:
      height = len(map)
      width = len(map[0])
      if coord[0] < 0 or coord[0] >= width or coord[1] < 0 or coord[1] >= height:
        return False
      else:
        return True

    '''
    The neighbor_cells method takes a 2 integer tuple parameter for the starting coordinate (where the light source is), a 2 integer tuple paraemter for where the coordinate light has reached so far, and a nested list of strings parameter for the map
    This method returns the tiles light can reach from the current tile the light is at.
    '''
    def neighbor_cells(starting_coord : (int,int), coord : (int,int), map) -> [(int, int)]:
      x1 = starting_coord[0]
      x2 = coord[0]
      y1 = starting_coord[1]
      y2 = coord[1]
      return_coords = []
      #East
      if x2 > x1 and y1 == y2: 
        c = (x2, y2+1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2, y2-1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2+1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #West
      elif x2 < x1 and y1 == y2: 
        c = (x2, y2+1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2, y2-1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2-1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #South
      elif x2 == x1 and y1 < y2: 
        c = (x2, y2+1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2-1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2+1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #north
      elif x2 < x1 and y1 > y2: 
        c = (x2, y2-1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2-1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2+1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #North East
      elif x2 > x1 and y1 > y2: 
        c = (x2, y2-1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2+1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #South East
      elif x2 > x1 and y1 < y2: 
        c = (x2, y2+1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2+1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #North West
      elif x2 < x1 and y1 > y2: 
        c = (x2, y2-1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2-1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      #South West
      elif x2 < x1 and y1 < y2: 
        c = (x2, y2+1)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
        c = (x2-1, y2)
        if FogofWar.is_in_map_bounds(c, map):
          return_coords.append(c)
      return return_coords

  
    '''
    This is the main function that we will call to determine what is visible and what is not
    The method takes a integer parameter as the radius, and will return a list of 2 integer tuples (coordinate pairs) of visible coordinates. We will later use these coordinates to know which cells to display

    To start our algorithm, we need to create a list 
    '''
    @staticmethod
    def determine_vision(vision_radius : int, starting_coord : (int, int), map : [[str]] ) -> [(int, int)]:
      #make sure to remove this pass when you start coding!!!
      pass
      #we need to create a list containing the tuple coordinates north, south, east, and west of our starting location
      #this will serve as a queue of tiles that we go through to determine visibility

      #we also need to create an empty list which will be tiles we know are visible
      #this list will also be a list of 2 integer tuples (coordinates) 
      

      #now we begin the core of our algorithm
      #from http://www.roguebasin.com/index.php?title=Spiral_Path_FOV
      #repeat:
      #  take one square off the front of the queue.*1
      #  mark it visible/lit.
      #  If it's within the sight radius and not opaque then
      #    pass light from it
      #      (this may add things to the end of the queue,
      #    or add light to things that are already in the queue)
      #  : until the queue is empty.
      #I will translate this in later comments if anything is confusing
      #FIRST we need a loop that runs until our queue list is empty (hmm i wonder what kind of loop that would be)


        #(tabbed comment means it is inside our loop)
        #NEXT we want to get the first coordinate from our queue list
        #we also want to remove this coordinate from our queue and place it in visible tiles list
        #explore the python list docs https://docs.python.org/3/tutorial/datastructures.html, and see if you can find a list method that can help you accomplish the two previous comments in one line
        #if you can't figure it out that way, its okay, do it however you think you can


        #NEXT we need to check if the following conditions are true
        #is the cell inside our vision radius. Use the FogOfWar.taxicab_distance() method to see the distance. If the taxicab distance is less than our vision radius than this is true
        #is the character at our coordinate in our map able to transmit light (aka transparent or not a wall). use the FogOfWar.is_cell_opaque() method


          #NEXT, if the previous conditions were true we want to get the next tiles to add to our queue. 
          #use the FogOfWar.neighbor_cells() method to return a list of neighboring cells. Go through this list and check to make sure they aren't already in our queue or return list
          #if they don't exist in either of our lists, then add them to our queue
      
      #LASTLY, we need to return our list of visible coordinates

