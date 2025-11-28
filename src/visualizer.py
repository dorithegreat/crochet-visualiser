import drawsvg as draw
import math
from draw_utilities import draw_chain, draw_base_chain, draw_starting_chain, angle_from_origin
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

        # how many of the first rounds are handled by special rules and can be skipped in the following for loop
        skipped = 0

        # this could be one long if but it would be utterly illegible
        if len(rounds[0]) == 2:
            if type(rounds[0][0].type) is tuple and rounds[0][0].type[0] == ComplexStitch.CH_SPACE:
                if type(rounds[0][1].type) == SingularStitch and rounds[0][1].type == SingularStitch.SLIP:
                    if len(rounds[0][1].anchors) == 1 and rounds[0][1].anchors[0] == rounds[0][1].previous:
                        # draws the ring of chains and the slip stitch
                        rounds[0][1].top_position = draw_base_chain(self.drawing, rounds[0][0].type[1])
                        # print(rounds[0][1].bottom_position)
                        skipped += 1
        else:
            # TODO figure out if there are any other common starts that I should support
            raise Exception("This is not a standard circular pattern and is not supported")
        

        while self.is_basic_round(rounds[skipped]):
            self.draw_basic_round(rounds[skipped], rounds[skipped - 1], 60)
            skipped += 1 # damn why can't python just have ++


        # ugly and un-pythonic but faster than array slices (because slices have to copy the array)
        for i in range(1, len(rounds)):
            self.visualize_round(rounds[i])
        
        print("test")
        self.drawing.save_svg("output.svg")
    

    def is_basic_round(self, round):
        # if it doesn't start with a chain
        # I can't think of a real life scenario where this would fail
        if type(round[0].type) != tuple or round[0].type[0] != ComplexStitch.CH_SPACE:
            return False
        
        # either not a circular pattern, or the round ends with something non-standard like a dc in the starting dc
        if round[-1].type != SingularStitch.SLIP or round[-1].anchors[0] != round[0]:
            return False

        # the round can either be all one stich type, or two alternating stitch types
        stich_type1 = round[1].type
        stich_type2 = round[2].type
        # if it's not a basic stitch, it's not a basic round
        # I'm quite curious though what kind of weird pattern would start with immediate clusters or something into the starting chain
        # type 1 may be a chain if the round starts with two separately defined chain spaces
        # which would be very awkward phrasing normally, but is the only way to make only part of the chain count as first dc within this grammar
        if type(stich_type1) != SingularStitch or (type(stich_type1) == ComplexStitch and stich_type1[0] != ComplexStitch.CH_SPACE):
            return False
        if type(stich_type2) != SingularStitch or (type(stich_type2) == ComplexStitch and stich_type2[0] != ComplexStitch.CH_SPACE):
            return False 

        for i in range(1, len(round) - 2):
            if i % 2 == 1 and round[i].type != stich_type1:
                return False
            if i % 2 == 0 and round[i].type != stich_type2:
                return False
        
        # if it manages to pass through all of the statements above, it's a basic round
        return True

    # this function takes rounds as parameter to calculate the size of canvas based on the amount of rounds
    def initialize_drawing(self, rounds):

        #* --- Initializing canvas ---
        # TODO find a more accurate constant
        side = 100 * (len(rounds) + 2)
        self.drawing = draw.Drawing(side, side, origin='center')
        self.drawing.append(draw.Rectangle(0 - side / 2, 0 -side / 2, side, side, fill='white'))

        #* --- Initializing drawsvg groups ---
        self.single_crochet = draw.Group()
        self.single_crochet.append(draw.Line(-10, -20, 10, 0, stroke_width = 2, stroke = 'black'))
        self.single_crochet.append(draw.Line(-10, 0, 10, -20, stroke_width = 2, stroke = 'black'))

        self.double_crochet = draw.Group()
        self.double_crochet.append(draw.Line(0, 0, 0, -40, stroke_width = 2, stroke='black'))
        self.double_crochet.append(draw.Line(-10, -40, 10, -40, stroke_width = 2, stroke='black'))
        self.double_crochet.append(draw.Line(-7, -25, 7, -20, stroke_width = 2, stroke='black'))

        self.half_double_crochet = draw.Group()
        self.half_double_crochet.append(draw.Line(0,0,0,-30, stroke_width = 2, stroke='black'))
        self.half_double_crochet.append(draw.Line(-10, -30, 10, -30, stroke_width = 2, stroke='black'))


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
                # if the destination is a chain space, it needs to be drawn differently
                if type(stitch.anchors[0].type) is tuple and stitch.anchors[0].type[0] == ComplexStitch.CH_SPACE:
                    special_cases.append(stitch)
                else:
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

    def draw_basic_round(self, round, previous_round, radius):
        # we've already verified these are valid and alternating, because this function is only called right after making that validation
        stitch_type1 =  round[1]
        stitch_type2 = round[2]

        base  = previous_round[-1].top_position
        draw_starting_chain(self.drawing, round[0].type[1], base)
        n = len(round) - 1

        ax, ay = base
        # necessary conversion because drawsvg uses coordinates where negative y is up and I forgot about it when writing code
        ay = -ay
        # dist = math.hypot(ax, ay)
        # if not math.isclose(dist, radius, rel_tol=1e-9, abs_tol=1e-9):
        #     raise ValueError("anchor_point must lie exactly on the circle of the given radius.")
        start_angle = angle_from_origin((ay, ax))
        step = 2 * math.pi / n
        
        for i in range(n):
            angle = start_angle + i * step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            if i != n - 1:
                self.drawing.append(draw.Use(self.get_group(stitch_type1), 0, 0, transform= f'translate({x}, {y}) rotate({angle_from_origin((x, y)) + 90}, 0, 0)'))
                

    def get_group(self, stitch_type):
        # TODO placeholder
        return self.half_double_crochet