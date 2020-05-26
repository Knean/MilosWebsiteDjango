from django.urls import path, include

from . import views

urlpatterns = [
    path('logout/',views.logoutView, name ="logout"),
    path('login/',views.loginView, name= "login"),
    path('register/',views.registerView, name = "register"),
    path('user/',views.getUser, name = "get_user")  
]