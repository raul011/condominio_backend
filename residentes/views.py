from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets
from .models import Residente, Unidad, Visita, Notificacion
from .serializers import ResidenteSerializer, UnidadSerializer, VisitaSerializer, NotificacionSerializer

class ResidenteViewSet(viewsets.ModelViewSet):
    queryset = Residente.objects.all()
    serializer_class = ResidenteSerializer

class UnidadViewSet(viewsets.ModelViewSet):
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer

class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
