import math
#from itertools import *
import numpy as np

def get_orientation(origin, p1, p2):
    difference = ((p2[0] - origin[0]) * (p1[1] - origin[1])) - (
        (p1[0] - origin[0]) * (p2[1] - origin[1])
    )
    return difference

def line_intersect(line1, line2):
    """ returns a (x, y) tuple or None if there is no intersection """
    if line1[0] == line2[0] or line1[0] == line2[1] or line1[1] == line2[1] or line1[1] == line2[0]: return False
    d = (line2[1][1] - line2[0][1]) * (line1[1][0] - line1[0][0]) - (line2[1][0] - line2[0][0]) * (line1[1][1] - line1[0][1])
    if d:
        uA = ((line2[1][0] - line2[0][0]) * (line1[0][1] - line2[0][1]) - (line2[1][1] - line2[0][1]) * (line1[0][0] - line2[0][0])) / d
        uB = ((line1[1][0] - line1[0][0]) * (line1[0][1] - line2[0][1]) - (line1[1][1] - line1[0][1]) * (line1[0][0] - line2[0][0])) / d
    else:
        return False
    if not(0 <= uA <= 1 and 0 <= uB <= 1):
        return False
    x = line1[0][0] + uA * (line1[1][0] - line1[0][0])
    y = line1[0][1] + uA * (line1[1][1] - line1[0][1])
 
    return True