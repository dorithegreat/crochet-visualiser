import drawsvg as draw
import math
from draw_chain import draw_chain

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

# d.append(double_crochet)
# d.append(single_crochet)


for i in range (16):
    x = 80 * math.cos(2 * math.pi * i / 16)
    y = 80 * math.sin((2 * math.pi * i / 16))
    d.append(draw.Use(single_crochet, 0, 0, transform= f'translate({x}, {y}) rotate({(360 / 16) * i + 90}, 0, 0)'))

for i in range (16):
    x = 100 * math.cos(2 * math.pi * i / 16)
    y = 100 * math.sin((2 * math.pi * i / 16))
    d.append(draw.Use(double_crochet, 0, 0, transform= f'translate({x}, {y}) rotate({(360 / 16) * i + 90}, 0, 0)'))



draw_chain(d,(-100, 110), (100, 110), 250, 20)
# draw_chain(d, (0,0), (100, -30), 120, 5)

d.save_svg("test2.svg")