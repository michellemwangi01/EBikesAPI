from django.urls import path
from . import views

urlpatterns = [
    path('calculate-distance/', views.calculate_distance, name='calculate_distance'),
]