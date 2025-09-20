from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Comunicado
from .serializers import ComunicadoSerializer

class ComunicadoViewSet(viewsets.ModelViewSet):
    queryset = Comunicado.objects.all()
    serializer_class = ComunicadoSerializer
