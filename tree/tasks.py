from celery import shared_task
from .models import Tree
@shared_task
def buy(amount, user):
    Tree.objects.first().buy(amount= amount, user= user) 