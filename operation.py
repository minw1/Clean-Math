import wolframalpha

class Operator:
    '''
    General operator class. Contains (but does not define) methods for checking if an operator is at a position in a string, finding an operator's operand(s), and creating a string out of an operator and its operands.
    '''
    #Intializer for an operation
    def __init__(self, strRep, makeString):
        '''
        makeString : Makes an expression string given the operator's operands
        '''
        self.makeString = makeString
        self.strRep = strRep
    #Makes a string out of the operator and given operands
    def makeStr(self, opList):
        opString = self.makeString(opList)
        return opString
    def __repr__(self):
        return self.strRep

