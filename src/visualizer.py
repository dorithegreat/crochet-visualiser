import drawsvg as draw
import math
from draw_utilities import draw_chain, draw_base_chain, draw_starting_chain, angle_from_origin, draw_cluster_lines
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
            if skipped >= len(rounds):
                break


        # ugly and un-pythonic but faster than array slices (because slices have to copy the array)
        for i in range(skipped, len(rounds)):
            self.visualize_round(rounds[i], rounds[i-1])
        
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
        self.double_crochet.append(draw.Line(0, 0, 0, -50, stroke_width = 2, stroke='black'))
        self.double_crochet.append(draw.Line(-10, -50, 10, -50, stroke_width = 2, stroke='black'))
        self.double_crochet.append(draw.Line(-7, -35, 7, -29, stroke_width = 2, stroke='black'))

        self.half_double_crochet = draw.Group()
        self.half_double_crochet.append(draw.Line(0,0,0,-30, stroke_width = 2, stroke='black'))
        self.half_double_crochet.append(draw.Line(-10, -30, 10, -30, stroke_width = 2, stroke='black'))


    def visualize_round(self, round, previous_round):
        # draw starting chain
        if type(round[0].type) is not tuple:
            raise Exception("what sort of weird round does not start with a chain?")
        draw_starting_chain(self.drawing,round[0].type[1] ,round[0].previous.top_position)


        # for stitch in previous round draw all dependents 
        for stitch in previous_round:
            self.draw_dependent(stitch, previous_round)

        # draw chains between already drawn stitches
        for i in range(1, len(round)):
            # not checking for out of bounds because a round can't end with a chain
            if type(round[i].type) == tuple and round[i].type[0] == ComplexStitch.CH_SPACE:
                if not type(round[i + 1].type) == tuple or (type(round[i + 1].type) == tuple and not round[i+1].type[0] == ComplexStitch.CH_SPACE):
                    if round[i + 1].type == SingularStitch.SLIP and not round[i + 1].anchors[0] == round[i]:
                        draw_chain(self.drawing, round[i].previous.top_position, round[i + 1].anchors[0].top_position, 30 * round[i].type[1] + 10, round[i].type[1])
                        self.drawing.append(draw.Ellipse(round[i+1].anchors[0].top_position[0], round[i + 1].anchors[0].top_position[0], 6, 3, fill='black', stroke='black'))

                    if round[i + 1].top_position is not None and round[i].previous.top_position is not None:
                        draw_chain(self.drawing, round[i].previous.top_position, round[i + 1].top_position, 30 * round[i].type[1] + 10, round[i].type[1])
        

        # draw all other stitches that have an anchor in the same round
        # draw weird edge cases
        
        # TODO handle special cases
        pass

    # def split_round_into_sets(self, round):
    #     anchored = []
    #     simple_chains = []
    #     special_cases = []
        
    #     for stitch in round:
    #         if hasattr(stitch, 'chain_destination_number'):
    #             special_cases.append(stitch)
    #         elif type(stitch.type) == SingularStitch:
    #             # if the destination is a chain space, it needs to be drawn differently
    #             if type(stitch.anchors[0].type) is tuple and stitch.anchors[0].type[0] == ComplexStitch.CH_SPACE:
    #                 special_cases.append(stitch)
    #             else:
    #                 anchored.append(stitch)
    #         elif stitch.type[0] == ComplexStitch.CH_SPACE:
    #             simple_chains.append(stitch)
    #         else:
    #             anchored.append(stitch)
        
    #     return (anchored, simple_chains, special_cases)
    

    def draw_dependent(self, stitch : Stitch, round):
        if type(stitch.type) == tuple and stitch.type[0] == ComplexStitch.CH_SPACE:
            if stitch == round[0]:
                pass
            else:
                # TODO implement stitches into chains
                # if previous stitch is a chain, put it into the center, otherwise align to right
                return # earl return to cut down on indentation
        
        if len(stitch.dependent) == 1:
            if stitch.dependent[0] in round:
                pass
            else:
                self.draw_stitch(stitch.dependent[0], stitch.top_position, angle_from_origin(stitch.top_position), round)
        else:
            n = 0
            for s in stitch.dependent:
                if s not in round:
                    n += 1

            base_angle = math.degrees(math.atan2(stitch.top_position[1], stitch.top_position[0]))
            skipped = 0
            for i in range(len(stitch.dependent)):
                if stitch.dependent[i] not in round:
                    angle = base_angle + ((n - 1) / 2) * 35 - (i - skipped) * 35
                    self.draw_stitch(stitch.dependent[i], stitch.top_position, angle, round)
                else:
                    skipped += 1

    def draw_stitch(self, stitch, position, angle, round):
        if stitch in round:
            return


        if stitch.type == SingularStitch.SLIP:
            return
        #     next_angle = angle_from_origin(stitch.anchors[0].top_position)
        #     prev_angle = angle_from_origin(stitch.previous.top_position)
        #     angle = (next_angle + prev_angle) / 2
        #     self.drawing.append(draw.Ellipse(6, 3, position[0], position[1]))
        #     return

        if type(stitch.type) == tuple and stitch.type[0] == ComplexStitch.CLUSTER:
            height = self.get_group_height(self.get_group(stitch.type[2]))
            px, py = position
            current_radius = math.hypot(px, py)
            angle = (math.atan2(py, px))
            x = (current_radius + height) * math.cos(angle)
            y = (current_radius + height) * math.sin(angle)

            if stitch.type[2] == SingularStitch.HDC:
                strikes = 0
            elif stitch.type[2] == SingularStitch.DC:
                strikes = 1
            elif stitch.type[2] == SingularStitch.TR : 
                strikes = 2
            elif stitch.type[2] == SingularStitch.DTR:
                strikes = 3
            else: 
                raise Exception("Can't make a cluster of this stitch type")
            
            draw_cluster_lines(self.drawing, position, (x, y), stitch.type[1], strikes, 0.15 * stitch.type[1])
            stitch.top_position = (x, y)
            return

        self.drawing.append(draw.Use(self.get_group(stitch.type), 0, 0, transform = f'translate({position[0]}, {position[1]}) rotate({angle + 90}, 0, 0)'))
        
        # current_radius = math.hypot(position[0], position[1])
        # x = (current_radius + self.get_group_height(self.get_group(stitch.type))) * math.cos(angle)
        # y = (current_radius + self.get_group_height(self.get_group(stitch.type))) * math.sin(angle)
        # stitch.top_position = (x, y)
        x = position[0] + self.get_group_height(self.get_group(stitch.type)) * math.cos(math.radians(angle))
        y = position[1] + self.get_group_height(self.get_group(stitch.type)) * math.sin(math.radians(angle))
        stitch.top_position = (x, y)

    def draw_chain(self, chain):
        pass

    def draw_basic_round(self, round, previous_round, radius):
        # we've already verified these are valid and alternating, because this function is only called right after making that validation
        stitch_type1 =  round[1].type
        stitch_type2 = round[2].type

        group1 = self.get_group(stitch_type1)
        group2 = self.get_group(stitch_type2)

        base  = previous_round[-1].top_position
        draw_starting_chain(self.drawing, round[0].type[1], base)
        n = len(round) - 1

        ax, ay = base        
        start_angle = math.degrees(math.atan2(ay, ax))
        step = 360.0 / n
        
        for i in range(n):
            angle_deg = start_angle - i * step
            angle_rad = math.radians(angle_deg)
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            if i != 0:
                # the for loop goes clockwise but the stitches are numbered counterclockwise
                # 0 -> 15
                # 1 -> 14
                # 14 -> 1
                # 15 is skipped (because it's n-1)
                round[i].bottom_position = (x, y)   

                if i % 2 == 0:
                    group = group1
                else:
                    group = group2

                rotation = angle_deg + 90
                self.drawing.append(draw.Use(
                    group, 0, 0,
                    transform=f"translate({x},{y}) rotate({rotation},0,0)"
                ))

                h = self.get_group_height(group)
                tx = (radius + h) * math.cos(angle_rad)
                ty = (radius + h) * math.sin(angle_rad)
                round[i].top_position = (tx, ty)
            
            else:
                max_h = max(self.get_group_height(group1), self.get_group_height(group2))
                gx = (radius + max_h) * math.cos(math.radians(start_angle))
                gy = (radius + max_h) * math.sin(math.radians(start_angle))

                round[0].top_position = (gx, gy)


    
        angle_rad = math.radians(start_angle + step * 0.5)
        # x and y were declared in a for loop, but can be accessed outside of it because python is idiotic
        x = (radius + max_h) * math.cos(angle_rad)
        y = (radius + max_h) * math.sin(angle_rad)
        self.drawing.append(draw.Ellipse(x, y, 6, 3, fill='black', stroke='black',transform=f'rotate({angle_rad},{x},{y})'))
        round[-1].top_position = (x, y)

    def get_group(self, stitch_type):
        if stitch_type == SingularStitch.SC:
            return self.single_crochet
        elif stitch_type == SingularStitch.HDC:
            return self.half_double_crochet
        elif stitch_type == SingularStitch.DC:
            return self.double_crochet
        else:
            raise Exception("Unsupported stitch type")
    
    def get_group_height(self, group):
        if group == self.single_crochet:
            return 25
        elif group == self.half_double_crochet:
            return 35
        elif group == self.double_crochet:
            return 45