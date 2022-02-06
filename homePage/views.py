from django.shortcuts import render, redirect
from django.http import HttpResponse
from tree import models
from tree.tasks import buy
from tree.forms import BuyForm
from tree.utilities import findParent
from authentication.forms import AuthForm, RegForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from tree.serializers import NodeSerializer
import json
# Create your views here.
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@ensure_csrf_cookie
def displayHomePage(request, userForm = None, registrationForm = None):
    if userForm ==None:
        userForm = AuthForm()
    if registrationForm == None:
        registrationForm = RegForm()
    tree = models.Tree.objects.all().first()    
    nodes = models.Node.objects.all()
    dataDictionaryList = []
    form = BuyForm()
    user = request.user
    
    return render(
        request, 'homePage/index.html',
        context ={"nodes":nodes, "form":form,"user":user, "userForm":userForm, "regForm":registrationForm})


def createTreeNode(request):
    print("node created")
    tree = models.Tree.objects.all().first()
    form = BuyForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data["amount"]
    #tree.buy(amount,1, user = request.user.id) 
    buy(amount = amount,user = request.user.id)    
    return redirect("home")

def resetTree(request):
    serialized_data = []
    models.Node.objects.all().delete()
    models.Tree.objects.all().delete()    
    nodes = models.Node.objects.all()
    serializer = NodeSerializer(nodes, many=True)        
    serialized_data.append( serializer.data)
    json_string = json.dumps(serialized_data)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": json_string,
        }
    )
    return redirect("home")
@csrf_exempt
@api_view(['POST'])
def requestListener(request):
    print("this is the request that came through request Listner:")
    print(request)
    print(request.body)
    print(request.POST)
    print(request.META)
    return (HttpResponse("this is a request listener, thanks"))

