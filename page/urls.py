from django.urls import path 
from .views import *

urlspatterns = [
    path('',home, name='home'),
    
]