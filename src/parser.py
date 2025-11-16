import ply.yacc as yacc
import ply.lex as lex

import nodes as nd

tokens = (
    'SC', 'DC', 'HDC', 'TR', 'DTR', 'CHAIN',
    'STITCH', #generic stitch
    'SLIP_STITCH',
    'NEXT', 'LAST', 'FIRST', 'SAME',
    'JOIN', 'TURN',
    'REPEAT', 'TIMES', 'AROUND',
    'POPCORN', 'BOBBLE', 'CLUSTER',
    'COMMA', 'COLON', #explicitly defined because I keep not noticing it if I use a literal for it
    'TO_MAKE', 'COUNTS_AS',
    'RING',
    'FROM_HOOK',
    'INCREASE', 'DECREASE',
    'NUMBER', 'ORDINAL',
    'INTO',
    'ROUND'
)

t_SC = r'sc|single crochet|scs'
t_DC = r'dc|double crochet|dcs'
t_TR = r'tr|treble|trs'
t_DTR = r'dtr|double treble|dtrs'
t_HDC = r'hdc|half double crochet|half-double crochet|hdcs'
t_SLIP_STITCH = r'slip|slip stitch|slip st|sl st|slst'
t_CHAIN = r'chain|ch'
t_STITCH = r'stitch|st'

t_NEXT = r'next'
t_LAST = r'last'
t_FIRST = r'first'
t_SAME = r'same'

t_JOIN = r'join'
t_TURN = r'turn'

t_REPEAT = r'repeat'
t_TIMES = r'times'
t_AROUND = r'around'

t_POPCORN = r'popcorn'
t_BOBBLE = r'bobble'
t_CLUSTER = r'cluster'

t_COMMA = r',' 
t_COLON = r':'

t_TO_MAKE = r'to make'
t_COUNTS_AS = r'counts as'
t_FROM_HOOK = r'from hook'
t_RING = r'ring'

t_INCREASE = r'increase'
t_DECREASE = r'decrease|split'

t_INTO = r'into|in'

t_ROUND = r'round|row'

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_ORDINAL(t):
    r"\d+(?:st|nd|rd|th)"
    t.value = int(t.value)
    return t

def t_error(t):
    t.lexer.skip(1)



# ! -- Parser --
literals = "*"

def p_all(p):
    'all : declarations rounds'
    p[0] = nd.All(p[1], p[2])
    
    
#TODO implement declarations
def p_declarations_multiple(p):
    'declarations : declarations declaration'
    p[0] = None

def p_declarations_single(p):
    'declarations : declaration'
    p[0] = None
    
def p_declaration(p):
    'declaration : empty'
    p[0] = None
    
def p_rounds_multiple(p):
    'rounds : rounds round'
    p[1].add_round(p[2])
    p[0] = p[1]
    
def p_rounds_single(p):
    'rounds : round'
    rounds = nd.Rounds()
    rounds.add_round(p[1])
    p[0] = rounds

def p_round(p):
    'round : ROUND NUMBER COLON expressions'
    p[0] = nd.Round(p[1])

def p_expressions_multiple(p):
    'expressions : expressions COMMA expression'
    p[1].add_expression(p[3])
    p[0] = p[1]
    
def p_expressions_single(p):
    'expressions : expression'
    expressions = nd.Expressions()
    expressions.add_expression(p[1])
    p[0] = expressions
    
    
#? --- Expressions  ---

def p_expression_stitch(p):
    'expression : stitch_type'
    p[0] = nd.StitchType(p[1], 1, None)

def p_expression_number_stitch(p):
    'expression : NUMBER stitch_type'
    stitch = nd.StitchGroup(p[2])
    stitch.set_number(p[1])
    p[0] = stitch

def p_expression_number_stitch_destination(p):
    'expression : NUMBER stitch_type INTO destination'
    stitch = nd.StitchGroup(p[2])
    stitch.set_number(p[1])
    stitch.set_destination(p[4])
    p[0] = stitch

def p_expression_stitch_destination(p):
    'expression : stitch_type INTO destination'
    stitch = nd.StitchGroup(p[1])
    stitch.set_destination(p[2])
    p[0] = stitch
    
def p_expression_loop(p):
    'expression : loop'
    p[0] = p[1]


#? -- Stitches --
def p_stitch_type_simple(p):
    'stitch_type : simple_stitch'
    p[0] = nd.StitchGroup(p[1])
    
def p_stitch_type_grouped(p):
    'stitch_type : grouped_stitch'
    p[0] = nd.StitchGroup(p[1])
    

def p_simple_stitch_sc(p):
    'simple_stitch : SC'
    p[0] = nd.SimpleStitch.SC

def p_simple_stitch_dc(p):
    'simple_stitch : DC'
    p[0] = nd.SimpleStitch.DC
    'simple_stitch : DC'
    p[0] = nd.SimpleStitch.DC

def p_simple_stitch_tr(p):
    'simple_stitch : TR'
    p[0] = nd.SimpleStitch.TR

def p_simple_stitch_dtr(p):
    'simple_stitch : DTR'
    p[0] = nd.SimpleStitch.DTR

def p_simple_stitch_hdc(p):
    'simple_stitch : HDC'
    p[0] = nd.SimpleStitch.HDC
    
def p_simple_stitch_slip(p):
    'simple_stitch : SLIP_STITCH'
    p[0] = nd.SimpleStitch.SLIP

def p_simple_stitch_chain(p):
    'simple_stitch : CHAIN'
    p[0] = nd.SimpleStitch.CH


def p_grouped_stitch_increase(p):
    'grouped_stitch : NUMBER simple_stitch INCREASE'
    p[0] = nd.Increase(p[2], p[1])

def p_grouped_stitch_decrease(p):
    'grouped_stitch : NUMBER simple_stitch DECREASE'
    p[0] = nd.Decrease(p[2], p[1])

def p_grouped_stitch_popcorn(p):
    'grouped_stitch : NUMBER simple_stitch POPCORN'
    p[0] = nd.Popcorn(p[2], p[1])


def p_destination_next(p):
    'destination : NEXT stitch_type'
    p[0] = nd.Destination(nd.DestinationType.NEXT, p[2])

def p_destination_ordinal(p):
    'destination : ORDINAL CHAIN FROM_HOOK'
    p[0] = nd.Destination_Ordinal(p[1])

def p_loop_number(p):
    '''loop : '*' expressions REPEAT '*' NUMBER TIMES '''
    p[0] = nd.Loop(p[2], p[5])

def p_loop_around(p):
    '''loop : '*' expressions REPEAT '*' AROUND '''
    p[0] = nd.Loop(p[2], None)

def p_empty(p):
    'empty :'
    pass




import logging
logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()
lex.lex(debug=True,debuglog=log)
parser = yacc.yacc(debug=True,debuglog=log)

if __name__ == "__main__":
    # f = open(sys.argv[1], "r")
    f = open("/home/dorithegreat/Documents/programs/praca inżynierska/crochet-visualiser/patterns/pinterest_1.txt", "r")
    text = f.read()


tree = parser.parse(text, debug=log)