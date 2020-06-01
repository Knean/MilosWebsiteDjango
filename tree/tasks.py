from celery import shared_task
from .models import Tree, Node
from .serializers import NodeSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
@shared_task
def buy(amount, user):
    
    nodestobuy = amount
    index =1
    serialized_data = []
    while nodestobuy > 0:
        tree, created = Tree.objects.get_or_create(id = index, defaults = {"name":str(index),"json_string": json.dumps([])})
        #tree = Tree.objects.first()

        nodestobuy = tree.buy(nodestobuy,user = user)
        index += 1

    for tree in Tree.objects.all():
        nodes = tree.node_set.all()
        serializer = NodeSerializer(nodes, many=True)        
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
