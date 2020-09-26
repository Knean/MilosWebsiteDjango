from .purchase_utils import *

def buy(tree,amount, startNode = None, user = 1, create = True): #look up model inheritance
    import pandas as pd
    import numpy as np
    import sys
    print(f"buying {amount} for the user: {user} in the tree: {self.id}")
    
    #tree = self
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
        
        node = getFirstFreeNode(payNode.name,id,tree.id,user,nodeSet)#naive as first node is not the best node
        createNode(nodeSet, node, id, tree.id, user)
        id += 1
        amount -=1
        #find the first free child of the easiest to pay Node
        startNode = node.name #payNode.name
        #update parents
        ancestors = [node["parent"] for node in parentGenerator(startNode)]  #use generator instead of list here
        nodeSet.loc[ancestors] = nodeSet.loc[ancestors].apply(updateParents, args = [startNode], axis = 1)
        
    #if the tree is empty the start node is 1
    if startNode == None and nodeSet.empty:            
        createNode(nodeSet, 1, id, tree.id, user)
        amount -= 1
        id += 1

    #while loop starts here
    while amount > 0:
        #getPaynode 
        payNode, created = get_or_create_payNode(nodeSet, startNode, user)
        if created:
            id+= 1                              
            amount -=1
            #update parents
            ancestors = [node["parent"] for node in parentGenerator(payNode.name)]  
            nodeSet.loc[ancestors] = nodeSet.loc[ancestors].apply(updateParents, args = [payNode.name], axis = 1)        
        
        
        
        #used nowhere         
        children, amountLeftover = planChildren(payNode, amount)                          
        amount = amountLeftover
        #payNode, children, nodeSet
        childrenStacks = decideChildren(payNode,children,nodeSet)            
        #generate nodes
        for node in childrenStacks:
            createNode(nodeSet, node, id, tree.id, user)
            id +=1 
        #update parents of nodes
        print(f"sold node: {payNode.name}, updating parents")                 
        for node in childrenStacks:                   
                ancestors = [node["parent"] for node in parentGenerator(node)]                                        
                nodeSet.loc[ancestors] = nodeSet.loc[ancestors].apply(updateParents, args = [node], axis = 1)
    

    #wrap up operations
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
    tree.json_string =nodeSet.loc[:,["userName","child1","child1Value","child2","child2Value","childrenMissing","parent","x","y"]].reset_index().to_json(orient="records")
    
    # save to database
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
    tree.save()
    return sold