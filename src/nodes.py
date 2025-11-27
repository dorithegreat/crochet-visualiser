from enum import Enum

class Alias:
    def __init__(self, alias):
        self.alias = alias
class All:
    def __init__(self, declarations, rounds):
        self.declarations : Declarations = declarations
        self.rounds : Rounds = rounds

class Cluster:
    def __init__(self, stitch, number):
        self.stitch = stitch
        self.number = number

class CountsAs:
    def __init__(self, stitch, alias):
        self.stitch = stitch
        self.alias = alias

class Declaration:
    def __init__(self):
        pass
    
class Declarations:
    def __init__(self):
        pass

class Decrease:
    def __init__(self, stitch, number):
        self.stitch : SimpleStitch = stitch
        self.number : int = number

class Destination:
    def __init__(self, stitch):
        self.stitch = stitch
    
    def set_type(self, type):
        self.type = type
class Destination_Ordinal:
    def __init__(self, number : int):
        self.number : int =  number

class Expressions:
    def __init__(self):
        self.expressions = []
    
    def add_expression(self, expression):
        self.expressions.append(expression)
    

class Increase:
    def __init__(self, stitch, number):
        self.stitch : SimpleStitch = stitch
        self.number : int = number

class Loop:
    def __init__(self, expressions, number):
        self.number = number
        self.expressions : Expressions = expressions

class Popcorn:
    def __init__(self, stitch, number):
        self.stitch : SimpleStitch = stitch
        self.number : int = number

class Rounds:
    def __init__(self):
        self.rounds = []
        
    def add_round(self, round):
        self.rounds.append(round)
    
class Round:
    def __init__(self, expressions):
        self.expressions : Expressions = expressions

class Skip:
    def __init__(self, stitch, number):
        self.stitch = stitch
        self.number = number

class StitchGroup:
    def __init__(self, stitch):
        self.stitch = stitch
        self.destination = None
        self.number = 1
        
    def set_number(self, number : int):
        self.number = number
        
    def set_destination(self, destination):
        self.destination = destination

class SimpleStitch(Enum):
    SC = 1
    DC = 2
    TR = 3
    DTR = 4
    HDC = 5
    SLIP = 6
    CH = 7
    STITCH = 8

class DestinationType(Enum):
    NEXT = 1
    LAST = 2
    SAME = 3
    FIRST = 4
    RING = 5
    CH_SPACE = 6