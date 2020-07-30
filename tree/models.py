from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import F
from .utilities import *
from timeit import default_timer as timer
import math
# Create your models here.
class Tree (models.Model):

  
    name = models.CharField("", max_length=50, blank=True)
    json_string = models.TextField("", null=True)
    class Meta:
        verbose_name = "Tree "
        verbose_name_plural = "Trees"

    def __str__(self):
        return self.name


    def buy(self,amount, startNode = None, user = 1, create = True):
        import pandas as pd
        import numpy as np
        import sys
        tree = Tree.objects.first()
        nodes = tree.node_set.all().values_list()
        nodeSet = pd.DataFrame.from_records(
            nodes, 
            columns = ["id","tree_id","childrenMissing","number","user_id","child1","child1Value","child2","child2Value"],
            index="number")
        nodeSet["value"]= nodeSet["child1Value"] + nodeSet["child2Value"] ### naive
        nodeSet.insert(1,"changed", False)
        nodeSet.insert(1,"sold", False)

        id = nodeSet.id.max() + 1 #naive gotta consider other trees
        #gotta test this
        id = id if not np.isnan(id) else 1

        from tree.utilities import childOf, nodeGenerator, getIndex
        #randomly picked start index
        startNode = 1   ###################### # start node can only be picked but not created

        #while loop starts here
        nodeSet.sort_values(by = "childrenMissing", inplace =True)
        mask1 = nodeSet.childrenMissing != 0
        mask2 = nodeSet.apply(lambda node : childOf(startNode, node.name) , axis=1)
        smallest = nodeSet.loc[mask1 & mask2, "childrenMissing"].min()
        allSmalls = nodeSet.loc[nodeSet.childrenMissing == smallest,:].copy()
        allSmalls["index"] = allSmalls.apply(lambda node: getIndex(node.name, startNode), axis=1)
        allSmalls.sort_values("index", inplace = True)
        payNode = allSmalls.iloc[0]

        # this amount is the number of nodes the user buys
        targetValue = 31
        # ideally each child would be eat least 31
        children = pd.DataFrame([
            [payNode.child1, payNode.child1Value],
            [payNode.child2, payNode.child2Value]],
            columns = ["number","value"])
        children["index"] = children.apply(lambda kid: getIndex(kid.number, payNode.name), axis = 1)
        children["pay"] = 0
        #children.sort_values("index")
        children.iloc[1,-3] = 3
        children.sort_values(by=["value", "index"], inplace = True) #index not necessary?

        #amount = 20 amount comes from function parameter

        #equalize children
        childDifference = children.iloc[1].value - children.iloc[0].value  #this might be pointless because the smaller one is always at the top
        valueMissing = max(targetValue - children.iloc[0].value, 0)
        pay = min(childDifference,valueMissing, amount)        
        amount -= pay
        children.iloc[0,-1]+= pay
        children.iloc[0,-3]+= pay
        

        # attempt to reach target
        children.sort_values(by=["index"], inplace = True)
        valueMissing = max(targetValue - children.iloc[0].value, 0) *2
        pay = min(amount, valueMissing)
        amount -= pay
        half = int(pay/2)
        children.iloc[[0,1],[-1, -3]] += half        
        leftover = pay - (half*2)
        children.iloc[[0],[-1, -3]] +=leftover #leftover is 1 or 0


        generator = nodeGenerator(payNode.name)
        child = 1
        childToggle ={0:1,1:0}
        childrenStacks = [[],[]]
        pay = children.pay.sum()
        while pay > 0 :   
            child = childToggle[child]    
            potentialNode = next(generator)    
            if not potentialNode in nodeSet.index:        
                if len(childrenStacks[child]) < children.iloc[child,-1]:
                    childrenStacks[child].append(potentialNode)
                    pay -= 1     
        
        childrenStacks = childrenStacks[0] + childrenStacks[1]              
        #generate nodes
        for node in childrenStacks:
            generator = nodeGenerator(node)
            next(generator) 
            id +=1 #### flawed if there are multiple trees
            row = {
                'id': id,
                'sold':False,
                'changed':True,
                'tree_id': 1, # should be a varaiable
                'childrenMissing': 62,
                'user_id': 1,
                'child1': next(generator),
                'child1Value': 0,
                'child2':next(generator),
                'child2Value': 0,
                'value': 299,    
                }
            nodeSet.loc[node] = row
        #update parents
        from tree.utilities import parentGenerator
        for node in childrenStacks:
            parentspaid = 0
            for nodePair in parentGenerator(node):
                # update child Value
                parentNodeNumber = nodePair["parent"]
                parentNode = nodeSet.loc[parentNodeNumber] #reference to the node
                if parentNode.child1 == nodePair["child"]:
                    parentNode.child1Value +=1                                         
                if parentNode.child2 ==  nodePair["child"]:
                    parentNode.child2Value +=1
                    
                #update childrenMissing value
                soldBefore = self.childrenMissing == 0            
                child1Value = parentNode.child1Value
                child1Value = child1Value if child1Value <32 else 31
                child2Value = parentNode.child2Value
                child2Value = child2Value if child2Value <32 else 31            
                parentNode.childrenMissing = 62 - child1Value - child2Value
                soldNow = self.childrenMissing == 0
                
                if (soldNow and not soldBefore):# if the node just got sold
                    parentNode.sold = True


        #out of the main loop
        #         
        newAndUpdatedIDList = nodeSet.loc[
            nodeSet.changed == True,[
                "id",
                "tree_id",
                "childrenMissing",
                "user_id",
                "child1",
                "child1Value",
                "child2",
                "child2Value"]].copy()
        
        #save results (solds) before destroying the table
        #sqlite allows only 999 elements in a query         
        while(newAndUpdatedIDList):           
            nodes = newAndUpdatedIDList[:950]  
            #sql delete
            oldSet = Node.objects.filter(pk__in = nodes.id.to_list())                            
            oldSet.delete()       
            #sql create            
            Node.objects.bulk_create(newAndUpdatedIDList[:950].to_dict(orient="record")) 
            newAndUpdatedIDList.drop(nodes.index, inplace = True)  
            
    def findFreeChild(self, startNode):
        #returns number only
        generator = nodeGenerator(startNode)
        tree = Node.objects.all()
        while True:
            number = next(generator)
            node = tree.filter(number = number)
            if not node.exists():
                return number

    
    
    def findNodeToPay(self, startNode = 1, amount = 100, user = None  ):
        tree = self.node_set.all().order_by("-id")
        
        try:
            id = tree[0].id
        except:
            id = 1
        payoutOrder = []
        completed = []       
        

        nodesList = self.node_set.all().exclude(childrenMissing =0).order_by("childrenMissing")
        if user:
            nodesList = nodesList.filter(user = user)

        
        #finds the first node if user has zero nodes so far
        if not nodesList.exists() and self.node_set.all().exists():
            easiestNodeInWholeTree = self.findNodeToPay(amount = 1)[0]
            easiestOwnerInWholeTree = easiestNodeInWholeTree.user.id
            
            #asignnode
            #reuse the buy logic
            #add for user perhaps?
            #
            startNode = self.buy(user = easiestOwnerInWholeTree, amount = 1, create = False).number
        
        generator = nodeGenerator(startNode)  
        while amount>0 and nodesList.exists():
            nodesList = nodesList.exclude(childrenMissing__in = completed)
            if nodesList.exists():
                easiest = nodesList[0].childrenMissing
                #first element is the one that is easiest to buy
                easyNodes = nodesList.filter(childrenMissing = easiest)
                #get all nodes with the same amount of children missing
                easyNodeDict = {node.number:node for node in easyNodes}
                completed.append(easiest)
                # keep track of the completed levels of nodes                
                easyNumbers = [node.number for node in easyNodes]
               
                generator = nodeGenerator(startNode)
                # find out which node should be done first and append to the payoutorder
                while easyNumbers:
                    number = next(generator)
                    if number in easyNumbers:                        
                        payoutOrder.append(easyNodeDict[number])
                        easyNumbers.remove(number)                       
                        amount -= 1
        #no more nodes now what
        while amount >0:
            number = next(generator)
            newNode = Node.create_object(
                #it has a user?
                
                tree = self,
                user =User.objects.get(id = user), 
                number = number) 
            payoutOrder.append(newNode)
            amount -= 1
        #print(payoutOrder, "payoutorder")
        return payoutOrder


