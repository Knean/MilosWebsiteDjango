from celery import shared_task
from .models import Tree, Node
from .serializers import NodeSerializer
@shared_task
def buy(amount, user):
    tree = Tree.objects.first()
    tree.buy(amount,1, user= user) 

    nodes = Node.objects.all()
    serializer = NodeSerializer(nodes, many=True)
    tree.json_string = serializer.data
    tree.save()