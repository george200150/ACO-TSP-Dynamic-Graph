'''
Created on 26 mar. 2020

@author: George
'''
import math

def dist(i,j): # i si j sunt puncte de forma (x,y)
    xi = i[0]
    yi = i[1]
    
    xj = j[0]
    yj = j[1]
    
    dx = (xi - xj)**2
    dy = (yi - yj)**2 # a nu se inelege ca ar fi derivate
    dist = math.sqrt( dx + dy )
    return dist
# !!! DIST MUST BE THE SAME FUNCTION USED IN THE MAIN MODULE.
# ELSE IT MAKES NO SENSE TO CREATE THE ADJACENCE MATRIX AND CALCULATE THE DISTANCE WITH DIFFERENT METHODS !!!

def parse(fileName): # safer method to parse file input to dict of label : (x,y) tuples
    nodes = {}
    
    f = open(fileName, "r")
    while True:
        
        line = f.readline()
        parts = line.split(" ")
        
        if len(parts) == 3:
            label = int(parts[0]) - 1
            x = float(parts[1])
            y = float(parts[2])
            nodes[label] = (x,y)
        else:
            break
    return nodes



def parseBerlin(fileName, dist_callback):
    f = open(fileName, "r")
    
    points = []
    
    while True:
        
        line = f.readline()
        parts = line.split(" ")
        
        if len(parts) == 3:
            label = int(parts[0]) - 1
            x = float(parts[1])
            y = float(parts[2])
            point = (label,x,y)
            points.append(point)
        else:
            break
    
    #N = len(points) # 52
    
    
    A = []
    for pointi in points:
        row = []
        for pointj in points:
            ij = dist_callback(pointi,pointj) # distance function is used here
            row.append(ij)
        A.append(row)
    
    return A # adjacence matrix
