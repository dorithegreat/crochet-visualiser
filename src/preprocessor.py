import nodes as nd

class Stitch:
    def __init__(self, type):
        self.type = type
    
    def __init__(self, previous, anchors):
        self.previous = previous
        self.anchors = anchors
        
    

class Preprocessor:
    def __init__(self):
        self.flattened = []
    
    def preprocess(self, tree : nd.All):
        # recursively process the tree
        # decide if the pattern is flat
        
        
        rounds = tree.rounds
        for round in rounds.rounds:
            self.process_round(round)
    
    
    def process_round(self, round : nd.Round):
        self.current_expressions = []
    
    
    def process_expression(self, expression):
        pass