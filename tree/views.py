from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Node
from .serializers import NodeSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
# Create your views here.
@api_view(['GET'])
def node_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def user_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)