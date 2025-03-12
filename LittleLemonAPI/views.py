from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import MenuItem
from .serializers import MenuItemSerializer

# Create your views here.
class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    search_fields = ['title', 'category__title']
    
    def get_throttles(self):
        if self.action == 'create':
            throttle_classes = [UserRateThrottle]
            
        else:
            throttle_classes = []
            
        return [throttle() for throttle in throttle_classes]
    