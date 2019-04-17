import operation as opn
import numpy as np
import wolframalpha

APP_ID = "8T8YA5-3V337TXULH"
client = wolframalpha.Client(APP_ID)

class Expression:
    #Initializer for composite expression
    def __init__(self, op, expList, parens=False, cursor=False, cursor_idx=None):
        '''
        Initializes a composite expression
        Parameters:
            self: Object being initialized
            op: operation the expression contains
            explist: List of expressions the expression contains (assumed to be ordered properly; for example, it would be [2,1] for 2+1 and [1,2] for 1+2)
        '''
        self.expList = expList #Stores expressions that this expression comprises
        self.op = op
        self.parens = parens
        self.cursor = cursor
        self.cursor_idx = cursor_idx
      
    #Gets string representation of expression
    def getString(self):
        returnString = self.op.makeStr(self.expList)
        if self.parens:
            returnString = "(" + returnString + ")"
        return returnString

    #Evaluates expression
    def eval(self):
        expString = self.getString()
        res = client.query(expString) #Gets result from WolframAlpha
        return next(res.results).text

	#Returns expression with parentheses
    def addParens(self):
        self.parens = True
        return self
	
	#Adds cursor and index
    def addCursor(self, idx):
        self.cursor = True
        self.cursor_idx = idx

    def __repr__(self):
        return repr(self.op)+' of ('+') and ('.join([repr(k) for k in self.expList])+')'

class NoOpExpression(Expression):
    #Initializer for a no-operator expression
    def __init__(self, strRep, cursor=False, cursor_idx=None):
        '''
        Parameters:
            self: Object being initialized
            strRep: String representation of expression.
            '''
        self.strRep = strRep
        self.cursor = cursor
        self.cursor_idx = cursor_idx

	#Adds cursor and index
    def addCursor(self, idx):
        self.cursor = True
        self.cursor_idx = idx
		
    def __repr__(self):
        return self.strRep

