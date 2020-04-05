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
    generator = parentGenerator(child)
    for gen_parent in generator:
        if gen_parent ["parent"] == parent:
            
            return True
    return False