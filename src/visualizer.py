import drawsvg as draw
import math
from draw_utilities import draw_chain, draw_base_chain, draw_starting_chain, angle_from_origin, draw_cluster_lines
from preprocessor import Stitch, SingularStitch, ComplexStitch
import nodes as nd

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
        self.color = 'black'

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
            raise Exception("This is not a standard circular pattern and is not supported")
        
        self.toggle_color()
        # if skipped >= len(rounds):
        #     self.drawing.save_svg("output.svg")
        #     return

        while self.is_basic_round(rounds[skipped]):
            if skipped == 1:
                radius = 60
            else:
                radius = radius + self.get_group_height(self.get_group(rounds[skipped - 1][1].type))
            self.draw_basic_round(rounds[skipped], rounds[skipped - 1], radius)
            self.toggle_color()
            skipped += 1 # damn why can't python just have ++
            if skipped >= len(rounds):
                break


        # ugly and un-pythonic but faster than array slices (because slices have to copy the array)
        for i in range(skipped, len(rounds)):
            self.visualize_round(rounds[i], rounds[i-1])
            self.toggle_color()
        
        print("test")
        self.drawing.save_svg("output.svg")
        # self.drawing.save_png("example_4.png")

    def toggle_color(self):
        if self.color == 'black':
            self.color = '#cf279c'
        else:
            self.color = 'black'
    

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
        side = 140 * (len(rounds) + 2)
        self.drawing = draw.Drawing(side, side, origin='center')
        self.drawing.append(draw.Rectangle(0 - side / 2, 0 -side / 2, side, side, fill='white'))

        #* --- Initializing drawsvg groups ---
        self.single_crochet = draw.Group(stroke_width = 2)
        self.single_crochet.append(draw.Line(0, 0, 0, -20))
        self.single_crochet.append(draw.Line(-10, -10, 10, -10))

        self.double_crochet = draw.Group(stroke_width = 2)
        self.double_crochet.append(draw.Line(0, 0, 0, -50))
        self.double_crochet.append(draw.Line(-10, -50, 10, -50))
        self.double_crochet.append(draw.Line(-7, -35, 7, -29))

        self.half_double_crochet = draw.Group(stroke_width = 2)
        self.half_double_crochet.append(draw.Line(0,0,0,-30))
        self.half_double_crochet.append(draw.Line(-10, -30, 10, -30))

        self.slip_stitch = draw.Group(stroke_width = 2, fill = 'black')
        self.slip_stitch.append(draw.Ellipse(0, -5, 6, 3))

        self.treble = draw.Group(stroke_width = 2)
        self.treble.append(draw.Line(0, 0, 0, -70))
        self.treble.append(draw.Line(-10, -70, 10, -70))
        self.treble.append(draw.Line(-7, -30, 7, -25))
        self.treble.append(draw.Line(-7, -40, 4, -35))


    def visualize_round(self, round, previous_round):
        # draw starting chain
        if type(round[0].type) is not tuple:
            if round[0].type == SingularStitch.SLIP:
                pass
            else:
                raise Exception("what sort of weird round does not start with a chain?")
        else:
            # TODO draw starting chains as regular stitches instead
            round[0].top_position = draw_starting_chain(self.drawing,round[0].type[1] ,round[0].previous.top_position, stroke=self.color)
            # radius = math.hypot(round[0].previous.top_position[0], round[0].previous.top_position[1])
            # angle = math.atan2(round[0].previous.top_position[1], round[0].previous.top_position[0])

            # x = (radius + self.get_group_height(self.get_group(round[0].alias))) * math.cos(angle)
            # y = (radius + self.get_group_height(self.get_group(round[0].alias))) * math.sin(angle)
            # round[0].top_position = (x, y)


        # for stitch in previous round draw all dependents 
        for stitch in previous_round:
            self.draw_dependent(stitch, previous_round)

        self.add_chains(round)

        # draw all other stitches that have an anchor in the same round
        for stitch in round:
            if hasattr(stitch, "anchors"):
                if stitch.top_position is None:
                    if stitch.anchors[0].top_position is not None:
                        angle = math.atan2(stitch.anchors[0].top_position[1], stitch.anchors[0].top_position[0])
                        self.draw_stitch(stitch, stitch.anchors[0].top_position, angle, round)
                        # stitch.top_position = (stitch.anchors[0].top_position)

        # draw chains between already drawn stitches
        self.add_chains(round)



        # draw weird edge cases
        
        # TODO handle special cases
        pass
    
    def add_chains(self, round):
        for i in range(1, len(round)):
            # not checking for out of bounds because a round can't end with a chain
            if type(round[i].type) == tuple and round[i].type[0] == ComplexStitch.CH_SPACE:
                if round[i].alias is not None:
                    round[i].top_position = draw_starting_chain(self.drawing,round[i].type[1], round[i].previous.top_position, stroke=self.color)
                    radius = math.hypot(round[i].previous.top_position[0], round[i].previous.top_position[1])
                    angle = math.atan2(round[i].previous.top_position[1], round[i].previous.top_position[0])
                    x = (radius + 10 * round[i].type[1]) * math.cos(angle)
                    y = (radius + 10 * round[i].type[1]) * math.sin(angle)
                    # round[i].top_position = (x, y)

                elif not type(round[i + 1].type) == tuple or (type(round[i + 1].type) == tuple and not round[i+1].type[0] == ComplexStitch.CH_SPACE):
                    # middle, right = self.split_chain_dependent(round[i])
                    middle = round[i].dependent # placeholder until I fix dependent splitting logic
                    if len(middle) % 2 == 1:
                        if len(round[i].dependent) % 2 == 0:
                            required_positions = 3 * len(round[i].dependent) + 1
                        else:
                            required_positions = 3 * len(round[i].dependent)
                    else:
                        if len(round[i].dependent) % 2 == 0:
                            required_positions = 3 * len(round[i].dependent)
                        else:
                            required_positions = 3 * len(round[i].dependent) + 1

                    if round[i + 1].type == SingularStitch.SLIP and not round[i + 1].anchors[0] == round[i]:
                        self.draw_stitch(round[i + 1], round[i + 1].anchors[0].top_position, 90, round)

                    if round[i + 1].top_position is not None and round[i].previous.top_position is not None:
                        # if round[i].type[1] == 1:
                        #     # Extract the two positions
                        #     x1, y1 = round[i + 1].top_position
                        #     x2, y2 = round[i].previous.top_position

                        #     # Midpoint between the two positions
                        #     xm = (x1 + x2) / 2
                        #     ym = (y1 + y2) / 2

                        #     n = len(round[i].dependent)
                        #     if n == 0:
                        #         pass
                        #     elif n == 1:
                        #         round[i].positions = [(xm, ym, math.degrees(math.atan2(ym, xm)))]
                        #     else:
                        #         round[i].positions = [
                        #             (
                        #                 x1 + (i/(n-1))*(x1 - x1),
                        #                 y1 + (i/(n-1))*(y2 - y1),
                        #                 math.degrees(math.atan2(y1 + (i/(n-1))*(y2 - y1), x1 + (i/(n-1))*(x1 - x1)))
                        #             )
                        #             for i in range(n)
                        #         ]

                        #     # Direction vector
                        #     dx = x2 - x1
                        #     dy = y2 - y1

                        #     # Angle of the line between the points
                        #     angle = math.degrees(math.atan2(dy, dx))

                        #     # Draw an ellipse centered at the midpoint, rotated along the axis
                        #     self.drawing.append(
                        #         draw.Ellipse(
                        #             xm, ym,                 # center of ellipse
                        #             8, 4,                   # radii
                        #             transform=f'rotate({angle}, {xm}, {ym})',
                        #             fill='white',
                        #             stroke='black',
                        #             stroke_width=1
                        #         )
                        #     )


                        # else:
                        self.drawing.save_svg("output.svg")
                        round[i].positions =  draw_chain(
                            self.drawing, 
                            round[i].previous.top_position, 
                            round[i + 1].top_position, 
                            30 * round[i].type[1] + 50 if round[i].type[1] > 1 else 25 * round[i].type[1] + 50, 
                            round[i].type[1], 
                            required_positions, 
                            stroke=self.color
                        )
        

    def draw_dependent(self, stitch : Stitch, round):
        if len(stitch.dependent) == 0:
            return

        if type(stitch.type) == tuple and stitch.type[0] == ComplexStitch.CH_SPACE:
            # if it counts as something other than a chain, then it is not processed as a chain
            if not hasattr(stitch, "positions"):
                pass
            else:
                middle, right, left = self.split_chain_dependent(stitch)

                # # draw the right stitches
                # for i in range(len(right)):
                #     angle = math.degrees(math.atan2(stitch.positions[i][1], stitch.positions[i][0]))
                #     self.draw_stitch(right[i], (stitch.positions[2 * i][0], stitch.positions[2 * i][1]), angle, round)

                # for i in range(len(left)):
                #     angle = math.degrees(math.atan2(stitch.positions[-i][1], stitch.positions[-i][0])) + 90
                #     self.draw_stitch(left[i], (stitch.positions[-i][0], stitch.positions[-i][1]), stitch.positions[-i][2], round)

                start_index = (len(stitch.positions) // 2 - len(stitch.dependent) // 2)
                end_index = (len(stitch.positions) // 2 + len(stitch.dependent) // 2)
                positions = stitch.positions[start_index: end_index + 1] if len(stitch.positions) > 1 else stitch.positions



                for i in range(len(stitch.dependent)):
                    if stitch.dependent[i] in round:
                        continue
                    self.draw_stitch(stitch.dependent[i], (positions[i][0], positions[i][1]), positions[i][2], round)

                return # early return to cut down on indentation
        
        if len(stitch.dependent) == 1:
            if stitch.dependent[0] in round:
                pass
            else:
                if len(stitch.top_position) == 3:
                    angle = stitch.top_position[2]
                else:
                    angle = angle_from_origin(stitch.top_position)
                self.draw_stitch(stitch.dependent[0], stitch.top_position, angle, round)
        else:
            n = 0
            for s in stitch.dependent:
                if s not in round:
                    n += 1

            base_angle = math.degrees(math.atan2(stitch.top_position[1], stitch.top_position[0]))
            skipped = 0
            for i in range(len(stitch.dependent)):
                if stitch.dependent[i] not in round:
                    if len(stitch.top_position) == 3:
                        angle = stitch.top_position[2]
                    else:
                        angle = base_angle + ((n - 1) / 2) * 35 - (i - skipped) * 35
                    self.draw_stitch(stitch.dependent[i], stitch.top_position, angle, round)
                else:
                    skipped += 1

    def draw_stitch(self, stitch, position, angle, round):

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
            
            draw_cluster_lines(self.drawing, position, (x, y), stitch.type[1], strikes, 0.15 * stitch.type[1], stroke=self.color)
            stitch.top_position = (x, y)
            return

        elif type(stitch.type) == tuple and stitch.type[0] == ComplexStitch.DECREASE:
            if stitch.type[1] % 2 == 1:
                base_point = stitch.anchors[stitch.type[1] // 2].top_position
            else:
                x1 = stitch.anchors[stitch.type[1] // 2].top_position[0]
                y1 = stitch.anchors[stitch.type[1] // 2].top_position[1]
                x2 = stitch.anchors[stitch.type[1] // 2 - 1].top_position[0]
                y2 = stitch.anchors[stitch.type[1] // 2 - 1].top_position[1]
                base_point = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            # base point coords
            xb, yb = base_point
            radius = math.hypot(xb, yb)
            angle = math.atan2(yb, xb)
            
            # visual coords
            x = (radius + self.get_group_height(self.get_group(stitch.type[2])) - 10) * math.cos(angle)
            y = (radius + self.get_group_height(self.get_group(stitch.type[2])) -10) * math.sin(angle)

            # top coords
            xt = (radius + self.get_group_height(self.get_group(stitch.type[2]))) * math.cos(angle)
            yt = (radius + self.get_group_height(self.get_group(stitch.type[2]))) * math.sin(angle)
            stitch.top_position = (xt, yt)


            top_line = draw.Group()
            top_line.append(draw.Line(-15, 0, 15, 0, stroke_width = 2))
            self.drawing.append(draw.Use(top_line, 0, 0, transform = f'translate({x}, {y}) rotate({math.degrees(angle) + 90}, 0, 0)', stroke = self.color))

            cross_line = draw.Group()
            if stitch.type[2] == SingularStitch.DC:
                cross_line.append(draw.Line(-7, 0, 7, 0, stroke_width=2))
            elif stitch.type[2] == SingularStitch.TR:
                cross_line.append(draw.Line(-7, 5, 7, 5, stroke_width=2))
                cross_line.append(draw.Line(-7, -5, 7, -5, stroke_width=2))

            # self.drawing.append(draw.Line(xb, yb, x, y, stroke=self.color, stroke_width=2))
            for anchor in stitch.anchors:
                xa = anchor.top_position[0]
                ya = anchor.top_position[1]
                self.drawing.append(draw.Line(xa, ya, x, y, stroke=self.color, stroke_width=2))

                xm = (x + xa) / 2
                ym = (y + ya) / 2
                self.drawing.append(draw.Use(cross_line, 0, 0, transform = f'translate({xm}, {ym}) rotate({math.degrees(angle) + 110}, 0, 0)', stroke = self.color))
            
            return

        self.drawing.append(draw.Use(self.get_group(stitch.type), 0, 0, transform = f'translate({position[0]}, {position[1]}) rotate({angle + 90}, 0, 0)', stroke = self.color))
        
        # current_radius = math.hypot(position[0], position[1])
        # x = (current_radius + self.get_group_height(self.get_group(stitch.type))) * math.cos(angle)
        # y = (current_radius + self.get_group_height(self.get_group(stitch.type))) * math.sin(angle)
        # stitch.top_position = (x, y)
        x = position[0] + self.get_group_height(self.get_group(stitch.type)) * math.cos(math.radians(angle))
        y = position[1] + self.get_group_height(self.get_group(stitch.type)) * math.sin(math.radians(angle))
        if stitch.type == SingularStitch.SLIP and stitch.anchors[0].top_position is not None:
            stitch.top_position = stitch.anchors[0].top_position
        else:
            stitch.top_position = (x, y)


    def split_chain_dependent(self, chain : Stitch):
        if type(chain.type) != tuple or chain.type[0] != ComplexStitch.CH_SPACE :
            raise Exception("can't split something that isn't a chain")
        
        middle = []
        right = []
        left = []
        if len(chain.dependent) == 1:
            middle.append(chain.dependent[0])
            return (middle, right, left)

        if not (type(chain.dependent[0].previous.type) == tuple and chain.dependent[0].previous.type[0] == ComplexStitch.CH_SPACE):
            right.append(chain.dependent[0])
        else:
            middle.append(chain.dependent[0])
        if not (type(chain.dependent[-1].next.type) == tuple and chain.dependent[-1].next.type[0] == ComplexStitch.CH_SPACE):
            left.append(chain.dependent[-1])
        # TODO if left is followed by a chain

        for i in range(1, len(chain.dependent)):
            if chain.dependent[i].previous in right:
                right.append(chain.dependent[i])
            elif chain.dependent[-i - 1] in left:
                left.insert(0, chain.dependent[-i - 1])
            else:
                middle.append(chain.dependent[i])
                

        return (middle, right, left)

    def draw_basic_round(self, round, previous_round, radius):
        # we've already verified these are valid and alternating, because this function is only called right after making that validation
        stitch_type1 =  round[1].type
        stitch_type2 = round[2].type

        group1 = self.get_group(stitch_type1)
        group2 = self.get_group(stitch_type2)

        base  = previous_round[-1].top_position
        draw_starting_chain(self.drawing, round[0].type[1], base, stroke=self.color)
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
                    transform=f"translate({x},{y}) rotate({rotation},0,0)",
                    stroke = self.color
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
        round[-1].top_position = round[0].top_position

    def get_group(self, stitch_type):
        if stitch_type == SingularStitch.SC:
            return self.single_crochet
        elif stitch_type == SingularStitch.HDC:
            return self.half_double_crochet
        elif stitch_type == SingularStitch.DC:
            return self.double_crochet
        elif stitch_type == SingularStitch.TR:
            return self.treble
        elif stitch_type == SingularStitch.SLIP:
            return self.slip_stitch
        else:
            raise Exception("Unsupported stitch type")
    
    def get_group_height(self, group):
        if group == self.single_crochet:
            return 25
        elif group == self.half_double_crochet:
            return 40
        elif group == self.double_crochet:
            return 60
        elif group == self.treble:
            return 80
        elif group == self.slip_stitch:
            return 10