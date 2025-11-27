import nodes as nd
from enum import Enum


class Stitch:
    
    def __init__(self, type, previous=None):
        # type is either a SingularStitch or a tuple of ComplexStitch and a number
        self.type = type
        self.previous = previous

    def counts_as(stitch_type):
        pass


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
    CLUSTER = 4
    POPCORN = 5
    BOBBLE = 6

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
            self.current_expressions.append(new_stitch)
            return
        
        # All stitch group variants other than chain mean multiple copies of identical stitch
        for i in range(stitch_group.number):
            new_stitch = None

            if type(stitch_group.stitch) == nd.SimpleStitch:
                new_stitch = Stitch(self.translate_enum(stitch_group.stitch))
            elif type(stitch_group.stitch) == nd.Increase:
                new_stitch = Stitch((ComplexStitch.INCREASE, stitch_group.number))
            elif type(stitch_group.stitch) == nd.Decrease:
                new_stitch = Stitch((ComplexStitch.DECREASE, stitch_group.number))
            elif type(stitch_group.stitch) == nd.Cluster:
                new_stitch = Stitch((ComplexStitch.CLUSTER, stitch_group.number))
                
            # if this is the first stitch of a round, but not the first in the whole project
            if not self.current_expressions: # current_expressions is empty
                if self.flattened: # flattened is not empty
                    new_stitch.previous = self.flattened[-1][-1]
            else:
                # the previous stitch is just the last on a list of expressions so far
                new_stitch.previous = self.current_expressions[-1]
            
            # setting anchors
            if type(new_stitch == SingularStitch):
                repeats = 1
            elif new_stitch.type[0] == ComplexStitch.DECREASE:
                repeats = new_stitch.type[1]
            else:
                repeats = new_stitch.type[1]
            
            # TODO rewrite it so that the whole stitch group can be anchored in the same stitch
            anchors = []
            for i in range(repeats):
                # TODO figure out a better way of dealing with Destination_Ordinal
                # maybe store data about location of each ellipsis of the chain
                if type(stitch_group.destination) == nd.Destination_Ordinal:
                    if self.current_expressions[-1].type[0] == ComplexStitch.CH_SPACE:
                        anchors.append(self.current_expressions[-1])
                        new_stitch.chain_destination_number = stitch_group.destination.number
                
                elif stitch_group.destination is None:
                    # if this is a chain stitch, it indeed has no anchor
                    # the if is only included for readability, and does nothing
                    if not (type(new_stitch.type) == SingularStitch) and (new_stitch.type[0] == ComplexStitch.CH_SPACE):
                        pass
                    elif len(self.flattened) == 0:
                        raise Exception("There is no default anchor for this stitch because there is no previous round")
                    else:
                        anchors.append(self.flattened[-1][self.previous_round_index])
                        self.previous_round_index += 1
                
                elif stitch_group.destination.type == nd.DestinationType.NEXT:
                    # skipping to the next stitch of a specific type
                    while self.previous_round_index < len(self.flattened[-1]) and not self.flattened[-1][self.previous_round_index].counts_as(stitch_group.destination.type):
                        self.previous_round_index += 1
                            
                    # TODO implement other destination types
                
                # if this is the first round
                if not self.flattened:
                    # TODO figure this out
                    pass
                
                elif self.previous_round_index < len(self.flattened[-1]):
                    anchors.append(self.flattened[-1][self.previous_round_index])
            
            new_stitch.anchors = anchors
            self.current_expressions.append(new_stitch)

    def process_loop(self, loop : nd.Loop):
        if loop.number is not None:
            for i in range(loop.number):
                for expression in loop.expressions.expressions:
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
            while not self.flattened[-1][self.previous_round_index].counts_as(skip.stitch):
                self.previous_round_index += 1 # annoyingly no ++ in python
            counter += 1
    
    
    def alias_last_stitch(self, alias : nd.Alias):
        pass
    
    def translate_enum(self, stitch : nd.SimpleStitch):
        if stitch == nd.SimpleStitch.CH:
            raise Exception("Something went wrong: chain is not a singular stitch")
        elif stitch == nd.SimpleStitch.SC:
            return SingularStitch.SC
        elif stitch == nd.SimpleStitch.DC:
            return SingularStitch.DC
        elif stitch == nd.SimpleStitch.HDC:
            return SingularStitch.HDC
        elif stitch == nd.SimpleStitch.TR:
            return SingularStitch.TR
        elif stitch == nd.SimpleStitch.SLIP:
            return SingularStitch.SLIP
        elif stitch == nd.SimpleStitch.DTR:
            return SingularStitch.DTR
        elif stitch == nd.SimpleStitch.STITCH:
            raise Exception("Generic stitch cannot be translated to singular stitch")
        else:
            raise Exception("Unknown stitch type detected")