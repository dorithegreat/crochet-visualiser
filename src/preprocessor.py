import nodes as nd
from enum import Enum


class Stitch:
    
    def __init__(self, type, previous=None, anchors=None):
        # type is either a SingularStitch or a tuple of ComplexStitch and a number
        self.type = type
        self.previous = previous
        self.anchors = anchors


# All the stitches that consist of one singular stitch and don't need to have a number specified
class SingularStitch(Enum):
    SC = 1
    DC = 2
    TR = 3
    DTR = 4
    HDC = 5
    SLIP = 6

class ComplexStitch(Enum):
    CH_SPACE = 1
    INCREASE = 2
    DECREASE = 3
    # TODO include popcorns etc.

class Preprocessor:
    def __init__(self):
        self.flattened = []
    
    def preprocess(self, tree : nd.All):
        # recursively process the tree
        # decide if the pattern is flat
        
        
        rounds = tree.rounds
        for round in rounds.rounds:
            self.process_round(round)
        
        # TODO determine if the pattern is flat
        
        return self.flattened
    
    
    def process_round(self, round : nd.Round):
        # global variable so that I don't have to pass it to all the functions
        self.current_expressions = []
        self.previous_round_index = 0
        for expression in round.expressions.expressions:
            self.process_expression(expression)

        self.flattened.append(self.current_expressions)
    
    def process_expression(self, expression):
        if type(expression) == nd.StitchGroup:
            self.process_stitch_group(expression)
        elif type(expression) == nd.CountsAs:
            self.process_stitch_group(expression.stitch)
            self.alias_last_stitch(expression.alias)
        elif type(expression) == nd.Loop:
            self.process_loop(expression)
        elif type(expression) == nd.Skip:
            self.skip_stitches(expression)

    def process_stitch_group(self, stitch_group : nd.StitchGroup):
        
        # Chains are the only stitch where the whole group needs to be treated as one for the purposes of visualization
        if stitch_group.stitch == nd.SimpleStitch.CH:
            # a chain space is not anchored in any stitch of the lower round
            new_stitch = Stitch((ComplexStitch.CH_SPACE, stitch_group.number))
            
            # if there are no stitches yet in the current round, but it is not the first round
            # the previous stitch is the last stitch of the previous round
            if self.flattened and not self.current_expressions:
                new_stitch.previous = self.flattened[-1][-1]
            # if this is not the first stitch of a round, the previous stitch is the last stitch of the current round
            elif self.current_expressions:
                new_stitch.previous = self.current_expressions[-1]
            # if it is the first stitch in the whole pattern, there is no previous stitch and the field is already correctly set to None
            
            #? a chain stitch has no anchor, so the setting the anchor is skipped
            
        
        # All stitch group variants other than chain mean multiple copies of identical stitch
        for i in range(stitch_group.number):
            new_stitch = None
            
            if type(stitch_group.stitch) == nd.SimpleStitch:
                new_stitch = Stitch(stitch_group.stitch)
                self.current_expressions.append(new_stitch)
            elif type(stitch_group.stitch) == nd.Increase:
                pass
                #! ???
                
            # if this is the first stitch of a round, but not the first in the whole project
            if not self.current_expressions: # current_expressions is empty
                if self.flattened: # flattened is not empty
                    new_stitch.previous = self.flattened[-1][-1]
            else:
                # the previous stitch is just the last on a list of expressions so far
                new_stitch.previous = self.current_expressions[-1]
                    
            # TODO set anchors
        
    
    def process_loop(self, loop : nd.Loop):
        if loop.number is not None:
            for i in range(loop.number):
                for expression in loop.expressions:
                    # process_expression automatically adds the processed stitch to the list
                    # it doesn't return anything
                    self.process_expression(expression)
        
        
        # TODO implement AROUND loops
    
    def skip_stitches(self, skip : nd.Skip):
        if skip.stitch == nd.SimpleStitch.STITCH:
            self.previous_round_index += skip.number
            return # early return tu cut down on indentation
        
        counter = 0
        while counter < skip.number:
            while not self.flattened[-1][self.previous_round_index].countsAs(skip.stitch):
                self.previous_round_index += 1 # annoyingly no ++ in python
            counter += 1
    
    
    def alias_last_stitch(self, alias : nd.Alias):
        pass