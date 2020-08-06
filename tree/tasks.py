from celery import shared_task
from .models import Tree, Node
from .serializers import NodeSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .utilities import findRow, getX, getY
@shared_task
def buy(amount, user):
    index = 1
    tree, created = Tree.objects.get_or_create(id = index, defaults = {"name":str(index),"json_string": json.dumps([])})
    tree.buy(amount = amount,user = user, startNode = None)
    serialized_data = "["
    for tree in Tree.objects.all():       
        serialized_data +=tree.json_string
    serialized_data += "]"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": serialized_data,
        }
    )
