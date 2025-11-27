import ply.yacc as yacc
import ply.lex as lex

from preprocessor import Preprocessor
from visualizer import Visualizer
import nodes as nd

tokens = (
    'SC', 'DC', 'HDC', 'TR', 'DTR', 'CHAIN',
    'STITCH', #generic stitch
    'SLIP_STITCH',
    'NEXT', 'LAST', 'FIRST', 'SAME',
    'JOIN', 'TURN',
    'REPEAT', 'TIMES', 'AROUND', 'TWICE',
    'POPCORN', 'BOBBLE', 'CLUSTER',
    'COMMA', 'COLON', #explicitly defined because I keep not noticing it if I use a literal for it
    'TO_MAKE', 'COUNTS_AS',
    'RING',
    'FROM_HOOK',
    'INCREASE', 'DECREASE',
    'NUMBER', 'ORDINAL',
    'INTO',
    'ROUND', 'SKIP'
)

#? All tokens are defined as functions due to PLY not correctly handling multi-word tokens otherwise

### --- Stitch Types (simple + multi-word variants) ---

def t_SC(t):
    r'(?:scs?|single\s+crochet)'
    return t

def t_DC(t):
    r'(?:dcs?|double\s+crochet)'
    return t

def t_TR(t):
    r'(?:trs?|treble)'
    return t

def t_DTR(t):
    r'(?:dtrs?|double\s+treble)'
    return t

def t_HDC(t):
    r'(?:hdcs?|hdc|half(?:-|\s+)double\s+crochet)'
    return t

def t_SLIP_STITCH(t):
    r'(?:slip(?:\s+stitch|(?:\s+st)?)|sl\s*st|slst)'
    return t

def t_CHAIN(t):
    r'(?:ch|chain)'
    return t

def t_STITCH(t):
    r'(?:stitch|st)'
    return t


### --- Simple one-word tokens ---

def t_NEXT(t):
    r'next'
    return t

def t_LAST(t):
    r'last'
    return t

def t_FIRST(t):
    r'first'
    return t

def t_SAME(t):
    r'same'
    return t


def t_JOIN(t):
    r'join'
    return t

def t_TURN(t):
    r'turn'
    return t


def t_REPEAT(t):
    r'repeat'
    return t

def t_TIMES(t):
    r'times'
    return t

def t_AROUND(t):
    r'around'
    return t

def t_TWICE(t):
    r'twice'
    return t


def t_POPCORN(t):
    r'popcorn'
    return t

def t_BOBBLE(t):
    r'bobble'
    return t

def t_CLUSTER(t):
    r'cluster'
    return t


### --- Multi-word grammatical tokens ---

def t_TO_MAKE(t):
    r'to\s+make'
    return t

def t_COUNTS_AS(t):
    r'counts\s+as'
    return t

def t_FROM_HOOK(t):
    r'from\s+hook'
    return t


### --- Other special tokens ---

def t_RING(t):
    r'ring'
    return t

def t_INCREASE(t):
    r'increase'
    return t

def t_DECREASE(t):
    r'(?:decrease|split)'
    return t

def t_SKIP(t):
    r'skip'
    return t

def t_INTO(t):
    r'(?:in|into|to)'
    # this allows for some weird phrasings but there is no reason to not allow them
    return t

def t_ROUND(t):
    r'(?:round|row)'
    return t


### --- Literal tokens (simple) ---

t_COMMA = r','
t_COLON = r':'


def t_NUMBER(t):
    r'\d+(?!st|nd|rd|th)' # to prevent ordinals from being detected as numbers
    t.value = int(t.value)
    return t

def t_ORDINAL(t):
    r'\d+(?:st|nd|rd|th)'
    t.value = int(t.value[:-2])
    return t

# comments that start with // and end with a newline or another //
def t_COMMENT(t):
    r'//([^/\n]|/(?!/))*?(//|\n)'
    pass 


def t_error(t):
    t.lexer.skip(1)



# ! -- Parser --
literals = "*()[]"

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
    p[0] = nd.Round(p[4])


#! --- Expressions  ---

def p_expressions_multiple(p):
    'expressions : expressions COMMA aliasable_expression'
    p[1].add_expression(p[3])
    p[0] = p[1]
    
def p_expressions_single(p):
    'expressions : aliasable_expression'
    expressions = nd.Expressions()
    expressions.add_expression(p[1])
    p[0] = expressions
    

def p_aliasable_expressions_counts_as(p):
    '''aliasable_expression : expression '(' COUNTS_AS alias ')' '''
    p[0] = nd.CountsAs(p[1], p[5])

def p_aliasable_expression_to_make(p):
    'aliasable_expression : expression TO_MAKE alias'
    p[0] = nd.CountsAs(p[1], p[3])

def p_aliasable_expression_base_expression(p):
    'aliasable_expression : expression'
    p[0] = p[1]


def p_expression_stitch(p):
    'expression : stitch_type'
    p[0] = nd.StitchGroup(p[1])

