from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Node, Tree
from .serializers import NodeSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from . import tasks
import json
from django.conf import settings
# Create your views here.
@api_view(['GET'])
def node_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        #nodes = Node.objects.all()
        #serializer = NodeSerializer(nodes, many=True)
        tree = Tree.objects.first()
        #return Response(serializer.data)
        #return Response(json.loads(tree.json_string or '{}'))
        return Response(tree.json_string)

@csrf_exempt
@api_view(['GET'])
def user_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        users = User.objects.all()
        print("someone requested the users")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def buy(request):
    print("node created")
    #tree = model.Tree.objects.all().first()
    #GET THIS FROM THE POST
    amount = int(request.data.get("amount"))        
    #tree.buy(amount,1, user = request.user.id) 
    print(request.user.id, " is buying: ", amount)  
    # we dont use celery locally
    if settings.LOCAL_DEPLOYMENT:
        tasks.buy(amount = amount,user =3)
        '''         try:
            print(request.user.id, " 'tis the id")
            tasks.buy(amount = amount,user =request.user.id)

        except:
            tasks.buy(amount = amount,user =1) '''
    else:
        tasks.buy.delay(amount = amount,user =request.user.id)  
    return Response(data= None, status = 200)  