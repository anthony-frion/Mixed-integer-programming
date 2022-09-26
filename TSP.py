# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 16:24:57 2020

@author: Anthony
"""

# Useful auxilary functions returning respectively the first and second element of a couple

def fst(couple) :
    a, b = couple
    return a

def snd(couple) :
    a, b = couple
    return b

# Very few imports needed

import random as rd
from math import sqrt

# Very simple class defining a TSP instance
class TSP :
    
    def __init__(self, points, distances) :
        self.numberPoints = len(points)
        self.points = points
        self.distances = distances
        
# Generates a random instance of TSP, with cities positioned on a 2D grid and corresponding euclidean distances
# numberPoints is the number of cities/nodes that you want to have
# Xsize and Ysize represent the resolution of the discrete grid on which we will place the cities
def generateRandomTSP(numberPoints, Xsize=1000, Ysize=600) :
    points = []
    for i in range(numberPoints) :
        newPoint = (rd.randint(0, Xsize-1), rd.randint(0, Ysize-1))
        points.append(newPoint)
    distances = []
    for i in range(numberPoints) :
        newDistancesRow = []
        for j in range(numberPoints) :
            newDistancesRow.append(sqrt((fst(points[i]) - fst(points[j])) **2 + (snd(points[i]) - snd(points[j])) **2))
        distances.append(newDistancesRow)
    return TSP(points, distances)

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
