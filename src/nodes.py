from enum import Enum


class All:
    def __init__(self, declarations, rounds):
        self.declarations : Declarations = declarations
        self.rounds : Rounds = rounds
    
    
class Declaration:
    def __init__(self):
        pass
    
class Declarations:
    def __init__(self):
        pass
    
    
class Expressions:
    def __init__(self):
        self.expressions = []
    
    def add_expression(self, expression):
        self.expressions.append(expression)
    
class Expression:
    def __init__(self):
        pass
    
class Loop:
    def __init__(self):
        pass
    
class Rounds:
    def __init__(self):
        self.rounds =[]
        
    def add_round(self, round):
        self.rounds.append(round)
    
class Round:
    def __init__(self, expressions):
        self.expressions : Expressions = expressions
        
class StitchGroup:
    def __init__(self, stitch, number):
        self.stitch = stitch
        self.number = number
        
class StitchType:
    def __init__(self, stitch, number, destination):
        self.stitch = stitch
        self.number = number
        self.destination = destination
        

class SimpleStitch(Enum):
    SC = 1
    DC = 2
    TR = 3
    DTR = 4
    HDC = 5
    