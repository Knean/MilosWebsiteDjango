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


    def buy(self,amount, startNode = None, user = 1, create = True): #look up model inheritance
        import pandas as pd
        import numpy as np
        import sys
        print(f"buying {amount} for the user: {user} in the tree: {self.id}")
        def updateParents(node, origin):   
            if parentOf(node.child1,origin):
                node.child1Value +=1                                         
            else:
                node.child2Value +=1
            soldBefore = node.childrenMissing == 0           
            child1Value = min(node.child1Value,31)
            child2Value = min(node.child2Value,31)
            node.childrenMissing = 62 - child1Value - child2Value
            soldNow = node.childrenMissing == 0 
            if (soldNow and not soldBefore):# if the node just got sold
                node.sold = True 
            node.changed =True  
            return node
        def getFirstFreeNode(startNode, id, tree_id, user, nodeSet):
            for node in nodeGenerator(startNode):
                if node not in nodeSet.index:
                    generator = nodeGenerator(node)
                    next(generator)
                    #### flawed if there are multiple trees
                    row = {
                        'id': id,
                        'sold':False,
                        'changed':True,
                        'tree_id': tree_id, # should be a varaiable
                        'childrenMissing': 62,
                        'userName': user,##fix this
                        'child1': next(generator),
                        'child1Value': 0,
                        'child2':next(generator),
                        'child2Value': 0,
                        'value': 299,    
                        }
                    nodeSet.loc[node] = row
                    return nodeSet.loc[node]
        tree = self
        nodes = tree.node_set.all().values_list()
        nodeSet = pd.DataFrame.from_records(
            nodes, 
            columns = ["id","tree_id","childrenMissing","number","userName","child1","child1Value","child2","child2Value"],
            index="number")
        nodeSet["value"]= nodeSet["child1Value"] + nodeSet["child2Value"] ### legacy -> remove later
        nodeSet.insert(1,"changed", False)
        nodeSet.insert(1,"sold", False) 
        try:     
            id = Node.objects.all().order_by("-id").first().id + 1 
        except:
            id = 1
        from tree.utilities import childOf, nodeGenerator, getIndex
        #assign startNode
        #tree not empty and user has some nodes in it find the lowest one
        startNode = nodeSet.loc[nodeSet.userName == user].index.min()
        if pd.isnull(startNode):
            startNode = None
        #only valid for newcomer to the tree 
        if startNode == None and not nodeSet.empty:            
            smallest = nodeSet.loc[nodeSet.childrenMissing != 0, "childrenMissing"].min()            
            allSmalls = nodeSet.loc[nodeSet.childrenMissing == smallest,:].copy()
            allSmalls["index"] = allSmalls.apply(lambda node: getIndex(node.name, 1), axis=1) #is it one?
            allSmalls.sort_values("index", inplace = True)            
            payNode = allSmalls.iloc[0]
            id += 1
            node = getFirstFreeNode(payNode.name,id,tree.id,user,nodeSet)#naive as first node is not the best node
            amount -=1
            #find the first free child of the easiest to pay Node
            startNode = node.name #payNode.name
            #update parents
            ancestors = [node["parent"] for node in parentGenerator(startNode)]  
            nodeSet.loc[ancestors] = nodeSet.loc[ancestors].apply(updateParents, args = [startNode], axis = 1)
            
        #if the tree is empty the start node is 1
        if startNode == None and nodeSet.empty:
            id += 1
            row = {
                'id': id,
                'sold':False,
                'changed':True,
                'tree_id': tree.id, 
                'childrenMissing': 62,
                'userName': user,
                'child1': 2,
                'child1Value': 0,
                'child2': 3,
                'child2Value': 0,
                'value': 299,    
                }
            nodeSet.loc[1] = row
            startNode = 1
            amount -= 1

        #while loop starts here
        while amount > 0:
            nodeSet.sort_values(by = "childrenMissing", inplace =True)
            mask1 = nodeSet.childrenMissing != 0
            mask2 = nodeSet.apply(lambda node : childOf(startNode, node.name) , axis=1) #pointless?
            mask4 = nodeSet.userName == user 
            smallest = nodeSet.loc[mask1 & mask2 & mask4, "childrenMissing"].min()#only pay out its own nodes, if none available, find next one that is
            mask3 = nodeSet.childrenMissing == smallest   
                  
            allSmalls = nodeSet.loc[mask1 & mask2 & mask3 & mask4,:].copy()
            allSmalls["index"] = allSmalls.apply(lambda node: getIndex(node.name, startNode), axis=1)
            allSmalls.sort_values("index", inplace = True)
            #the node that is easiest to pay out given the parameters
            if not allSmalls.empty:
                payNode = allSmalls.iloc[0]
            else:
                #if empty -> find first free node of the startNode to buy and set as the payNode 
                id+= 1
                payNode = getFirstFreeNode(startNode,id,tree.id,user,nodeSet)
                           
                amount -=1
                ancestors = [node["parent"] for node in parentGenerator(payNode.name)]  
                nodeSet.loc[ancestors] = nodeSet.loc[ancestors].apply(updateParents, args = [payNode.name], axis = 1)
         
            targetValue = 31
            # ideally each child would be eat least 31
            children = pd.DataFrame([
                [payNode.child1, payNode.child1Value],
                [payNode.child2, payNode.child2Value]],
                columns = ["number","value"])
            children["index"] = children.apply(lambda kid: getIndex(kid.number, payNode.name), axis = 1)
            children["pay"] = 0                 
            children.sort_values(by=["value", "index"], inplace = True)      
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
            children.iloc[[0],[-1, -3]] +=leftover        
            generator = nodeGenerator(payNode.name)
            child = 0
            childToggle ={0:1,1:0}
            childrenStacks = [[],[]]
            pay = children.pay.sum()    
            #invest points
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
                id +=1 
                row = {
                    'id': id,
                    'sold':False,
                    'changed':True,
                    'tree_id': tree.id, 
                    'childrenMissing': 62,
                    'userName': user, 
                    'child1': next(generator),
                    'child1Value': 0,
                    'child2':next(generator),
                    'child2Value': 0,
                    'value': 299,    
                    }
                nodeSet.loc[node] = row
            #update parents 
            print(f"sold node: {payNode.name}, updating parents")                 
            for node in childrenStacks:                   
                    ancestors = [node["parent"] for node in parentGenerator(node)]                                        
                    nodeSet.loc[ancestors] = nodeSet.loc[ancestors].apply(updateParents, args = [node], axis = 1)
        #make a copy of all the "sold" nodes   
        print("updating the database")      
        newAndUpdatedIDList = nodeSet.loc[
            nodeSet.changed == True,[
                "id",
                "tree_id",
                "childrenMissing",
                "userName",
                "child1",
                "child1Value",
                "child2",
                "child2Value",
                #"number"
                ]].reset_index().rename(columns={"userName": "user_id","id":"pk"}).copy()
        #update the json field
        #sold dictionary that is returned at the end
        sold = nodeSet.loc[nodeSet.sold == True,["sold","userName"]].groupby("userName").count().copy()
        sold = sold.reset_index().to_dict(orient="record" )
        sold = {item["userName"]:item["sold"] for item in sold}
        #add some fields that are needed in the front end
        nodeSet.sort_index(inplace = True)
        nodeSet["parent"] = nodeSet.apply(lambda node: findParent(node.name), axis = 1)
        nodeSet.iloc[0,-3] = ""
        biggest_number = nodeSet.iloc[-1].name
        nodeSet["x"]= nodeSet.apply(lambda node: getX(node.name), axis = 1)
        nodeSet["y"]= nodeSet.apply(lambda node: getY(node.name,biggest_number), axis = 1)          
        users = User.objects.only("username","id").values()
        comprehensiveUsers = {user["id"]:user["username"] for user in users}
        nodeSet["userName"] = nodeSet["userName"].apply(lambda user: comprehensiveUsers[user])
        self.json_string =nodeSet.loc[:,["userName","child1","child1Value","child2","child2Value","childrenMissing","parent","x","y"]].reset_index().to_json(orient="records")
        #add parent, x, y fields
        #sqlite allows only 999 elements in a query 
        while not newAndUpdatedIDList.empty:           
            nodes = newAndUpdatedIDList[:950]  
            #sql delete
            oldSet = Node.objects.filter(pk__in = nodes.pk.to_list())                            
            oldSet.delete()       
            #sql create
            NodeList = [Node(**node) for node in nodes.to_dict(orient="record")]            
            Node.objects.bulk_create(NodeList)#newAndUpdatedIDList[:950].to_dict(orient="record")) 
            newAndUpdatedIDList.drop(nodes.index, inplace = True)  
        self.save()
        return sold

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
