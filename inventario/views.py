from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import CategoriaInventario
from .serializers import CategoriaInventarioSerializer

class CategoriaInventarioViewSet(viewsets.ModelViewSet):
    queryset = CategoriaInventario.objects.all()
    serializer_class = CategoriaInventarioSerializer
