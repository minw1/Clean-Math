import operation as opn
import numpy as np

import copy

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

binOps = {
    "+":0,
    "-":0,
    "*":1,
    "/":1,
    "^":2,
}
digits = ["0","1","2","3","4","5","6","7","8","9"]

def intcastable(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False




class Expression:
    #Initializer for composite expression
    def __init__(self, op="w", expList=[], parent=None):
        '''
        Initializes a composite expression
        Parameters:
            self: Object being initialized
            op: operation the expression contains
            explist: List of expressions the expression contains (assumed to be ordered properly; for example, it would be [2,1] for 2+1 and [1,2] for 1+2)
        '''
        self.expList = expList #Stores expressions that this expression comprises
        self.op = op
        self.parent = parent

    def print_tree(self,depth=0):
        currentNode = self
        if currentNode.op in binOps:
            print( ("    "*depth) + currentNode.op + " connects ")
        else:
            print(("    "*depth) + currentNode.op )

        for node in currentNode.expList:
            node.print_tree(depth+1)




    def find_working(self):
        currentNode = self
        if(currentNode.op == "w"):
            return currentNode
        if len(currentNode.expList) > 0:
            for node in currentNode.expList:
                fw = node.find_working()
                if not (fw == None):
                    return fw
        return None

    def add_child(self,node):
        node.parent = self
        self.expList += [node]

    def detach_child(self,op):
        for index, node in enumerate(self.expList):
            if node.op == op: 
                toDetachIndices = index
        del self.expList[index]

    def scrub_working(self):
        currentNode = self
        currentNode.detach_child("w")
        for node in currentNode.expList:
            node.detach_child("w")


    def youngestLPAC(self,node,thisop):#child of youngest lower precedence ancestor
        currentNode = node
        while True:
            if currentNode.parent == None:
                return currentNode
            if currentNode.parent.op in binOps:
                if binOps[currentNode.parent.op] < binOps[thisop]:
                    return currentNode
            currentNode = currentNode.parent

    def changeNodeParents(expList, newParent):
        for i in expList:
            i.parent = newParent



    def add(self,added):
        workingNode = self.find_working()
        if workingNode == None:
            print("something very bad has happened")
        elif workingNode.parent == None:
            if added in binOps:
                thisop = Expression(added,[],None)
                first = Expression("e",[],None)
                second = Expression("e",[],None)
                w = Expression("w",[],None)
                second.add_child(w)
                thisop.add_child(first)
                thisop.add_child(second)
                Expression.changeNodeParents(thisop.expList,self)
                self.__dict__ = copy.copy(thisop.__dict__)
            if added in digits:
                thisdig = Expression(added,[],None)
                w = Expression("w",[],None)
                thisdig.add_child(w)
                thisdig.expList[0].parent = self #self will 'become' thisdig, but pointer will remain fixed
                self.__dict__ = copy.copy(thisdig.__dict__)
        elif intcastable(workingNode.parent.op) and added in digits:
                workingNode.parent.op += added
        elif workingNode.parent.op == "e" and added in digits:
                workingNode.parent.op = added
        elif added in binOps:
            YLPAC = workingNode.youngestLPAC(workingNode,added)
            treeflip = False
            if(YLPAC == self):
                treeflip = True              
            if treeflip:
                self.scrub_working()
                top = Expression(added,[],None)
                second = Expression("e",[],None)
                w = Expression("w",[],None)
                second.add_child(w)
                top.add_child(copy.copy(self))
                top.add_child(second)
                Expression.changeNodeParents(top.expList,self)
                self.__dict__ = copy.copy(top.__dict__)
            else:
                YLPAC.scrub_working()
                medium = Expression(added,[],None)
                second = Expression("e",[],None)
                w = Expression("w",[],None)
                second.add_child(w)
                medium.add_child(copy.copy(YLPAC))
                medium.add_child(second)
                YLPAC.__dict__= copy.copy(medium.__dict__)
        else:
            print("that case is not supported")


e =  Expression()
e.add("3")
e.add("+")
e.add("*")
e.add("5")
e.print_tree()

