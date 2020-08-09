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
        #merge result dictionary with the current one
        for k,v in payments[index].items():       
            for k, v in tree.buy(amount = v,user = k).items():
                payments.setdefault(index+1,{})
                payments[index+1][k] = payments[index+1].get(k,0) + v   #           
        index += 1 # fucked
    serialized_data = "["
    for tree in Tree.objects.all():              
        serialized_data +=tree.json_string
        serialized_data +="," 
    serialized_data = serialized_data[:-1]   
    serialized_data += "]"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": serialized_data,
        }
    )
