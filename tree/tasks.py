from celery import shared_task
from .models import Tree
@shared_task
def buy(amount, user):
    tree = Tree.objects.first()
    tree.buy(amount,1, user= user) 
    tree.json_string = "aaaaaaaaa"
    tree.save()