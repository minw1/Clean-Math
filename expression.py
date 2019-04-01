import wolframalpha
import operation as opn
import numpy as np

APP_ID = "8T8YA5-3V337TXULH"
client = wolframalpha.Client(APP_ID)

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

    def __repr__(self):
        return repr(self.op)+' of ('+') and ('.join([repr(k) for k in self.expList])+')'

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
        return self.strRep
    def __repr__(self):
        return self.strRep
