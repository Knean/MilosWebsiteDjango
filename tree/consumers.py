from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio

from .models import Tree
class TreeConsumer(WebsocketConsumer):
    
    def connect(self):
        print(self.scope["url_route"])
        self.accept()
        print ("connection made")
        async_to_sync(self.channel_layer.group_add)("tree", self.channel_name)

        tree = Tree.objects.first()
        async_to_sync(self.channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": tree.json_string,
        }
    )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("tree", self.channel_name)

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
        "tree",
        {
            "type": "tree.data",
            "text": text_data,
        },
    )

    def tree_data(self, event):
        self.send(text_data=event["text"])