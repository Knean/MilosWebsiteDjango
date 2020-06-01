from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import AuthForm, RegForm
from homePage.views import displayHomePage
from .serializers import UserSerializer
# Create your views here.
""" def loginView(request):
    form = AuthForm(request.POST)
    
    if form.is_valid():       
        user = authenticate(request, username= form.cleaned_data["name"], password = form.cleaned_data["password"])
        if user:
            login(request, user)
    if user == None:
        form.add_error(field = None, error ="password or name could be wrong")
    return redirect("home") """

@api_view(['POST'])
@csrf_exempt
def loginView(request):
    #print(request.META['HTTP_X_CSRFTOKEN'], 'loooooooooooooooooooogin')
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    print("tried to login")
    if user is not None:
        login(request, user)
        return Response(data= None, status = 200)        
    else:
        # Return an 'invalid login' error message.
        return Response(data= None, status = 404)   

@csrf_exempt
@api_view(['GET'])
def logoutView(request):
    logout(request)
    return Response(data= None, status = 200)


@csrf_exempt
@api_view(['POST'])
def registerView(request):
    """     form = RegForm(request.POST)
    if form.is_valid():
        user = User.objects.create_user(username = form.cleaned_data["name"], password = form.cleaned_data["password1"])
        user.save()
        login(request, user)
        return redirect("home") """
    #insecure data is not cleaned!
    username = request.data.get('username')
    password = request.data.get('password')
    new_user = User.objects.create_user(username,'',password)
    new_user.save()
    return Response(data= None, status = 201)


@api_view(['GET'])
@csrf_exempt
def getUser(request):
    user = request.user
    print(request.user.username)
    print( " fuck ")
    return Response(data = UserSerializer(user).data, status = 201)