class Node (models.Model):   
    tree = models.ForeignKey( "Tree",  on_delete=models.CASCADE, verbose_name ="related tree",)
    childrenMissing = models.IntegerField(default = 62)
    number = models.IntegerField(default = 1)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    child1 = models.IntegerField()
    child1Value = models.IntegerField(default = 0)
    child2 = models.IntegerField()
    child2Value = models.IntegerField(default = 0)
    
    @classmethod
    def create_object(cls,tree,user,number, id = None):
        generator = nodeGenerator(number)
        next(generator)
        return cls(
            tree = tree,
            user = user,
            number = number,
            child1 = next(generator),
            child2 = next(generator),
            child1Value = 0,
            child2Value = 0,
            childrenMissing = 62,
            id = id if id else "missing",
              )


    @classmethod
    def create(cls,nodesDict):
        
        newAndUpdatedIDList = [node.id for node in nodesDict.values()]
        createNodes = [node for node in nodesDict.values()] 
        
        #sqlite allows only 999 elements in a query         
        while(newAndUpdatedIDList):           
            
            oldSet = Node.objects.filter(pk__in = newAndUpdatedIDList[:950])
            del newAndUpdatedIDList[:950]            
            oldSet.delete()
            
            
            
            Node.objects.bulk_create(createNodes[:950]) 
            
            del createNodes[:950]
        
    def updateChildrenMissing(self):
        #this is naive
        soldBefore = self.childrenMissing == 0
        child1Value = self.child1Value
        child1Value = child1Value if child1Value <32 else 31

        child2Value = self.child2Value
        child2Value = child2Value if child2Value <32 else 31

        self.childrenMissing = 62 - child1Value - child2Value

        soldNow = self.childrenMissing == 0
        if ( not soldBefore and soldNow):
            return 1
        else:
            return 0


    
    class Meta:
        verbose_name = "A node"
        verbose_name_plural = "Nodes"

    def __str__(self):
        return "number: {} id: {} , tree: {}".format(self.number, self.id, self.tree)
        self.tree.name + str(self.number) +" node"
class ChildNode(models.Model):
    parentNode = models.ForeignKey("Node", verbose_name="Child", on_delete=models.CASCADE)
    number = models.IntegerField()
    children = models.IntegerField(default = 0)
    #def get_absolute_url(self):
        #return reverse("_detail", kwargs={"pk": self.pk})
