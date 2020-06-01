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
        paidcount = 0
        def updateParents(nodeNumber):
            parentspaid = 0
            for nodePair in parentGenerator(nodeNumber):
               
                parentNodeNumber = nodePair["parent"]
                try:
                    parentNode = buyDict[parentNodeNumber]
                except(KeyError):
                    #never happens
                    print(nodeNumber)
                    parentNode = tree.get(number = parentNodeNumber)
                                           
                if parentNode.child1 == nodePair["child"]:
                    parentNode.child1Value +=1                                         
                if parentNode.child2 ==  nodePair["child"]:
                    parentNode.child2Value +=1 
                
                
                buyDict[parentNodeNumber] = parentNode
                parentspaid += parentNode.updateChildrenMissing()

            return parentspaid

        buyDict = {}
        nodesToPay = self.findNodeToPay(amount = amount, user = user)
        nodesDict = {node.number: node for node in nodesToPay}
        allRelevantNodes = []
        buyList = []
        
        tree = Node.objects.all().order_by("-id")
        #tree = tree.filter(user = user)
        #id doesnt auto increment in sqlite  
        try:
            id = tree.first().id + 1
        except:
            id = 1
        tree = self.node_set.all()

        #calculate find smaller child
        while nodesToPay and amount>0:
            
            
            # print(currentNodeNumber, " this is the node we're working on")
            #why tho?
            currentNode = nodesToPay.pop(0)
            try:
                currentNode = buyDict[currentNode.number]
            except KeyError:
                pass
            currentNodeNumber = currentNode.number
            
            # buyNodes could be a dictionary would be sexier for adding parents
             
            
            untilPay = currentNode.childrenMissing
            if not tree.filter(number = currentNodeNumber).exists() and currentNodeNumber not in buyDict:
                #pass
                untilPay += 1
                #move this logic onto the class
                # this is broken
            #if node exists figure out which child branch is smaller

            child1 = currentNode.child1
            child2 = currentNode.child2
            child1Value = currentNode.child1Value
            child2Value = currentNode.child2Value
            smallerChild = child1 if child1Value <= child2Value else child2  

            childrenDict = {child1:child1Value, child2:child2Value}

            difference = abs(child1Value - child2Value)  

                
            generator = nodeGenerator(currentNodeNumber)

            #make this less retarded
            #createnew node and keep updating its children
            #add all parent nodes automatically to the buy list
            while amount > 0 and untilPay>0:
                nodeNumber = next(generator)               
                #in the tree
                #not in tree but in buylist
                #not in tree or in buylist but on a wrong branch
                #generator doesnt reset when branches equalize
                #create new node if it is not already in the tree or the buy list    
                # any(list(filter (lambda x:x.number == nodeNumber, buyList))):          
                if not tree.filter(number = nodeNumber).exists() and not nodeNumber in buyDict:
                    try:
                        newNode = nodesDict[nodeNumber]
                        try:
                            value = int(newNode.id)
                        except ValueError:
                            id +=1
                            newNode.id = id 
                            
                        #check if id is retarded
                    except KeyError:
                        # it is not in nodesdict or buydict
                        #createnew one
                        id +=1
                        theTree = self
                        newNode = Node.create_object(
                            tree = theTree,
                            id = id, 
                            user =User.objects.get(id = user), 
                            number = nodeNumber)
                    try: 
                        parent = identifyParent(newNode.number, *childrenDict)
                    except:
                        parent = currentNodeNumber 
                           
                    if difference == 0:
                        #if parent is not paid
                        #get the right parent
                        # if parent is paid : continue
                        # 



                        #cemu ovo preseravanje kad vec imamo child value?????????????
                        #it could be in the tree
                        # or it could not exist
                        #am i overcomplicating?
                        # maybe use a function that gets the node instead of copying the smae logic over and over again
                        #if parent of child value < 31
                        #ipak mi treba dictionary
                        # plus jedan u dicitonary

                        if  parent == currentNodeNumber or childrenDict[parent] < 31:
                            try:
                                childrenDict[parent] += 1
                            except KeyError:
                                pass
                            buyDict[newNode.number] = newNode
                            if create == False:
                                return newNode
                            paidcount += updateParents(newNode.number)
                            amount -=1                        
                            untilPay -= 1
                        #add all parents here
                        #create fetchallparentesmethod???

                    #if child nodes are not the same, append to smaller child
                    #child of could be a node method

                    if difference >0 and childOf(smallerChild, nodeNumber):
                        
                        childrenDict[parent] += 1
                        difference -= 1 
                        amount -=1                        
                        untilPay -= 1
                        buyDict[newNode.number] = newNode
                        if create == False:
                            return newNode
                        paidcount += updateParents(newNode.number)
                        if difference == 0:
                            #reset generator as we may have skipped a few nodes
                            generator = nodeGenerator(currentNodeNumber)
                        


                #add parents
          

                 
            # do the parent update for every node in buydict
            # makes sure we have an up to date number of childrenmissing
            # parents are not in buy dict and they should be
            # when adding a single element add all parents                    

        
        #get values from dictionary
        Node.create(buyDict)
        print ( paidcount, " sold nodes")
        return paidcount
    #not used anywhere
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
