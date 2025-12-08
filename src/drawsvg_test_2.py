import drawsvg as draw
import math
from draw_utilities import draw_chain, draw_base_chain, draw_starting_chain, draw_cluster_lines

d = draw.Drawing(100,  80, origin='center')
d.append(draw.Rectangle(-250, -250, 500, 500, fill='white'))

single_crochet = draw.Group()
single_crochet.append(draw.Line(0, 0, 0, -40, stroke_width = 2, stroke = 'black'))
single_crochet.append(draw.Line(-20, -20, 20, -20, stroke_width = 2, stroke = 'black'))
# single_crochet.append(draw.Circle(0, 0, 2, fill = 'black'))
# single_crochet.append(draw.Circle(-10, -10, 2, fill = 'gray'))

double_crochet = draw.Group()
double_crochet.append(draw.Line(0, 0, 0, -40, stroke_width = 2, stroke='black'))
double_crochet.append(draw.Line(-10, -40, 10, -40, stroke_width = 2, stroke='black'))
double_crochet.append(draw.Line(-7, -25, 7, -20, stroke_width = 2, stroke='black'))

half_double_crochet = draw.Group()
half_double_crochet.append(draw.Line(0,0,0,-30, stroke_width = 2, stroke='black'))
half_double_crochet.append(draw.Line(-10, -30, 10, -30, stroke_width = 2, stroke='black'))

treble = draw.Group()
treble.append(draw.Line(0, 0, 0, -60, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-10, -60, 10, -60, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-7, -30, 7, -25, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-7, -40, 7, -35, stroke_width = 2, stroke='black'))

treble = draw.Group()
treble.append(draw.Line(0, 0, 0, -80, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-10, -80, 10, -80, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-7, -35, 7, -30, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-7, -45, 7, -40, stroke_width = 2, stroke='black'))
treble.append(draw.Line(-7, -55, 7, -50, stroke_width = 2, stroke='black'))

# d.append(treble)
# d.append(single_crochet)

# d.append(draw.Use(half_double_crochet, 0, 20, transform='rotate(20, 0, 20)'))
# d.append(draw.Use(half_double_crochet, 0, 20, transform='rotate(-20, 0, 20)'))
# d.append(draw.Ellipse(0, 0, 12, 5, stroke='black', stroke_width=2, fill='white'))

draw_cluster_lines(d, (0, 20), (0, -20), 3, 1, 0.4)
d.append(draw.Line(-10, -20, 10, -20, stroke_width = 2, stroke='black'))

# d = draw.Drawing(200, 200)
# d.save_svg("test2.svg")
d.save_png("cl.png")