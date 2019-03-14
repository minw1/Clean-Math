import wolframalpha
import operation as opn
import numpy as np
import pandas as pd

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
    opLocs = {}
    for op in opn.opList:
        posList = op.getPos(expStr)
        for newPos in posList:
            contained = False
            for oldPos in opLocs.keys():
                if all(elem in newPos for elem in oldPos):
                    del opLocs[oldPos]
                elif all(elem in oldPos for elem in newPos):
                    contained = True
            if not contained:
                opLocs[newPos] = op
        
	#Finds operands of located operators	
    opDF = pd.DataFrame(opLocs.items(), columns=["Locations", "Operator"])
    operandList = []
    for row in opDF.itertuples(index=False):
        locs, op = row
        opndsDict = op.getOps(expStr, locs)
        operandList.append(opndsDict)
    opDF["Operands"] = operandList

    #Creates expressions in order of execution
    returnExpList = []
    operandLocs = opDF["Operands"]
    opDF["Expressions"] = pd.Series(index = range(0, len(operandLocs)))
    while not operandLocs.empty:
        workingOps = np.zeros(len(operandLocs))
        for i in operandLocs:
            workingOps[i] = 1
            for j in range(0, i):
                for newOpPos in operandLocs[i].keys():
                    for oldOpPos in operandLocs[j].keys():
                        if all(elem in newOpPos for elem in oldOpPos):
                            workingOps[i] = 0
                        elif all(elem in oldOpPos for elem in newOpPos):
                            workingOps[j] = 0
        for i in workingOps:
            if workingOps[i] == 1:
                expList = [None] * len(operandLocs[i].keys())
                count = -1
                for operand in operandLocs[i].keys():
                    count += 1
                    for row in opDF.itertuples(index=False):
                        opLocs = row[0]
                        for operandLocation in row[2].keys():
                            opLocs += operandLocation
                        if all(elem in operand for elem in opLocs) and all(elem in opLocs for elem in operand):
                            expList[count] = row[3]
                            break
                    if expList[count] == None:
                        newExp = NoOpExpression[operandLocs[i][operand]]
                        returnExpList.append(newExp)
                        expList[count] = newExp
                newExp = Expression(opDF["Operator"][i], expList)
                returnExpList.append(newExp)
                opDF["Expressions"][i] = newExp
                operandLocs.drop(i, 0)
    return returnExpList    


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