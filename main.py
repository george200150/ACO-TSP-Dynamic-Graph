'''
Created on 26 mar. 2020

@author: George
'''

from ant_colony import AntColony as createColony
from parse import parse, parseBerlin
from parse import dist
import matplotlib.pyplot as plt
from random import seed

import numpy as np
import warnings
import networkx as nx

'''
Ar avea sens sa schimb formatul datelor si sa adaug grafului nodul sursa de doua ori? (Plus constrangerea ca sa fie si destinatie?)
'''

def plotRawNetwork(net):
    warnings.simplefilter('ignore')
    
    A=np.matrix(net) # network["mat"]
    G=nx.from_numpy_matrix(A)
    pos = nx.spring_layout(G)
    plt.figure(figsize=(7, 7)) 
    nx.draw_networkx_nodes(G, pos, node_size=600, cmap=plt.cm.RdYlBu)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    plt.show(G)


# http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/berlin52.tsp        BEST: x =  [46, 25, 26, 27, 11, 24, 3, 5, 14, 4, 47, 23, 37, 36, 39, 38, 35, 34, 33, 43, 45, 15, 49, 19, 22, 30, 17, 2, 16, 20, 41, 6, 1, 29, 28, 21, 0, 48, 31, 44, 18, 40, 7, 8, 9, 42, 32, 50, 10, 51, 12, 13, 46]  f(x) =  7850.70197482827 of 7544.3659...
# http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/bier127.tsp        BEST: x =  [14, 107, 19, 16, 20, 3, 21, 18, 71, 7, 22, 23, 8, 10, 113, 104, 6, 0, 15, 36, 35, 40, 13, 11, 30, 26, 25, 24, 28, 31, 27, 121, 32, 37, 38, 33, 42, 29, 41, 39, 34, 43, 44, 102, 53, 56, 120, 50, 1, 49, 12, 114, 9, 119, 99, 2, 89, 115, 59, 61, 60, 90, 57, 63, 112, 124, 88, 91, 98, 64, 65, 54, 51, 123, 55, 4, 46, 48, 117, 52, 47, 93, 45, 111, 110, 106, 126, 92, 94, 122, 96, 97, 100, 101, 82, 81, 125, 80, 83, 116, 77, 75, 74, 68, 69, 70, 67, 73, 72, 66, 58, 103, 109, 84, 85, 86, 87, 108, 95, 118, 62, 17, 76, 78, 79, 5, 105, 14]  f(x) =  129435.67577377794 of 118293.52...
if __name__ == '__main__':
    
    fileName = "berlin.txt"
    #fileName = "bier.txt"
    nodes = parse(fileName)
    A = parseBerlin(fileName, dist)
    plotRawNetwork(A)
    
    
    seed(1)
    
    # 0 <= alpha 
    # beta > 1
    # beta > alpha
    # alpha & beta > 1 - faster convergence
    colony = createColony(nodes, dist, antCount=40, alpha=0.9, beta=2.0, pheromoneEvaporationCoefficient=0.4, pheromoneConstant=1000.0, iterations=300)
    answer, dist, generations, allBestFitnesses, allAvgFitnesses  = colony.mainloop()
    print("BEST: x = ", answer, " f(x) = ", dist)
    
    # GRAFIC DE CONVERGENTA
    plt.ioff()
    best, = plt.plot(generations, allBestFitnesses, 'ro', label = 'best')
    mean, = plt.plot(generations, allAvgFitnesses, 'bo', label = 'mean')
    plt.legend([best, (best, mean)], ['Best', 'Mean'])
    plt.show()    
