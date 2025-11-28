import drawsvg as draw
import math
from draw_utilities import draw_chain, draw_base_chain, draw_starting_chain

d = draw.Drawing(500, 500, origin='center')
d.append(draw.Rectangle(-250, -250, 500, 500, fill='white'))

single_crochet = draw.Group()
single_crochet.append(draw.Line(-10, -20, 10, 0, stroke_width = 2, stroke = 'black'))
single_crochet.append(draw.Line(-10, 0, 10, -20, stroke_width = 2, stroke = 'black'))
# single_crochet.append(draw.Circle(0, 0, 2, fill = 'black'))
# single_crochet.append(draw.Circle(-10, -10, 2, fill = 'gray'))

double_crochet = draw.Group()
double_crochet.append(draw.Line(0, 0, 0, -40, stroke_width = 2, stroke='black'))
double_crochet.append(draw.Line(-10, -40, 10, -40, stroke_width = 2, stroke='black'))
double_crochet.append(draw.Line(-7, -25, 7, -20, stroke_width = 2, stroke='black'))

half_double_crochet = draw.Group()
half_double_crochet.append(draw.Line(0,0,0,-30, stroke_width = 2, stroke='black'))
half_double_crochet.append(draw.Line(-10, -30, 10, -30, stroke_width = 2, stroke='black'))

# d.append(double_crochet)
# d.append(single_crochet)


for i in range (16):
    x = 60 * math.cos(2 * math.pi * i / 16)
    y = 60 * math.sin((2 * math.pi * i / 16))
    d.append(draw.Use(half_double_crochet, 0, 0, transform= f'translate({x}, {y}) rotate({(360 / 16) * i + 90}, 0, 0)'))

for i in range (16):
    x = 95 * math.cos(2 * math.pi * i / 16)
    y = 95 * math.sin((2 * math.pi * i / 16))
    d.append(draw.Use(double_crochet, 0, 0, transform= f'translate({x}, {y}) rotate({(360 / 16) * i + 90}, 0, 0)'))

# last = (0,0)
# for i in range (8):

#     x = 130 * math.cos(2 * math.pi * i / 8)
#     top_x = 175 * math.cos(2 * math.pi * i / 8)
#     y = 130 * math.sin((2 * math.pi * i / 8))
#     top_y = 175 * math.sin((2 * math.pi * i / 8))
#     d.append(draw.Use(double_crochet, 0, 0, transform= f'translate({x}, {y}) rotate({(360 / 8) * i + 90}, 0, 0)'))


#     if last != (0,0):
#         draw_chain(d, last, (top_y, top_x), 150, 5)
#     last = (top_y, top_x)




draw_chain(d,(-100, 110), (100, 110), 250, 10)
# draw_chain(d, (0,0), (0,0), 100, 7)

draw_base_chain(d, 10, 50, 12, 5)

draw_starting_chain(d, n=5, start=(100, 120))

d.save_svg("test2.svg")