from .utilities import *
def createNode(nodeSet, node, id, tree_id, user):
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
            'value': 299,#what is this for? 
            }
        nodeSet.loc[node] = row
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
            return node
def get_or_create_payNode(nodeSet, startNode, user):
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
        return payNode, False
    else:
        #if empty -> find first free node of the startNode to buy and set as the payNode 
        
        payNode = getFirstFreeNode(startNode,id,tree.id,user,nodeSet)# this one is fine
        createNode(nodeSet, node, id, tree.id, user)
        #bad separation
        return nodeSet.loc[payNode], True   

def planChildren(payNode, amount):
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
    return children, amount        

def decideChildren(payNode, children, nodeSet):
    
    #arguments could be simplified
    generator = nodeGenerator(payNode.name)
    child = 0
    childToggle ={0:1,1:0}
    childrenStacks = [[],[]]
    pay = children.pay.sum()    
    #invest points
    #pay is the total amount for a single node
    while pay > 0 :   
        child = childToggle[child]                 
        potentialNode = next(generator)                   
        if not potentialNode in nodeSet.index:        
            if len(childrenStacks[child]) < children.iloc[child,-1]:
                childrenStacks[child].append(potentialNode)
                pay -= 1          
    childrenStacks = childrenStacks[0] + childrenStacks[1] 
    return childrenStacks
        