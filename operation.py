import wolframalpha

def atLocation(subStr, searchStr, loc):
    out = True
    for i in range(0, len(subStr)):
        if searchStr[loc+i] != subStr[i]:
            out = False
    return out

class Operator:
    '''
    General operator class. Contains (but does not define) methods for checking if an operator is at a position in a string, finding an operator's operand(s), and creating a string out of an operator and its operands.
    '''
    #Intializer for an operation
    def __init__(self, getPosition, getOperands, makeString, strRep):
        '''
        atPosition : Method that returns whether the operator is at a given position in a given string
        getOperands : Get operator's operands and their positions given the operator's position in a given string
        makeString : Makes an expression string given the operator's operands
        '''
        self.getPosition = getPosition
        self.getOperands = getOperands
        self.makeString = makeString
        self.strRep = strRep
    
    #Determines what positions an operator occupies in a given string
    def getPos(self, searchStr):
        '''
        Returns python list
        '''
        positions = self.getPosition(searchStr)
        return positions

    #Gets operands and operand locations given operator location(s) in given string
    def getOps(self, searchStr, pos):
        operandLocDict = self.getOperands(searchStr, pos) #Returns a dictionary with lists of each operand's positions as keys and the operand strings as values
        return operandLocDict

    #Makes a string out of the operator and given operands
    def makeStr(self, opList):
        opString = self.makeString(opList)
        return opString

opList = []