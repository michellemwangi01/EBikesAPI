from django.urls import path
from .views import create_place, create_payload, create_order

urlpatterns = [
    path('create-place/', create_place, name='create-pickup'),
    path('create-payload/', create_payload, name='create-payload'),
     path('create-order/', create_order, name='create-order'),
]
