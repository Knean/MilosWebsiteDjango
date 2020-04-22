from django.shortcuts import render, redirect
from django.http import HttpResponse
from tree import models
from tree.tasks import buy
from tree.forms import BuyForm
from tree.utilities import findParent
from authentication.forms import AuthForm, RegForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
# Create your views here.
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
        request, 'homePage/homePage.html',
        context ={"nodes":nodes, "form":form,"user":user, "userForm":userForm, "regForm":registrationForm})



def createTreeNode(request):
    tree = models.Tree.objects.all().first()
    form = BuyForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data["amount"]
    #tree.buy(amount,1, user = request.user.id) 
    buy.delay(amount = amount,user = request.user.id)    
    return redirect("home")

def resetTree(request):
    models.Node.objects.all().delete()
    tree = models.Tree.objects.first()
    tree.json_string = None
    tree.save()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tree", 
        {
        "type": "tree.data", 
        "text": tree.json_string,
        }
    )
    return redirect("home")

