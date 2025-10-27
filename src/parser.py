import ply.yacc as yacc
import ply.lex as lex

import nodes as nd

tokens = (
    'SC', 'DC', 'HDC', 'TR', 'DTR', 'CH',
    'STITCH', #generic stitch
    'SLIP_STITCH',
    'NEXT', 'LAST', 'FIRST', 'SAME',
    'JOIN', 'TURN',
    'REPEAT',
    'POPCORN', 'BOBBLE', 'CLUSTER',
    'COMMA',
    'TO_MAKE', 'COUNTS_AS',
    'RING',
    'FROM_HOOK',
    'INCREASE', 'DECREASE'
)

t_SC = r'sc|single crochet|scs'
t_DC = r'dc|double crochet|dcs'


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_ORDINAL(t):
    r" \d+(?:st|nd|rd|th)"
    t.value = int(t.value)
    return t

# ! -- Parser --

def p_all(p):
    'all : declarations rounds'
    p[0] = nd.All(p[1], p[2])
    
def rounds_multiple(p):
    'rounds : rounds round'
    p[1].add_round(p[2])
    p[0] = p[1]
    
def rounds_single(p):
    'rounds : round'
    pass #TODO figure this out

def expressions_multiple(p):
    'expressions : expressions COMMA expression'
    p[1].add_expression(p[3])
    p[0] = p[1]
    
def expressions_single(p):
    'expressions : expression'
    expressions = nd.Expressions()
    expressions.add_expression(p[1])
    p[0] = expressions
    
    
#? --- Expressions  ---

def expression_stitch(p):
    'expression : stitch_type'
    p[0] = nd.StitchType(p[1], 1, None)

def expression_number_stitch(p):
    'expression : number stitch_type'
    p[0] = nd.StitchType(p[2], p[1], None)

def expression_number_stitch_destination(p):
    'expression : number stitch_type destination'
    p[0] = nd.StitchType(p[2], p[1], p[3])

def expression_stitch_destination(p):
    'expression : stitch_type destination'
    p[0] = nd.StitchType(p[1], 1, p[2])
    
def expression_loop(p):
    'expression : loop'
    p[0] = p[1]



import logging
logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()
lex.lex(debug=True,debuglog=log)