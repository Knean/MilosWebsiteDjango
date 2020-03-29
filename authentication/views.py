from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User


from .forms import AuthForm, RegForm
from homePage.views import displayHomePage
# Create your views here.
def loginView(request):
    form = AuthForm(request.POST)
    
    if form.is_valid():       
        user = authenticate(request, username= form.cleaned_data["name"], password = form.cleaned_data["password"])
        if user:
            login(request, user)
    if user == None:
        form.add_error(field = None, error ="password or name could be wrong")
    return redirect("home")

def logoutView(request):
    logout(request)
    return redirect("home")

def registerView(request):
    form = RegForm(request.POST)
    if form.is_valid():
        user = User.objects.create_user(username = form.cleaned_data["name"], password = form.cleaned_data["password1"])
        user.save()
        login(request, user)
        return redirect("home")
    else:
        return redirect("home",registrationForm = form)
    
    #validate form
    #return form with errors


