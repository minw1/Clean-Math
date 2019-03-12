import wolframalpha

APP_ID = "8T8YA5-3V337TXULH"
client = wolframalpha.Client(APP_ID)

opList = ["+", "-", "/", "*", "%", "^"]
numList = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

#Here's the big one: the function that converts a given string into a bunch of expressions
def parseToExp(strIn):
    newExpressions = []
	expLocs = []
	strCurrent = strIn
	strTemp = ""
	while strCurrent != "?":
		strTemp = ""
		for i in len(strCurrent):
			if strCurrent[i] in opList:
		
	
    return newExpression

class Operator:
    #Intializer for an operation
    def __init__(self, strRep):
        '''
        strRep: String object representing the string of the operation
        '''
        self.strRep = strRep

    #Gets string representation of operator
    def getString(self):
        return self.strRep

class Expression:
    #Initializer for composite expression
    def __init__(self, op, explist, parens=False, first=0):
        '''
        Initializes a composite expression
        Parameters:
            self: Object being initialized
            op: operation the expression contains
            explist: List of expressions the expression contains
            first: operations have order (for example 2 - 1 != 1 - 2). This just denotes which of the expressions in this one is the "first" on which the operator should operate
        '''
        self.expList = expList #Stores expressions that this expression comprises
        self.op = op
        self.first = first
        self.parens = parens

    #Gets string representation of expression
    def getString(self):
        returnString = getString(selfcompExp[first]) + getString(self.op) + getString(self.compExp[1-first])
        if parens:
            returnString = "(" + returnString + ")"
        return returnString

    #Evaluates expression
    def eval(self):
        expString = getString(self)
        res = client.query(expString) #Gets result from WolframAlpha
        return next(res.results).text

class NoOpExpression(Expression):
    #Initializer for a no-operator expression from a string
    def __init__(self, strRep, func=None, exp0=None, parens=False):
        '''
        Parameters:
            self: Object being initialized
			locs: Locations of the expression within the string being parsed
            strRep: String representation of expression. User must set this to None if they're initializing from a function and a smaller expression
            func: Function that makes up the expression. Function object if the user is initializing an expression in the form function(expression), None otherwise
            exp0: Expression being acted on by the function. Expression object if the user is initializing an expression in the form function(expression), None otherwise
        '''
        self.strRep = strRep
        self.func = func
        self.exp0 = exp0
        self.parens = parens

    #Get string representation of expression
    def getString(self):
        if strRep:
            returnString = strRep
        else:
            returnString = func.getString + exp0.getString

        if parens:
            returnString = "(" + returnString + ")"
