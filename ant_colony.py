'''
Created on 26 mar. 2020

@author: George
'''

from threading import Thread
from foolproof_validation import FoolProof
import random
from random import randint

'''
Am folosit formatul de input al nodurilor din Berlin.
'''
class AntColony:
    class ant(Thread):
        def __init__(self, initialLocation, possibleLocations, pheromoneMatrix, distanceCallback, alpha, beta, isFirstPass=False):
            """
            initialized an ant, to traverse the map
            @param initialLocation: marks where in the MAP that the ant starts
            @param possibleLocations: a LIST of possible nodes the ant can go to
            @param pheromoneMatrix: MAP of pheromone values for each traversal between each node
            @param distanceCallback: is a FUNCTION to calculate the distance between two nodes
            @param alpha: a FLOAT parameter from the ACO algorithm to control the influence of the amount of pheromone when making a choice in _pickPath()
            @param beta: a FLOAT parameter from ACO that controls the influence of the distance to the next node in _pickPath()
            @param isFirstPass: BOOLEAN flag to indicate if this is a first pass on a map, then do some steps differently, noted in methods below
            
            @param route: a LIST that is updated with the labels of the nodes that the ant has traversed
            @param pheromone_trail: a LIST of pheromone amounts deposited along the ants trail, maps to each traversal in route
            @param distanceTraveled: total distance tranveled along the steps in route as a FLOAT
            @param location: marks where the ant currently is
            @param isTourComplete: BOOLEAN flag to indicate the ant has completed its traversal (used by getRoute() and getDistanceTravelled())
            """
            Thread.__init__(self)
            
            self.initialLocation = initialLocation
            self.possibleLocations = list(possibleLocations)            
            self.route = []
            self.distanceTraveled = 0.0
            self.location = initialLocation
            self.pheromoneMatrix = pheromoneMatrix
            self.distanceCallback = distanceCallback
            self.alpha = alpha
            self.beta = beta
            self.isFirstPass = isFirstPass
            
            #append start location to the route
            self._updateRoute(initialLocation)
            
            self.isTourComplete = False
        
        
        def run(self):
            """
            Run till all the nodes have been visited.
            The ant picks a path, then traverses the edge by updating its route and distance travelled.
            Does pheromone updates and checks for optimal solutions
            @return: the ants route and its distance for further usage
            """
            while self.possibleLocations:
                Next = self._pickPath()
                self._traverse(self.location, Next)
                
            self.isTourComplete = True
        
        
        def _pickPath(self):
            """
            source: https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms#Edge_selection
            implements the path selection algorithm of ACO
            calculate the attractiveness of each possible transition from the current location, then randomly choose a next path, based on its attractiveness
            """
            #on the first pass (no pheromones), then we can just choice() to find the next one
            if self.isFirstPass:
                return random.choice(self.possibleLocations)
            
            attractiveness = dict()
            totalSum = 0.0
            #for each possible location, find its attractiveness ((pheromone amount)*1/distance [tau*eta, from the algortihm])
            #sum all attrativeness amounts for calculating probability of each route in the next step
            for nextPossibleLocation in self.possibleLocations:
                
                pheromoneAmount = float(self.pheromoneMatrix[self.location][nextPossibleLocation])
                distance = float(self.distanceCallback(self.location, nextPossibleLocation))
                
                #[tau il] ^ alpha * [eta il] ^ beta
                attractiveness[nextPossibleLocation] = pheromoneAmount**self.alpha * (1/distance)**self.beta
                totalSum += attractiveness[nextPossibleLocation]
            
            #WARNING!
            #It is possible to have small values for pheromone amount / distance ~= 0.0
            #handle when it happens (AVOID ZERO DIVISION EXCEPTION)
            if totalSum == 0.0:
                #increment all zeros, such that they are the smallest non-zero values supported by the system
                #source: http://stackoverflow.com/a/10426033/5343977
                def next_up(x):
                    import math
                    import struct
                    # NaNs and positive infinity map to themselves.
                    if math.isnan(x) or (math.isinf(x) and x > 0):
                        return x

                    # 0.0 and -0.0 both map to the smallest +ve float.
                    if x == 0.0:
                        x = 0.0

                    n = struct.unpack('<q', struct.pack('<d', x))[0]
                    
                    if n >= 0:
                        n += 1
                    else:
                        n -= 1
                    return struct.unpack('<d', struct.pack('<q', n))[0]
                    
                for key in attractiveness:
                    attractiveness[key] = next_up(attractiveness[key])
                totalSum = next_up(totalSum)
            
            #cumulative probability behavior - randomly choose the next path
            toss = random.random()
                    
            cummulative = 0
            for nextPossibleLocation in attractiveness:
                weight = (attractiveness[nextPossibleLocation] / totalSum)
                if toss <= weight + cummulative:
                    return nextPossibleLocation
                cummulative += weight
        
        
        def _traverse(self, start, end):
            """
            Show the new traversal, then record new distance traveled, then update to new location (called from run())
            """
            self._updateRoute(end)
            self._updateDistanceTraveled(start, end)
            self.location = end
        
        
        def _updateRoute(self, new):
            """
            Add a new node to self.route and remove it form self.possibleLocations (called from _traverse() & __init__())
            """
            self.route.append(new)
            self.possibleLocations.remove(new)
            #MODIFIED TO CLOSE THE CYCLE
            if len(self.possibleLocations) == 0:
                self._updateDistanceTraveled(self.route[-1], self.route[0])
                self.route.append(self.route[0])
            
        
        def _updateDistanceTraveled(self, start, end):
            """
            Use self.distanceCallback to update self.distanceTraveled
            """
            self.distanceTraveled += float(self.distanceCallback(start, end))
        
        
        def getRoute(self):
            if self.isTourComplete:
                return self.route
            return None
        
        
        def getDistanceTravelled(self):
            if self.isTourComplete:
                return self.distanceTraveled
            return None
    
    #----------------------------------------------- end of ant subclass -----------------------------------------------
    
    def __init__(self, nodes, distanceCallback, start=None, antCount=50, alpha=0.5, beta=1.2, pheromoneEvaporationCoefficient=0.4, pheromoneConstant=1000.0, iterations=80):
        """
        initializes an ant colony (houses a number of worker ants that will traverse a map to find an optimal route as per ACO [Ant Colony Optimization])
        source: https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms
        @param nodes: is assumed to be a dict() mapping node id-s to values that are understandable by distanceCallback
        @param distanceCallback: is assumed to take a pair of coordinates and return the distance between them populated into distanceMatrix on each call to get_distance()
        @param start: if set, then is assumed to be the node where all ants start their traversal if unset, then assumed to be the first key of nodes when sorted()
        @param distanceMatrix: holds values of distances calculated between nodes populated on demand by _getDistance()
        @param pheromoneMatrix: holds final values of pheromones (used by ants to determine traversals) pheromone dissipation happens to these values first, before adding pheromone values from the ants during their traversal (in antUpdatedpheromoneMatrix)
        @param antUpdatedpheromoneMatrix: a matrix to hold the pheromone values that the ants lay down not used to dissipate, values from here are added to pheromoneMatrix after dissipation step (reset for each traversal)
        @param alpha: a parameter from the ACO algorithm to control the influence of the amount of pheromone when an ant makes a choice
        @param beta: a parameters from ACO that controls the influence of the distance to the next node in ant choice making
        @param pheromoneConstant: a parameter used in depositing pheromones on the map (Q in ACO algorithm) (used by _updatePheromoneMatrix())
        @param pheromoneEvaporationCoefficient: a parameter used in removing pheromone values from the pheromoneMatrix (rho in ACO algorithm) (used by _updatePheromoneMatrix())
        @param ants: holds worker ants - they traverse the map as per ACO ( notable properties: total distance traveled; route)
        @param isFirstPass: flags a first pass for the ants, which triggers unique behavior
        @param iterations: how many iterations to let the ants traverse the map
        @param shortestDistance: the shortest distance seen from an ant traversal
        @param shortets_path_seen: the shortest path seen from a traversal (shortestDistance is the distance along this path)
        """
        # these two lines can be omitted anytime
        #fp = FoolProof(nodes, distanceCallback, start, antCount, alpha, beta,  pheromoneEvaporationCoefficient, pheromoneConstant, iterations) # constructor params + other objects for validation
        #fp.validate() # !!! this will raise assertion errors if data types or values are faulty
        
        #create internal mapping and mapping for return to caller
        self.mapIDToKey, self.nodes = self._initNodes(nodes)
        #create matrix to hold distance calculations between nodes
        self.distanceMatrix = self._initMatrix(len(nodes))
        #create matrix for master pheromone map, that records pheromone amounts along routes
        self.pheromoneMatrix = self._initMatrix(len(nodes))
        #create a matrix for ants to add their pheromones to, before adding those to pheromoneMatrix during the updatePheromoneMatrix step
        self.antUpdatedpheromoneMatrix = self._initMatrix(len(nodes))
        
        self.distanceCallback = distanceCallback
        
        if start is None:
            self.start = 0 #init it with first node
        
        self.antCount = antCount
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.pheromoneEvaporationCoefficient = float(pheromoneEvaporationCoefficient) # just float it
        self.pheromoneConstant = float(pheromoneConstant) # make it float
        self.iterations = iterations
        
        #====================other internal variable init====================
        self.isFirstPass = True
        self.ants = self._initAnts(self.start) # call in inner class
        self.shortestDistance = None
        self.shortestPathFoundYet = None
    
    
    def _getDistance(self, start, end):
        """
        Uses the distanceCallback to return the distance between nodes
        If a distance has not been calculated before, then it is populated in distanceMatrix and returned
        If a distance has been called before, then its value is returned from distanceMatrix
        """
        if not self.distanceMatrix[start][end]:
            distance = self.distanceCallback(self.nodes[start], self.nodes[end])
            
            self.distanceMatrix[start][end] = float(distance)
            return distance
        return self.distanceMatrix[start][end]
    
    
    def _initNodes(self, nodes):
        """
        Create a mapping of internal id numbers (0..n) to the keys in the nodes passed 
        Create a mapping of the id's to the values of nodes
        We use mapIDToKey to return the route in the node names the caller expects in mainloop()
        """
        mapIDToKey = dict()
        mapIDToValues = dict()
        
        ID = 0
        for key in sorted(nodes.keys()):
            mapIDToKey[ID] = key
            mapIDToValues[ID] = nodes[key]
            ID += 1
            
        return mapIDToKey, mapIDToValues
    
    
    def _initMatrix(self, size, value=0.0):
        """
        Create a matrix of NxN (where N = number of nodes in the graph = size)
        (used in both self.distanceMatrix and self.pheromoneMatrix, as they need the same initialization)
        """
        ret = []
        for _ in range(size): # foreach row
            ret.append([float(value) for _ in range(size)])
        return ret
    
    
    iterationToChangeMatrix = 0 # used for dynamic graphs
    cachedDistanceMatrixInfo = {} # DYNAMIC GRAPH
    
    def _initAnts(self, start):
        """
        On first pass: create a number of ant objects
        On subsequent passes: just call __init__ on each to reset them
        By default, all ants start at the first node, 0
        """
        self.iterationToChangeMatrix += 1 # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH
        if self.iterationToChangeMatrix % 5 == 0: # if 5 iterations have passed, modify distance matrix and pheromone matrix
            for _ in range(0,20):
                i = randint(0,len(self.nodes)-1)
                j = randint(0,len(self.nodes)-1)
                try:
                    self.cachedDistanceMatrixInfo[(i,j)] += 1 # save the edge that is going to be overwritten
                    self.cachedDistanceMatrixInfo[(i,j)] -= 1
                except KeyError:
                    self.cachedDistanceMatrixInfo[(i,j)] = self.distanceMatrix[i][j] 
                self.distanceMatrix[i][j] = 9999 # the edge is suddenly lost and we suppose that the cost is close to infinity 
                self.pheromoneMatrix[i][j] = 0 # no ants will ever walk here again
                pass
            pass # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH # DYNAMIC GRAPH
        #CHANGE IN ALGORITHM: all ants start from random nodes. not as set. start parameter becomes useless now
        
        #allocate new ants on the first pass
        if self.isFirstPass:
            #return [self.ant(start, self.nodes.keys(), self.pheromoneMatrix, self._getDistance,self.alpha, self.beta, isFirstPass=True) for _ in range(self.antCount)]
            return [self.ant(randint(0,len(self.nodes)-1), self.nodes.keys(), self.pheromoneMatrix, self._getDistance,self.alpha, self.beta, isFirstPass=True) for _ in range(self.antCount)]
        #else, just reset them to use on another pass
        for ant in self.ants:
            #ant.__init__(start, self.nodes.keys(), self.pheromoneMatrix, self._getDistance, self.alpha, self.beta)
            ant.__init__(randint(0,len(self.nodes)-1), self.nodes.keys(), self.pheromoneMatrix, self._getDistance, self.alpha, self.beta)
    
    
    def _updatePheromoneMatrix(self):
        """
        1. Update self.pheromoneMatrix by decaying values contained therein via the ACO algorithm
        2. Add the pheromone values from all ants from antUpdatedpheromoneMatrix
        (called by: mainloop() (after all ants have traveresed))
        """
        #always a square matrix
        for start in range(len(self.pheromoneMatrix)):
            for end in range(len(self.pheromoneMatrix)):
                #decay the pheromone value at this location
                #tau_il := (1-rho)*tau_il    (ACO)
                self.pheromoneMatrix[start][end] = (1-self.pheromoneEvaporationCoefficient)*self.pheromoneMatrix[start][end]
                
                #then add all contributions to this location for each ant that travered it(ACO)
                #tau_il := tau_il + delta tau_il_k
                #delta tau_il_k = Q / L_k
                self.pheromoneMatrix[start][end] += self.antUpdatedpheromoneMatrix[start][end]
    
    
    def _populateAntUpdatedpheromoneMatrix(self, ant):
        """
        Given an ant, populate antUpdatedpheromoneMatrix with pheromone values according to ACO policies along the ant's route
        (called from: mainloop() (before _updatePheromoneMatrix()))
        """
        route = ant.getRoute()
        for i in range(len(route)-1):
            #find the pheromone over the route the ant traversed
            currentPheromoneValue = float(self.antUpdatedpheromoneMatrix[route[i]][route[i+1]])
        
            #update the pheromone along that section of the route (ACO)
            #delta tau_il_k = Q / L_k
            newPheromoneValue = self.pheromoneConstant / ant.getDistanceTravelled()
            
            self.antUpdatedpheromoneMatrix[route[i]][route[i+1]] = currentPheromoneValue + newPheromoneValue
            self.antUpdatedpheromoneMatrix[route[i+1]][route[i]] = currentPheromoneValue + newPheromoneValue
    
    
    def testRoadExists(self,path): # DYNAMIC GRAPH
        if path is None:
            return True
        for i in range(0,len(path)-2):
            if self.distanceMatrix[i][i+1] == 9999:
                return False
        return True
        pass
    
    def mainloop(self):
        """
        Runs the worker ants, collects their returns and updates the pheromone map with pheromone values from workers
        (calls: _updatePheromoneMatrix(); ant.run())
        Runs the simulation self.iterations times
        """
        generations = [] # list of (list of ant paths)
        allBestFitnesses = []
        allAvgFitnesses = []
        
        for epochIndex in range(0,self.iterations):
            #start the multi-threaded ants, calls ant.run() in a new thread
            for ant in self.ants:
                ant.start() # calls the run @overriden method of Thread class, that ant inherits
            
            #wait until the ants are finished, before moving on to modifying shared resources
            for ant in self.ants:
                ant.join()
            
            if not self.testRoadExists(self.shortestPathFoundYet): # DYNAMIC GRAPH
                self.shortestPathFoundYet = None # DYNAMIC GRAPH
                self.shortestDistance = None # DYNAMIC GRAPH
            
            for ant in self.ants:
                #update antUpdatedpheromoneMatrix with this ant's contribution of pheromones deposited along its route
                self._populateAntUpdatedpheromoneMatrix(ant)
                
                #if we haven't seen any paths yet, then populate for comparisons later
                if not self.shortestDistance:
                    self.shortestDistance = ant.getDistanceTravelled()
                
                if not self.shortestPathFoundYet:
                    self.shortestPathFoundYet = ant.getRoute()
                    
                #if we see a shorter path, then save for return
                if ant.getDistanceTravelled() < self.shortestDistance:
                    self.shortestDistance = ant.getDistanceTravelled()
                    self.shortestPathFoundYet = ant.getRoute()
                
            #_DEBUG NOTES
            print("Best in generation {} : x = {} f(x) = {}".format(epochIndex,self.shortestPathFoundYet,self.shortestDistance))
            
            allBestFitnesses.append(self.shortestDistance)
            suma = 0
            for ant in self.ants:
                suma += ant.getDistanceTravelled()
            allAvgFitnesses.append(suma / len(self.ants))
            generations.append(epochIndex)
            
            #decay current pheromone values and add all pheromone values we saw during traversal (from antUpdatedpheromoneMatrix)
            self._updatePheromoneMatrix()
            
            #flag that we finished the first pass of the ants traversal
            if self.isFirstPass:
                self.isFirstPass = False
            
            #reset all ants to default for the next iteration
            self._initAnts(self.start)
            
            #reset antUpdatedpheromoneMatrix to record pheromones for ants on next pass
            self.antUpdatedpheromoneMatrix = self._initMatrix(len(self.nodes), value=0)
        
        #translate shortest path back into callers node id's
        ret = []
        for ID in self.shortestPathFoundYet:
            ret.append(self.mapIDToKey[ID])
        
        
        return ret, self.shortestDistance, generations, allBestFitnesses, allAvgFitnesses




