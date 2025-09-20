from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import AreaComun, Inventario, VerificacionInventario, Reserva
from .serializers import AreaComunSerializer, InventarioSerializer, VerificacionInventarioSerializer, ReservaSerializer

class AreaComunViewSet(viewsets.ModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer

class VerificacionInventarioViewSet(viewsets.ModelViewSet):
    queryset = VerificacionInventario.objects.all()
    serializer_class = VerificacionInventarioSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
