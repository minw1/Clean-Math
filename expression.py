import wolframalpha

APP_ID = "8T8YA5-3V337TXULH"
client = wolframalpha.Client(APP_ID)

def atLocation(subStr, searchStr, loc):
    out = True
    for i in range(0, len(subStr)):
        if searchStr[loc+i] != subStr[i]:
            out = False
    return out

#Here's the big one: the function that converts a given string into a bunch of expressions
def parseToExp(strIn):
	expStr = strIn
    
	#Finds operators within the string
	opPosDict = {}
	expStrIter = iter(range(0, len(expStr)))
	#Iterates through positions in the input string and stores operators it finds
	for i in expStrIter:
		op = ""
		for key in opFuncDict:
			if len(key) > len(op) and atLocation(key, expStr, i):
				op = key
		if op != "":
			#Add operation to dictionary
			st = i
			end = st + len(op) - 1
			posList = [st, end]
			opPosDict[posList] = op
			
			#Advance for loop
			for i in range(0, len(op)-1):
				next(expStrIter)
	
	#Finds operands of located operators
	
	
	#Ranks operators in order of execution
	
	#"Executes" operators to create list of expressions

class Operator:
    '''
    General operator class. Contains (but does not define) methods for checking if an operator is at a position in a string, finding an operator's operand(s), and creating a string out of an operator and its operands.
    '''
    #Intializer for an operation
    def __init__(self, atPosition, getOperands, makeString):
        '''
        atPosition : Method that returns whether the operator is at a given position in a given string
        getOperands : Get operator's operands given its position in a given string
        makeString : Makes an expression string given the operator's operands
        '''
        self.atPosition = atPosition
        self.getOperands = getOperands
        self.makeString = makeString
    
    #Determines whether or not the operator is at a given position in a given string
    def atPos(self, searchStr, pos):
        present = self.atPosition(searchStr, pos)
        return present

    #Gets operands given operator location in given string
    def getOps(self, searchStr, pos):
        operands = self.getOperands(searchStr, pos)
        return operands

    #Makes a string out of the operator and given operands
    def makeStr(self, opList):
        opString = self.makeString(opList)
        return opString

class Expression:
    #Initializer for composite expression
    def __init__(self, op, expList):
        '''
        Initializes a composite expression
        Parameters:
            self: Object being initialized
            op: operation the expression contains
            explist: List of expressions the expression contains (assumed to be ordered properly; for example, it would be [2,1] for 2+1 and [1,2] for 1+2)
        '''
        self.expList = expList #Stores expressions that this expression comprises
        self.op = op
      
    #Gets string representation of expression
    def getString(self):
        returnString = self.op.makeStr(expList)
        return returnString

    #Evaluates expression
    def eval(self):
        expString = getString(self)
        res = client.query(expString) #Gets result from WolframAlpha
        return next(res.results).text

class NoOpExpression(Expression):
    #Initializer for a no-operator expression
    def __init__(self, strRep):
        '''
        Parameters:
            self: Object being initialized
            strRep: String representation of expression.
            '''
        self.strRep = strRep

    #Get string representation of expression
    def getString(self):
        return strRep