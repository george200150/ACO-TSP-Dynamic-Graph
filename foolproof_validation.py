'''
Created on 26 mar. 2020

@author: George
'''


class FoolProof:
    def __init__(self, nodes, distance_callback, start, ant_count, alpha, beta,  pheromone_evaporation_coefficient, pheromone_constant, iterations):
        self.nodes=nodes
        self.distance_callback=distance_callback
        self.start=start
        self.ant_count=ant_count
        self.alpha=alpha
        self.beta=beta
        self.pheromone_evaporation_coefficient=pheromone_evaporation_coefficient
        self.pheromone_constant=pheromone_constant
        self.iterations=iterations
        
        try:
            self.id_to_key, self.id_to_values = self.init_nodes(nodes) # this might also throw
            assert True
        except Exception:
            assert False
    
    
    def init_nodes(self, nodes):
        """
        Copy of _init_nodes from ant_colony - used here for validating data.
        Validation can be omitted anytime we know everything runs smoothly and input is safe.
        This is useful for validating new data file formats and test updated methods compatibility.
        """
        id_to_key = dict()
        id_to_values = dict()
        
        ID = 0
        for key in sorted(nodes.keys()):
            id_to_key[ID] = key
            id_to_values[ID] = nodes[key]
            ID += 1
            
        return id_to_key, id_to_values
    
    
    def validate(self):
        #====================NODES====================
        assert type(self.nodes) is dict
        assert len(self.nodes) >= 1
        
        #====================DISTANCE_CALLBACK====================
        assert callable(self.distance_callback) == True
        
        #====================START====================
        if self.start != None:
            start = None
            #init start to internal id of node id passed
            for key, value in self.id_to_key.items():
                if value == self.start:
                    start = key
            
            assert start != None #if we didn't find a key in the nodes passed in
        
        #====================ANT_COUNT====================
        assert type(self.ant_count) is int
        assert self.ant_count >= 1
        
        #====================ALPHA====================
        assert type(self.alpha) is int or type(self.alpha) is float
        assert self.alpha >= 0
        
        #====================BETA====================
        assert type(self.beta) is int or type(self.beta) is float
        assert self.beta >= 0
        
        #====================PHEROMONE_EVAPORATION_COEFFICIENT====================
        assert type(self.pheromone_evaporation_coefficient) is int or type(self.pheromone_evaporation_coefficient) is float
        
        #====================PHEROMONE_CONSTANT====================
        assert type(self.pheromone_constant) is int or type(self.pheromone_constant) is float
        
        #====================ITERATIONS====================
        assert type(self.iterations) is int
        assert self.iterations >= 0
        
        return True




