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
        self.index = 0 if op == "w" else None

    def print_tree(self,depth=0):
        currentNode = self
        if currentNode.op in binOps:
            print( ("    "*depth) + currentNode.op+("_"+str(currentNode.index) if currentNode.op=="w" else "") + " connects ")
        else:
            print(("    "*depth) + currentNode.op+("_"+str(currentNode.index) if currentNode.op=="w" else "") )

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

    def move_working(self, newPlace, index=0):
        self.scrub_working()
        w = Expression("w",[],None)
        w.index = index
        newPlace.add_child(w)

    def add_child(self,node):
        node.parent = self
        self.expList += [node]

    def detach_child(self,op):#will only detach the last node with matching op
        toDetachIndex = -1
        for index, node in enumerate(self.expList):
            if node.op == op: 
                toDetachIndex = index
        if not (toDetachIndex == -1):
            del self.expList[toDetachIndex]

    def scrub_working(self):#removes all w nodes from a tree
        currentNode = self
        currentNode.detach_child("w")
        for node in currentNode.expList:
            node.scrub_working()


    def youngestLPAC(self,node,thisop):#child of youngest lower precedence ancestor
        currentNode = node
        while True:
            if currentNode.parent == None:
                return currentNode
            if currentNode.parent.op in binOps:
                if binOps[currentNode.parent.op] < binOps[thisop]:
                    return currentNode
            currentNode = currentNode.parent

    def changeNodeParents(expList, newParent): #may have working moving issues
        for i in expList:
            i.parent = newParent

    def backspace(self):
        workingNode = self.find_working()
        if workingNode == None:
            print("something very bad has happened")
        elif workingNode == self:
            print("backspace called on an empty expression; expression unchanged")
        elif intcastable(workingNode.parent.op) and workingNode.index>0: #deal with being at the beginning of a number later
            if(len(workingNode.parent.op) == 1):
                workingNode.parent.op = "e"
            else:
                workingNode.parent.op = workingNode.parent.op[:workingNode.index-1]+workingNode.parent.op[workingNode.index:]
            workingNode.index -= 1
        else:
            print("that case is not yet implemented")

    def leftmost(node):
        if len(node.expList) < 2: #can't go left if there is only down
            return node
        return Expression.leftmost(node.expList[0])
    
    def is_leftnode(node):
        if node.parent == None:
            return None
        return True if node.parent.expList.index(node)==0 else False
    
    def first_rightward_ancestor(node):
        if node.parent == None:
            return None
        if not Expression.is_leftnode(node):
            return node.parent
        return Expression.first_rightward_ancestor(node.parent)
                
    def to_left(self):
        w = self.find_working()
        working = w.parent
        lm = Expression.leftmost(working)

        if Expression.leftmost(self) == w:
            return working
        elif lm == working:
            return Expression.first_rightward_ancestor(working)
        else:
            return lm

    def shift_left(self):
        self.move_working(self.to_left(),1)

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
                Expression.changeNodeParents(thisop.expList,self)#because self  will 'become' thisop, but self's pointer will remain fixed
                self.__dict__ = copy.copy(thisop.__dict__)#shalllow copy because we want the pointers to maintain the hierarchy's connections
            if added in digits:
                thisdig = Expression(added,[],None)
                w = Expression("w",[],None)
                w.index = 1
                thisdig.add_child(w)
                thisdig.expList[0].parent = self #self will 'become' thisdig, but self's pointer will remain fixed
                self.__dict__ = copy.copy(thisdig.__dict__) #shallow copy because we want the pointers to maintain the hierarchy's connections
        elif intcastable(workingNode.parent.op) and added in digits:
                number = workingNode.parent.op
                before, after = number[:workingNode.index],number[workingNode.index:]
                workingNode.parent.op = before+added+after
                workingNode.index += 1
        elif workingNode.parent.op == "e" and added in digits:
                workingNode.parent.op = added
                workingNode.index += 1
        elif added in binOps:
            parent = workingNode.parent
            if intcastable(parent.op) and 0<workingNode.index<len(parent.op):
                print("that case is not yet implemented") #insertion is hard
            elif workingNode.index == 0:
                YLPAC = workingNode.youngestLPAC(workingNode,added)
                treeflip = False
                if(YLPAC == self):
                    treeflip = True              
                if treeflip:
                    self.scrub_working()
                    top = Expression(added,[],None)
                    first = Expression("e",[],None)
                    w = Expression("w",[],None)
                    first.add_child(w)
                    top.add_child(first)
                    top.add_child(copy.copy(self))
                    Expression.changeNodeParents(top.expList,self)
                    self.__dict__ = copy.copy(top.__dict__)
                else:
                    YLPAC.scrub_working()
                    medium = Expression(added,[],None)
                    first = Expression("e",[],None)
                    w = Expression("w",[],None)
                    first.add_child(w)
                    medium.add_child(first)
                    medium.add_child(copy.copy(YLPAC))
                    YLPAC.__dict__= copy.copy(medium.__dict__)
            elif workingNode.index == 1:
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
                print("i don't think this should happen")

        else:
            print("that case is not yet supported")

    


e =  Expression()
e.add("*")
e.add("3")
e.add("2")
e.add("+")
e.add("^")
e.add("4")
thirtytwo = e.expList[0].expList[1]
e.move_working(thirtytwo,1)
e.add("1")
e.print_tree()
e.backspace()
e.print_tree()
