import drawsvg as draw
from draw_utilities import draw_chain, draw_base_chain
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

        # this could be one long if but it would be utterly illegible
        if len(rounds[0]) == 2:
            if type(rounds[0][0].type) is tuple and rounds[0][0].type[0] == ComplexStitch.CH_SPACE:
                if type(rounds[0][1].type) == SingularStitch and rounds[0][1].type == SingularStitch.SLIP:
                    if len(rounds[0][1].anchors) == 1 and rounds[0][1].anchors[0] == rounds[0][1].previous:
                        draw_base_chain(self.drawing, rounds[0][0].type[1])
        
        for round in rounds:
            self.visualize_round(round)
        
        print("test")
        self.drawing.save_svg("output.svg")
    
    # this function takes rounds as parameter to calculate the size of canvas based on the amount of rounds
    def initialize_drawing(self, rounds):
        # TODO find a more accurate constant
        side = 100 * len(rounds)
        self.drawing = draw.Drawing(side, side, origin='center')
        self.drawing.append(draw.Rectangle(0 - side / 2, 0 -side / 2, side, side, fill='white'))
    
    def visualize_round(self, round):
        anchored, simple_chains, special_cases = self.split_round_into_sets(round)
        
        for stitch in anchored:
            self.draw_stitch(stitch)
        for chain in simple_chains:
            self.draw_chain(chain)
        
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
    
    def draw_stitch(self, stitch):
        pass
    
    def draw_chain(self, chain):
        pass