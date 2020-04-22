from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio
class TreeConsumer(WebsocketConsumer):
    
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("tree", self.channel_name)

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