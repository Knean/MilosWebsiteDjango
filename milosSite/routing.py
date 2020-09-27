from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from tree.consumers import TreeConsumer

application = ProtocolTypeRouter({
       "websocket": URLRouter([
        path("treeChannel/<target>/", TreeConsumer,{"argument":"answer"}),
      
    ]),
        
   
    # Empty for now (http->django views is added by default)
})