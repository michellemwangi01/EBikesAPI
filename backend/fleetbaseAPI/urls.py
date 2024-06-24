from django.urls import path
from .views import CreatePlaceView, CreatePayloadView, CreateOrderView
from . import views
urlpatterns = [
    path('', views.status, name='status'),
    path('create-place/', CreatePlaceView.as_view(), name='create-pickup'),
    path('create-payload/', CreatePayloadView.as_view(), name='create-payload'),
     path('create-order/', CreateOrderView.as_view(), name='create-order'),
]
