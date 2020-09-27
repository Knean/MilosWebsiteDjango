from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from tree.serializers import NodeSerializer
import json
import asyncio

from .models import Tree, Node
class TreeConsumer(WebsocketConsumer):
    
    def connect(self):
        print(self.scope["url_route"]," this is the socket route")
        target = self.scope["url_route"]["kwargs"]["target"]
        self.accept()
        print ("connection made")
        async_to_sync(self.channel_layer.group_add)(target, self.channel_name)
        
        if target =="tree":
            serialized_data = []
            if Tree.objects.all().exists():
                print("there are trees")
                for tree in Tree.objects.all():       
                    serialized_data.append(json.loads( tree.json_string))#retarded
            else:
                print("no trees")
                nodes = Node.objects.all()
                serializer = NodeSerializer(nodes, many=True)        
                serialized_data.append( serializer.data)           
                
            tree = Tree.objects.first()
            #sends to everyone????
            async_to_sync(self.channel_layer.group_send)(
            "tree", 
            {
            "type": "tree.data", 
            "text": json.dumps(serialized_data),
            }
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("tree", self.channel_name)
        async_to_sync(self.channel_layer.group_discard)("task", self.channel_name)

    def receive(self, text_data):
        print("receieve happened")
        async_to_sync(self.channel_layer.group_send)(
        "tree",
        {
            "type": "tree.data",
            "text": text_data,
        },
    )

    def tree_data(self, event):
        self.send(text_data=event["text"])