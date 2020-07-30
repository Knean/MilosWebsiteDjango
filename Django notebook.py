#!/usr/bin/env python
# coding: utf-8

# In[2]:


import django
django.setup()
from tree.models import Tree, Node

import os
from django.contrib.auth.models import User
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

#python manage.py shell_plus --notebook


# In[89]:


import pandas as pd
import numpy as np
import sys
tree = Tree.objects.first()
nodes = tree.node_set.all().values_list()
nodeSet = pd.DataFrame.from_records(
    nodes, 
    columns = ["id","tree_id","childrenMissing","number","user_id","child1","child1Value","child2","child2Value"],
    index="number")
nodeSet["value"]= nodeSet["child1Value"] + nodeSet["child2Value"]
nodeSet.insert(1,"changed", False)
nodeSet.insert(1,"sold", False)
nodeSet


# get the __ID__

# In[4]:


id = nodeSet.id.max() + 1
#gotta test this
id = id if not np.isnan(id) else 1


# find easiest node to pay __findNodeToPay__

# In[5]:


from tree.utilities import childOf, nodeGenerator, getIndex
#randomly picked start index
startNode = 1 # start node can only be picked but not created
nodeSet.sort_values(by = "childrenMissing", inplace =True)
mask1 = nodeSet.childrenMissing != 0
mask2 = nodeSet.apply(lambda node : childOf(startNode, node.name) , axis=1)
smallest = nodeSet.loc[mask1 & mask2, "childrenMissing"].min()
allSmalls = nodeSet.loc[nodeSet.childrenMissing == smallest,:].copy()
allSmalls["index"] = allSmalls.apply(lambda node: getIndex(node.name, startNode), axis=1)
allSmalls.sort_values("index", inplace = True)
payNode = allSmalls.iloc[0]
payNode


# __Make Children Table__

# In[27]:


# this amount is the number of nodes the user buys
targetValue = 31
# ideally each child would be eat least 31
#using copy just for testing
#children = nodeSet.loc[[payNode.child1, payNode.child2]].copy()
children = pd.DataFrame([
    [payNode.child1, payNode.child1Value],
    [payNode.child2, payNode.child2Value]],
    columns = ["number","value"])
#if child does not exist it will throw error

children["index"] = children.apply(lambda kid: getIndex(kid.number, payNode.name), axis = 1)
children["pay"] = 0
#children.sort_values("index")
children.iloc[1,-3] = 3
children.sort_values(by=["value", "index"], inplace = True) #index not necessary?
children


# __distribute an amount__
# 
# figure out how many nodes go under each side

# In[28]:


amount = 20

#equalize children

childDifference = children.iloc[1].value - children.iloc[0].value
#this might be pointless because the smaller one is always at the top
valueMissing = max(targetValue - children.iloc[0].value, 0)
pay = min(childDifference,valueMissing, amount)
firstChild += pay
amount -= pay
children.iloc[0,-1]+= pay
children.iloc[0,-3]+= pay

children.sort_values(by=["index"], inplace = True)
# attempt to reach target

valueMissing = max(targetValue - children.iloc[0].value, 0) *2
pay = min(amount, valueMissing)
amount -= pay
half = int(pay/2)
children.iloc[[0,1],[-1, -3]] += half
secondChild += half
leftover = pay - (half*2)
children.iloc[[0],[-1, -3]] +=leftover #leftover is 1 or 0


first_child_until_pay = max(targetValue - children.iloc[0].value, 0)

children


# __pick the right node numbers__

# In[45]:


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
print(childrenStacks)
childrenStacks = childrenStacks[0] + childrenStacks[1] #merge them as it doesnt matter later on in code


# __append rows__

# In[51]:



for node in childrenStacks:
    generator = nodeGenerator(node)
    next(generator) # skip the first one
    id +=1 #### flawed if there are multiple trees
    row = {
    'id': id,
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
    
nodeSet.loc[129]


# __Update Parents__

# In[60]:


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


# In[ ]:




