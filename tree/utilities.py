def findChildren(number):
    if number == 1:
        return [2,3]
    if number %2 == 0:
        return[number *2 +2, number *2, ]
    if number % 2 ==1:
        return [number*2 -1, number *2 +1]

def findParent(Node):
    #returns plain number
    if Node %2 == 0:
        parent = int(Node / 2)
        if not parent % 2 == 0 and not parent == 1:
            parent -= 1
    else:
        if Node == 1:
            return None
        parent = int(Node /2)
        if parent % 2 == 0:
            parent += 1
    return parent

def getRow(startNode, rowNumber):
    rowNumber  = rowNumber 
    
    if startNode == 1:
        limits = [2, 3]
        centerTwo = [2,3]
        while rowNumber >0:
            limits = [limits[0] *2 +2, limits[1] * 2 +1]
            rowNumber -=1

            center = int(limits[0] /2)
            centerTwo =[center +1, center +2]   
        return limits, centerTwo

    if startNode % 2 == 1 and startNode != 1:        
        limits = [startNode * 2 -1, startNode * 2 +1]
        while rowNumber >0:
            limits = [limits[0] *2 -1, limits[1] * 2 +1]
            rowNumber -=1
        center = int(limits[0] + (limits [1] - limits[0])/2)
        centerTwo =[center -1, center +1]   
        return limits, centerTwo

    if startNode % 2 == 0:
        limits = [startNode * 2 +2, startNode * 2 ]
        while rowNumber >0:
            limits = [limits[0] *2 +2, limits[1] * 2]
            rowNumber -=1
        center = int((limits[0] - limits[1] )/2)
        centerTwo =[limits[1]+ center +1, limits[1] + center -1]   
        return limits, centerTwo
def getFreeNode(user = None):
    suggestedNode = 1;
    while True:
        if not suggestedNode in tree:
            return suggestedNode
        else:
            suggestedNode += 1

def nodeGenerator(startNode = 1):
    row = 0
    yield startNode   
        
    if startNode ==1:
        while True:
            limits, centerTwo = getRow(startNode,row)
            smallerNode = centerTwo[0]
            largerNode = centerTwo[1]
            while smallerNode <= limits[0]:                
                yield smallerNode                  
                              
                yield largerNode                   

                smallerNode +=2
                largerNode += 2
            row += 1

            limits, centerTwo = getRow(startNode,row)        
        
    
    if startNode % 2 == 1 and not startNode == 1:    
        while True:
            limits, centerTwo = getRow(startNode,row)
            smallerNode = centerTwo[0]
            largerNode = centerTwo[1]
            while smallerNode >= limits[0]:             
                
                                   
                yield smallerNode                                   
                              
                yield largerNode                 


                smallerNode -=2
                largerNode += 2
            row += 1

            limits, centerTwo = getRow(startNode,row)
        
            
    if startNode % 2 == 0:    
        while True:
            limits, centerTwo = getRow(startNode,row)
            
            upperNode = centerTwo[0] 
            lowerNode = centerTwo[1] 
            while lowerNode >= limits[1]:               
                                
                yield upperNode                
                                 
                yield lowerNode                    

                upperNode +=2
                lowerNode -= 2
            row += 1
            limits, centerTwo = getRow(startNode,row)

def parentGenerator(Node):
    
    while True:
        if Node ==1:            
            break
            
        if Node %2 == 0:
            parent = int(Node / 2)
            if not parent % 2 == 0 and not parent == 1:
                parent -= 1
                
            yield {"parent":parent, "child":Node}
            Node = parent
            
        if Node %2 == 1 and not Node == 1:
            parent = int(Node /2)
            if parent % 2 == 0:
                parent += 1
            yield {"parent":parent, "child":Node}
            Node = parent

def childOf(parent, child):
    if parent == child:
        return True
    generator = parentGenerator(child)
    for gen_parent in generator:
        if gen_parent ["parent"] == parent:
            
            return True
    return False

def identifyParent(node, *args):
    #which argument is the nodes parent
    for parent in args:
        if parent == node:
            return parent
    generator = parentGenerator(node)
    while True:
        node = next(generator)        
        for parent in args:
            if parent == node["parent"]:
                return parent


def findRow(nodeNumber, startNode =1):
    #potential infinite loop D:
    if nodeNumber == startNode:
        return {"rowNumber":0, "limits": {"even_limits": None, "odd_limits": None}, "size":1,"index" : 0}

    if startNode == 1:

        rowNumber  = 1
        limits = [2, 3]
        nodes_in_row = 2
        even_limits = [2,2]
        odd_limits = [3,3]
        while not (nodeNumber >limits[0]/2 and nodeNumber <= limits[1]):
            limits = [limits[0] *2 +2, limits[1] * 2 +1]
            even_limits = [int(limits [0]/2) + 1, limits[0]]
            odd_limits = [int(limits[0]/2) +2, limits[1]]       
            rowNumber +=1
            nodes_in_row = int(limits[1]- limits[0]/2)
        #return rowNumber, [even_limits, odd_limits], 
        row = {
            "rowNumber":rowNumber, 
            "limits": {
                "even_limits": even_limits, 
                "odd_limits": odd_limits},
            "size":limits[1] - limits[0]+1,
            "index": nodeNumber - 1
        }
        return row
    if startNode % 2 == 1:
        rowNumber  = 1
        index = 0
        limits = [startNode*2 -1, startNode *2 +1]
        
        while not (nodeNumber >=limits[0] and nodeNumber <= limits[1]):
            rowNumber +=1
            index += (limits[0]+1)/2 -1            
            limits[0] = limits[0] * 2 -1
            limits[1] = limits [1] *2 +1
        middle = limits[0] + (limits[1]-limits[0])/2        
        if nodeNumber < middle:
            index += middle - nodeNumber            
        if nodeNumber > middle:
            index +=  nodeNumber - middle +1
        row = {
            "rowNumber":rowNumber, 
            "limits": limits,
            "size":(limits[1] - limits[0])/2+1,
            "index": index
        }
        return row
    if startNode % 2 == 0:       
        rowNumber  = 1
        index = 0
        limits = [startNode*2 +2, startNode *2]
        while not (nodeNumber >=limits[1] and nodeNumber <= limits[0]):
            rowNumber +=1
            index += limits[1]/2            
            limits[0] = limits[0] * 2 +2
            limits[1] = limits [1] *2 
        middle = limits[0] - ((limits[0] - limits[1])/2)          
        if nodeNumber < middle:
            index += middle - nodeNumber +1         
        if nodeNumber > middle:
            index +=  nodeNumber - middle
        row = {
            "rowNumber":rowNumber, 
            "limits": limits,
            "size":(limits[1] - limits[0])/2+1,
            "index": index
        }
        return row
def getIndex(finish, start = 1):
    return findRow(finish, start)["index"]


def getX(nodeNumber):
    if nodeNumber == 1:
        return 0.5
    row = findRow(nodeNumber)
    
    if nodeNumber % 2 == 1:
        #all even numbers are considered smaller
        smaller_even_numbers = row["limits"]["even_limits"][0] / 2
        smaller_odd_numbers = ( nodeNumber - row["limits"]["odd_limits"][0] )/2
    else:
        smaller_even_numbers = (row["limits"]["even_limits"][1] - nodeNumber)/2
        smaller_odd_numbers = 0 
    

        
  
    smaller_numbers_sum = smaller_odd_numbers + smaller_even_numbers        
    nodes_sum = row["limits"]["even_limits"][0]
    #fairCut = 1/ (nodes_sum + 2)
    fairCut = 1/ (nodes_sum)
    #fraction of all the smaller numbers which counts in the two borders as well
    #location = fairCut* (smaller_numbers_sum + 1) + fairCut/2
    location = fairCut* (smaller_numbers_sum) + fairCut/2
    return round(location, 5)   
    

def getY(row, rowCount):
    row = findRow(row).get("rowNumber")
    rowCount = findRow(rowCount).get("rowNumber")
    if rowCount == 0:
        return 0
    fairCut = 1/rowCount
    return row * fairCut

def parentOf(parent,node):
    if parent == node:
        return True
    for node in parentGenerator(node):
        if node["parent"] == parent:
            return True
    return False