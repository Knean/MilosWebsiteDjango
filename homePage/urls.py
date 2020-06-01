from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.displayHomePage, name='home'),
    path('gay', views.createTreeNode, name = 'creation'),
    path('delete',views.resetTree, name = 'delete'),
    path('auth/', include ("authentication.urls"))
]