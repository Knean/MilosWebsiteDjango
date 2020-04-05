from .models import Node, Tree
from .utilities import *
class BuyObject():
    def __init__(self, amount, user, tree):
        self.amount = amount
        self.user = user
        self.tree = tree


    def findNodeToPay(self,tree, startNode = 1, amount = 100, user = self.user  ):
        tree = self.tree.node_set.all().order_by("-id")
        
        try:
            id = tree[0].id
        except:
            id = 1
        payoutOrder = []
        completed = []       
        

        nodesList = Node.objects.all().exclude(childrenMissing =0).order_by("childrenMissing")
        if user:
            nodesList = nodesList.filter(user = self.user)

        
        #finds the first node if user has zero nodes so far
        if not nodesList.exists() and Node.objects.all().exists():
            easiestNodeInWholeTree = self.findNodeToPay(amount = 1)[0]
            startNode = self.findFreeChild(easiestNodeInWholeTree)
        
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
                id = id,
                tree = tree,
                user = user, 
                number = number) 
            payoutOrder.append(newNode)
            amount -= 1
        #print(payoutOrder, "payoutorder")
        return payoutOrder