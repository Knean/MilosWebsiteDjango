from celery import shared_task
from .models import Tree, Node
from .serializers import NodeSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
@shared_task
def buy(amount, user):
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
        "type": "chat.message", 
        "text": tree.json_string,
        }
    )
