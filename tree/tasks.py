from celery import shared_task
from .models import Tree, Node
from .serializers import NodeSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .utilities import findRow, getX, getY
@shared_task
def buy(amount, user):
    
    payments = {1:{user: amount}}
    index =1
    serialized_data = []
    while bool(payments.get(index)):
        tree, created = Tree.objects.get_or_create(id = index, defaults = {"name":str(index),"json_string": json.dumps([])})
        #tree = Tree.objects.first()
    #next row update payments
        for k,v in payments[index].items():        
            for k, v in tree.buy(v,user = k).items():
                payments.setdefault(index+1,{})
                payments[index+1][k] = payments[index+1].get(k,0) + v     
            #payments = tree.buy(nodestobuy,user = user)
        index += 1

    for tree in Tree.objects.all():
        

        nodes = tree.node_set.all().order_by("-number")
        highestRow = findRow(nodes.first().number).get("rowNumber")

        serializer = NodeSerializer(nodes, many=True)
        for node in serializer.data:
            node["x"] = getX(node["number"])
            nodeRow = findRow(node["number"]).get("rowNumber")
            node["y"] = getY(nodeRow, highestRow)        
        serialized_data.append( serializer.data)
        tree.json_string = json.dumps(serializer.data)
        tree.save()


    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": json.dumps(serialized_data),
        }
    )

    '''    
    tree = Tree.objects.first()
    tree.buy(amount,1, user= user) 

    nodes = Node.objects.all()
    serializer = NodeSerializer(nodes, many=True)
    tree.json_string = json.dumps(serializer.data)
    tree.save()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": tree.json_string,
        }
    ) '''
