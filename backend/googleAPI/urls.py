from django.urls import path
from . import views

urlpatterns = [
    path('calculate-distance/', views.calculateDistanceView.as_view(), name='calculate_distance'),

]