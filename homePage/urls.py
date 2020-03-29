from django.urls import path

from . import views
from authentication.views import loginView, logoutView, registerView
urlpatterns = [
    path('', views.displayHomePage, name='home'),
    path('gay', views.createTreeNode, name = 'creation'),
    path('delete',views.resetTree, name = 'delete'),
    path('logout',logoutView, name ="logout"),
    path('login',loginView, name= "login"),
    path('register',registerView, name = "register")
]