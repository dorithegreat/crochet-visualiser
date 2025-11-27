import drawsvg as draw
from draw_chain import draw_chain
from preprocessor import Stitch, SingularStitch, ComplexStitch

# go through each round one by one
# split the round into 3 sets: fixed stitches, chain arcs and special cases
# find all the stitches that are anchored in place (simple stitches, decreases, etc) and draw them one by one
# draw them in line with the anchor
# draw chains between already drawn stitches
# TODO figure out what to do about ordinal destinations

# first 2 rounds will probably require special handling
# check if the first round is just a number of chains with a slip stitch to its beginning
# if the whole second row is just a number of the same stitches around the ring, I can reuse the code from the test file

class Visualizer:
    
    def visualize(self, rounds):
        self.initialize_drawing(rounds)
        
        for round in rounds:
            pass
        
        print("test")
        self.drawing.save_svg("output.svg")
    
    # this function takes rounds as parameter to calculate the size of canvas based on the amount of rounds
    def initialize_drawing(self, rounds):
        # TODO find a more accurate constant
        self.drawing = draw.Drawing(30 * len(rounds), 30 * len(rounds), origin='center')
    
    def visualize_round(self, round):
        anchored, simple_chains, special_cases = self.split_round_into_sets(round)
        
        for stitch in anchored:
            self.draw_stitch(stitch)
        for chain in simple_chains:
            self.draw_chain()
        
        # TODO handle special cases

    def split_round_into_sets(self, round):
        anchored = []
        simple_chains = []
        special_cases = []
        
        for stitch in round:
            if hasattr(stitch, 'chain_destination_number'):
                special_cases.append(stitch)
            elif type(stitch.type) == SingularStitch:
                anchored.append(stitch)
            elif stitch.type[0] == ComplexStitch.CH_SPACE:
                simple_chains.append(stitch)
            else:
                anchored.append(stitch)
        
        return (anchored, simple_chains, special_cases)
    
    def draw_stitch():
        pass
    
    def draw_chain():
        pass