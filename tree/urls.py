from django.urls import path, include
from homePage.views import displayHomePage
from .views import buy
urlpatterns = [
    path('buy/', buy),

   

]
