from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import F
from .utilities import *
from timeit import default_timer as timer
import math
# Create your models here.
class Tree (models.Model):
    name = models.CharField("", max_length=50)

    class Meta:
        verbose_name = "Tree "
        verbose_name_plural = "Trees"

    def __str__(self):
        return self.name
    def updateParents(self, Node): 
        currentNodeNumber = Node.number
        while True:
            parent = findParent(currentNodeNumber)
            if parent:
                #self.node_set.get(number=parent).children ADD CHILDRNE ATTRIBUTES
                tree[parent].children[currentNodeNumber] +=1
                tree[parent].calculateNodes()
                currentNodeNumber  = findParent(currentNodeNumber)
            else:
                return


    def buy(self,amount, startNode = None, user = User.objects.first()):
        nodesToPay = self.findNodeToPay(amount = amount, user = user)
        
        buyList = []
        tree = self.node_set.all().order_by("-id")
        
        if startNode == None:
            startNode = getFreeNode() 
        try:
            id = tree[0].id
        except:
            id = 1
        while nodesToPay and amount>0:
            currentNodeNumber = nodesToPay.pop(0)
            print(currentNodeNumber, " this is the node we're working on")
            currentNode = Node.objects.filter(number=currentNodeNumber)
            try:
                untilPay = Node.objects.get(number=currentNodeNumber).childrenMissing
            except:
                untilPay = 63 
            if currentNode.exists():
                currentNode = currentNode.first()
                child1 = currentNode.child1Value
                child2 = currentNode.child2Value
                child1Value = currentNode.child1Value
                child2Value = currentNode.child2Value
                smallerChild = currentNode.child1 if child1Value - child2Value < 0 else currentNode.child2  
                print (smallerChild , "this is the smaller child")              
                difference = abs(child1Value - child2Value)
                generator = nodeGenerator(smallerChild)


                while difference >0 and amount > 0 and untilPay > 0:# and node is not paid????
                    nodeNumber = next(generator)
                    if not tree.filter(number = nodeNumber).exists() and not any(filter(lambda x:x.number == nodeNumber, buyList)):
                        difference -= 1
                        amount -=1
                        untilPay -= 1
                        id += 1
                        buyList.append(
                            Node(tree = self, id = id, user =user, number = nodeNumber)
                        )

            
                #generator
                #if not in tree
                # generator next
                # else add to buy list
                #child one or two?
                #get the node
                #while lower child < bigger child and ammount > 0
                # while 
                
            generator = nodeGenerator(currentNodeNumber)
          
            
            while amount > 0 and untilPay>0:
                nodeNumber = next(generator)
                #not in tree or in buy list
                if not tree.filter(number = nodeNumber).exists() and not any(filter(lambda x:x.number == nodeNumber, buyList)):
                    
                    amount -=1
                    untilPay -= 1
                    id += 1
                    buyList.append(
                        Node(tree = self, id = id, user =user, number = nodeNumber))
        
        Node.create(buyList,tree)
    
    def findFreeChild(self, startNode):
        generator = nodeGenerator(startNode)
        tree = Node.objects.all()
        while True:
            number = next(generator)
            node = tree.filter(number = number)
            if not node.exists():
                return number

    
    
    def findNodeToPay(self, startNode = 1, amount = 100, user = None ):
        payoutOrder = []
        completed = []
        
        

        nodesList = Node.objects.all().exclude(childrenMissing =0).order_by("childrenMissing")
        if user:
            nodesList = nodesList.filter(user = user)

        
        #finds the first node if user has zero nodes so far
        if not nodesList.exists() and Node.objects.all().exists():
            easiestNodeInWholeTree = self.findNodeToPay(amount = 1)[0]
            startNode = self.findFreeChild(easiestNodeInWholeTree)
        generator = nodeGenerator(startNode)
            
        while amount>0 and nodesList.exists():
            nodesList = nodesList.exclude(childrenMissing__in = completed)
            if nodesList.exists():
                easiest = nodesList[0].childrenMissing
                easyNodes = list(nodesList.filter(childrenMissing = easiest))
                completed.append(easiest)
                
                easyNumbers = [node.number for node in easyNodes]
               
                generator = nodeGenerator(startNode)
                while easyNumbers:
                    number = next(generator)
                    if number in easyNumbers:                        
                        payoutOrder.append(number)
                        easyNumbers.remove(number)
                        #print("this bit is running")
                        amount -= 1
        #no more nodes now what
        while amount >0:
           
            payoutOrder.append(next(generator))
            amount -= 1
        print(payoutOrder, "payoutorder")
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
    #def create(cls,tree,owner,number):



    def create(cls,nodes, tree):
     
        createNodes = []        
        childList =[]

        # move this bit to the init section of the class
        for node in nodes:           
            #populate children fields 
            childGenerator = nodeGenerator(node.number)   
            next(childGenerator)         
            node.child1 = next(childGenerator)
            node.child2 = next(childGenerator)          
      

        createNodes = [node for node in nodes]        
        tree = Node.objects.all()   

        #update all parent nodes
       
        for node in nodes: 
            #print(node, " this node is being updated")
            generator = parentGenerator(node.number)
            
            for parent in generator:
                
                try:
                    parentNode = next(m for m in createNodes if m.number == parent["parent"])
                except:
                    parentNode = tree.get(number = parent["parent"])
                    #print(parentNode, "adding this to create list")
                    createNodes.append(parentNode)

                if parentNode.child1 == parent["child"]:
                    parentNode.child1Value +=1                                         
                if parentNode.child2 ==  parent["child"]:
                    parentNode.child2Value +=1 
                    
        for node in createNodes:
            node.updateChildrenMissing()

        #update the database
        
        newAndUpdatedIDList = [node.id for node in createNodes]
        #print (createNodes, "nodes about to be saved")
        #sqlite allows only 999 elements in a query
        while(newAndUpdatedIDList):
            fraction = newAndUpdatedIDList[:950]
            del newAndUpdatedIDList[:950]
            oldSet = Node.objects.filter(pk__in = fraction)
            oldSet.delete()

            Node.objects.bulk_create(createNodes[:950]) 
            del createNodes[:950]
        
    def updateChildrenMissing(self):
        #call save manually
        child1Value = self.child1Value
        child1Value = child1Value if child1Value <31 else 30

        child2Value = self.child2Value
        child2Value = child2Value if child2Value <31 else 30

        self.childrenMissing = 60 - child1Value - child2Value


    
    class Meta:
        verbose_name = "A node"
        verbose_name_plural = "Nodes"

    def __str__(self):
        return self.tree.name + str(self.number) +" node"
class ChildNode(models.Model):
    parentNode = models.ForeignKey("Node", verbose_name="Child", on_delete=models.CASCADE)
    number = models.IntegerField()
    children = models.IntegerField(default = 0)
    #def get_absolute_url(self):
        #return reverse("_detail", kwargs={"pk": self.pk})