#? Chains are the only stitch commonly written as "ch n" rather than "n chs"
def p_expression_chain_number(p):
    'expression : CHAIN NUMBER'
    stitch = nd.StitchGroup(nd.SimpleStitch.CH)
    stitch.set_number(p[2])
    p[0] = stitch

def p_expression_number_stitch(p):
    'expression : NUMBER stitch_type'
    stitch = p[2]
    stitch.set_number(p[1])
    p[0] = stitch

def p_expression_number_stitch_destination(p):
    'expression : NUMBER stitch_type INTO destination'
    stitch = p[2]
    stitch.set_number(p[1])
    stitch.set_destination(p[4])
    p[0] = stitch

def p_expression_stitch_destination(p):
    'expression : stitch_type INTO destination'
    stitch = p[1]
    stitch.set_destination(p[3])
    p[0] = stitch
    
def p_expression_loop(p):
    'expression : loop'
    p[0] = p[1]

def p_expression_ring(p):
    'expression : RING'
    p[0] = p[1]
    
def p_expression_skip_one(p):
    'expression : SKIP stitch_type'
    p[0] = nd.Skip(p[2], 1)

def p_expression_skip_next(p):
    'expression : SKIP NEXT stitch_type'
    p[0] = nd.Skip(p[3], 1)

def p_expression_skip_multiple(p):
    'expression : SKIP NUMBER stitch_type'
    p[0] = nd.Skip(p[3], p[2])

#! --- Aliases ---

def p_alias_ring(p):
    'alias : RING'
    p[0] = nd.Alias(p[1])

def p_alias_simple_stitch(p):
    'alias : simple_stitch'
    p[0] = nd.Alias(p[1])

def p_alias_first_stitch(p):
    'alias : FIRST simple_stitch'
    p[0] = nd.Alias(p[2]) 
    #? aliases are usually used for counting ch 3 at the beginning of a round as a dc


#! --- Stitches ---

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

def p_simple_stitch_generic(p):
    'simple_stitch : STITCH'
    p[0] = nd.SimpleStitch.STITCH


def p_grouped_stitch_increase(p):
    'grouped_stitch : NUMBER simple_stitch INCREASE'
    p[0] = nd.Increase(p[2], p[1])

def p_grouped_stitch_decrease(p):
    'grouped_stitch : NUMBER simple_stitch DECREASE'
    p[0] = nd.Decrease(p[2], p[1])

def p_grouped_stitch_cluster(p):
    'grouped_stitch : NUMBER simple_stitch CLUSTER'
    p[0] = nd.Cluster(p[2], p[1])

def p_grouped_stitch_popcorn(p):
    'grouped_stitch : NUMBER simple_stitch POPCORN'
    p[0] = nd.Popcorn(p[2], p[1])

#! --- Destination ---

def p_destination_next(p):
    'destination : NEXT stitch_type'
    destination = nd.Destination(p[2])
    destination.set_type(nd.DestinationType.NEXT)
    p[0] = destination

def p_destination_last(p):
    'destination : LAST stitch_type'
    destination = nd.Destination(p[2])
    destination.set_type(nd.DestinationType.LAST)
    p[0] = destination

def p_destination_first(p):
    'destination : FIRST stitch_type'
    destination = nd.Destination(p[2])
    destination.set_type(nd.DestinationType.FIRST)
    p[0] = destination

def p_destination_same(p):
    'destination : SAME stitch_type'
    destination = nd.Destination(p[2])
    destination.set_type(nd.DestinationType.SAME)
    p[0] = destination

def p_destination_ordinal(p):
    'destination : ORDINAL CHAIN FROM_HOOK'
    p[0] = nd.Destination_Ordinal(p[1])

def p_destination_ring(p):
    'destination : RING'
    destination = nd.Destination(p[1])
    destination.set_type(nd.DestinationType.RING)
    p[0] = destination

def p_loop_number(p):
    '''loop : '*' expressions REPEAT '*' number_times '''
    p[0] = nd.Loop(p[2], p[5])

def p_loop_around(p):
    '''loop : '*' expressions REPEAT '*' AROUND '''
    p[0] = nd.Loop(p[2], None)

def p_loop_number_brackets(p):
    ''' loop :  '[' expressions ']' number_times '''
    p[0] = nd.Loop(p[2], p[4])

def p_loop_around_brackets(p):
    ''' loop : '[' expressions ']' AROUND '''
    p[0] = nd.Loop(p[2], None)

def p_number_times(p):
    'number_times : NUMBER TIMES'
    p[0] = p[1]

def p_number_times_twice(p):
    'number_times : TWICE'
    p[0] = 2

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
    text = text.lower()


tree = parser.parse(text, debug=log)
# print(tree)

preprocessor = Preprocessor()
flattened = preprocessor.preprocess(tree)

visualizer = Visualizer()
visualizer.visualize(flattened)