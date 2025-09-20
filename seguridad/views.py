from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import RegistroSeguridad, Reclamo
from .serializers import RegistroSeguridadSerializer, ReclamoSerializer

class RegistroSeguridadViewSet(viewsets.ModelViewSet):
    queryset = RegistroSeguridad.objects.all()
    serializer_class = RegistroSeguridadSerializer

class ReclamoViewSet(viewsets.ModelViewSet):
    queryset = Reclamo.objects.all()
    serializer_class = ReclamoSerializer
