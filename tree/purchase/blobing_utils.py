def merge_blobs(blobs):
    #section.sort_index(inplace = True)
    fat_node = blobs[0]
    last_node = blobs[1]
    fat_node.grow_to = last_node.x
    fat_node.number = last_node.number
    return fat_node

def nodes_match(first, second):
    return (
        second.name == first.name + 1 
        and first.userName == second.userName
        and first.sold ==second.sold        
        )